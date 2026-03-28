"""调度器 - 串联 AI 生成与多平台发布"""

import json
import os
import time
from datetime import datetime

import yaml
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

from generators.article import ArticleGenerator
from generators.image import ImageGenerator
from publishers.xiaohongshu import XiaohongshuPublisher
from publishers.douyin import DouyinPublisher
from publishers.wechat import WechatPublisher

console = Console()

PUBLISHERS = {
    "xiaohongshu": XiaohongshuPublisher,
    "douyin": DouyinPublisher,
    "wechat": WechatPublisher,
}


def load_config(path: str = "config/settings.yaml") -> dict:
    if not os.path.exists(path):
        example = path + ".example"
        if os.path.exists(example):
            raise FileNotFoundError(
                f"配置文件 {path} 不存在。\n"
                f"请先执行：cp {example} {path}\n"
                f"然后填写真实的 API Key 和平台 cookies 路径。"
            )
        raise FileNotFoundError(f"配置文件 {path} 不存在，且未找到示例文件 {example}。")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompt_templates(config: dict) -> dict:
    """加载 prompt 模板"""
    templates = {}
    prompt_dir = "templates"
    if os.path.exists(prompt_dir):
        for f in os.listdir(prompt_dir):
            if f.endswith(".txt"):
                key = f.replace(".txt", "")
                with open(os.path.join(prompt_dir, f), "r", encoding="utf-8") as fp:
                    templates[key] = fp.read()
    return templates


def run(topic: str, platforms: list[str] = None, auto_publish: bool = False):
    """执行一次完整的「生成→发布」流程

    Args:
        topic: 文章主题
        platforms: 目标平台列表，None 则使用配置中所有启用的平台
        auto_publish: 是否跳过人工审核直接发布
    """
    config = load_config()

    # 确定目标平台
    if not platforms:
        platforms = [
            name for name, cfg in config["platforms"].items()
            if cfg.get("enabled", True)
        ]

    console.print(f"\n🚀 [bold]自媒体助手[/bold] 开始执行")
    console.print(f"📌 主题: {topic}")
    console.print(f"📱 目标平台: {', '.join(platforms)}\n")

    # ===== Step 1: AI 生成内容 =====
    console.print("[cyan]✍️  步骤 1/3: AI 生成文章...[/cyan]")
    article_gen = ArticleGenerator(config)
    articles = article_gen.generate_batch(topic, platforms)

    for platform, article in articles.items():
        console.print(f"  ✅ [{platform}] 标题: {article['title']}")

    # ===== Step 2: AI 生成配图 =====
    console.print("\n[cyan]🎨 步骤 2/3: AI 生成配图...[/cyan]")
    img_gen = ImageGenerator(config)
    images = {}

    for platform, article in articles.items():
        img_prompt = article.get("image_prompt", topic)
        try:
            img_path = img_gen.generate(img_prompt, f"{platform}_{int(time.time())}.png")
            images[platform] = img_path
            console.print(f"  ✅ [{platform}] 配图已生成: {img_path}")
        except Exception as e:
            console.print(f"  ⚠️ [{platform}] 配图生成失败: {e}")
            images[platform] = None

    # ===== Step 3: 人工审核 =====
    if not auto_publish and config["publish"].get("review_before_publish", True):
        console.print("\n[cyan]👀 步骤 3/3: 人工审核[/cyan]")

        for platform in platforms:
            article = articles[platform]
            table = Table(title=f"【{platform}】发布预览")
            table.add_column("字段", style="bold")
            table.add_column("内容")
            table.add_row("标题", article["title"])
            table.add_row("正文", article["content"][:200] + "...")
            table.add_row("标签", ", ".join(article.get("tags", [])))
            table.add_row("配图", images.get(platform, "无"))
            console.print(table)

        console.print()
        if not Confirm.ask("确认发布到上述平台？"):
            console.print("[yellow]已取消发布[/yellow]")
            _save_drafts(articles, images, topic, platforms)
            return

    # ===== Step 4: 发布 =====
    console.print("\n[cyan]📤 执行发布...[/cyan]")
    results = {}

    for platform in platforms:
        article = articles[platform]
        publisher_cls = PUBLISHERS.get(platform)
        if not publisher_cls:
            console.print(f"  ⚠️ [{platform}] 暂不支持，跳过")
            results[platform] = False
            continue

        publisher = publisher_cls(config)
        success = publisher.publish(
            title=article["title"],
            content=article["content"],
            image_path=images.get(platform),
            tags=article.get("tags"),
        )
        results[platform] = success

        # 发布间隔，避免触发风控
        if platform != platforms[-1]:
            interval = config["publish"].get("interval_minutes", 60)
            console.print(f"  ⏳ 等待 {interval} 分钟后发布下一个平台...")
            time.sleep(interval * 60)

    # ===== 结果汇总 =====
    console.print("\n[bold]📊 发布结果:[/bold]")
    for platform, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        console.print(f"  {platform}: {status}")

    # 保存草稿备份
    _save_drafts(articles, images, topic, platforms)


def _save_drafts(articles: dict, images: dict, topic: str, platforms: list[str]):
    """保存生成内容到本地草稿"""
    draft_dir = f"output/drafts/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(draft_dir, exist_ok=True)

    for platform in platforms:
        article = articles.get(platform, {})
        draft = {
            "topic": topic,
            "platform": platform,
            "title": article.get("title", ""),
            "content": article.get("content", ""),
            "tags": article.get("tags", []),
            "image_path": images.get(platform, ""),
            "created_at": datetime.now().isoformat(),
        }
        filepath = os.path.join(draft_dir, f"{platform}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(draft, f, ensure_ascii=False, indent=2)

    console.print(f"\n📝 草稿已保存到: {draft_dir}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="自媒体多平台发布助手")
    parser.add_argument("topic", help="文章主题")
    parser.add_argument("-p", "--platforms", nargs="+", help="目标平台")
    parser.add_argument("--auto", action="store_true", help="跳过人工审核直接发布")
    args = parser.parse_args()

    run(args.topic, args.platforms, args.auto)
