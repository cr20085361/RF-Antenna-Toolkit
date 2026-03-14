# -*- coding: utf-8 -*-
"""
射频天线工具集 - 国际化 (i18n) 核心管理模块
RF Antenna Toolkit - Internationalization Core

版本: v2.0.0
功能: 单例化加载 JSON 语言字典，提供全局翻译接口和语言切换播报注册
"""

import os
import json
import sys
from typing import Dict, Any

from PyQt6.QtCore import QObject, pyqtSignal


def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和 PyInstaller 打包后的环境 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), relative_path)


class Translator(QObject):
    """
    全局多语言翻译器 (单例模式)
    
    使用方式:
    from core.i18n import translator, tr
    
    text = tr("nav.antenna_tools")
    
    # 监听语言切换信号刷新UI
    translator.language_changed.connect(self.retranslate_ui)
    """
    
    # 全局语言切换信号
    language_changed = pyqtSignal(str)
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        super().__init__()
        self._current_lang = "zh_CN"
        self._dict: Dict[str, Any] = {}
        self._locales_dir = resource_path(os.path.join("assets", "locales"))
        
        # 尝试读取上次使用的语言配置
        self._load_preferences()
        
        # 加载初始语言字典
        self.load_language(self._current_lang)
        self._initialized = True

    def _load_preferences(self):
        """读取语言偏好设置"""
        config_path = resource_path("config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self._current_lang = config.get("language", "zh_CN")
        except Exception as e:
            print(f"Error loading language preferences: {e}")

    def _save_preferences(self):
        """保存语言偏好设置"""
        config_path = resource_path("config.json")
        try:
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
            config["language"] = self._current_lang
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving language preferences: {e}")

    def load_language(self, lang_code: str):
        """加载指定的语言字典 (如 'zh_CN', 'en_US')"""
        file_path = os.path.join(self._locales_dir, f"{lang_code}.json")
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._dict = json.load(f)
                    self._current_lang = lang_code
                    self._save_preferences()
                    # 发出信号，通知全局重绘
                    self.language_changed.emit(lang_code)
                    return True
            else:
                print(f"Warning: Locale file not found: {file_path}")
                return False
        except Exception as e:
            print(f"Error loading translation file {lang_code}: {e}")
            return False

    def toggle_language(self):
        """中英双语切换快捷方法"""
        new_lang = "en_US" if self._current_lang == "zh_CN" else "zh_CN"
        self.load_language(new_lang)
        return new_lang

    def get_current_language(self):
        return self._current_lang

    def translate(self, key: str, default: str = None) -> str:
        """
        获取翻译文本
        支持形如 "nav.antenna_tools" 的扁平化或嵌套字典路径查询
        """
        keys = key.split('.')
        current_dict = self._dict
        
        try:
            for k in keys:
                current_dict = current_dict[k]
            return str(current_dict)
        except (KeyError, TypeError):
            # 未找到翻译时，返回默认值或者直接返回Key
            if default is not None:
                return default
            return key


# 全局单例实例
translator = Translator()

# 全局快捷翻译函数
def tr(key: str, default: str = None) -> str:
    return translator.translate(key, default)
