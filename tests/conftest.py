# tests/conftest.py
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_scene():
    """创建 mock manim Scene"""
    scene = MagicMock()
    scene.mobjects = []
    scene._persistent_env = {}
    scene.renderer = MagicMock()
    scene.renderer.get_frame.return_value = MagicMock(size=100)
    scene.renderer._frame_rate = 2
    return scene


@pytest.fixture
def mock_session(mock_scene):
    """创建 mock DirectManimSession（不触发 manim 初始化）"""
    with patch('manim_web.core.session.DirectManimSession.__init__', lambda self, **kw: None):
        from manim_web.core.session import DirectManimSession
        session = DirectManimSession.__new__(DirectManimSession)
        session.scene = mock_scene
        session.project = "test"
        session._initialized = True
        session._mobjects = {}
        session._accumulated_lines = []
        session._animating = False
        session._anim_lock = MagicMock()
        session._executor = MagicMock()
        session._frame_lock = MagicMock()
        session._cached_frame = b''
        session._cached_mime = 'image/webp'
        session._cached_raw_frame = None
        session._frame_counter = 0
        session.renderer = "cairo"
        session.sandbox = "strict"
        session.quality = "medium"
        session.orientation = "landscape"
        session._preview_running = False
        session._preview_port = None
        session._ws_clients = set()
        session._recovery_count = 0
        session._max_recovery = 3
        return session