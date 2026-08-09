"""project store 纯逻辑测试 — 端口检测、项目状态管理"""
import json
import pytest
from pathlib import Path

from manim_web.project.store import (
    auto_project_name,
    find_available_port,
    has_saved_state,
    is_port_available,
    list_all_projects,
    list_saved_projects,
    load_state,
    clear_saved_state,
)


# ── 端口检测 ────────────────────────────────────────────────────────


class TestPortAvailable:
    """is_port_available 端口可用性检测"""

    def test_unused_port_available(self):
        """随机高位端口通常可用"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        # 端口已释放，应该可用
        assert is_port_available(port) is True

    def test_occupied_port_not_available(self):
        """占用中的端口不可用"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
            # socket 仍然打开，端口被占用
            assert is_port_available(port) is False


class TestFindAvailablePort:
    """find_available_port 查找可用端口"""

    def test_returns_int(self):
        port = find_available_port()
        assert isinstance(port, int)

    def test_port_in_range(self):
        port = find_available_port(start=9000, end=9100)
        assert 9000 <= port < 9100

    def test_fallback_when_range_full(self):
        """范围全满时回退到 OS 分配"""
        import socket
        sockets = []
        try:
            for p in range(9200, 9210):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(("127.0.0.1", p))
                sockets.append(s)
            port = find_available_port(start=9200, end=9210)
            assert isinstance(port, int)
            assert port > 0
        finally:
            for s in sockets:
                s.close()


# ── 项目状态管理（使用 tmp_path 替代 PROJECTS_DIR）──────────────────


class TestProjectState:
    """项目状态 CRUD 操作"""

    @pytest.fixture
    def projects_dir(self, tmp_path, monkeypatch):
        """创建临时项目目录并 monkeypatch PROJECTS_DIR"""
        from manim_web.project import store
        pdir = tmp_path / "projects"
        pdir.mkdir()
        monkeypatch.setattr(store, "PROJECTS_DIR", pdir)
        return pdir

    def test_load_state_missing_project(self, projects_dir):
        result = load_state("nonexistent")
        assert result is None

    def test_load_state_existing_project(self, projects_dir):
        proj = projects_dir / "test_proj"
        proj.mkdir()
        state = {"accumulated_lines": ["a=1", "b=2"], "persistent_env_keys": ["a", "b"]}
        (proj / "state.json").write_text(json.dumps(state), encoding="utf-8")
        result = load_state("test_proj")
        assert result is not None
        assert result["accumulated_lines"] == ["a=1", "b=2"]

    def test_has_saved_state_false(self, projects_dir):
        assert has_saved_state("no_such_project") is False

    def test_has_saved_state_true(self, projects_dir):
        proj = projects_dir / "existing"
        proj.mkdir()
        (proj / "state.json").write_text("{}", encoding="utf-8")
        assert has_saved_state("existing") is True

    def test_list_saved_projects_empty(self, projects_dir):
        assert list_saved_projects() == []

    def test_list_saved_projects_with_data(self, projects_dir):
        for name in ("proj_a", "proj_b"):
            p = projects_dir / name
            p.mkdir()
            (p / "state.json").write_text("{}", encoding="utf-8")
        # 空目录不算
        (projects_dir / "empty_dir").mkdir()
        result = list_saved_projects()
        assert set(result) == {"proj_a", "proj_b"}

    def test_list_all_projects_includes_empty(self, projects_dir):
        (projects_dir / "with_state").mkdir()
        (projects_dir / "with_state" / "state.json").write_text("{}", encoding="utf-8")
        (projects_dir / "empty_dir").mkdir()
        result = list_all_projects()
        assert "with_state" in result
        assert "empty_dir" in result

    def test_auto_project_name_first(self, projects_dir):
        name = auto_project_name("demo")
        assert name == "demo1"

    def test_auto_project_name_increment(self, projects_dir):
        (projects_dir / "demo1").mkdir()
        (projects_dir / "demo2").mkdir()
        name = auto_project_name("demo")
        assert name == "demo3"

    def test_clear_saved_state(self, projects_dir):
        proj = projects_dir / "to_clear"
        proj.mkdir()
        (proj / "state.json").write_text("{}", encoding="utf-8")
        (proj / "scene.py").write_text("pass", encoding="utf-8")
        clear_saved_state("to_clear")
        assert not (proj / "state.json").exists()
        assert not (proj / "scene.py").exists()
        # 目录本身保留
        assert proj.exists()

    def test_clear_saved_state_nonexistent(self, projects_dir):
        """清理不存在的项目不报错"""
        clear_saved_state("no_such_project")  # 不应抛异常