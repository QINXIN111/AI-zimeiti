"""微信视频号发布器"""

import time
from publishers.base import BasePublisher


class WechatVideoPublisher(BasePublisher):

    URL = "https://channels.weixin.qq.com/"

    def __init__(self, config: dict):
        super().__init__(config, "wechat_video")

    def publish(self, title: str, content: str, image_path: str = None, tags: list = None, is_html: bool = False) -> bool:
        try:
            self.start_browser()
            self.page.goto(self.URL)
            time.sleep(5)

            # 检查登录状态
            if "login" in self.page.url or "qrcode" in self.page.url:
                print(f"[{self.platform_name}] 请手动扫码登录...")
                while "login" in self.page.url or "qrcode" in self.page.url:
                    time.sleep(2)
                self._save_cookies(self.page.context)

            # 点击发布按钮（视频号主界面）
            publish_btn = self.page.locator('text=发布, button:has-text("发布")').first
            publish_btn.click()
            time.sleep(2)

            # 输入标题
            title_input = self.page.locator('[placeholder*="标题"], [placeholder*="说点什么"]').first
            title_input.click()
            title_input.fill(title)
            time.sleep(0.5)

            # 输入正文
            content_input = self.page.locator('[placeholder*="内容"], [placeholder*="正文"]').first
            content_input.click()
            if is_html:
                content_input.evaluate("el => el.innerHTML = arguments[0]", content)
            else:
                content_input.fill(content)
            time.sleep(0.5)

            # 上传图片
            if image_path:
                upload_input = self.page.locator('input[type="file"]').first
                upload_input.set_input_files(image_path)
                time.sleep(5)

            # 添加标签
            if tags:
                for tag in tags[:5]:
                    tag_input = self.page.locator('[placeholder*="标签"], [placeholder*="话题"]').first
                    tag_input.click()
                    tag_input.fill(f"#{tag}")
                    time.sleep(1)
                    self.page.keyboard.press("Enter")
                    time.sleep(0.5)

            # 点击发布
            publish_confirm = self.page.locator('button:has-text("发布"), button:has-text("立即发布")').first
            publish_confirm.click()
            time.sleep(3)

            print(f"[{self.platform_name}] 发布成功 ✅")
            return True

        except Exception as e:
            print(f"[{self.platform_name}] 发布失败 ❌: {e}")
            return False
        finally:
            self.stop_browser()
