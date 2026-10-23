"""验证发行验收入口的成功与失败报告，确保发布检查可信。"""

import json

import pytest
from PyQt6.QtWidgets import QApplication

from ui.help.installation_check import verify_installation


@pytest.fixture(scope="session")
def qapp():
    """取得当前测试会话的应用。"""
    return QApplication.instance() or QApplication([])


def test_installation_check_reports_success(qapp, tmp_path):
    """源码模式先验证完整诊断路径，真正冻结模式在安装后再执行。"""
    target = tmp_path / "report.json"
    assert verify_installation(qapp, str(target)) == 0
    report = json.loads(target.read_text(encoding="utf-8"))
    assert report["success"] is True
    assert len(report["checks"]) == 17
    assert all(item["passed"] for item in report["checks"])


def test_installation_check_fails_when_bundled_resource_missing(qapp, tmp_path, monkeypatch):
    """缺少资源时必须失败并记录具体检查，不能只以进程正常退出认定通过。"""
    monkeypatch.setattr("ui.help.installation_check.resource_path", lambda asset: str(tmp_path / "missing" / asset))
    target = tmp_path / "failed.json"
    assert verify_installation(qapp, str(target)) == 1
    report = json.loads(target.read_text(encoding="utf-8"))
    assert report["success"] is False
    assert report["checks"][0]["passed"] is False
    assert "assets/app.ico" in report["error"]
