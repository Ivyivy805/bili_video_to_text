"""
简化的字幕提取模块
直接使用HTTP请求获取字幕
"""

import json
import requests
import re
from typing import List, Dict, Optional


class SubtitleExtractor:
    """简化的字幕提取器"""

    def __init__(self, api):
        """
        初始化字幕提取器

        Args:
            api: BilibiliAPI实例
        """
        self.api = api

    def get_subtitles(self, bvid: str, cid: int) -> List[Dict]:
        """
        获取视频字幕列表

        Args:
            bvid: 视频BV号
            cid: 视频CID

        Returns:
            字幕列表
        """
        return self.api.get_subtitles(bvid, cid)

    def download_subtitle(self, subtitle_url: str) -> Optional[List[Dict]]:
        """
        下载字幕内容

        Args:
            subtitle_url: 字幕URL

        Returns:
            字幕内容列表
        """
        try:
            # B站字幕URL可能不带协议
            if not subtitle_url.startswith('http'):
                subtitle_url = 'https:' + subtitle_url

            print(f"⬇️  正在下载字幕...")

            response = requests.get(subtitle_url, timeout=10)
            response.raise_for_status()

            subtitle_data = response.json()

            if 'body' not in subtitle_data:
                print("❌ 字幕格式错误")
                return None

            print(f"✓ 字幕下载成功，共 {len(subtitle_data['body'])} 条")
            return subtitle_data['body']

        except Exception as e:
            print(f"❌ 下载字幕失败: {str(e)}")
            return None

    def extract_and_save(self, bvid: str, cid: int, output_dir: str = ".") -> bool:
        """
        提取并保存字幕

        Args:
            bvid: 视频BV号
            cid: 视频CID
            output_dir: 输出目录

        Returns:
            是否成功
        """
        # 获取字幕列表
        subtitles = self.get_subtitles(bvid, cid)

        if not subtitles:
            return False

        success = False

        # 下载所有可用字幕
        for sub in subtitles:
            lang = sub.get('lan_doc', sub.get('lan', 'unknown'))
            subtitle_url = sub.get('subtitle_url', '')

            if not subtitle_url:
                continue

            print(f"\n📥 正在处理 {lang} 字幕...")

            # 下载字幕内容
            subtitle_content = self.download_subtitle(subtitle_url)

            if not subtitle_content:
                continue

            # 生成文件名
            safe_lang = self._safe_filename(lang)
            json_filename = f"{output_dir}/{bvid}_{safe_lang}.json"
            srt_filename = f"{output_dir}/{bvid}_{safe_lang}.srt"
            txt_filename = f"{output_dir}/{bvid}_{safe_lang}.txt"

            # 保存JSON格式
            self.save_json(subtitle_content, json_filename)

            # 保存SRT格式
            self.save_srt(subtitle_content, srt_filename)

            # 保存纯文本格式
            self.save_text(subtitle_content, txt_filename)

            success = True

        return success

    def save_json(self, subtitle_content: List[Dict], filename: str):
        """保存为JSON格式"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(subtitle_content, f, ensure_ascii=False, indent=2)
            print(f"✓ JSON格式已保存: {filename}")
        except Exception as e:
            print(f"❌ 保存JSON失败: {str(e)}")

    def save_srt(self, subtitle_content: List[Dict], filename: str):
        """保存为SRT格式"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for index, item in enumerate(subtitle_content, 1):
                    start_time = self._format_srt_time(item.get('from', 0))
                    end_time = self._format_srt_time(item.get('to', 0))
                    text = item.get('content', '')

                    f.write(f"{index}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")

            print(f"✓ SRT格式已保存: {filename}")
        except Exception as e:
            print(f"❌ 保存SRT失败: {str(e)}")

    def save_text(self, subtitle_content: List[Dict], filename: str):
        """保存为纯文本格式"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for item in subtitle_content:
                    text = item.get('content', '').strip()
                    if text:
                        f.write(f"{text}\n")

            print(f"✓ TXT格式已保存: {filename}")
        except Exception as e:
            print(f"❌ 保存TXT失败: {str(e)}")

    def get_text_only(self, subtitle_content: List[Dict]) -> str:
        """提取纯文本内容"""
        return '\n'.join([item.get('content', '') for item in subtitle_content])

    def _format_srt_time(self, seconds: float) -> str:
        """格式化SRT时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _safe_filename(self, filename: str) -> str:
        """生成安全的文件名"""
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.strip()
        return filename if filename else 'subtitle'
