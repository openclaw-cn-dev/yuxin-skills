#!/usr/bin/env python3
"""
学习助手任务收件箱检查脚本
用于Cron定时巡检飞书云盘是否有新任务
"""
import urllib.request
import json
import sys

# 学习助手Bot凭证
APP_ID = "cli_a964873dd7b8dbda"
APP_SECRET = "***SECRET***"

# 正确的文件夹 Token（已验证）
STUDY_HELPER_TASK_FOLDER = "VsMRfTb3qlj4tJd3V7ncJTL6noe"
OUTPUT_FOLDER = "HW6kfR1SuliuR4dALeDcnJwwnch"

def get_tenant_token():
    """获取 tenant_access_token"""
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    return data["tenant_access_token"]

def list_folder_files(token, folder_token):
    """列出文件夹内容"""
    url = f"https://open.feishu.cn/open-apis/drive/v1/files?folder_token={folder_token}&page_size=50"
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    return data.get("data", {}).get("files", [])

def main():
    try:
        token = get_tenant_token()
        files = list_folder_files(token, STUDY_HELPER_TASK_FOLDER)
        
        # 过滤掉产出文件夹，剩下的就是待处理任务
        task_files = [f for f in files if f["name"] != "产出"]
        
        if len(task_files) == 0:
            print("✅ 学习助手 当前无待处理任务")
            return 0
        else:
            print(f"找到 {len(task_files)} 个待处理任务:")
            for f in task_files:
                print(f"  - [{f['type']}] {f['name']} (token: {f['token']})")
            return 1  # 返回1表示有任务需要处理
            
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
