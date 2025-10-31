#!/usr/bin/env python3
"""
Bilibili视频字幕提取工具 - 主程序
"""

import argparse
import sys
from bilibili_api import BilibiliAPI
from subtitle_handler import SubtitleExtractor
from config_manager import ConfigManager


def print_banner():
    """打印工具横幅"""
    banner = """
╔══════════════════════════════════════════════╗
║   Bilibili 视频字幕提取工具                  ║
║   Bilibili Video Subtitle Extractor         ║
╚══════════════════════════════════════════════╝
"""
    print(banner)


def cmd_config(args):
    """配置命令"""
    config = ConfigManager()

    if args.clear:
        config.clear_config()
    else:
        config.setup_interactive()


def cmd_search(args):
    """搜索命令"""
    config = ConfigManager()
    cookies = config.get_cookies()

    if not cookies:
        print("提示: 未配置cookies，搜索功能可能受限")
        print("运行 'python main.py config' 进行配置\n")

    api = BilibiliAPI(cookies)

    try:
        print(f"搜索: {args.keyword}\n")
        results = api.search_videos(args.keyword, page_size=args.limit)

        if not results:
            print("未找到相关视频")
            return

        print(f"找到 {len(results)} 个结果:\n")
        for i, video in enumerate(results, 1):
            print(f"{i}. {video['title']}")
            print(f"   作者: {video['author']}")
            print(f"   时长: {video['duration']}")
            print(f"   播放: {video['play']}")
            print(f"   BV号: {video['bvid']}")
            print(f"   URL: {video['url']}")
            print()

    except Exception as e:
        print(f"搜索失败: {e}")
        sys.exit(1)


def cmd_extract(args):
    """提取字幕命令"""
    config = ConfigManager()

    if not config.is_configured():
        print("错误: 未配置cookies，无法提取字幕")
        print("请运行 'python main.py config' 进行配置")
        sys.exit(1)

    cookies = config.get_cookies()
    api = BilibiliAPI(cookies)
    extractor = SubtitleExtractor(api)

    try:
        # 提取BV号
        bvid = BilibiliAPI.extract_bvid(args.video)
        print(f"提取BV号: {bvid}\n")

        # 提取并保存字幕
        saved_files = extractor.extract_and_save(
            bvid=bvid,
            output_dir=args.output,
            format=args.format,
            language=args.language
        )

        if saved_files:
            print(f"\n成功! 共保存 {len(saved_files)} 个字幕文件")
        else:
            print("\n未找到可提取的字幕")

    except Exception as e:
        print(f"提取失败: {e}")
        sys.exit(1)


def cmd_info(args):
    """显示视频信息命令"""
    config = ConfigManager()
    cookies = config.get_cookies()

    if not cookies:
        print("提示: 未配置cookies，部分信息可能无法获取")
        print("运行 'python main.py config' 进行配置\n")

    api = BilibiliAPI(cookies)

    try:
        # 提取BV号
        bvid = BilibiliAPI.extract_bvid(args.video)
        print(f"查询视频: {bvid}\n")

        # 获取视频信息
        info = api.get_video_info(bvid)

        print("=== 视频信息 ===")
        print(f"标题: {info['title']}")
        print(f"作者: {info['author']}")
        print(f"时长: {info['duration']}秒")
        print(f"播放: {info['view']}")
        print(f"点赞: {info['like']}")
        print(f"\n简介:\n{info['description']}")

        # 获取字幕信息
        print("\n=== 字幕信息 ===")
        subtitle_list = api.get_subtitle_list(bvid, info['cid'])

        if subtitle_list:
            print(f"该视频有 {len(subtitle_list)} 个字幕:")
            for sub in subtitle_list:
                print(f"  - {sub['language']} ({sub['language_code']})")
                if sub['author']:
                    print(f"    贡献者: {sub['author']}")
        else:
            print("该视频没有字幕")

    except Exception as e:
        print(f"获取信息失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Bilibili视频字幕提取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 配置cookies
  python main.py config

  # 搜索视频
  python main.py search "Python教程"

  # 提取字幕
  python main.py extract BV1xx411c7mD
  python main.py extract https://www.bilibili.com/video/BV1xx411c7mD

  # 查看视频信息
  python main.py info BV1xx411c7mD

  # 指定输出格式和语言
  python main.py extract BV1xx411c7mD --format txt --language zh-CN
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # config命令
    config_parser = subparsers.add_parser('config', help='配置cookies')
    config_parser.add_argument('--clear', action='store_true', help='清除配置')

    # search命令
    search_parser = subparsers.add_parser('search', help='搜索视频')
    search_parser.add_argument('keyword', help='搜索关键词')
    search_parser.add_argument('--limit', type=int, default=10, help='结果数量限制 (默认: 10)')

    # extract命令
    extract_parser = subparsers.add_parser('extract', help='提取字幕')
    extract_parser.add_argument('video', help='视频BV号或URL')
    extract_parser.add_argument('-o', '--output', default='subtitles', help='输出目录 (默认: subtitles)')
    extract_parser.add_argument('-f', '--format', choices=['srt', 'txt', 'json'], default='srt',
                               help='输出格式 (默认: srt)')
    extract_parser.add_argument('-l', '--language', help='语言代码 (例如: zh-CN, en-US)')

    # info命令
    info_parser = subparsers.add_parser('info', help='查看视频信息')
    info_parser.add_argument('video', help='视频BV号或URL')

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)

    # 执行对应命令
    if args.command == 'config':
        cmd_config(args)
    elif args.command == 'search':
        cmd_search(args)
    elif args.command == 'extract':
        cmd_extract(args)
    elif args.command == 'info':
        cmd_info(args)


if __name__ == '__main__':
    main()
