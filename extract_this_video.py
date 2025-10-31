#!/usr/bin/env python3
"""
专门提取 BV1QwdzYgEpw 这个视频的字幕
请在你的本地电脑上运行此脚本
"""

import requests
import json
import os

# 你的Cookie信息
SESSDATA = "87d63d06%2C1777451405%2C37449%2Aa1CjAKiOeLP27Db6YwVeEkQptaWZDpVaAVbFw8m69S1DOs4dOKwJeEVb64BrG5vgLF0N4SVjlxQVAybXdUNUxOV0ctaE05NDFLVDJjUEJMMVFndnNmcEM2Vl9paldxN3EyM2tZRXBEVGxna256S3BSek5rVGp4VFJhdkJyR1UxLVF4djM3dXlKMkZBIIEC"
BILI_JCT = "268f333f7ec5472e366bf3f0f1555f42"
BUVID3 = "44DC86F9-677A-07B7-171D-DE6BC0E0CD2889904infoc"

BVID = "BV1QwdzYgEpw"

def main():
    session = requests.Session()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': f'https://www.bilibili.com/video/{BVID}/',
        'Accept': 'application/json, text/plain, */*',
    }

    cookies = {
        'SESSDATA': SESSDATA,
        'bili_jct': BILI_JCT,
        'buvid3': BUVID3,
    }

    # 1. 获取视频信息
    print(f"📺 正在获取视频信息: {BVID}")
    video_url = f'https://api.bilibili.com/x/web-interface/view?bvid={BVID}'

    try:
        response = session.get(video_url, headers=headers, cookies=cookies)
        response.raise_for_status()

        data = response.json()

        if data.get('code') != 0:
            print(f"❌ 错误: {data.get('message')}")
            return

        info = data['data']
        title = info.get('title', '')
        author = info.get('owner', {}).get('name', '')
        cid = info.get('cid')

        print(f"✓ 视频标题: {title}")
        print(f"✓ 作者: {author}")
        print(f"✓ CID: {cid}")

        if not cid:
            print("❌ 无法获取CID")
            return

        # 2. 获取字幕
        print(f"\n📝 正在获取字幕...")
        subtitle_url = f'https://api.bilibili.com/x/player/v2?bvid={BVID}&cid={cid}'

        sub_response = session.get(subtitle_url, headers=headers, cookies=cookies)
        sub_response.raise_for_status()

        sub_data = sub_response.json()

        if sub_data.get('code') != 0:
            print(f"❌ 获取字幕失败: {sub_data.get('message')}")
            return

        subtitle_info = sub_data.get('data', {}).get('subtitle', {})
        subtitles = subtitle_info.get('subtitles', [])

        if not subtitles:
            print("ℹ 该视频没有字幕")
            return

        print(f"✓ 找到 {len(subtitles)} 个字幕")

        # 3. 下载字幕
        for sub in subtitles:
            lang = sub.get('lan_doc', 'unknown')
            sub_url = sub.get('subtitle_url', '')

            if not sub_url.startswith('http'):
                sub_url = 'https:' + sub_url

            print(f"\n📥 下载 {lang} 字幕...")

            content_response = requests.get(sub_url)
            content_response.raise_for_status()

            subtitle_content = content_response.json()
            body = subtitle_content.get('body', [])

            print(f"✓ 获取到 {len(body)} 条字幕")

            # 保存为JSON
            json_file = f"{BVID}_{lang}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(body, f, ensure_ascii=False, indent=2)
            print(f"✓ 已保存: {json_file}")

            # 保存为SRT
            srt_file = f"{BVID}_{lang}.srt"
            with open(srt_file, 'w', encoding='utf-8') as f:
                for idx, item in enumerate(body, 1):
                    start = format_time(item.get('from', 0))
                    end = format_time(item.get('to', 0))
                    text = item.get('content', '')
                    f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")
            print(f"✓ 已保存: {srt_file}")

            # 保存为TXT
            txt_file = f"{BVID}_{lang}.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                for item in body:
                    f.write(item.get('content', '') + '\n')
            print(f"✓ 已保存: {txt_file}")

            # 保存为Markdown
            md_file = f"{BVID}_{lang}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"**作者**: {author}  \n")
                f.write(f"**BV号**: {BVID}  \n")
                f.write(f"**语言**: {lang}  \n\n")
                f.write("---\n\n")

                for item in body:
                    start_time = format_time(item.get('from', 0))
                    text = item.get('content', '')
                    f.write(f"**[{start_time}]** {text}\n\n")

            print(f"✓ 已保存: {md_file}")

            # 打印前几条预览
            print(f"\n📄 字幕预览:")
            for item in body[:5]:
                print(f"  {item.get('content', '')}")
            if len(body) > 5:
                print(f"  ... (共 {len(body)} 条)")

        print(f"\n✅ 完成！")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

def format_time(seconds):
    """格式化SRT时间"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

if __name__ == '__main__':
    main()
