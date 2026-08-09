"""Preview server: HTTP + WebSocket for browser-based live preview.

Extracted from DirectManimSession methods:
  - start_preview (l1108-1188)
  - stop_preview (l1394-1407)
  - ensure_preview_visible (l1190-1204)
  - ensure_terminal (l1206-1228)
  - _serve_preview (l1230-1253)
  - _process_http_request (l1286-1381)
  - _PREVIEW_HTML (l1069-1106)
"""
import asyncio
import base64
import json
import logging
import threading
import time
import webbrowser
from typing import Any, Dict

from ..logging import close_render_terminal, launch_render_terminal, terminal_processes
from ..project import (
    PROJECTS_DIR,
    find_available_port,
    is_port_available,
    load_port_info,
    load_state,
)
from ..render import encode_frame
from .websocket import handle_ws

try:
    from websockets.asyncio.server import serve as ws_serve
    _WS_AVAILABLE = True
    import logging as _ws_log
    _ws_log.getLogger('websockets').setLevel(logging.CRITICAL)
except ImportError:
    _WS_AVAILABLE = False

logger = logging.getLogger(__name__)

# ── Preview HTML (class constant → module constant) ──────────────

_PREVIEW_HTML = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Manim Live Preview</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;background:#0d0d0d;overflow:hidden}
body{display:flex;flex-direction:column;font-family:'Segoe UI',system-ui,sans-serif;color:#e0e0e0}
#header{flex:0 0 auto;display:flex;align-items:center;gap:10px;padding:6px 16px;background:#1a1a1a;border-bottom:1px solid #333}
#dot{width:8px;height:8px;border-radius:50%;background:#555;transition:background .3s}
#dot.live{background:#00e676;box-shadow:0 0 8px #00e676}
#status{font-size:12px;color:#666;letter-spacing:2px;font-weight:600}
#status.live{color:#00e676}
#project{font-size:12px;color:#aaa;background:#2a2a2a;padding:2px 10px;border-radius:10px;border:1px solid #444;letter-spacing:1px;font-weight:600}
#fps{font-size:11px;color:#555;margin-left:auto}
#res{font-size:11px;color:#555;margin-left:8px}
#img-wrap{flex:1 1 auto;display:flex;align-items:center;justify-content:center;min-height:120px;overflow:hidden;padding:4px;background:#000}
#img-wrap img{width:100%;height:100%;object-fit:contain;display:block}
</style></head><body>
<div id="header"><div id="dot"></div><div id="status">CONNECTING</div><div id="project">__PROJECT__</div><div id="fps"></div><div id="res"></div></div>
<div id="img-wrap"><img id="cv" src="" alt=""></div>
<script>
const cv=document.getElementById('cv'),dot=document.getElementById('dot'),st=document.getElementById('status'),fpsEl=document.getElementById('fps'),resEl=document.getElementById('res');
let lastUrl='',frameCount=0,lastFpsTime=0;
cv.onload=()=>{if(cv.naturalWidth>0){resEl.textContent=cv.naturalWidth+'×'+cv.naturalHeight}};
function setLive(live){st.textContent=live?'LIVE':'RECONNECTING';st.className=live?'live':'';dot.className=live?'live':''}
const wsProto=location.protocol==='https:'?'wss:':'ws:';
const wsUrl=wsProto+'//'+location.host+'/ws';
let ws=null,retryMs=500,reconnectTimer=null;
function connectWs(){if(ws){try{ws.close()}catch(e){}}ws=new WebSocket(wsUrl);ws.binaryType='arraybuffer';
ws.onopen=()=>{setLive(true);retryMs=500};
ws.onclose=()=>{setLive(false);reconnectTimer=setTimeout(connectWs,retryMs);retryMs=Math.min(retryMs*1.5,3000)};
ws.onerror=()=>{try{ws.close()}catch(e){}};
ws.onmessage=(e)=>{if(typeof e.data==='string'){try{const d=JSON.parse(e.data)}catch(err){}}else{
const buf=new Uint8Array(e.data);if(buf[0]===0x01){const mimeLen=buf[1];const mime=new TextDecoder().decode(buf.slice(2,2+mimeLen));
const frameData=buf.slice(2+mimeLen);if(lastUrl)URL.revokeObjectURL(lastUrl);const blob=new Blob([frameData],{type:mime});
lastUrl=URL.createObjectURL(blob);cv.src=lastUrl;setLive(true);frameCount++;const now=performance.now();
if(now-lastFpsTime>1000){fpsEl.textContent=Math.round(frameCount*1000/(now-lastFpsTime))+' fps';frameCount=0;lastFpsTime=now}}}}}
connectWs();
function pollFrame(){if(!ws||ws.readyState!==WebSocket.OPEN){fetch('/frame').then(r=>r.json()).then(d=>{if(d.data&&d.data!==lastB64){lastB64=d.data;cv.src='data:'+(d.mime||'image/jpeg')+';base64,'+d.data;setLive(true)}}).catch(()=>{})}setTimeout(pollFrame,2000)}
let lastB64='';setTimeout(pollFrame,1000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&(!ws||ws.readyState!==WebSocket.OPEN)){if(reconnectTimer)clearTimeout(reconnectTimer);connectWs()}});
</script></body></html>"""


# ── Public functions ──────────────────────────────────────────────

def start_preview(session, port: int = 0) -> Dict[str, Any]:
    """Start the browser preview server (WebSocket + HTTP).

    If port=0, auto-discovers the best available port:
    1. Try saved port from port.info (cross-conversation reconnection)
    2. Try saved port from state.json
    3. Find any available port in 8700-8800 range

    If the preview server thread has crashed (daemon thread died),
    automatically restarts it.

    Returns dict with 'success', 'port', 'preview_url', 'port_source'.
    """
    if not _WS_AVAILABLE:
        return {"success": False, "error": "websockets package not installed"}

    # 检测预览服务器线程是否已崩溃 — 如果 daemon 线程死了但 _preview_running 仍为 True
    if session._preview_running and session._preview_thread is not None:
        if not session._preview_thread.is_alive():
            logger.warning("Preview server thread crashed, restarting...")
            session._preview_running = False
            session._preview_port = None
            session._ws_server = None
            session._ws_clients.clear()
            # 继续往下重启

    if session._preview_running:
        return {
            "success": True,
            "already_running": True,
            "port": session._preview_port,
            "preview_url": f"http://127.0.0.1:{session._preview_port}/preview",
        }

    port_source = "specified"
    if port == 0:
        port_info = load_port_info(session.project)
        if port_info and port_info.get("preview_port"):
            saved_port = port_info["preview_port"]
            if is_port_available(saved_port):
                port = saved_port
                port_source = "port.info"
                logger.info("Reusing saved port %d from port.info for project '%s'",
                           saved_port, session.project)

        if port == 0:
            state = load_state(session.project)
            if state and state.get("preview_port"):
                saved_port = state["preview_port"]
                if is_port_available(saved_port):
                    port = saved_port
                    port_source = "state.json"
                    logger.info("Reusing saved port %d from state.json for project '%s'",
                               saved_port, session.project)

        if port == 0:
            port = find_available_port()
            port_source = "auto"
            logger.info("Auto-discovered port %d for project '%s'", port, session.project)

    def _run_preview_server():
        session._preview_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(session._preview_loop)
        try:
            session._preview_loop.run_until_complete(_serve_preview(session, port))
        except RuntimeError as exc:
            if "Event loop stopped" in str(exc):
                logger.debug("Preview server event loop stopped during shutdown")
            else:
                logger.error("Preview server RuntimeError: %s", exc)
        except Exception as exc:
            logger.error("Preview server crashed unexpectedly: %s", exc)
        finally:
            session._preview_running = False

    session._preview_thread = threading.Thread(target=_run_preview_server, daemon=True)
    session._preview_thread.start()

    for _ in range(50):
        if session._preview_port is not None:
            break
        time.sleep(0.1)

    if session._preview_port is None:
        return {"success": False, "error": "Preview server failed to start"}

    preview_url = f"http://127.0.0.1:{session._preview_port}/preview"
    logger.info("[manim-web | %s] Preview: %s (source: %s)", session.project, preview_url, port_source)
    try:
        webbrowser.open(preview_url)
    except Exception:
        pass

    try:
        session.auto_save_workspace()
    except Exception:
        pass

    return {
        "success": True,
        "port": session._preview_port,
        "preview_url": preview_url,
        "port_source": port_source,
    }


def stop_preview(session) -> Dict[str, Any]:
    """Stop the preview server gracefully.

    Uses ``run_coroutine_threadsafe`` to close the WebSocket server on the
    event-loop thread, then lets the loop finish naturally when
    ``_serve_preview`` returns.  This avoids the ``RuntimeError: Event loop
    stopped before Future completed`` that occurred when ``loop.stop()`` was
    called while ``_serve_preview`` was still awaiting ``wait_closed()``.
    """
    session._preview_running = False
    session._ws_clients.clear()

    ws_server = session._ws_server
    session._ws_server = None

    loop = session._preview_loop
    if ws_server is not None and loop is not None and loop.is_running():
        async def _graceful_close():
            try:
                await ws_server.close()
            except Exception:
                pass

        try:
            asyncio.run_coroutine_threadsafe(_graceful_close(), loop)
        except Exception:
            pass
        # Do NOT call loop.stop() — let the event loop finish naturally
        # when _serve_preview returns after ws_server.wait_closed() completes.

    session._preview_port = None
    return {"success": True, "message": "Preview server stopped"}


def ensure_preview_visible(session) -> Dict[str, Any]:
    """Re-open the browser tab for the preview server.

    Call this when the session is already running but the browser was closed.
    Always opens a new tab — the preview server is still running.
    """
    if not session._preview_running or session._preview_port is None:
        return {"success": False, "error": "Preview server not running"}
    preview_url = f"http://127.0.0.1:{session._preview_port}/preview"
    try:
        webbrowser.open(preview_url)
        logger.info("[manim-web | %s] Re-opened browser: %s", session.project, preview_url)
    except Exception as e:
        logger.warning("Failed to open browser: %s", e)
    return {"success": True, "preview_url": preview_url, "port": session._preview_port}


def ensure_terminal(session, force: bool = False) -> Dict[str, Any]:
    """Ensure the render log terminal is visible.

    If the terminal process died or was closed, re-launch it.
    On Windows, closing the cmd window may not immediately kill the
    subprocess (poll() can still return None), so callers should pass
    force=True when reconnecting to guarantee a fresh terminal.
    """
    proc = terminal_processes.get(session.project)
    needs_launch = force

    if not needs_launch:
        if proc is None:
            needs_launch = True
        elif proc.poll() is not None:
            terminal_processes.pop(session.project, None)
            needs_launch = True

    if needs_launch:
        close_render_terminal(session.project)
        log_path = launch_render_terminal(session.project)
        return {"success": True, "launched": True, "log_file": log_path or ""}
    return {"success": True, "launched": False, "message": "Terminal already running"}


# ── Internal async functions ─────────────────────────────────────

async def _serve_preview(session, port: int):
    """Run the WebSocket + HTTP preview server."""
    try:
        ws_server = await ws_serve(
            lambda ws: handle_ws(session, ws),
            '127.0.0.1', port,
            process_request=lambda conn, req: _process_http_request(session, conn, req),
            compression=None,
            max_size=10 * 1024 * 1024,
            ping_interval=20,
            ping_timeout=30,
        )
        for sock in ws_server.sockets:
            addr = sock.getsockname()
            session._preview_port = addr[1]
            break
        session._ws_server = ws_server
        session._preview_running = True
        logger.info("Preview server started on port %d", session._preview_port)
        await ws_server.wait_closed()
    except Exception as e:
        logger.error("Preview server error: %s", e)
    finally:
        session._preview_running = False


async def _process_http_request(session, connection, request):
    """Process HTTP requests (preview page, frame endpoint, log endpoints)."""
    try:
        from websockets import Headers, Response
    except ImportError:
        return None

    path = request.path.split('?')[0]

    if path == '/ws':
        return None

    if path == '/preview':
        body = _PREVIEW_HTML.replace('__PROJECT__', session.project).encode('utf-8')
        return Response(200, 'OK',
            Headers([('Content-Type', 'text/html; charset=utf-8'),
                     ('Content-Length', str(len(body))),
                     ('Connection', 'close'),
                     ('Access-Control-Allow-Origin', '*')]),
            body)

    if path == '/frame':
        with session._frame_lock:
            if not session._cached_frame and session._cached_raw_frame is not None:
                session._cached_frame, session._cached_mime = encode_frame(session._cached_raw_frame, 90)
                session._cached_raw_frame = None
            frame_data = session._cached_frame
            frame_mime = session._cached_mime
        if frame_data:
            b64 = base64.b64encode(frame_data).decode('utf-8')
            from manim import config
            body = json.dumps({'type': 'frame', 'data': b64,
                               'width': config.pixel_width if session._initialized else 0,
                               'height': config.pixel_height if session._initialized else 0,
                               'mime': frame_mime}).encode('utf-8')
        else:
            body = json.dumps({'type': 'frame', 'data': '', 'width': 0, 'height': 0, 'mime': ''}).encode('utf-8')
        return Response(200, 'OK',
            Headers([('Content-Type', 'application/json'),
                     ('Content-Length', str(len(body))),
                     ('Connection', 'close'),
                     ('Access-Control-Allow-Origin', '*')]),
            body)

    if path == '/log':
        log_path = PROJECTS_DIR / session.project / "render.log"
        lines_param = ""
        if '?' in request.path:
            qs = request.path.split('?', 1)[1]
            for pair in qs.split('&'):
                if pair.startswith('lines='):
                    lines_param = pair.split('=', 1)[1]
        n_lines = int(lines_param) if lines_param.isdigit() else 100
        try:
            if log_path.exists():
                all_lines = log_path.read_text(encoding='utf-8', errors='replace').splitlines()
                tail_lines = all_lines[-n_lines:] if len(all_lines) > n_lines else all_lines
                log_content = '\n'.join(tail_lines)
            else:
                log_content = f"[No render log found for project '{session.project}']"
        except Exception as e:
            log_content = f"[Error reading log: {e}]"
        body = log_content.encode('utf-8')
        return Response(200, 'OK',
            Headers([('Content-Type', 'text/plain; charset=utf-8'),
                     ('Content-Length', str(len(body))),
                     ('Connection', 'close'),
                     ('Access-Control-Allow-Origin', '*')]),
            body)

    if path == '/log/stream':
        log_path = PROJECTS_DIR / session.project / "render.log"
        try:
            if log_path.exists():
                all_lines = log_path.read_text(encoding='utf-8', errors='replace').splitlines()
                tail_lines = all_lines[-50:] if len(all_lines) > 50 else all_lines
                sse_data = ""
                for line in tail_lines:
                    sse_data += f"data: {line}\n\n"
                sse_data += "data: [streaming...]\n\n"
            else:
                sse_data = "data: [No render log yet]\n\n"
        except Exception as e:
            sse_data = f"data: [Error: {e}]\n\n"
        body = sse_data.encode('utf-8')
        return Response(200, 'OK',
            Headers([('Content-Type', 'text/event-stream'),
                     ('Cache-Control', 'no-cache'),
                     ('Connection', 'keep-alive'),
                     ('Access-Control-Allow-Origin', '*')]),
            body)
    not_found_body = b'Not Found'
    return Response(404, 'Not Found',
        Headers([('Content-Type', 'text/plain'),
                 ('Content-Length', str(len(not_found_body))),
                 ('Connection', 'close')]),
        not_found_body)
