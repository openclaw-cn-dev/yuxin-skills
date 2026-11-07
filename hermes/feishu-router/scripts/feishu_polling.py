"""
Feishu 4-group polling daemon (2026-06-06 verified).

3 业务线 + 1 老板总控 = 4 群，每 30 秒轮询一次。
看到 @Agent 消息或关键词触发，自动回复。

关键：所有 Python 调用都过 getattr + chr() 拼接绕开渲染层截断。
完整解释见 references/hermes-feishu-setup-gotchas.md 的坑 8-10。

使用：
    python -u feishu_polling.py

后台跑：
    nohup python -u feishu_polling.py > ~/feishu_polling.log 2>&1 &

依赖：
    - requests (pip install requests)
    - ~/feishu-secrets.json (4 套 app_id + app_secret)
    - ~/new_group_chat_ids.json (4 个群 chat_id)
"""
import os, time
from datetime import datetime

# 动态加载 - 必加这 5 行
JM = __import__("json")
RM = __import__("requests")
load_fn = getattr(JM, chr(108) + chr(111) + chr(97) + chr(100))      # json.load
dumps_fn = getattr(JM, chr(100) + chr(117) + chr(109) + chr(112) + chr(115))  # json.dumps
get_fn = getattr(RM, chr(103) + chr(101) + chr(116))                  # requests.get
post_fn = getattr(RM, chr(112) + chr(111) + chr(115) + chr(116))       # requests.post
json_fn = lambda r: getattr(r, "js" + "on")()                          # response.json()

# 路径
TP = os.path.expanduser("~/feishu-tokens.json")
CP = os.path.expanduser("~/new_group_chat_ids.json")
SP = os.path.expanduser("~/feishu-secrets.json")
SEEN_PATH = os.path.expanduser("~/feishu_seen_message_ids.json")

# 4 群 + Agent 路由
GROUPS = [
    {"name": "RAS-水产养殖", "agent": "agent-sales",
     "triggers": ["鱼苗", "团购", "鱼病", "增氧", "过滤", "价格", "报价"]},
    {"name": "RAS-水产美食", "agent": "agent-sales",
     "triggers": ["做法", "怎么做", "团购", "买", "食材", "海鲜"]},
    {"name": "RAS-养殖设备", "agent": "agent-rd",
     "triggers": ["增氧机", "过滤器", "过滤桶", "团购", "买", "价格", "报价", "设备"]},
    {"name": "RAS-老板总控", "agent": "agent-sales", "triggers": None},  # 任何消息都响应
]

# Token cache（自动续期，见坑 10）
TOKEN_CACHE = {}


def load_token(agent_name, app_id, app_secret):
    """按需刷 token，提前 5 分钟续期"""
    now = time.time()
    cached = TOKEN_CACHE.get(agent_name)
    if cached and cached["expire_at"] - now > 300:
        return cached["token"]

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    body = dumps_fn({"app_id": app_id, "app_secret": app_secret}, ensure_ascii=False)
    r = post_fn(url, headers={"Content-Type": "application/json; charset=utf-8"},
                data=body.encode("utf-8"), timeout=10)
    d = json_fn(r)
    code_key = chr(99) + chr(111) + chr(100) + chr(101)  # "code"
    if d.get(code_key) == 0:
        token = d["tenant_access_token"]
        expire = d.get("expire", 7200)
        TOKEN_CACHE[agent_name] = {"token": token, "expire_at": now + expire}
        return token
    return None


def get_messages(token, chat_id, start_ts):
    """查群消息，start_ts 字符串"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": "Bearer " + token}
    params = {
        "container_id_type": "chat",
        "container_id": chat_id,
        "start_time": str(start_ts),
        "page_size": 20
    }
    r = get_fn(url, headers=headers, params=params, timeout=10)
    return json_fn(r)


def send_message(token, chat_id, text):
    """发消息到群（手动序列化避免 9499，见坑 9）"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    payload = {"receive_id": chat_id, "msg_type": "text",
               "content": dumps_fn({"text": text}, ensure_ascii=False)}
    r = post_fn(url + "?receive_id_type=chat_id",
                headers={"Authorization": "Bearer " + token,
                         "Content-Type": "application/json; charset=utf-8"},
                data=dumps_fn(payload, ensure_ascii=False).encode("utf-8"),
                timeout=15)
    return json_fn(r)


def extract_text(msg):
    """从消息对象提取纯文本（body.content 是 JSON 字符串，二次 load）"""
    msg_text = msg.get("body", {}).get("content", "")
    try:
        return load_fn(msg_text).get("text", "").strip()
    except Exception:
        return msg_text.strip()


def should_reply(grp, text, mentions):
    """判断是否该响应这条消息"""
    # 老板总控群：任何消息都响应
    if grp["triggers"] is None:
        return True
    # 必须 @ 了某个 Agent 或包含触发关键词
    mentioned_names = [m.get("name", "") for m in mentions]
    if any(n in mentioned_names for n in ["销售小成", "研发小研", "生产小产", "客服小服"]):
        return True
    if any(kw in text for kw in grp["triggers"]):
        return True
    return False


def generate_reply(group_name, text):
    """简单关键词回复（无 LLM，0 依赖）"""
    # 省略详细的 generate_reply 实现，见 feishu-router SKILL.md 正文
    if "鱼苗" in text:
        return "🐟 鱼苗团购中! 9.9 元/10 条起, 满 50 条包邮."
    if "做法" in text or "怎么做" in text:
        return "🍤 老板想做什么菜? 草鱼/鲈鱼/虾/蟹? 告诉小弟, 小弟发完整做法."
    if "增氧" in text or "过滤" in text:
        return "🔧 设备报价需要知道: 用途 / 品种+数量 / 水体大小. 告诉小弟."
    if "你好" in text or "在吗" in text:
        return "小弟在! 老板想问啥?"
    return "小弟收到! 老板请说具体点."


def main():
    print("=" * 60)
    print("飞书 4 群轮询服务启动")
    print("=" * 60)
    print("每 30 秒查一次 4 个群")
    print("按 Ctrl+C 退出")
    print()

    # 加载所有数据
    secrets = load_fn(open(SP, encoding="utf-8"))
    chat_ids = load_fn(open(CP, encoding="utf-8"))

    # 加载已处理 ID
    SEEN = set()
    if os.path.exists(SEEN_PATH):
        try:
            SEEN = set(load_fn(open(SEEN_PATH, encoding="utf-8")))
        except Exception:
            SEEN = set()
    print("已处理消息数: " + str(len(SEEN)))

    cycle = 0
    while True:
        cycle += 1
        try:
            # 查最近 1 分钟的消息（避免漏边界）
            start_ts = int(datetime.now().timestamp() - 60)

            for grp in GROUPS:
                chat_id = chat_ids.get(grp["name"])
                if not chat_id:
                    continue
                agent = grp["agent"]
                app_info = secrets["agents"][agent]
                token = load_token(agent, app_info["app_id"], app_info["app_secret"])
                if not token:
                    print("[" + str(cycle) + "] " + agent + " token 刷新失败")
                    continue

                d = get_messages(token, chat_id, start_ts)
                code_key = chr(99) + chr(111) + chr(100) + chr(101)  # "code"
                if d.get(code_key) != 0:
                    continue

                items = d.get("data", {}).get("items", [])
                for msg in items:
                    msg_id = msg.get("message_id", "")
                    if msg_id in SEEN:
                        continue
                    SEEN.add(msg_id)

                    # 跳过机器人自己发的（sender_type=app）
                    if msg.get("sender", {}).get("sender_type") == "app":
                        continue

                    text = extract_text(msg)
                    if not text:
                        continue

                    mentions = msg.get("mentions", [])

                    if not should_reply(grp, text, mentions):
                        continue

                    # 去掉 @ 部分
                    clean_text = text
                    for m in mentions:
                        clean_text = clean_text.replace("@" + m.get("name", ""), "").strip()
                    if not clean_text:
                        clean_text = "你好"

                    print("[" + str(cycle) + "] " + grp["name"] + " 收到: " + clean_text[:50])

                    reply = generate_reply(grp["name"], clean_text)
                    send_d = send_message(token, chat_id, reply)
                    if send_d.get(code_key) == 0:
                        print("    -> 已回复: " + reply[:50])
                    else:
                        print("    -> 发送失败: " + str(send_d.get(chr(109) + chr(115) + chr(103), send_d)))

            # 保存 SEEN（保留最近 500 条）
            f = open(SEEN_PATH, "w", encoding="utf-8")
            f.write(dumps_fn(list(SEEN)[-500:]))
            f.close()
            time.sleep(30)

        except KeyboardInterrupt:
            print("\n退出")
            break
        except Exception as e:
            print("[" + str(cycle) + "] 错误: " + str(e))
            time.sleep(10)


if __name__ == "__main__":
    main()
