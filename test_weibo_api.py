import requests
import json

# 测试微博热搜 API
token = "LwExDtUWhF3rH5ib"
url = f"https://v2.alapi.cn/api/new/wbtop?token={token}&num=10"

resp = requests.get(url, timeout=10)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    print(f"\nSuccess: {data.get('success')}")
    print(f"Message: {data.get('message')}")

    items = data.get('data', [])
    print(f"\nTotal: {len(items)} items\n")

    for i, item in enumerate(items[:5], 1):
        print(f"{i}. {item.get('hot_word')} - 热度:{item.get('hot_num', 'N/A')}")
        print(f"   URL: {item.get('url')[:80]}...")
        print()
else:
    print(f"Failed: {resp.text}")
