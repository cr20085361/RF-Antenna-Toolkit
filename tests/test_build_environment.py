"""验证编译环境隔离，防止外部工具的同名动态库进入发行包。"""

import os
import sys

import pytest

from build_exe import isolated_build_environment


@pytest.mark.skipif(sys.platform != "win32", reason="验证Windows的动态库搜索路径")
def test_build_path_excludes_external_tools_and_restores_environment(monkeypatch):
    """带有冲突工具的原始路径只在构建期间隔离，结束后完整恢复。"""
    old_path = r"C:\external-tools\poppler\bin;C:\other-tools"
    monkeypatch.setenv("PATH", old_path)
    monkeypatch.setenv("QT_PLUGIN_PATH", r"C:\unrelated-qt\plugins")
    monkeypatch.delenv("QT_QPA_PLATFORM_PLUGIN_PATH", raising=False)
    with isolated_build_environment():
        assert "poppler" not in os.environ["PATH"]
        assert str(os.path.join(os.environ["SystemRoot"], "System32")) in os.environ["PATH"]
        assert "QT_PLUGIN_PATH" not in os.environ
        assert "QT_QPA_PLATFORM_PLUGIN_PATH" not in os.environ
    assert os.environ["PATH"] == old_path
    assert os.environ["QT_PLUGIN_PATH"] == r"C:\unrelated-qt\plugins"
    assert "QT_QPA_PLATFORM_PLUGIN_PATH" not in os.environ


def test_build_environment_restored_even_if_compilation_fails(monkeypatch):
    """构建异常不能污染后续终端和程序的环境。"""
    monkeypatch.setenv("QT_QPA_PLATFORM_PLUGIN_PATH", "original-plugin-path")
    before = dict(os.environ)
    with pytest.raises(RuntimeError):
        with isolated_build_environment():
            raise RuntimeError("模拟编译失败")
    for key in ("PATH", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH"):
        assert os.environ.get(key) == before.get(key)
