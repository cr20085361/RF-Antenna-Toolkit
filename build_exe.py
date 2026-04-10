import os
from importlib import import_module
from pathlib import Path

from core.app_metadata import APP_VERSION, APP_VERSION_LABEL


PROJECT_DIR = Path(__file__).resolve().parent
DIST_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"
APP_EXE_NAME = "RFAntennaToolkit"


def _add_data_args() -> list[str]:
    add_data_args: list[str] = []
    hook_utils = import_module("PyInstaller.utils.hooks")
    collect_data_files = getattr(hook_utils, "collect_data_files")
    data_pairs = [
        (PROJECT_DIR / "assets", "assets"),
        (PROJECT_DIR / "resources", "resources"),
        (PROJECT_DIR / "ui" / "assets", "ui/assets"),
        (PROJECT_DIR / "ui" / "styles", "ui/styles"),
    ]

    for source, target in data_pairs:
        if source.exists():
            add_data_args.append(f"--add-data={source}{os.pathsep}{target}")

    for source, target in collect_data_files("skrf", include_py_files=False):
        add_data_args.append(f"--add-data={source}{os.pathsep}{target}")

    return add_data_args


def _hidden_import_args() -> list[str]:
    hook_utils = import_module("PyInstaller.utils.hooks")
    collect_submodules = getattr(hook_utils, "collect_submodules")
    hidden_imports = {
        "matplotlib.backends.backend_qtagg",
        "matplotlib.backends.backend_qt5agg",
        "matplotlib.backends.qt_compat",
        "sip",
        *collect_submodules(
            "skrf",
            filter=lambda module_name: not module_name.startswith("skrf.vi"),
            on_error="ignore",
        ),
    }
    return [f"--hidden-import={module_name}" for module_name in sorted(hidden_imports)]


def build_executable():
    pyinstaller_main = import_module("PyInstaller.__main__")
    pyinstaller_args = [
        str(PROJECT_DIR / "main.py"),
        f"--name={APP_EXE_NAME}",
        "--windowed",
        "--onedir",
        "--clean",
        "--noconfirm",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        f"--specpath={BUILD_DIR}",
        f"--paths={PROJECT_DIR}",
        f"--icon={PROJECT_DIR / 'assets' / 'app.ico'}",
    ]
    pyinstaller_args.extend(_add_data_args())
    pyinstaller_args.extend(_hidden_import_args())

    print(f"开始编译 {APP_EXE_NAME} {APP_VERSION_LABEL} ...")
    pyinstaller_main.run(pyinstaller_args)
    print(f"编译完成，输出目录：{DIST_DIR / APP_EXE_NAME}")
    print(f"当前应用版本：{APP_VERSION}")


if __name__ == "__main__":
    build_executable()
