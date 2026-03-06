---
description: 如何将射频天线工具集正确编译并打包为可执行的 EXE 文件
---

# 射频天线工具集 (RFAntennaToolkit) 编译打包工作流

当用户要求“编译为 exe”或“重新打包”时，请严格按照以下标准化工作流执行，以确保各类图形界面、样式表和 SVG 图片资源能够被正确加载。

## 1. 核心常见问题与前置须知
在历史上，直接打包曾出现以下致命问题：
- **资源路径崩溃**：Python 源码中的 `os.path.abspath(".")` 在 PyInstaller 环境下会变成 EXE 所在目录，而不是临时解压目录，导致资源找不到。
- **多资产目录遗漏**：本项目不仅有 UI 样式，还有多处存放图片的地方 (`assets/`, `ui/assets/`, `resources/icons/`)。
- **WinError 5 (运行中锁定)**：重新打包前，如果老版本的 EXE 还在后台运行，会导致新文件覆盖失败报错。

## 2. 代码级资源路径兼容 (Resource Path Function)
**在打包前，必须确保代码中使用专门的函数取用资源。**

在 `main.py` 和 `ui/main_window.py` 甚至是工具类 (`ToolBase`) 中，必须使用以下兼容性路径解析逻辑获取 `.qss`, `.png`, `.svg` 和 `.ico` 等静态资产：

```python
import sys
import os

def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和 PyInstaller 打包后的环境 """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 运行时的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境下的根目录
    return os.path.join(os.path.abspath("."), relative_path)
```
*注：如果在子目录下（如 `ui/base/tool_base.py`），使用相对层级推导根目录，再作拼装。*

## 3. spec 文件配置要点 (核心资产挂载)
当你新生成或修改 `RFAntennaToolkit.spec` 时，务必检查 `Analysis` 的 `datas` 数组和 `exe` 的 `icon`：

```python
# 必须显式声明所有包含静态文件（样式、图片、矢量图）的文件夹
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    # 【核心配置】缺少这些会导致工具打开时图标空白或白屏！
    datas=[
        ('ui/styles', 'ui/styles'),       # QSS 样式表
        ('ui/assets', 'ui/assets'),       # 工具截屏、微图
        ('assets', 'assets'),             # APP Icon，各类计算模型架构图
        ('resources/icons', 'resources/icons') # 链路预算用的全套 SVG 小组件图标
    ],
    # ...
)

exe = EXE(
    # ...
    console=False,           # 必须关闭控制台黑框 (GUI 软件标准)
    icon='assets/app.ico',   # 必须指定独立图标
    # ...
)
```

## 4. 一键执行编译构建步骤

**// turbo-all**

在执行打包前，务必按照以下顺序运行命令：

### Step 1: 强制清理残留进程
避免因为上一次测试未关闭，导致打包重写 EXE 时触发 `PermissionError: [WinError 5]`。
```powershell
taskkill /F /IM RFAntennaToolkit.exe
```

### Step 2: 在虚拟环境中执行编译 (-y 强制覆盖)
确保使用 `.venv` 中的 `PyInstaller`，仅包含项目所需依赖，大幅削减打包后的体积。
```powershell
.\.venv\Scripts\python.exe -m PyInstaller -y RFAntennaToolkit.spec
```

### Step 3: 原型验证
打包完成后，产物位于 `dist/RFAntennaToolkit/`。可通过运行以下命令验证核心图片资源是否成功注入了 `_internal` 内部工作目录：
```powershell
.\.venv\Scripts\python.exe -c "import os; print('Icons check:', os.path.exists('dist/RFAntennaToolkit/_internal/resources/icons/amplifier.svg'))"
```

如果输出 `True`，即代表打包成功，通知使用者即可！
