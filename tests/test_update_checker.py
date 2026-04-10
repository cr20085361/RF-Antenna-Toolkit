import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.update_checker import ReleaseInfo, check_for_updates, matches_asset_name_patterns
from core.update_settings import UpdateSettings, load_update_settings, save_update_settings


class UpdateCheckerTests(unittest.TestCase):
    def _build_release(self, *, version: str = "2.2.0", asset_name: str = "RF-Antenna-Toolkit-Setup-v2.2.0.exe"):
        return ReleaseInfo(
            version=version,
            tag_name=f"v{version}",
            name=f"v{version}",
            html_url="https://github.com/example/repo/releases/tag/v2.2.0",
            download_url="https://github.com/example/repo/releases/download/v2.2.0/setup.exe",
            asset_api_url="https://api.github.com/repos/example/repo/releases/assets/1",
            asset_name=asset_name,
            published_at="2026-04-10 12:00:00 UTC",
            body="release notes",
        )

    def test_matches_asset_name_patterns_supports_wildcard_and_keyword(self):
        self.assertTrue(
            matches_asset_name_patterns(
                "RF-Antenna-Toolkit-Setup-v2.2.0.exe",
                "RF-Antenna-Toolkit-Setup-*.exe",
            )
        )
        self.assertTrue(matches_asset_name_patterns("portable.zip", "portable"))
        self.assertFalse(matches_asset_name_patterns("release.tar.gz", "*.exe;*.msi"))

    @patch("core.update_checker.fetch_latest_release")
    def test_check_for_updates_returns_ignored_state(self, mocked_fetch):
        mocked_fetch.return_value = self._build_release(version="2.2.0")
        settings = UpdateSettings(ignored_version="v2.2.0")

        result = check_for_updates("2.1.0", settings)

        self.assertEqual(result.state, "ignored")

    @patch("core.update_checker.fetch_latest_release")
    def test_check_for_updates_requires_matching_asset(self, mocked_fetch):
        mocked_fetch.return_value = self._build_release(asset_name="")
        settings = UpdateSettings(asset_name_patterns="*.exe")

        result = check_for_updates("2.1.0", settings)

        self.assertEqual(result.state, "no_matching_asset")

    @patch("core.update_checker.fetch_latest_release")
    def test_check_for_updates_returns_update_available(self, mocked_fetch):
        mocked_fetch.return_value = self._build_release(version="2.2.0")
        settings = UpdateSettings(asset_name_patterns="*.exe")

        result = check_for_updates("2.1.0", settings)

        self.assertEqual(result.state, "update_available")
        self.assertIsNotNone(result.latest_release)
        latest_release = result.latest_release
        assert latest_release is not None
        self.assertEqual(latest_release.asset_name, "RF-Antenna-Toolkit-Setup-v2.2.0.exe")

    def test_update_settings_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = Path(temp_dir) / "update_settings.json"
            settings = UpdateSettings(
                owner="private-owner",
                repo="private-repo",
                token="github_pat_demo",
                asset_name_patterns="*.exe\nportable",
                ignored_version="v2.3.1",
            )

            save_update_settings(settings, settings_path)
            loaded = load_update_settings(settings_path)

            self.assertEqual(loaded.owner, "private-owner")
            self.assertEqual(loaded.repo, "private-repo")
            self.assertEqual(loaded.token, "github_pat_demo")
            self.assertEqual(loaded.asset_name_patterns, "*.exe\nportable")
            self.assertEqual(loaded.ignored_version, "2.3.1")