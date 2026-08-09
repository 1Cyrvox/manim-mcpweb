"""WebSocket handler for browser preview connections.

Extracted from DirectManimSession._handle_ws (l1257-1286).
"""
import json
import logging

try:
    from websockets.exceptions import InvalidMessage
except ImportError:
    InvalidMessage = None  # type: ignore

logger = logging.getLogger(__name__)


async def handle_ws(session, ws) -> None:
    """Handle a WebSocket connection from the browser.

    On connect: send cached frame (binary) or status JSON.
    On message: respond to ping commands.

    Args:
        session: DirectManimSession instance (accesses _ws_clients, _frame_lock,
                 _cached_frame, _cached_mime).
        ws: WebSocket connection object from websockets server.
    """
    session._ws_clients.add(ws)
    try:
        # Send cached frame on connect
        with session._frame_lock:
            if session._cached_frame:
                mime_bytes = session._cached_mime.encode('utf-8')
                header = bytes([0x01, len(mime_bytes)]) + mime_bytes
                await ws.send(header + session._cached_frame)
            else:
                await ws.send(json.dumps({'type': 'status', 'scene': 'ready', 'frame': 'empty'}))

        # Message loop
        async for message in ws:
            if isinstance(message, str):
                try:
                    cmd = json.loads(message)
                    if cmd.get('type') == 'ping':
                        await ws.send(json.dumps({'type': 'pong', 'status': 'ok'}))
                except json.JSONDecodeError:
                    pass
    except (InvalidMessage if InvalidMessage is not None else Exception):
        pass
    except ConnectionError:
        pass
    except Exception as e:
        err_str = str(e)
        if 'no close frame' not in err_str and 'connection closed' not in err_str.lower():
            logger.debug("WebSocket handler error: %s", e)
    finally:
        session._ws_clients.discard(ws)
