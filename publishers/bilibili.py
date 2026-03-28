"""B站发布器（图文专栏）"""

import time
from publishers.base import BasePublisher


class BilibiliPublisher(BasePublisher):

    URL = "https://member.bilibili.com/platform/upload/text/article"

    def __init__(self, config: dict):
        super().__init__(config, "bilibili")

    def publish(self, title: str, content: str, image_path: str = None, tags: list = None, is_html: bool = False) -> bool:
        try:
            self.start_browser()
            self.page.goto(self.URL)
            time.sleep(5)

            # 检查登录状态
            if "login" in self.page.url:
                print(f"[{self.platform_name}] 请手动扫码登录...")
                while "login" in self.page.url:
                    time.sleep(2)
                self._save_cookies(self.page.context)

            # 输入标题
            title_input = self.page.locator('[placeholder*="请输入标题"], .input-title').first
            title_input.click()
            title_input.fill(title)
            time.sleep(0.5)

            # 输入正文（B站专栏支持 Markdown）
            content_input = self.page.locator('[placeholder*="请输入正文"], .editor-textarea').first
            content_input.click()
            if is_html:
                # 如果是 HTML，需要转换成 Markdown 或富文本
                # 这里先简单处理，直接填入
                content_input.fill(content)
            else:
                content_input.fill(content)
            time.sleep(0.5)

            # 上传封面图片
            if image_path:
                cover_input = self.page.locator('input[type="file"][accept*="image"]').first
                cover_input.set_input_files(image_path)
                time.sleep(5)

            # 添加标签
            if tags:
                tag_input = self.page.locator('[placeholder*="标签"], [placeholder*="请添加标签"]').first
                for tag in tags[:5]:
                    tag_input.click()
                    tag_input.fill(tag)
                    time.sleep(1)
                    self.page.keyboard.press("Enter")
                    time.sleep(0.5)

            # 点击发布
            publish_btn = self.page.locator('button:has-text("发布"), button:has-text("立即发布")').first
            publish_btn.click()
            time.sleep(3)

            print(f"[{self.platform_name}] 发布成功 ✅")
            return True

        except Exception as e:
            print(f"[{self.platform_name}] 发布失败 ❌: {e}")
            return False
        finally:
            self.stop_browser()
