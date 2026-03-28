"""AI 图片生成模块"""

import os
import requests
from openai import OpenAI


class ImageGenerator:
    """基于 DALL·E / SD 的图片生成器"""

    def __init__(self, config: dict):
        img_config = config["image"]
        self.provider = img_config.get("provider", "dall-e")
        self.client = OpenAI(
            api_key=img_config["api_key"],
            base_url=img_config.get("base_url", "https://api.openai.com/v1"),
        )
        self.model = img_config.get("model", "dall-e-3")
        self.size = img_config.get("size", "1024x1024")
        self.output_dir = "output/images"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, prompt: str, filename: str = None) -> str:
        """生成图片并保存到本地

        Returns:
            图片文件路径
        """
        if self.provider == "dall-e":
            return self._generate_dalle(prompt, filename)
        else:
            raise NotImplementedError(f"暂不支持的图片生成器: {self.provider}")

    def _generate_dalle(self, prompt: str, filename: str = None) -> str:
        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size=self.size,
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        # 下载图片
        if not filename:
            safe_prompt = prompt[:30].replace(" ", "_").replace("/", "_")
            filename = f"{safe_prompt}.png"

        filepath = os.path.join(self.output_dir, filename)
        img_data = requests.get(image_url).content
        with open(filepath, "wb") as f:
            f.write(img_data)

        return filepath
