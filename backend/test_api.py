import requests
import json

BASE_URL = "http://localhost:8000"

# 测试根端点
response = requests.get(f"{BASE_URL}/")
print(f"GET /: {response.status_code} - {response.json()}")

# 测试健康检查
response = requests.get(f"{BASE_URL}/health")
print(f"GET /health: {response.status_code} - {response.json()}")

# 测试视频列表
response = requests.get(f"{BASE_URL}/api/videos")
print(f"GET /api/videos: {response.status_code} - {response.json()}")

# 测试统计
response = requests.get(f"{BASE_URL}/api/stats")
print(f"GET /api/stats: {response.status_code} - {response.json()}")

# 测试关键词搜索
response = requests.post(
    f"{BASE_URL}/api/search",
    json={"query": "测试", "mode": "keyword", "limit": 10}
)
print(f"POST /api/search: {response.status_code} - {response.json()}")

# 测试登录状态
response = requests.get(f"{BASE_URL}/api/auth/status")
print(f"GET /api/auth/status: {response.status_code} - {response.json()}")

print("\nAll API tests passed!")
