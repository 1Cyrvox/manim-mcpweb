
import argparse
import os
import sys
import time
from pathlib import Path

# Working directory for output (same logic as manim_web.__init__: cwd by default)
# ⚠️ tail_render_log.py 是 __main__ 脚本，不能用 from manim_web import WORK_DIR
# 直接运行时 manim_web 包可能不在 sys.path 中，相对导入会失败
WORK_DIR = Path(os.environ.get("MANIM_WEB_WORK_DIR", str(Path.cwd()))).resolve()
PROJECTS_DIR = WORK_DIR / "media" / "projects"


def find_log_files(project: str = None) -> list[Path]:
    """Find render log files for the given project or all projects."""
    if project:
        log_path = PROJECTS_DIR / project / "render.log"
        if log_path.exists():
            return [log_path]
        # Try to find it
        print(f"[!] No render log found for project '{project}'")
        print(f"    Expected: {log_path}")
        return []

    # Find all project logs
    logs = []
    if PROJECTS_DIR.exists():
        for proj_dir in sorted(PROJECTS_DIR.iterdir()):
            if proj_dir.is_dir():
                log_path = proj_dir / "render.log"
                if log_path.exists():
                    logs.append(log_path)
    return logs


def wait_for_log_file(log_path: Path, timeout: float = 30.0) -> bool:
    """Wait for a log file to be created. Returns True if found."""
    start = time.time()
    while not log_path.exists():
        elapsed = time.time() - start
        if elapsed > timeout:
            return False
        # Print a waiting message every 2 seconds
        if int(elapsed) % 2 == 0 and elapsed > 0.5:
            sys.stdout.write(f"\r[Waiting for {log_path.name}... {int(elapsed)}s]")
            sys.stdout.flush()
        time.sleep(0.5)
    # Clear the waiting message
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()
    return True


def tail_file(path: Path, n_lines: int = 20, prefix: str = ""):
    """Print the last n_lines of a file, then tail for new content.

    Handles file truncation (e.g. when init_scene re-creates the log):
    if the file shrinks below the current read position, we reopen it
    from the beginning so no new content is missed.

    This function NEVER exits on exceptions — it always retries so the
    terminal window stays alive and continues showing output.
    """
    file_pos = 0
    idle_count = 0

    while True:  # 永不退出的外层循环
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                # On first open or after truncation, show last n_lines
                if file_pos == 0:
                    lines = f.readlines()
                    for line in lines[-n_lines:]:
                        print(f"{prefix}{line.rstrip()}")
                        sys.stdout.flush()
                    file_pos = f.tell()
                else:
                    f.seek(file_pos)

                # Tail for new content
                while True:
                    where = f.tell()
                    line = f.readline()
                    if line:
                        print(f"{prefix}{line.rstrip()}")
                        sys.stdout.flush()
                        file_pos = f.tell()
                        idle_count = 0
                    else:
                        # Check for truncation: if file size < our position
                        try:
                            current_size = path.stat().st_size
                        except OSError:
                            current_size = where
                        if current_size < where:
                            # File was truncated — break to re-open
                            print(f"{prefix}[Log file rotated, re-opening...]")
                            sys.stdout.flush()
                            file_pos = 0
                            break
                        # 强制刷新 Python 文件缓冲区 — 在 Windows 上
                        # readline() 可能因内部缓冲而不返回新内容
                        time.sleep(0.1)
                        try:
                            f.seek(0, 2)  # seek to end to refresh size
                            f.seek(where)  # seek back to read position
                        except (OSError, ValueError):
                            f.seek(where)
                        idle_count += 1

        except FileNotFoundError:
            if idle_count == 0:
                print(f"{prefix}[!] Log file not found: {path}")
                print(f"{prefix}[Waiting for log file to re-appear...]")
                sys.stdout.flush()
            time.sleep(1)
            file_pos = 0
            idle_count += 1
            continue
        except KeyboardInterrupt:
            print("\n[tail stopped]")
            return
        except Exception as e:
            print(f"{prefix}[!] Error: {e}, retrying in 2s...")
            sys.stdout.flush()
            time.sleep(2)
            file_pos = 0
            continue


def main():
    parser = argparse.ArgumentParser(
        description="Tail manim-web render logs in real-time",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tail_render_log.py              # Tail default project
  python tail_render_log.py math1        # Tail specific project
  python tail_render_log.py --all        # Tail all projects
  python tail_render_log.py --lines 50   # Show last 50 lines
        """
    )
    parser.add_argument("project", nargs="?", default="default",
                        help="Project name to tail (default: 'default')")
    parser.add_argument("--all", action="store_true",
                        help="Tail all project logs merged")
    parser.add_argument("--lines", type=int, default=20,
                        help="Number of initial lines to show (default: 20)")
    parser.add_argument("--list", action="store_true",
                        help="List all projects with log files")
    parser.add_argument("--wait", type=float, default=30.0,
                        help="Seconds to wait for log file to appear (default: 30)")
    parser.add_argument("--log-path", type=str, default=None,
                        help="Absolute path to the render.log file (overrides project name resolution)")
    args = parser.parse_args()

    # Set console window title on Windows so taskkill /FI WINDOWTITLE can find it
    if sys.platform == "win32" and args.project and args.project != "default":
        os.system(f"title Manim-Render-{args.project}")

    if args.list:
        logs = find_log_files(project=None)
        if not logs:
            print("No render log files found.")
            print(f"Projects directory: {PROJECTS_DIR}")
        else:
            print(f"Found {len(logs)} render log(s):")
            for log_path in logs:
                project_name = log_path.parent.name
                size = log_path.stat().st_size
                lines = len(log_path.read_text(encoding='utf-8', errors='replace').splitlines())
                print(f"  {project_name}: {lines} lines, {size} bytes")
                print(f"    {log_path}")
        return

    if args.all:
        logs = find_log_files(project=None)
        if not logs:
            print("No render log files found.")
            print(f"Projects directory: {PROJECTS_DIR}")
            print("\nTip: Start a manim-web session first, then run this script.")
            return
        # For --all, we just tail the most recently modified log
        latest = max(logs, key=lambda p: p.stat().st_mtime)
        project_name = latest.parent.name
        print(f"[Tailing all projects - showing latest: {project_name}]")
        print(f"[Log file: {latest}]")
        print("[Press Ctrl+C to stop]\n")
        tail_file(latest, n_lines=args.lines)
    else:
        # Use --log-path if provided (absolute path from caller), otherwise resolve from project name
        if args.log_path:
            log_path = Path(args.log_path)
        else:
            log_path = PROJECTS_DIR / args.project / "render.log"
        print(f"[Tailing render log for project: {args.project}]")
        print(f"[Log file: {log_path}]")

        # Wait for the log file to be created if it doesn't exist yet
        if not log_path.exists():
            print(f"[Log file doesn't exist yet, waiting up to {args.wait}s...]")
            if not wait_for_log_file(log_path, timeout=args.wait):
                print(f"[!] Timed out waiting for {log_path}")
                print(f"    Make sure a manim-web session is running for project '{args.project}'")
                # Don't close the window immediately on Windows
                print("\nPress Enter to close...")
                try:
                    input()
                except Exception:
                    pass
                return

        print("[Press Ctrl+C to stop]\n")
        tail_file(log_path, n_lines=args.lines)


if __name__ == "__main__":
    main()
