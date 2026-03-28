import requests

# 测试 fallback 机制（假 token）
token = "fake_token_12345"
url = f"https://v2.alapi.cn/api/new/wbtop?token={token}&num=5"

resp = requests.get(url, timeout=10)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
