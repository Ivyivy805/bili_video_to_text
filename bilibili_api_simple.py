"""
简化的B站API实现
不依赖bilibili-api-python，直接调用B站API
"""

import requests
import json
import re
import hashlib
import time
from typing import List, Dict, Optional
from urllib.parse import urlencode


class BilibiliAPI:
    """B站API封装类 - 简化版"""

    def __init__(self, sessdata: str = None, bili_jct: str = None, buvid3: str = None):
        """
        初始化B站API

        Args:
            sessdata: B站Cookie中的SESSDATA值（可选）
            bili_jct: B站Cookie中的bili_jct值（可选）
            buvid3: B站Cookie中的buvid3值（可选）
        """
        self.sessdata = sessdata
        self.bili_jct = bili_jct
        self.buvid3 = buvid3

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Origin': 'https://www.bilibili.com'
        }

        if sessdata:
            self.cookies = {
                'SESSDATA': sessdata,
                'bili_jct': bili_jct or '',
                'buvid3': buvid3 or ''
            }
            print("✓ 已加载登录凭证")
        else:
            self.cookies = {}
            print("ℹ 未配置登录凭证，将以游客模式运行")

    def extract_bvid_from_url(self, url: str) -> Optional[str]:
        """
        从B站URL中提取BV号

        Args:
            url: B站视频URL

        Returns:
            BV号，如果提取失败则返回None
        """
        pattern = r'BV[a-zA-Z0-9]+'
        match = re.search(pattern, url)
        return match.group(0) if match else None

    def search_videos(self, keyword: str, page: int = 1, page_size: int = 10) -> List[Dict]:
        """
        搜索B站视频

        Args:
            keyword: 搜索关键词
            page: 页码（从1开始）
            page_size: 每页结果数量

        Returns:
            视频列表
        """
        print(f"🔍 正在搜索: {keyword}")
        print("ℹ 注意: 搜索功能可能需要登录凭证，如遇问题请直接使用BV号或URL")

        try:
            # 使用web-interface/wbi/search/all/v2接口
            url = 'https://api.bilibili.com/x/web-interface/wbi/search/all/v2'
            params = {
                'keyword': keyword,
                'page': page,
                'page_size': page_size,
                'platform': 'pc',
                'search_type': 'video'
            }

            response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params, timeout=10)

            # 如果403，尝试使用另一个接口
            if response.status_code == 403:
                print("ℹ 尝试使用备用搜索接口...")
                url = f'https://search.bilibili.com/api/search'
                params = {
                    'keyword': keyword,
                    '__refresh__': 'true',
                    'page': page,
                    'pagesize': page_size,
                    'search_type': 'video'
                }
                response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params, timeout=10)

            if response.status_code != 200:
                print(f"❌ 搜索接口返回 {response.status_code}")
                print(f"💡 建议: 请直接使用 --bvid 或 --url 参数来提取字幕")
                return []

            data = response.json()

            # 尝试解析不同的响应格式
            result_list = []
            if 'data' in data and 'result' in data['data']:
                # 格式1
                for item_group in data['data']['result']:
                    if isinstance(item_group, dict) and item_group.get('result_type') == 'video':
                        result_list = item_group.get('data', [])
                        break
            elif 'result' in data:
                # 格式2
                result_list = data['result']

            if not result_list:
                print("❌ 搜索无结果")
                print(f"💡 建议: 请直接使用 --bvid 或 --url 参数来提取字幕")
                return []

            videos = []
            for item in result_list:
                # 清理HTML标签
                title = re.sub(r'<[^>]+>', '', item.get('title', ''))

                video_info = {
                    'title': title,
                    'bvid': item.get('bvid', ''),
                    'author': item.get('author', item.get('owner', {}).get('name', '')),
                    'duration': item.get('duration', ''),
                    'play': item.get('play', item.get('view', 0)),
                    'description': item.get('description', item.get('desc', '')),
                }
                videos.append(video_info)

            print(f"✓ 找到 {len(videos)} 个视频")
            return videos

        except Exception as e:
            print(f"❌ 搜索出错: {str(e)}")
            print(f"💡 建议: 请直接使用 --bvid 或 --url 参数来提取字幕")
            return []

    def get_video_info(self, bvid: str) -> Optional[Dict]:
        """
        获取视频详细信息

        Args:
            bvid: 视频BV号

        Returns:
            视频信息字典
        """
        print(f"📺 正在获取视频信息: {bvid}")

        try:
            url = 'https://api.bilibili.com/x/web-interface/view'
            params = {'bvid': bvid}

            response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('code') != 0:
                print(f"❌ API返回错误: {data.get('message', 'Unknown error')}")
                return None

            info = data['data']
            pages = info.get('pages', [])
            cid = pages[0]['cid'] if pages else None

            video_info = {
                'bvid': bvid,
                'aid': info.get('aid', 0),
                'title': info.get('title', ''),
                'author': info.get('owner', {}).get('name', ''),
                'description': info.get('desc', ''),
                'duration': info.get('duration', 0),
                'play': info.get('stat', {}).get('view', 0),
                'cid': cid,
                'pages': len(pages),
            }

            print(f"✓ 视频标题: {video_info['title']}")
            print(f"  作者: {video_info['author']}")
            print(f"  分P数: {video_info['pages']}")

            return video_info

        except Exception as e:
            print(f"❌ 获取视频信息失败: {str(e)}")
            return None

    def get_subtitles(self, bvid: str, cid: int) -> List[Dict]:
        """
        获取视频字幕列表

        Args:
            bvid: 视频BV号
            cid: 视频CID

        Returns:
            字幕列表
        """
        print(f"📝 正在获取字幕信息...")

        try:
            url = 'https://api.bilibili.com/x/player/v2'
            params = {
                'bvid': bvid,
                'cid': cid
            }

            response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('code') != 0:
                print(f"ℹ 无法获取字幕信息")
                return []

            subtitle_info = data.get('data', {}).get('subtitle', {})
            subtitles = subtitle_info.get('subtitles', [])

            if not subtitles:
                print("ℹ 该视频没有字幕")
                return []

            print(f"✓ 找到 {len(subtitles)} 个字幕")
            for sub in subtitles:
                lang = sub.get('lan_doc', sub.get('lan', 'unknown'))
                print(f"  - {lang}")

            return subtitles

        except Exception as e:
            print(f"❌ 获取字幕失败: {str(e)}")
            return []


def format_duration(seconds: int) -> str:
    """
    格式化时长

    Args:
        seconds: 秒数

    Returns:
        格式化后的时长字符串
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"
