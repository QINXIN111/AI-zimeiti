"""发布器基类"""

import json
import os
import time
from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright, Page, Browser


class BasePublisher(ABC):
    """平台发布器基类"""

    def __init__(self, config: dict, platform_name: str):
        self.config = config
        self.platform_name = platform_name
        self.platform_config = config["platforms"].get(platform_name, {})
        self.cookies_file = self.platform_config.get(
            "cookies_file", f"config/cookies/{platform_name}.json"
        )
        self.headless = self.platform_config.get("headless", True)
        self.browser: Browser = None
        self.page: Page = None

    def _load_cookies(self, context) -> bool:
        """加载 cookies 登录态"""
        if not os.path.exists(self.cookies_file):
            return False
        with open(self.cookies_file, "r") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        return True

    def _save_cookies(self, context):
        """保存 cookies 登录态"""
        cookies = context.cookies()
        os.makedirs(os.path.dirname(self.cookies_file), exist_ok=True)
        with open(self.cookies_file, "w") as f:
            json.dump(cookies, f, indent=2)

    def start_browser(self):
        """启动浏览器"""
        pw = sync_playwright().start()
        self.browser = pw.chromium.launch(headless=self.headless)
        context = self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        self._load_cookies(context)
        self.page = context.new_page()

    def stop_browser(self):
        """关闭浏览器"""
        if self.browser:
            # 保存 cookies
            context = self.page.context
            self._save_cookies(context)
            self.browser.close()

    @abstractmethod
    def publish(self, title: str, content: str, image_path: str = None, tags: list = None) -> bool:
        """发布内容到平台"""
        pass

    def safe_click(self, selector: str, timeout: int = 5000):
        """安全点击元素"""
        self.page.wait_for_selector(selector, timeout=timeout)
        self.page.click(selector)
        time.sleep(0.5)

    def safe_type(self, selector: str, text: str, clear: bool = True):
        """安全输入文本"""
        self.page.wait_for_selector(selector, timeout=5000)
        if clear:
            self.page.fill(selector, "")
        self.page.type(selector, text, delay=50)
