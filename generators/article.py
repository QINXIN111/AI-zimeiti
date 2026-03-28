"""AI 文章生成模块"""

import json
import os
from openai import OpenAI


class ArticleGenerator:
    """基于大模型的文章生成器"""

    PLATFORM_STYLES = {
        "xiaohongshu": {"word_count": 500, "style": "小红书种草风"},
        "douyin": {"word_count": 300, "style": "抖音短平快风格"},
        "wechat": {"word_count": 800, "style": "公众号深度风格"},
    }

    def __init__(self, config: dict):
        ai_config = config["ai"]
        self.client = OpenAI(
            api_key=ai_config["api_key"],
            base_url=ai_config.get("base_url", "https://api.openai.com/v1"),
        )
        self.model = ai_config.get("model", "gpt-4o")
        self.temperature = ai_config.get("temperature", 0.7)

        # 加载 prompt 模板
        prompt_path = config["templates"]["article_prompt"]
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.prompt_template = f.read()
        else:
            self.prompt_template = self._default_prompt()

    def _default_prompt(self) -> str:
        return """你是一个自媒体内容创作者。请根据以下主题生成一篇适合{platform}的文章。
主题：{topic}
要求：标题吸引眼球，正文{word_count}字左右，口语化，适合移动端阅读。
请按JSON格式输出：{{"title": "标题", "content": "正文", "tags": ["标签"], "image_prompt": "配图描述"}}"""

    def generate(self, topic: str, platform: str) -> dict:
        """生成指定平台的文章

        Returns:
            {
                "title": str,
                "content": str,
                "tags": list[str],
                "image_prompt": str,
            }
        """
        style = self.PLATFORM_STYLES.get(platform, {"word_count": 500, "style": "通用风格"})

        prompt = self.prompt_template.format(
            topic=topic,
            platform=style["style"],
            word_count=style["word_count"],
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )

        raw = response.choices[0].message.content.strip()

        # 尝试提取 JSON
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        return json.loads(raw)

    def generate_batch(self, topic: str, platforms: list[str]) -> dict[str, dict]:
        """为多个平台批量生成文章"""
        results = {}
        for platform in platforms:
            results[platform] = self.generate(topic, platform)
        return results
