"""
Bilibili API 调用模块
用于搜索视频、获取视频信息和提取字幕
"""

import requests
import re
import json
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs


class BilibiliAPI:
    """B站API封装类"""

    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        """
        初始化API客户端

        Args:
            cookies: B站cookies字典，包含SESSDATA, bili_jct, buvid3
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.bilibili.com'
        })

        if cookies:
            self.session.cookies.update(cookies)

    def search_videos(self, keyword: str, page: int = 1, page_size: int = 20) -> List[Dict]:
        """
        搜索视频

        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量

        Returns:
            视频列表
        """
        url = "https://api.bilibili.com/x/web-interface/search/type"
        params = {
            'search_type': 'video',
            'keyword': keyword,
            'page': page,
            'page_size': page_size
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data['code'] != 0:
                raise Exception(f"API错误: {data.get('message', '未知错误')}")

            results = []
            for item in data['data']['result']:
                results.append({
                    'bvid': item.get('bvid'),
                    'aid': item.get('aid'),
                    'title': self._clean_html(item.get('title', '')),
                    'author': item.get('author', ''),
                    'duration': item.get('duration', ''),
                    'play': item.get('play', 0),
                    'description': self._clean_html(item.get('description', '')),
                    'url': f"https://www.bilibili.com/video/{item.get('bvid')}"
                })

            return results

        except Exception as e:
            raise Exception(f"搜索视频失败: {str(e)}")

    def get_video_info(self, bvid: str) -> Dict:
        """
        获取视频详细信息

        Args:
            bvid: 视频BV号

        Returns:
            视频信息字典
        """
        url = "https://api.bilibili.com/x/web-interface/view"
        params = {'bvid': bvid}

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data['code'] != 0:
                raise Exception(f"API错误: {data.get('message', '未知错误')}")

            video_data = data['data']
            return {
                'bvid': video_data['bvid'],
                'aid': video_data['aid'],
                'cid': video_data['cid'],
                'title': video_data['title'],
                'description': video_data['desc'],
                'author': video_data['owner']['name'],
                'duration': video_data['duration'],
                'pub_date': video_data['pubdate'],
                'view': video_data['stat']['view'],
                'like': video_data['stat']['like'],
                'pages': [{'cid': p['cid'], 'page': p['page'], 'part': p['part']}
                         for p in video_data.get('pages', [])]
            }

        except Exception as e:
            raise Exception(f"获取视频信息失败: {str(e)}")

    def get_subtitle_list(self, bvid: str, cid: Optional[int] = None) -> List[Dict]:
        """
        获取视频字幕列表

        Args:
            bvid: 视频BV号
            cid: 视频分P的cid，如果不提供则使用第一P

        Returns:
            字幕列表
        """
        # 如果没有提供cid，先获取视频信息得到cid
        if cid is None:
            video_info = self.get_video_info(bvid)
            cid = video_info['cid']

        # 使用新的API端点
        url = "https://api.bilibili.com/x/player/wbi/v2"
        params = {
            'bvid': bvid,
            'cid': cid
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data['code'] != 0:
                # 尝试旧API
                return self._get_subtitle_list_legacy(bvid, cid)

            subtitle_data = data.get('data', {}).get('subtitle', {})
            subtitles = subtitle_data.get('subtitles', [])

            result = []
            for sub in subtitles:
                result.append({
                    'language': sub.get('lan_doc', sub.get('lan', '')),
                    'language_code': sub.get('lan', ''),
                    'subtitle_url': 'https:' + sub['subtitle_url'] if not sub['subtitle_url'].startswith('http') else sub['subtitle_url'],
                    'author': sub.get('author', {}).get('name', '')
                })

            return result

        except Exception as e:
            raise Exception(f"获取字幕列表失败: {str(e)}")

    def _get_subtitle_list_legacy(self, bvid: str, cid: int) -> List[Dict]:
        """使用旧版API获取字幕列表"""
        url = "https://api.bilibili.com/x/player/v2"
        params = {
            'bvid': bvid,
            'cid': cid
        }

        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['code'] != 0:
            raise Exception(f"API错误: {data.get('message', '未知错误')}")

        subtitle_data = data.get('data', {}).get('subtitle', {})
        subtitles = subtitle_data.get('subtitles', [])

        result = []
        for sub in subtitles:
            result.append({
                'language': sub.get('lan_doc', sub.get('lan', '')),
                'language_code': sub.get('lan', ''),
                'subtitle_url': 'https:' + sub['subtitle_url'] if not sub['subtitle_url'].startswith('http') else sub['subtitle_url'],
                'author': sub.get('author', {}).get('name', '')
            })

        return result

    def download_subtitle(self, subtitle_url: str) -> List[Dict]:
        """
        下载字幕内容

        Args:
            subtitle_url: 字幕URL

        Returns:
            字幕内容列表
        """
        try:
            response = self.session.get(subtitle_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            return data.get('body', [])

        except Exception as e:
            raise Exception(f"下载字幕失败: {str(e)}")

    @staticmethod
    def extract_bvid(url_or_bvid: str) -> str:
        """
        从URL或字符串中提取BV号

        Args:
            url_or_bvid: B站视频URL或BV号

        Returns:
            BV号
        """
        # 如果已经是BV号格式
        if url_or_bvid.startswith('BV'):
            return url_or_bvid

        # 从URL中提取
        bv_pattern = r'BV[a-zA-Z0-9]+'
        match = re.search(bv_pattern, url_or_bvid)

        if match:
            return match.group(0)

        raise ValueError(f"无法从 '{url_or_bvid}' 中提取BV号")

    @staticmethod
    def _clean_html(text: str) -> str:
        """清理HTML标签"""
        text = re.sub(r'<em[^>]*>', '', text)
        text = re.sub(r'</em>', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        return text
