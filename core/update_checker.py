# -*- coding: utf-8 -*-
"""
GitHub Release 更新检查
"""

import fnmatch
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional, Tuple

from core.update_settings import UpdateSettings, load_update_settings


@dataclass(frozen=True)
class ReleaseInfo:
    """GitHub Release 摘要信息"""

    version: str
    tag_name: str
    name: str
    html_url: str
    download_url: str
    asset_api_url: str
    asset_name: str
    published_at: str
    body: str


@dataclass(frozen=True)
class UpdateCheckResult:
    """更新检查结果"""

    state: str
    current_version: str
    latest_release: Optional[ReleaseInfo]
    repo_slug: str
    asset_patterns: str


_VERSION_PATTERN = re.compile(r"\d+")


def _build_releases_api_url(settings: UpdateSettings) -> str:
    return f"https://api.github.com/repos/{settings.owner}/{settings.repo}/releases?per_page=10"


def _build_releases_page_url(settings: UpdateSettings) -> str:
    return f"https://github.com/{settings.owner}/{settings.repo}/releases"


def normalize_version(version_text: str) -> Tuple[int, ...]:
    """提取版本号中的数字段用于比较"""
    parts = [int(part) for part in _VERSION_PATTERN.findall(version_text or "")]
    return tuple(parts or [0])


def is_newer_version(latest_version: str, current_version: str) -> bool:
    """判断 latest 是否新于 current"""
    latest = normalize_version(latest_version)
    current = normalize_version(current_version)

    max_len = max(len(latest), len(current))
    latest = latest + (0,) * (max_len - len(latest))
    current = current + (0,) * (max_len - len(current))
    return latest > current


def _format_published_at(raw_text: str) -> str:
    """格式化 GitHub 返回的发布时间"""
    if not raw_text:
        return "未知"
    return raw_text.replace("T", " ").replace("Z", " UTC")


def _build_request(
    url: str,
    settings: UpdateSettings,
    *,
    accept: str = "application/vnd.github+json",
) -> urllib.request.Request:
    headers = {
        "Accept": accept,
        "User-Agent": "RF-Antenna-Toolkit-UpdateChecker",
    }
    if settings.has_token:
        headers["Authorization"] = f"Bearer {settings.token.strip()}"
    return urllib.request.Request(url, headers=headers)


def _split_asset_patterns(patterns_text: str) -> list[str]:
    return [segment.strip() for segment in re.split(r"[;,\n\r]+", patterns_text or "") if segment.strip()]


def matches_asset_name_patterns(asset_name: str, patterns_text: str) -> bool:
    """判断资产名是否命中用户设置的匹配规则"""
    patterns = _split_asset_patterns(patterns_text)
    if not patterns:
        return True

    lowered_name = (asset_name or "").lower()
    for pattern in patterns:
        lowered_pattern = pattern.lower()
        if any(char in pattern for char in "*?[]"):
            if fnmatch.fnmatch(lowered_name, lowered_pattern):
                return True
        elif lowered_pattern in lowered_name:
            return True
    return False


def _pick_matching_asset(payload: dict, settings: UpdateSettings) -> tuple[str, str, str]:
    for asset in payload.get("assets") or []:
        asset_name = str(asset.get("name") or "")
        if asset_name and matches_asset_name_patterns(asset_name, settings.asset_name_patterns):
            return (
                asset_name,
                str(asset.get("browser_download_url") or ""),
                str(asset.get("url") or ""),
            )
    return "", "", ""


def _build_release_info(payload: dict, settings: UpdateSettings) -> ReleaseInfo:
    raw_tag = str(payload.get("tag_name") or "")
    raw_name = str(payload.get("name") or raw_tag or "最新版本")
    normalized_version = raw_tag.lstrip("vV") or raw_name.lstrip("vV")
    asset_name, download_url, asset_api_url = _pick_matching_asset(payload, settings)

    return ReleaseInfo(
        version=normalized_version,
        tag_name=raw_tag or normalized_version,
        name=raw_name,
        html_url=str(payload.get("html_url") or _build_releases_page_url(settings)),
        download_url=download_url,
        asset_api_url=asset_api_url,
        asset_name=asset_name,
        published_at=_format_published_at(str(payload.get("published_at") or "")),
        body=str(payload.get("body") or "").strip(),
    )


def fetch_latest_release(
    settings: Optional[UpdateSettings] = None,
    timeout: int = 5,
) -> Optional[ReleaseInfo]:
    """获取最新 GitHub Release"""
    effective_settings = (settings or load_update_settings()).cleaned()
    request = _build_request(_build_releases_api_url(effective_settings), effective_settings)

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            if effective_settings.has_token:
                return None
            raise RuntimeError(
                "未找到可访问的 GitHub Release；如果使用的是私有仓库，请先在“帮助 -> 更新设置”中填写令牌。"
            ) from exc
        if exc.code in (401, 403):
            raise RuntimeError(
                "GitHub 访问被拒绝，请检查令牌是否有效，并确认其具有仓库 Metadata / Contents 读取权限。"
            ) from exc
        raise RuntimeError(f"GitHub Release 接口返回 HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("无法连接 GitHub Release 接口，请检查网络环境") from exc

    if not isinstance(payload, list):
        raise RuntimeError("GitHub Release 接口返回了异常数据格式")

    for release_payload in payload:
        if release_payload.get("draft") or release_payload.get("prerelease"):
            continue
        return _build_release_info(release_payload, effective_settings)

    return None


def check_for_updates(
    current_version: str,
    settings: Optional[UpdateSettings] = None,
    timeout: int = 5,
) -> UpdateCheckResult:
    """比较当前版本与 GitHub 最新 Release"""
    effective_settings = (settings or load_update_settings()).cleaned()
    latest_release = fetch_latest_release(effective_settings, timeout=timeout)
    if latest_release is None:
        return UpdateCheckResult(
            state="no_release",
            current_version=current_version,
            latest_release=None,
            repo_slug=effective_settings.repository_slug,
            asset_patterns=effective_settings.asset_name_patterns,
        )

    if not is_newer_version(latest_release.version, current_version):
        return UpdateCheckResult(
            state="up_to_date",
            current_version=current_version,
            latest_release=latest_release,
            repo_slug=effective_settings.repository_slug,
            asset_patterns=effective_settings.asset_name_patterns,
        )

    ignored_version = effective_settings.ignored_version.strip().lstrip("vV")
    if ignored_version and normalize_version(ignored_version) == normalize_version(latest_release.version):
        return UpdateCheckResult(
            state="ignored",
            current_version=current_version,
            latest_release=latest_release,
            repo_slug=effective_settings.repository_slug,
            asset_patterns=effective_settings.asset_name_patterns,
        )

    if not latest_release.asset_name or not latest_release.download_url:
        return UpdateCheckResult(
            state="no_matching_asset",
            current_version=current_version,
            latest_release=latest_release,
            repo_slug=effective_settings.repository_slug,
            asset_patterns=effective_settings.asset_name_patterns,
        )

    return UpdateCheckResult(
        state="update_available",
        current_version=current_version,
        latest_release=latest_release,
        repo_slug=effective_settings.repository_slug,
        asset_patterns=effective_settings.asset_name_patterns,
    )


def download_release_asset(
    release: ReleaseInfo,
    settings: Optional[UpdateSettings],
    destination_path: str,
    timeout: int = 30,
):
    """下载命中的 Release 资产到本地"""
    if not release.asset_name:
        raise RuntimeError("当前 Release 没有可下载的安装包资产。")

    effective_settings = (settings or load_update_settings()).cleaned()
    download_endpoint = release.asset_api_url or release.download_url
    if not download_endpoint:
        raise RuntimeError("当前 Release 缺少可下载资产地址。")

    request = _build_request(
        download_endpoint,
        effective_settings,
        accept="application/octet-stream",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            with open(destination_path, "wb") as file_handle:
                while True:
                    chunk = response.read(1024 * 128)
                    if not chunk:
                        break
                    file_handle.write(chunk)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise RuntimeError("下载资产失败：当前令牌无权访问该安装包。") from exc
        raise RuntimeError(f"下载资产失败：HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("下载资产失败：无法连接 GitHub。") from exc