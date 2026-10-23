# v2.3 离线发行验收

验收日期：2026-10-24。基于中文主线 v2.2（`cb70509`）增加跳频测向捕获评估，并修复构建依赖路径污染。

## 构建与自动测试

- 构建解释器：Python 3.12.14，隔离环境 `env/fh-capture`。
- 独立程序：PyInstaller 6.22.3，使用 `python build_exe.py` 构建窗口应用。
- 安装包：Inno Setup 6.7.3，编译 `installer_setup.iss`；编译器安装文件的官方数字签名验证通过。
- 自动测试：`python -m pytest -q`，95项通过。
- `git diff --check` 通过。

首次独立启动发现构建工具从外部 Poppler 搜索路径误收集了 `icuuc.dll`，其导出接口与 Qt 所需的系统接口不同。已在构建期间隔离 Windows PATH 及外部 Qt 插件路径；重新构建产物的依赖清单不再包含该错误的国际化库。正常模式启动后，主窗口标题为 v2.3，进程响应正常。

## 最终安装包的实装验收

- 安装文件：`RFAntennaToolkit_CN_v2_Setup_v2.3.exe`，120,030,772字节。
- SHA-256：`c03a496f8fbccd0349da72ca692f45118570c1d21f74c0222bba0881ee6d13fe`。
- 在 Windows 11 x64 上使用 `/CURRENTUSER /VERYSILENT /SUPPRESSMSGBOXES /NORESTART` 实际安装，退出码0，安装日志确认成功且无需重启。
- 安装位置：`%LOCALAPPDATA%\Programs\RFAntennaToolkit`；已创建当前用户卸载注册项。
- 安装后EXE与构建目录EXE的SHA-256一致。

从项目目录之外执行安装后的EXE：

```powershell
& "$env:LOCALAPPDATA\Programs\RFAntennaToolkit\RFAntennaToolkit.exe" --verify-installation "installation-validation-v2.3.json"
```

验收进程只保留 Windows 系统 PATH，清空 `PYTHONPATH`、`PYTHONHOME`、`VIRTUAL_ENV`，并将HTTP、HTTPS和通用代理指向不可连接的本地端口。未修改用户或系统网络配置。报告确认 `frozen: true`、`success: true`，退出码0。

17项检查全部通过：四类关键资源存在、PNG解码、SVG渲染、主题样式、工具导航、44 μs基准、43.5 μs基准、25,000跳/秒缺4 μs判定、超时时间轴、跳速曲线、采样换算、错误输入清理、版本说明页和波导参考页。

验证使用隐藏的Qt窗口，不发送桌面键鼠输入。桌面自动控制已在收到Esc停止信号后终止。以上结果证明本机实装及隔离环境下的功能可用性，不代表对所有Windows版本和硬件的兼容性认证。

## 发布资产

- 离线安装包。
- `SHA256SUMS.txt`：安装包和验收JSON的摘要。
- `installation-validation-v2.3.json`：由实际安装后的EXE生成的17项检查报告。

安装后的本地计算无需联网；检查GitHub更新和访问外部资料需要网络。跳频工具只判断单跳时间预算，不预测实际捕获概率或测向精度。
