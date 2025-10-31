#!/usr/bin/env python3
"""
B站视频字幕提取工具 - 主程序
支持搜索视频、获取视频信息、提取字幕
"""

import argparse
import os
import sys
from bilibili_api_simple import BilibiliAPI, format_duration
from subtitle_extractor_simple import SubtitleExtractor


def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🎬 B站视频字幕提取工具")
    print("=" * 60)
    print()


def print_video_info(video_info: dict, index: int = None):
    """
    打印视频信息

    Args:
        video_info: 视频信息字典
        index: 序号（可选）
    """
    prefix = f"[{index}] " if index is not None else ""

    print(f"{prefix}📺 {video_info.get('title', 'N/A')}")
    print(f"    👤 作者: {video_info.get('author', 'N/A')}")

    if 'duration' in video_info:
        duration = video_info['duration']
        if isinstance(duration, str):
            print(f"    ⏱️  时长: {duration}")
        elif isinstance(duration, int):
            print(f"    ⏱️  时长: {format_duration(duration)}")

    if 'play' in video_info:
        play_count = video_info['play']
        if play_count >= 10000:
            print(f"    👀 播放: {play_count / 10000:.1f}万")
        else:
            print(f"    👀 播放: {play_count}")

    print(f"    🔗 BV号: {video_info.get('bvid', 'N/A')}")
    print()


def search_mode(api: BilibiliAPI, keyword: str):
    """
    搜索模式

    Args:
        api: BilibiliAPI实例
        keyword: 搜索关键词
    """
    print_banner()

    # 搜索视频
    videos = api.search_videos(keyword, page_size=10)

    if not videos:
        print("❌ 没有找到相关视频")
        return

    print(f"\n{'=' * 60}")
    print("搜索结果:")
    print('=' * 60)
    print()

    # 显示搜索结果
    for i, video in enumerate(videos, 1):
        print_video_info(video, i)

    # 提示用户选择
    print("=" * 60)
    print(f"💡 找到 {len(videos)} 个视频")
    print(f"💡 使用以下命令提取字幕:")
    print(f"   python main.py --bvid <BV号>")
    print()


def extract_mode(api: BilibiliAPI, extractor: SubtitleExtractor, bvid: str, output_dir: str):
    """
    提取模式

    Args:
        api: BilibiliAPI实例
        extractor: SubtitleExtractor实例
        bvid: 视频BV号
        output_dir: 输出目录
    """
    print_banner()

    # 获取视频信息
    video_info = api.get_video_info(bvid)

    if not video_info:
        print("❌ 无法获取视频信息")
        return

    print("\n" + "=" * 60)
    print("视频信息:")
    print("=" * 60)
    print()
    print_video_info(video_info)

    cid = video_info.get('cid')

    if not cid:
        print("❌ 无法获取视频CID")
        return

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 提取字幕
    print("=" * 60)
    success = extractor.extract_and_save(bvid, cid, output_dir)

    print("\n" + "=" * 60)
    if success:
        print("✅ 字幕提取成功！")
        print(f"📁 字幕已保存到: {output_dir}")
    else:
        print("❌ 字幕提取失败或该视频没有字幕")
    print("=" * 60)


def url_mode(api: BilibiliAPI, extractor: SubtitleExtractor, url: str, output_dir: str):
    """
    URL模式

    Args:
        api: BilibiliAPI实例
        extractor: SubtitleExtractor实例
        url: B站视频URL
        output_dir: 输出目录
    """
    # 从URL提取BV号
    bvid = api.extract_bvid_from_url(url)

    if not bvid:
        print("❌ 无法从URL中提取BV号")
        print(f"   URL: {url}")
        return

    print(f"✓ 提取到BV号: {bvid}")

    # 调用提取模式
    extract_mode(api, extractor, bvid, output_dir)


def interactive_mode(api: BilibiliAPI, extractor: SubtitleExtractor):
    """
    交互模式

    Args:
        api: BilibiliAPI实例
        extractor: SubtitleExtractor实例
    """
    print_banner()
    print("📋 交互模式")
    print()
    print("请选择操作:")
    print("  1. 搜索视频")
    print("  2. 提取字幕（通过BV号）")
    print("  3. 提取字幕（通过URL）")
    print("  0. 退出")
    print()

    try:
        choice = input("请输入选项 (0-3): ").strip()

        if choice == '1':
            keyword = input("\n请输入搜索关键词: ").strip()
            if keyword:
                search_mode(api, keyword)
            else:
                print("❌ 关键词不能为空")

        elif choice == '2':
            bvid = input("\n请输入BV号: ").strip()
            if bvid:
                output_dir = input("输出目录 (默认为当前目录): ").strip() or "."
                extract_mode(api, extractor, bvid, output_dir)
            else:
                print("❌ BV号不能为空")

        elif choice == '3':
            url = input("\n请输入B站视频URL: ").strip()
            if url:
                output_dir = input("输出目录 (默认为当前目录): ").strip() or "."
                url_mode(api, extractor, url, output_dir)
            else:
                print("❌ URL不能为空")

        elif choice == '0':
            print("👋 再见！")

        else:
            print("❌ 无效的选项")

    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except EOFError:
        print("\n\n👋 再见！")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='B站视频字幕提取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 搜索视频
  python main.py --search "Python教程"

  # 通过BV号提取字幕
  python main.py --bvid BV1xx411c7mD

  # 通过URL提取字幕
  python main.py --url "https://www.bilibili.com/video/BV1xx411c7mD"

  # 指定输出目录
  python main.py --bvid BV1xx411c7mD --output ./subtitles

  # 交互模式
  python main.py
        """
    )

    parser.add_argument('--search', '-s', type=str, help='搜索关键词')
    parser.add_argument('--bvid', '-b', type=str, help='视频BV号')
    parser.add_argument('--url', '-u', type=str, help='B站视频URL')
    parser.add_argument('--output', '-o', type=str, default='.', help='输出目录（默认为当前目录）')

    parser.add_argument('--sessdata', type=str, help='B站Cookie: SESSDATA')
    parser.add_argument('--bili-jct', type=str, help='B站Cookie: bili_jct')
    parser.add_argument('--buvid3', type=str, help='B站Cookie: buvid3')

    args = parser.parse_args()

    # 初始化API
    api = BilibiliAPI(
        sessdata=args.sessdata,
        bili_jct=args.bili_jct,
        buvid3=args.buvid3
    )

    # 初始化字幕提取器
    extractor = SubtitleExtractor(api=api)

    # 根据参数选择模式
    if args.search:
        # 搜索模式
        search_mode(api, args.search)

    elif args.bvid:
        # BV号提取模式
        extract_mode(api, extractor, args.bvid, args.output)

    elif args.url:
        # URL提取模式
        url_mode(api, extractor, args.url, args.output)

    else:
        # 无参数时进入交互模式
        interactive_mode(api, extractor)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已终止")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        sys.exit(1)
