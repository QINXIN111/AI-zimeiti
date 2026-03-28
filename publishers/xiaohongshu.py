"""小红书发布器"""

import time
from publishers.base import BasePublisher


class XiaohongshuPublisher(BasePublisher):

    URL = "https://creator.xiaohongshu.com/publish/publish"

    def __init__(self, config: dict):
        super().__init__(config, "xiaohongshu")

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

            # 点击上传图片
            if image_path:
                upload_input = self.page.locator('input[type="file"]')
                upload_input.set_input_files(image_path)
                time.sleep(3)

            # 输入标题
            title_selector = '[data-v-a264b01a][contenteditable]'
            # 尝试通用选择器
            self.page.wait_for_selector('.title-input, [placeholder*="标题"]', timeout=10000)
            title_input = self.page.locator('.title-input, [placeholder*="标题"]').first
            title_input.click()
            title_input.fill(title)
            time.sleep(0.5)

            # 输入正文
            content_input = self.page.locator('.desc-input, [placeholder*="正文"], .ql-editor').first
            content_input.click()
            content_input.fill(content)
            time.sleep(0.5)

            # 添加标签
            if tags:
                for tag in tags[:5]:
                    tag_input = self.page.locator('[placeholder*="标签"], [placeholder*="话题"]').first
                    tag_input.click()
                    tag_input.fill(f"#{tag}")
                    time.sleep(1)
                    # 回车确认
                    self.page.keyboard.press("Enter")
                    time.sleep(0.5)

            # 点击发布
            publish_btn = self.page.locator('button:has-text("发布"), button:has-text("发布笔记")').first
            publish_btn.click()
            time.sleep(3)

            print(f"[{self.platform_name}] 发布成功 ✅")
            return True

        except Exception as e:
            print(f"[{self.platform_name}] 发布失败 ❌: {e}")
            return False
        finally:
            self.stop_browser()
