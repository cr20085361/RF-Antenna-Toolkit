; 射频天线工具集 - Inno Setup 打包脚本
; 需要先运行 python build_exe.py 生成 dist/RFAntennaToolkit 目录后再执行此脚本

[Setup]
AppId={{RF-ANTENNA-TOOLKIT-1234-5678}
AppName=射频天线工具集
AppVersion=1.0.0
AppPublisher=RF Antenna Team
AppPublisherURL=https://github.com/
AppSupportURL=https://github.com/
AppUpdatesURL=https://github.com/
DefaultDirName={autopf}\RFAntennaToolkit
DisableProgramGroupPage=yes
; 最终生成的安装包输出目录
OutputDir=Output
; 最终生成的安装包文件名
OutputBaseFilename=RFAntennaToolkit_Setup_v2.0.0
; 安装包压缩算法
Compression=lzma
SolidCompression=yes
; 采用现代安装向导样式
WizardStyle=modern

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 将 PyInstaller 编译好的整个单目录下所有文件打包
Source: "dist\RFAntennaToolkit\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 生成开始菜单快捷方式
Name: "{autoprograms}\射频天线工具集"; Filename: "{app}\RFAntennaToolkit.exe"
; 生成桌面快捷方式
Name: "{autodesktop}\射频天线工具集"; Filename: "{app}\RFAntennaToolkit.exe"; Tasks: desktopicon

[Run]
; 安装完成后是否立即运行
Filename: "{app}\RFAntennaToolkit.exe"; Description: "{cm:LaunchProgram,射频天线工具集}"; Flags: nowait postinstall skipifsilent
