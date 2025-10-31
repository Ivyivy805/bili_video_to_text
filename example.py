#!/usr/bin/env python3
"""
使用示例脚本
演示如何将工具作为Python模块使用
"""

from bilibili_api import BilibiliAPI
from subtitle_handler import SubtitleExtractor
from config_manager import ConfigManager


def example_search():
    """示例：搜索视频"""
    print("=== 示例：搜索视频 ===\n")

    # 初始化API（不需要cookies也可以搜索）
    api = BilibiliAPI()

    # 搜索视频
    results = api.search_videos("Python教程", page_size=5)

    print(f"找到 {len(results)} 个结果:\n")
    for i, video in enumerate(results, 1):
        print(f"{i}. {video['title']}")
        print(f"   BV号: {video['bvid']}")
        print(f"   作者: {video['author']}")
        print()


def example_get_video_info():
    """示例：获取视频信息"""
    print("\n=== 示例：获取视频信息 ===\n")

    # 初始化API
    config = ConfigManager()
    cookies = config.get_cookies()
    api = BilibiliAPI(cookies)

    # 示例BV号（请替换为实际的BV号）
    bvid = "BV1xx411c7mD"

    try:
        # 获取视频信息
        info = api.get_video_info(bvid)

        print(f"标题: {info['title']}")
        print(f"作者: {info['author']}")
        print(f"时长: {info['duration']}秒")
        print(f"播放量: {info['view']}")
        print()

        # 获取字幕信息
        subtitle_list = api.get_subtitle_list(bvid)
        if subtitle_list:
            print("可用字幕:")
            for sub in subtitle_list:
                print(f"  - {sub['language']} ({sub['language_code']})")
        else:
            print("该视频没有字幕")

    except Exception as e:
        print(f"错误: {e}")


def example_extract_subtitle():
    """示例：提取字幕"""
    print("\n=== 示例：提取字幕 ===\n")

    # 加载配置
    config = ConfigManager()

    if not config.is_configured():
        print("请先运行 'python main.py config' 配置cookies")
        return

    cookies = config.get_cookies()
    api = BilibiliAPI(cookies)
    extractor = SubtitleExtractor(api)

    # 示例BV号（请替换为实际的BV号）
    bvid = "BV1xx411c7mD"

    try:
        # 提取所有语言的字幕，保存为SRT格式
        saved_files = extractor.extract_and_save(
            bvid=bvid,
            output_dir="subtitles",
            format="srt"
        )

        if saved_files:
            print(f"\n成功保存 {len(saved_files)} 个字幕文件:")
            for file in saved_files:
                print(f"  - {file}")
        else:
            print("该视频没有字幕")

    except Exception as e:
        print(f"错误: {e}")


def example_custom_processing():
    """示例：自定义处理字幕"""
    print("\n=== 示例：自定义处理字幕 ===\n")

    config = ConfigManager()
    if not config.is_configured():
        print("请先运行 'python main.py config' 配置cookies")
        return

    cookies = config.get_cookies()
    api = BilibiliAPI(cookies)

    bvid = "BV1xx411c7mD"

    try:
        # 获取字幕列表
        subtitle_list = api.get_subtitle_list(bvid)

        if not subtitle_list:
            print("该视频没有字幕")
            return

        # 下载第一个字幕
        subtitle_url = subtitle_list[0]['subtitle_url']
        subtitle_data = api.download_subtitle(subtitle_url)

        # 自定义处理：统计字数
        total_chars = sum(len(item['content']) for item in subtitle_data)
        print(f"字幕总字数: {total_chars}")

        # 自定义处理：提取关键词（简单示例）
        all_text = " ".join(item['content'] for item in subtitle_data)
        words = all_text.split()
        print(f"总词数: {len(words)}")

        # 自定义处理：按时间筛选（例如只要前5分钟的字幕）
        first_5_min = [item for item in subtitle_data if item['from'] < 300]
        print(f"前5分钟字幕条数: {len(first_5_min)}")

    except Exception as e:
        print(f"错误: {e}")


def main():
    """运行所有示例"""
    print("Bilibili字幕提取工具 - 使用示例\n")
    print("=" * 50)

    # 1. 搜索视频（不需要配置）
    try:
        example_search()
    except Exception as e:
        print(f"搜索示例出错: {e}")

    # 2. 获取视频信息（需要配置）
    try:
        example_get_video_info()
    except Exception as e:
        print(f"获取视频信息示例出错: {e}")

    # 3. 提取字幕（需要配置）
    # example_extract_subtitle()

    # 4. 自定义处理（需要配置）
    # example_custom_processing()

    print("\n" + "=" * 50)
    print("\n提示: 部分示例需要先配置cookies")
    print("运行: python main.py config")


if __name__ == '__main__':
    main()
