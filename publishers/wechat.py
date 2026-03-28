"""微信公众号发布器"""

import time
from publishers.base import BasePublisher


class WechatPublisher(BasePublisher):

    URL = "https://mp.weixin.qq.com/"

    def __init__(self, config: dict):
        super().__init__(config, "wechat")

    def publish(self, title: str, content: str, image_path: str = None, tags: list = None) -> bool:
        try:
            self.start_browser()
            self.page.goto(self.URL)
            time.sleep(3)

            # 检查登录状态
            qr_code = self.page.locator('.login__type__container__scan__qrcode, img[alt*="二维码"]')
            if qr_code.count() > 0:
                print(f"[{self.platform_name}] 请扫码登录...")
                while qr_code.count() > 0:
                    time.sleep(2)
                time.sleep(3)
                self._save_cookies(self.page.context)

            # 导航到草稿箱
            self.page.goto("https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10")
            time.sleep(3)

            # 输入标题
            title_input = self.page.locator('#title, .title-input, [placeholder*="标题"]').first
            title_input.click()
            title_input.fill(title)

            # 切换到正文区域（富文本编辑器）
            # 公众号使用的是自定义编辑器，需要特殊处理
            editor = self.page.locator('#ueditor_0, .rich_media_content, .note-editor').first
            editor.click()

            # 输入正文内容（使用参数传递，避免字符串拼接导致 JS 注入）
            self.page.evaluate(
                """(content) => {
                    const el = document.querySelector('#ueditor_0, .rich_media_content, .note-editor');
                    if (el) el.innerHTML = content;
                }""",
                content,
            )
            time.sleep(1)

            # 上传封面图
            if image_path:
                # 点击上传封面
                cover_btn = self.page.locator('a:has-text("选择封面"), .choose-cover-btn').first
                if cover_btn.count() > 0:
                    cover_btn.click()
                    time.sleep(2)
                    upload_input = self.page.locator('input[type="file"]').first
                    upload_input.set_input_files(image_path)
                    time.sleep(3)

            # 保存草稿（不直接发布，先人工审核）
            save_btn = self.page.locator('a:has-text("保存"), button:has-text("保存")').first
            save_btn.click()
            time.sleep(2)

            print(f"[{self.platform_name}] 保存草稿成功 ✅（请手动审核后发布）")
            return True

        except Exception as e:
            print(f"[{self.platform_name}] 操作失败 ❌: {e}")
            return False
        finally:
            self.stop_browser()
