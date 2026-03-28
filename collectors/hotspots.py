"""热点采集模块 - HTTP API + Playwright 混合模式

优先使用免费的 HTTP API，失败时降级到 Playwright。
"""

import re
import time
import json
import requests
from datetime import datetime


class HotspotCollector:
    """多平台热点采集器（API + Playwright 混合）"""

    def __init__(self, use_fallback: bool = True):
        self.use_fallback = use_fallback  # API 失败时是否降级到 Playwright

    def collect_all(self, sources: list[str] = None) -> list[dict]:
        """采集所有来源的热点"""
        if sources is None:
            sources = ["weibo", "baidu", "toutiao"]

        all_hotspots = []
        collectors = {
            "weibo": self.collect_weibo_api,
            "baidu": self.collect_baidu_playwright,
            "toutiao": self.collect_toutiao_playwright,
        }

        for source in sources:
            fn = collectors.get(source)
            if fn:
                try:
                    hotspots = fn()
                    all_hotspots.extend(hotspots)
                    print(f"[热点] OK {source}: {len(hotspots)} 条")
                except Exception as e:
                    print(f"[热点] FAIL {source}: {e}")

        # 去重
        seen = set()
        unique = []
        for h in all_hotspots:
            key = h["title"][:10]
            if key not in seen and h["title"]:
                seen.add(key)
                unique.append(h)

        return unique

    # ==================== 微博 API 方案 ====================

    def collect_weibo_api(self) -> list[dict]:
        """使用 ALAPI 微博热搜接口（需要 token）"""
        try:
            token = "LwExDtUWhF3rH5ib"  # free-api.com 获取
            url = "https://v2.alapi.cn/api/new/wbtop"
            params = {
                "token": token,
                "num": 30  # 返回条数
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                raise Exception(f"API 返回 {response.status_code}")

            data = response.json()
            if not data.get("success"):
                raise Exception(f"API 错误: {data.get('message')}")

            items = data.get("data", [])

            hotspots = []
            for item in items[:30]:
                try:
                    title = item.get("hot_word", "")
                    heat = item.get("hot_num", 0)
                    url = item.get("url", "")
                    if title:
                        hotspots.append({
                            "title": title,
                            "url": url,
                            "source": "微博",
                            "heat": str(heat) if heat else "0",
                            "category": "综合",
                            "time": datetime.now().strftime("%H:%M"),
                        })
                except:
                    continue

            return hotspots

        except Exception as e:
            if self.use_fallback:
                print(f"[微博] API 失败，降级到 Playwright: {e}")
                return self.collect_weibo_playwright()
            raise

    # ==================== Playwright 方案 ====================

    def _start_browser(self):
        from playwright.sync_api import sync_playwright
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True)
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

    def _stop_browser(self):
        try:
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, 'pw') and self.pw:
                self.pw.stop()
        except:
            pass

    def collect_weibo_playwright(self) -> list[dict]:
        """使用 Playwright 抓取微博热搜（备用方案）"""
        self._start_browser()
        try:
            page = self.context.new_page()
            page.goto("https://s.weibo.com/top/summary", wait_until="domcontentloaded", timeout=30000)
            time.sleep(8)

            # 检查是否被跳转到登录页
            if "visitor" in page.url or "passport" in page.url:
                print(f"[微博] 页面需要登录或验证，URL: {page.url}")
                return []

            hotspots = []
            rows = page.locator("table tbody tr").all()
            for row in rows[:30]:
                try:
                    title_el = row.locator("td.td-02 a").first
                    if title_el.count() > 0:
                        title = title_el.inner_text().strip()
                        heat_el = row.locator("td.td-02 span").first
                        heat = heat_el.inner_text().strip() if heat_el.count() > 0 else "0"
                        if title:
                            hotspots.append({
                                "title": title,
                                "url": f"https://s.weibo.com/weibo?q={title}",
                                "source": "微博",
                                "heat": heat,
                                "category": "综合",
                                "time": datetime.now().strftime("%H:%M"),
                            })
                except:
                    continue
            return hotspots
        finally:
            self._stop_browser()

    def collect_baidu_playwright(self) -> list[dict]:
        """使用 Playwright 抓取百度热搜"""
        self._start_browser()
        try:
            page = self.context.new_page()
            page.goto("https://top.baidu.com/board?tab=realtime", wait_until="networkidle", timeout=15000)
            time.sleep(2)

            hotspots = []
            items = page.locator(".category-wrap_iQLoo .content_1YWBm").all()
            for item in items[:30]:
                try:
                    title_el = item.locator(".c-single-text-ellipsis").first
                    if title_el.count() > 0:
                        title = title_el.inner_text().strip()
                        heat_el = item.locator(".hot-index_1Bl1a").first
                        heat = heat_el.inner_text().strip() if heat_el.count() > 0 else "0"
                        if title:
                            hotspots.append({
                                "title": title,
                                "url": f"https://www.baidu.com/s?wd={title}",
                                "source": "百度",
                                "heat": heat,
                                "category": "综合",
                                "time": datetime.now().strftime("%H:%M"),
                            })
                except:
                    continue
            return hotspots
        finally:
            self._stop_browser()

    def collect_toutiao_playwright(self) -> list[dict]:
        """使用 Playwright 抓取今日头条热榜"""
        self._start_browser()
        try:
            page = self.context.new_page()
            page.goto("https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
                      wait_until="networkidle", timeout=15000)
            time.sleep(2)

            hotspots = []
            body_text = page.inner_text("body")
            data = json.loads(body_text)
            items = data.get("data", data) if isinstance(data, dict) else data
            for item in items[:30]:
                title = item.get("Title", "")
                url = item.get("Url", "")
                hot_value = item.get("HotValue", 0)
                label = item.get("Label", "综合")
                if title:
                    hotspots.append({
                        "title": title,
                        "url": url if url.startswith("http") else f"https://www.toutiao.com{url}",
                        "source": "头条",
                        "heat": str(hot_value),
                        "category": label or "综合",
                        "time": datetime.now().strftime("%H:%M"),
                    })
            return hotspots
        except Exception as e:
            print(f"[头条] 解析失败: {e}")
            return []
        finally:
            self._stop_browser()


def format_hotspots_for_display(hotspots: list[dict], limit: int = 20) -> str:
    lines = []
    for i, h in enumerate(hotspots[:limit], 1):
        lines.append(f"{i}. {h['title']} [{h['source']}] 热度:{h['heat']}")
    return "\n".join(lines)
