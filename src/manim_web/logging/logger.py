import time as _time
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from manim_web import WORK_DIR

logger = logging.getLogger(__name__)

_PROJECTS_DIR = WORK_DIR / "media" / "projects"

terminal_processes: Dict[str, Any] = {}


def launch_render_terminal(project: str) -> Optional[str]:
    global terminal_processes
    log_path = _PROJECTS_DIR / project / "render.log"
    tail_script = Path(__file__).parent / "render_log.py"

    log_path.parent.mkdir(parents=True, exist_ok=True)

    close_render_terminal(project)

    try:
        if sys.platform == "win32":
            # 优先使用 Windows Terminal 在同一窗口开新 tab
            wt_exe = shutil.which("wt")
            if wt_exe:
                cmd = [
                    wt_exe, "-w", "0", "nt",
                    "--title", f"Manim-Render-{project}",
                    sys.executable, str(tail_script),
                    project, "--log-path", str(log_path.resolve()),
                ]
                proc = subprocess.Popen(cmd)
            else:
                proc = subprocess.Popen(
                    [
                        "cmd", "/k",
                        sys.executable, str(tail_script),
                        project, "--log-path", str(log_path.resolve()),
                    ],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
            terminal_processes[project] = proc
        else:
            log_path_abs = str(log_path.resolve())
            if shutil.which("xterm"):
                cmd = ["xterm", "-T", f"Manim Render - {project}", "-e",
                       sys.executable, str(tail_script), project, "--log-path", log_path_abs]
            elif shutil.which("gnome-terminal"):
                cmd = ["gnome-terminal", "--title", f"Manim Render - {project}",
                       "--", sys.executable, str(tail_script), project, "--log-path", log_path_abs]
            elif shutil.which("osascript"):
                script_cmd = f'{sys.executable} {tail_script} {project} --log-path {log_path_abs}'
                apple_script = f'tell application "Terminal" to do script "{script_cmd}"'
                cmd = ["osascript", "-e", apple_script]
            else:
                logger.info("No terminal emulator found, skipping auto-terminal launch")
                return str(log_path)
            proc = subprocess.Popen(cmd, start_new_session=True)
            terminal_processes[project] = proc

        logger.info("Launched render terminal for project '%s' (PID: %s)", project,
                    proc.pid if proc else "N/A")
        return str(log_path)
    except Exception as e:
        logger.warning("Failed to launch render terminal for project '%s': %s", project, e)
        return str(log_path)


def close_render_terminal(project: str):
    global terminal_processes
    proc = terminal_processes.pop(project, None)
    if proc is not None:
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                    capture_output=True, timeout=5,
                )
            else:
                proc.terminate()
        except Exception:
            pass

    if sys.platform == "win32":
        window_title = f"Manim-Render-{project}"
        try:
            subprocess.run(
                ["taskkill", "/F", "/FI", f"WINDOWTITLE eq {window_title}"],
                capture_output=True, timeout=5,
            )
        except Exception:
            pass


class RenderLogFileHandler(logging.Handler):
    def __init__(self, log_path: Path, project: str = None):
        super().__init__()
        self.log_path = log_path
        self._project = project  # 用于多项目日志隔离
        self._file = None
        self._open()

    def _open(self):
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self._file = open(self.log_path, 'a', encoding='utf-8', buffering=1)
        except Exception as e:
            logger.warning("Failed to open render log file %s: %s", self.log_path, e)
            self._file = None

    def emit(self, record):
        if self._file is None:
            return
        # 多项目隔离：只在活跃项目匹配时写入
        if self._project and _active_render_project and self._project != _active_render_project:
            return
        try:
            msg = self.format(record)
            self._file.write(msg + '\n')
            self._file.flush()
        except Exception:
            pass

    def close(self):
        if self._file:
            try:
                self._file.close()
            except Exception:
                pass
        super().close()

    def reopen(self):
        """重新打开日志文件句柄。

        在 render.log 被外部清空/截断后调用，
        确保后续日志写入从文件开头开始。
        """
        if self._file:
            try:
                self._file.close()
            except Exception:
                pass
        self._open()


def setup_render_logging(project: str) -> RenderLogFileHandler:
    log_path = _PROJECTS_DIR / project / "render.log"
    handler = RenderLogFileHandler(log_path, project=project)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(name)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S"
    ))
    manim_logger = logging.getLogger("manim")
    manim_logger.addHandler(handler)
    manim_logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    tee_stderr_to_log(project, log_path)

    return handler


def teardown_render_logging(handler: RenderLogFileHandler, project: str = None):
    try:
        logging.getLogger("manim").removeHandler(handler)
        logger.removeHandler(handler)
        handler.close()
    except Exception:
        pass
    if project:
        remove_stderr_tee(project)
    else:
        restore_stderr()


_original_stderr = sys.stderr
_stderr_tee_files: dict[str, object] = {}  # project -> file handle
_active_render_project: str | None = None  # 当前正在渲染的项目名


def set_active_render_project(project: str):
    """设置当前正在渲染的项目，用于日志隔离。"""
    global _active_render_project
    _active_render_project = project


def clear_active_render_project():
    """清除当前渲染项目标记。"""
    global _active_render_project
    _active_render_project = None


class _StderrTee:
    """将 stderr 同时输出到原始 stderr 和当前活跃项目的 render.log。

    多项目并行时，只写入 _active_render_project 对应的项目日志文件，
    避免不同项目的渲染日志串写。
    """

    def __init__(self, original):
        self._original = original

    def write(self, data):
        # 原始 stderr 同步输出（终端显示）
        self._original.write(data)
        self._original.flush()
        if data:
            f = _stderr_tee_files.get(_active_render_project)
            if f:
                try:
                    f.write(data)
                except Exception:
                    pass

    def flush(self):
        self._original.flush()

    def __getattr__(self, name):
        return getattr(self._original, name)


def tee_stderr_to_log(project: str, log_path: Path):
    """为指定项目注册 stderr tee 到其 render.log。"""
    global _original_stderr
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        # 关闭该项目旧的 tee file（如果有）
        old = _stderr_tee_files.pop(project, None)
        if old:
            try:
                old.close()
            except Exception:
                pass
        _stderr_tee_files[project] = open(log_path, 'a', encoding='utf-8', buffering=1)
        # 首次安装 _StderrTee
        if not isinstance(sys.stderr, _StderrTee):
            _original_stderr = sys.stderr
            sys.stderr = _StderrTee(_original_stderr)
    except Exception as e:
        logger.warning("Failed to tee stderr to log file: %s", e)


def remove_stderr_tee(project: str):
    """移除指定项目的 stderr tee。"""
    f = _stderr_tee_files.pop(project, None)
    if f:
        try:
            f.close()
        except Exception:
            pass
    # 没有活跃项目时恢复原始 stderr
    if not _stderr_tee_files and isinstance(sys.stderr, _StderrTee):
        sys.stderr = _original_stderr


def reopen_stderr_tee(project: str):
    """重新打开指定项目的 stderr tee 文件句柄。

    在 render.log 被外部清空/截断后调用，确保后续写入从文件开头开始，
    而非跳到旧的偏移位置（Windows append 模式下截断后的已知问题）。
    """
    log_path = _PROJECTS_DIR / project / "render.log"
    if project in _stderr_tee_files:
        tee_stderr_to_log(project, log_path)


def restore_stderr():
    """恢复原始 stderr，关闭所有 tee file。"""
    global _original_stderr
    for f in list(_stderr_tee_files.values()):
        try:
            f.close()
        except Exception:
            pass
    _stderr_tee_files.clear()
    if isinstance(sys.stderr, _StderrTee):
        sys.stderr = _original_stderr
