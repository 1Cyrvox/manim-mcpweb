"""沙箱检查器扩展测试 — 危险模式覆盖、受限 import、restricted open"""
import os
import pytest

from manim_web.sandbox import (
    RELAXED_EXTRA_NS,
    SAFE_BUILTINS_STRICT,
    get_sandbox_builtins,
    scan_dangerous_patterns,
)


class TestDangerousPatterns:
    """scan_dangerous_patterns 各类危险模式"""

    def test_os_remove_critical(self):
        result = scan_dangerous_patterns("os.remove('file.txt')", "full")
        assert any(d["level"] == "critical" for d in result)

    def test_os_unlink_critical(self):
        result = scan_dangerous_patterns("os.unlink('file.txt')", "full")
        assert any(d["level"] == "critical" for d in result)

    def test_shutil_rmtree_critical(self):
        result = scan_dangerous_patterns("shutil.rmtree('/tmp/dir')", "full")
        assert any(d["level"] == "critical" for d in result)

    def test_subprocess_critical(self):
        result = scan_dangerous_patterns("subprocess.run(['ls'])", "full")
        assert any(d["level"] == "critical" for d in result)

    def test_os_system_critical(self):
        result = scan_dangerous_patterns("os.system('rm -rf /')", "full")
        assert any(d["level"] == "critical" for d in result)

    def test_os_environ_warning(self):
        result = scan_dangerous_patterns("os.environ['HOME']", "full")
        assert any(d["level"] == "warning" for d in result)

    def test_socket_warning(self):
        result = scan_dangerous_patterns("import socket", "full")
        assert any(d["level"] == "warning" for d in result)

    def test_exec_warning(self):
        result = scan_dangerous_patterns("exec('print(1)')", "full")
        assert len(result) > 0

    def test_eval_warning(self):
        result = scan_dangerous_patterns("eval('1+1')", "full")
        assert len(result) > 0

    def test_multiple_dangers(self):
        code = "os.remove('a')\nos.environ['X']"
        result = scan_dangerous_patterns(code, "full")
        levels = {d["level"] for d in result}
        assert "critical" in levels
        assert "warning" in levels

    def test_safe_code_no_dangers(self):
        result = scan_dangerous_patterns("x = [1, 2, 3]\ny = sum(x)", "full")
        assert result == []

    def test_strict_mode_no_scan(self):
        result = scan_dangerous_patterns("os.remove('file')", "strict")
        assert result == []

    def test_relaxed_mode_no_scan(self):
        result = scan_dangerous_patterns("os.remove('file')", "relaxed")
        assert result == []


class TestRestrictedImport:
    """relaxed 模式受限 import"""

    def test_whitelisted_import_allowed(self):
        builtins = get_sandbox_builtins("relaxed", "/tmp/project")
        import_func = builtins["__import__"]
        # json 在白名单中
        json_mod = import_func("json")
        assert hasattr(json_mod, "dumps")

    def test_blocked_import_raises(self):
        builtins = get_sandbox_builtins("relaxed", "/tmp/project")
        import_func = builtins["__import__"]
        with pytest.raises(ImportError, match="Sandbox restriction"):
            import_func("subprocess")

    def test_os_path_allowed(self):
        builtins = get_sandbox_builtins("relaxed", "/tmp/project")
        import_func = builtins["__import__"]
        # os.path 在白名单中，__import__("os.path") 返回 os 模块
        # 但 os.path 子模块会被正确加载
        import_func("os.path")
        import os.path
        assert hasattr(os.path, "join")


class TestRestrictedOpen:
    """relaxed 模式受限 open"""

    def test_open_within_project(self, tmp_path):
        project_dir = str(tmp_path)
        builtins = get_sandbox_builtins("relaxed", project_dir)
        open_func = builtins["open"]
        # 在项目目录内创建文件应成功
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello", encoding="utf-8")
        with open_func(str(test_file), "r") as f:
            content = f.read()
        assert content == "hello"

    def test_open_outside_project_blocked(self, tmp_path):
        project_dir = str(tmp_path / "project")
        os.makedirs(project_dir, exist_ok=True)
        builtins = get_sandbox_builtins("relaxed", project_dir)
        open_func = builtins["open"]
        with pytest.raises(PermissionError, match="outside project"):
            open_func("/etc/passwd", "r")


class TestRelaxedExtraNS:
    """RELAXED_EXTRA_NS 验证"""

    def test_json_available(self):
        assert "json" in RELAXED_EXTRA_NS

    def test_re_available(self):
        assert "re" in RELAXED_EXTRA_NS

    def test_pathlib_available(self):
        assert "pathlib" in RELAXED_EXTRA_NS


class TestSafeBuiltinsStrict:
    """SAFE_BUILTINS_STRICT 验证"""

    def test_has_basic_types(self):
        for name in ("int", "str", "float", "list", "dict", "set", "tuple", "bool"):
            assert name in SAFE_BUILTINS_STRICT

    def test_blocked_builtins_raise(self):
        for name in ("open", "exec", "eval", "compile", "__import__", "input"):
            assert name in SAFE_BUILTINS_STRICT
            with pytest.raises(PermissionError):
                SAFE_BUILTINS_STRICT[name]()

    def test_globals_blocked(self):
        assert "globals" in SAFE_BUILTINS_STRICT
        with pytest.raises(PermissionError):
            SAFE_BUILTINS_STRICT["globals"]()

    def test_print_allowed(self):
        assert "print" in SAFE_BUILTINS_STRICT
        # print 不应抛异常
        SAFE_BUILTINS_STRICT["print"]("test")