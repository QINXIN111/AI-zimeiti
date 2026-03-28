#!/usr/bin/env python3
"""自媒体多平台发布助手 - 入口文件"""

import argparse
from scheduler import run


def main():
    parser = argparse.ArgumentParser(
        description="🤖 自媒体多平台同步发布助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py "今天分享一个Python小技巧"
  python main.py "AI绘画教程" -p xiaohongshu douyin
  python main.py "热点新闻点评" --auto
        """,
    )
    parser.add_argument("topic", help="文章主题/关键词")
    parser.add_argument(
        "-p", "--platforms",
        nargs="+",
        choices=["xiaohongshu", "douyin", "wechat"],
        help="目标平台 (默认: 全部启用)",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="跳过人工审核，直接发布",
    )

    args = parser.parse_args()
    run(args.topic, args.platforms, args.auto)


if __name__ == "__main__":
    main()
