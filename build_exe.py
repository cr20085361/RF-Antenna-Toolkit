import PyInstaller.__main__
import os
import shutil

# 获取当前脚本所在目录作为项目根目录
project_dir = os.path.dirname(os.path.abspath(__file__))

# 定义要传递给 PyInstaller 的参数
pyinstaller_args = [
    'main.py',                         # 主程序入口
    '--name=RFAntennaToolkit',         # 生成的 exe 名称
    '--windowed',                      # 隐藏控制台窗口 (GUI 程序必备)
    '--onedir',                        # 生成单目录模式 (比单文件启动快，适合包含大量资源的项目)
    '--clean',                         # 每次打包前清理临时文件
    '--noconfirm',                     # 覆盖原有输出目录
    
    # 附带资源文件 (格式: 来源:目标文件夹)
    # Windows 下使用分号(;)分割，Linux/Mac 下使用冒号(:)
    f'--add-data=assets;assets',       
    f'--add-data=core;core',
    f'--add-data=ui;ui',
    f'--add-data=resources;resources',
    
    # 如果有图标，可以取消下方注释并添加 .ico
    # '--icon=assets/icon.ico',
]

print("开始编译射频天线工具集...")
PyInstaller.__main__.run(pyinstaller_args)
print("编译完成！可执行文件位于 dist/RFAntennaToolkit 目录下。")
