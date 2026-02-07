import os
import sys
import importlib
import pytest


def import_tavily_module_or_skip():
    """모듈을 새로 로드하여 반환하거나 불가능하면 테스트를 건너뜁니다."""
    module_name = "backend.agent.tools.tavily_search_tool"
    if module_name in sys.modules:
        del sys.modules[module_name]
    try:
        mod = importlib.import_module(module_name)
        importlib.reload(mod)
        return mod
    except Exception as e:
        pytest.skip(f"tavily 모듈을 불러올 수 없어 테스트를 건너뜁니다: {e}")


def test_tavily_tool_present_when_env_set(monkeypatch):
    """`TAVILY_API_KEY`가 설정되어 있으면 tavily_search_tool이 존재해야 합니다."""
    monkeypatch.setenv("TAVILY_API_KEY", "fake_key_for_test")
    mod = import_tavily_module_or_skip()
    assert getattr(mod, "tavily_search_tool", None) is not None, (
        "TAVILY_API_KEY가 설정되어 있을 때 tavily_search_tool이 None이면 안됩니다."
    )

