# -*- coding: utf-8 -*-
"""
GitHub 更新检查本地设置
"""

import json
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Optional

from core.app_metadata import GITHUB_OWNER, GITHUB_REPO


_CONFIG_DIR_NAME = "RF-Antenna-Toolkit"
_CONFIG_FILE_NAME = "update_settings.json"


@dataclass(frozen=True)
class UpdateSettings:
    """更新检查设置"""

    owner: str = GITHUB_OWNER
    repo: str = GITHUB_REPO
    token: str = ""
    asset_name_patterns: str = ""
    ignored_version: str = ""

    def with_updates(self, **changes) -> "UpdateSettings":
        return replace(self, **changes)

    @property
    def repository_slug(self) -> str:
        return f"{self.owner}/{self.repo}"

    @property
    def has_token(self) -> bool:
        return bool(self.token.strip())

    def cleaned(self) -> "UpdateSettings":
        return UpdateSettings(
            owner=(self.owner or GITHUB_OWNER).strip(),
            repo=(self.repo or GITHUB_REPO).strip(),
            token=self.token.strip(),
            asset_name_patterns=self.asset_name_patterns.strip(),
            ignored_version=self.ignored_version.strip().lstrip("vV"),
        )


def get_update_settings_path() -> Path:
    """返回更新设置文件路径"""
    app_data = os.getenv("APPDATA")
    base_dir = Path(app_data) if app_data else (Path.home() / ".config")
    return base_dir / _CONFIG_DIR_NAME / _CONFIG_FILE_NAME


def load_update_settings(file_path: Optional[Path | str] = None) -> UpdateSettings:
    """读取本地更新设置"""
    path = Path(file_path) if file_path else get_update_settings_path()
    default_settings = UpdateSettings().cleaned()

    if not path.exists():
        return default_settings

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default_settings

    if not isinstance(payload, dict):
        return default_settings

    return UpdateSettings(
        owner=str(payload.get("owner") or GITHUB_OWNER),
        repo=str(payload.get("repo") or GITHUB_REPO),
        token=str(payload.get("token") or ""),
        asset_name_patterns=str(payload.get("asset_name_patterns") or ""),
        ignored_version=str(payload.get("ignored_version") or ""),
    ).cleaned()


def save_update_settings(
    settings: UpdateSettings,
    file_path: Optional[Path | str] = None,
) -> Path:
    """保存本地更新设置"""
    path = Path(file_path) if file_path else get_update_settings_path()
    clean_settings = settings.cleaned()

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(clean_settings), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path