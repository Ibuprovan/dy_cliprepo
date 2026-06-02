import requests
import json

BASE_URL = "http://localhost:8000"

print("=== 阶段五：端到端测试 ===\n")

# 测试 1: 根端点
print("测试 1: 根端点")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200
    print("  通过\n")
except Exception as e:
    print(f"  失败: {e}\n")

# 测试 2: 健康检查
print("测试 2: 健康检查")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200
    print("  通过\n")
except Exception as e:
    print(f"  失败: {e}\n")

# 测试 3: 登录状态
print("测试 3: 登录状态")
try:
    response = requests.get(f"{BASE_URL}/api/auth/status", timeout=5)
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200
    print("  通过\n")
except Exception as e:
    print(f"  失败: {e}\n")

# 测试 4: 视频列表
print("测试 4: 视频列表")
try:
    response = requests.get(f"{BASE_URL}/api/videos", timeout=5)
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200
    print("  通过\n")
except Exception as e:
    print(f"  失败: {e}\n")

# 测试 5: 视频详情
print("测试 5: 视频详情")
try:
    response = requests.get(f"{BASE_URL}/api/videos/1", timeout=5)
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200
    print("  通过\n")
except Exception as e:
    print(f"  失败: {e}\n")

# 测试 6: 不存在的视频
print("测试 6: 不存在的视频")
try:
    response = requests.get(f"{BASE_URL}/api/videos/999", timeout=5)
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 404
    print("  通过\n")
except Exception as e:
    print(f"  失败: {e}\n")

# 测试 7: 统计数据
print("测试 7: 统计数据")
try:
    response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200
    print("  通过\n")
except Exception as e:
    print(f"  失败: {e}\n")

# 测试 8: 关键词搜索
print("测试 8: 关键词搜索")
try:
    response = requests.post(
        f"{BASE_URL}/api/search",
        json={"query": "测试", "mode": "keyword", "limit": 10},
        timeout=5
    )
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200
    print("  通过\n")
except Exception as e:
    print(f"  失败: {e}\n")

print("=== 所有测试完成！ ===")
