"""
配置管理模块
用于管理B站cookies等配置信息
"""

import json
import os
from typing import Dict, Optional


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            return {}

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}

    def _save_config(self) -> None:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def get_cookies(self) -> Optional[Dict[str, str]]:
        """获取B站cookies"""
        cookies_data = self.config.get('cookies', {})

        # 检查必需的cookie字段
        required_fields = ['SESSDATA', 'bili_jct', 'buvid3']
        if not all(field in cookies_data for field in required_fields):
            return None

        return cookies_data

    def set_cookies(self, sessdata: str, bili_jct: str, buvid3: str) -> None:
        """
        设置B站cookies

        Args:
            sessdata: SESSDATA cookie值
            bili_jct: bili_jct cookie值
            buvid3: buvid3 cookie值
        """
        self.config['cookies'] = {
            'SESSDATA': sessdata,
            'bili_jct': bili_jct,
            'buvid3': buvid3
        }
        self._save_config()
        print("配置已保存!")

    def is_configured(self) -> bool:
        """检查是否已配置"""
        return self.get_cookies() is not None

    def setup_interactive(self) -> None:
        """交互式配置"""
        print("\n=== B站Cookie配置 ===")
        print("\n获取步骤:")
        print("1. 在浏览器中登录 bilibili.com")
        print("2. 按 F12 打开开发者工具")
        print("3. 进入 Application/应用 -> Cookies")
        print("4. 找到 bilibili.com 下的以下cookie:")
        print("   - SESSDATA")
        print("   - bili_jct")
        print("   - buvid3")
        print("\n请依次输入这些值:\n")

        sessdata = input("SESSDATA: ").strip()
        bili_jct = input("bili_jct: ").strip()
        buvid3 = input("buvid3: ").strip()

        if not all([sessdata, bili_jct, buvid3]):
            print("\n错误: 所有字段都是必需的!")
            return

        self.set_cookies(sessdata, bili_jct, buvid3)
        print("\n配置成功! 现在可以使用字幕提取功能了。")

    def clear_config(self) -> None:
        """清除配置"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
            print("配置已清除!")
        self.config = {}
