"""抖音发布器"""

import time
from publishers.base import BasePublisher


class DouyinPublisher(BasePublisher):

    URL = "https://creator.douyin.com/creator-micro/home"

    def __init__(self, config: dict):
        super().__init__(config, "douyin")

    def publish(self, title: str, content: str, image_path: str = None, tags: list = None) -> bool:
        try:
            self.start_browser()
            self.page.goto(self.URL)
            time.sleep(3)

            # 检查登录状态
            if "login" in self.page.url:
                print(f"[{self.platform_name}] 请手动扫码登录...")
                while "login" in self.page.url:
                    time.sleep(2)
                self._save_cookies(self.page.context)

            # 导航到发布页
            publish_link = self.page.locator('a:has-text("发布"), a[href*="upload"]').first
            publish_link.click()
            time.sleep(3)

            # 上传图片
            if image_path:
                upload_input = self.page.locator('input[type="file"]')
                upload_input.set_input_files(image_path)
                time.sleep(3)

            # 输入标题
            title_input = self.page.locator('[placeholder*="标题"], [placeholder*="作品"]').first
            title_input.click()
            title_input.fill(title)

            # 输入描述
            content_input = self.page.locator('[placeholder*="描述"], [placeholder*="简介"]').first
            content_input.click()
            content_input.fill(content)

            # 添加标签
            if tags:
                tag_input = self.page.locator('[placeholder*="话题"], [placeholder*="标签"]').first
                for tag in tags[:5]:
                    tag_input.click()
                    tag_input.fill(f"#{tag}")
                    time.sleep(1)
                    self.page.keyboard.press("Enter")
                    time.sleep(0.5)

            # 点击发布
            publish_btn = self.page.locator('button:has-text("发布")').first
            publish_btn.click()
            time.sleep(3)

            print(f"[{self.platform_name}] 发布成功 ✅")
            return True

        except Exception as e:
            print(f"[{self.platform_name}] 发布失败 ❌: {e}")
            return False
        finally:
            self.stop_browser()
