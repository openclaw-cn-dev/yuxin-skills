#!/usr/bin/env python3
"""
RKR文档中转站轮询脚本
每10分钟检查飞书云盘"00-上传文档中转站"文件夹，
发现待处理文档后自动上传到RKR平台处理。

依赖: 标准库 (urllib, json, os, time)
用法: python3 /tmp/rkr_polling.py

⚠️ 注意: 中转站 folder_token 需先确认有效，见 references/rkr-folder-status.md
"""
import urllib.request, urllib.error, json, os, time

app_id = "cli_a964873dd7b8dbda"
app_secret = "***SECRET***"
MIDDLE_FOLDER = "CpnFcsZ7ql4d0bx6oBbXcWcbnJd"
RKR_API = "http://localhost:8000/api/v1/external/documents"
RKR_API_KEY = "***SECRET***"
CHAT_ID = "***SECRET***"


def get_token():
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode('utf-8')
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=body, method='POST'
    )
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())['tenant_access_token']


def check_folder_accessible(token, folder_token):
    """Use upload_all as existence probe — returns True if folder exists and writable."""
    import subprocess
    probe_path = "/tmp/rkr_probe.txt"
    with open(probe_path, 'w') as f:
        f.write('probe')
    size = os.path.getsize(probe_path)
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://open.feishu.cn/open-apis/drive/v1/files/upload_all',
        '-H', f'Authorization: Bearer {token}',
        '-F', f'file=@{probe_path}',
        '-F', 'file_name=rkr_probe.txt',
        '-F', 'parent_type=explorer',
        '-F', f'parent_node={folder_token}',
        '-F', f'size={size}',
    ], capture_output=True, text=True, timeout=30)
    os.unlink(probe_path)
    resp = json.loads(result.stdout)
    return resp.get('code') == 0


def get_files(token, folder_token):
    url = f'https://open.feishu.cn/open-apis/drive/v1/files?parent_node={folder_token}&page_size=50'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            result = json.loads(r.read())
            if result.get('code') == 0:
                return result.get('data', {}).get('files', [])
            if result.get('data', {}).get('files', [{}])[0].get('name') == '渔芯科技':
                return '__ROOT_ONLY__'
    except Exception:
        pass
    return None


def upload_to_rkr(filepath, filename):
    boundary = '***SECRET***'
    with open(filepath, 'rb') as f:
        file_content = f.read()
    size = len(file_content)
    parts = [
        f'--{boundary}\r\n'.encode(),
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode(),
        b'Content-Type: application/octet-stream\r\n\r\n',
        file_content,
        f'\r\n--{boundary}\r\n'.encode(),
        b'Content-Disposition: form-data; name="filename"\r\n\r\n',
        filename.encode(),
        f'\r\n--{boundary}--\r\n'.encode(),
    ]
    data = b''.join(parts)
    req = urllib.request.Request(RKR_API, data=data, method='POST')
    req.add_header('Authorization', f'Bearer {RKR_API_KEY}')
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    req.add_header('X-API-Key', RKR_API_KEY)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'body': e.read().decode(errors='replace')[:200]}
    except Exception as e:
        return {'error': str(e)}


def send_feishu_message(token, chat_id, text):
    body = json.dumps({
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
        data=body, method='POST'
    )
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'error': str(e)}


def main():
    token = get_token()

    # Step 1: Verify folder exists
    if not check_folder_accessible(token, MIDDLE_FOLDER):
        print("[SILENT] — 中转站文件夹不可访问")
        return

    # Step 2: Get file list (parent_node workaround)
    files_result = get_files(token, MIDDLE_FOLDER)
    if files_result == '__ROOT_ONLY__' or files_result is None:
        print("[SILENT] — 无法列出文件")
        return

    # Step 3: Filter actual files
    actual_files = [
        f for f in files_result
        if f.get('type') == 'file'
        and not f.get('name', '').startswith('RKR_PROBE')
        and not f.get('name', '').startswith('rkr_heartbeat')
        and not f.get('name', '').startswith('rkr_probe')
    ]
    if not actual_files:
        print("[SILENT] — 无待处理文档")
        return

    # Step 4: Upload each file
    uploaded, failed = [], []
    for f in actual_files:
        fname, ftoken = f.get('name', 'unknown'), f.get('token', '')
        download_url = f'https://open.feishu.cn/open-apis/drive/v1/files/{ftoken}/download'
        dl_req = urllib.request.Request(download_url, headers={'Authorization': f'Bearer {token}'})
        try:
            with urllib.request.urlopen(dl_req, timeout=60) as r:
                content = r.read()
            local_path = f"/tmp/rkr_dl_{int(time.time())}_{fname}"
            with open(local_path, 'wb') as out:
                out.write(content)
        except Exception as e:
            failed.append((fname, f'Download error: {e}'))
            continue

        result = upload_to_rkr(local_path, fname)
        os.unlink(local_path)
        if result.get('error'):
            failed.append((fname, result.get('error')))
        else:
            uploaded.append(fname)

    # Step 5: Report
    if uploaded or failed:
        lines = ["📤 RKR文档处理报告\n"]
        if uploaded:
            lines.append(f"✅ 成功上传 ({len(uploaded)}个):")
            for n in uploaded:
                lines.append(f"  • {n}")
        if failed:
            lines.append(f"❌ 失败 ({len(failed)}个):")
            for n, err in failed:
                lines.append(f"  • {n}: {err}")
        send_feishu_message(token, CHAT_ID, '\n'.join(lines))
    else:
        print("[SILENT]")


if __name__ == '__main__':
    main()
