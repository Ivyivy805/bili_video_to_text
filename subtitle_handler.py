"""
字幕处理模块
用于格式化、转换和保存字幕
"""

import os
import json
from typing import List, Dict
from datetime import timedelta


class SubtitleHandler:
    """字幕处理类"""

    @staticmethod
    def format_time_srt(seconds: float) -> str:
        """
        将秒数转换为SRT时间格式 (HH:MM:SS,mmm)

        Args:
            seconds: 秒数

        Returns:
            SRT格式时间字符串
        """
        td = timedelta(seconds=seconds)
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        secs = td.seconds % 60
        millis = td.microseconds // 1000

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def to_srt(subtitle_data: List[Dict]) -> str:
        """
        将B站字幕数据转换为SRT格式

        Args:
            subtitle_data: B站字幕数据列表

        Returns:
            SRT格式字符串
        """
        srt_lines = []

        for i, item in enumerate(subtitle_data, 1):
            start_time = item.get('from', 0)
            end_time = item.get('to', 0)
            text = item.get('content', '').strip()

            if not text:
                continue

            # SRT序号
            srt_lines.append(str(i))

            # 时间轴
            start_str = SubtitleHandler.format_time_srt(start_time)
            end_str = SubtitleHandler.format_time_srt(end_time)
            srt_lines.append(f"{start_str} --> {end_str}")

            # 字幕文本
            srt_lines.append(text)

            # 空行分隔
            srt_lines.append("")

        return "\n".join(srt_lines)

    @staticmethod
    def to_txt(subtitle_data: List[Dict]) -> str:
        """
        将B站字幕数据转换为纯文本格式

        Args:
            subtitle_data: B站字幕数据列表

        Returns:
            纯文本字符串
        """
        text_lines = []

        for item in subtitle_data:
            text = item.get('content', '').strip()
            if text:
                text_lines.append(text)

        return "\n".join(text_lines)

    @staticmethod
    def to_json(subtitle_data: List[Dict], indent: int = 2) -> str:
        """
        将B站字幕数据转换为JSON格式

        Args:
            subtitle_data: B站字幕数据列表
            indent: JSON缩进空格数

        Returns:
            JSON格式字符串
        """
        return json.dumps(subtitle_data, ensure_ascii=False, indent=indent)

    @staticmethod
    def save_subtitle(content: str, output_path: str) -> None:
        """
        保存字幕到文件

        Args:
            content: 字幕内容
            output_path: 输出文件路径
        """
        # 创建输出目录
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        清理文件名，移除不合法字符

        Args:
            filename: 原始文件名

        Returns:
            清理后的文件名
        """
        # 替换不合法字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # 限制长度
        if len(filename) > 200:
            filename = filename[:200]

        return filename

    @staticmethod
    def generate_filename(title: str, bvid: str, language: str, format: str) -> str:
        """
        生成字幕文件名

        Args:
            title: 视频标题
            bvid: 视频BV号
            language: 字幕语言
            format: 输出格式

        Returns:
            文件名
        """
        safe_title = SubtitleHandler.sanitize_filename(title)
        return f"{safe_title}_{bvid}_{language}.{format}"


class SubtitleExtractor:
    """字幕提取器"""

    def __init__(self, api_client):
        """
        初始化提取器

        Args:
            api_client: BilibiliAPI实例
        """
        self.api = api_client
        self.handler = SubtitleHandler()

    def extract_and_save(
        self,
        bvid: str,
        output_dir: str = "subtitles",
        format: str = "srt",
        language: str = None
    ) -> List[str]:
        """
        提取并保存字幕

        Args:
            bvid: 视频BV号
            output_dir: 输出目录
            format: 输出格式 (srt/txt/json)
            language: 指定语言代码，None表示下载所有语言

        Returns:
            保存的文件路径列表
        """
        # 获取视频信息
        video_info = self.api.get_video_info(bvid)
        title = video_info['title']
        cid = video_info['cid']

        print(f"视频标题: {title}")
        print(f"视频BV号: {bvid}")

        # 获取字幕列表
        subtitle_list = self.api.get_subtitle_list(bvid, cid)

        if not subtitle_list:
            print("该视频没有字幕")
            return []

        print(f"找到 {len(subtitle_list)} 个字幕:")
        for sub in subtitle_list:
            print(f"  - {sub['language']} ({sub['language_code']})")

        # 筛选要下载的字幕
        if language:
            subtitle_list = [s for s in subtitle_list if s['language_code'] == language]
            if not subtitle_list:
                print(f"未找到语言代码为 '{language}' 的字幕")
                return []

        # 下载并保存字幕
        saved_files = []
        for sub in subtitle_list:
            lang_code = sub['language_code']
            lang_name = sub['language']
            subtitle_url = sub['subtitle_url']

            print(f"\n下载字幕: {lang_name}...")

            # 下载字幕数据
            subtitle_data = self.api.download_subtitle(subtitle_url)

            # 转换格式
            if format == 'srt':
                content = self.handler.to_srt(subtitle_data)
            elif format == 'txt':
                content = self.handler.to_txt(subtitle_data)
            elif format == 'json':
                content = self.handler.to_json(subtitle_data)
            else:
                raise ValueError(f"不支持的格式: {format}")

            # 生成文件名和路径
            filename = self.handler.generate_filename(title, bvid, lang_code, format)
            output_path = os.path.join(output_dir, filename)

            # 保存文件
            self.handler.save_subtitle(content, output_path)
            saved_files.append(output_path)

            print(f"已保存: {output_path}")

        return saved_files
