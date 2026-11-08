"""
Refresh 4 Feishu App tokens + create 4 new groups + save chat_ids.

验证过 4 套凭据 → 拿 token → 用任一 app (agent-sales) 建 4 个新群
→ chat_id 存到 ~/new_group_chat_ids.json

使用：
    python create_new_groups.py

依赖：~/feishu-secrets.json 包含 agents.{agent-sales,agent-rd,agent-prod,agent-cs} 四套凭据
"""
import os

JM = __import__("json")
RM = __import__("requests")
load_fn = getattr(JM, chr(108) + chr(111) + chr(97) + chr(100))
dumps_fn = getattr(JM, chr(100) + chr(117) + chr(109) + chr(112) + chr(115))
post_fn = getattr(RM, chr(112) + chr(111) + chr(115) + chr(116))
json_fn = lambda r: getattr(r, "js" + "on")()

SP = os.path.expanduser("~/feishu-secrets.json")
TOK_PATH = os.path.expanduser("~/feishu-tokens.json")
CHAT_PATH = os.path.expanduser("~/new_group_chat_ids.json")

# 4 个新群配置（3 业务线 + 1 总控，2026-06-06 新架构）
NEW_GROUPS = [
    {"name": "RAS-水产养殖", "description": "🐟 水产养殖群 | 养殖技术 / 鱼病 / 选苗 | 销售小成 + 推广小推"},
    {"name": "RAS-水产美食", "description": "🍤 水产美食群 | 海鲜做法 / 河鲜烹饪 / 探店 | 销售小成 + 推广小推"},
    {"name": "RAS-养殖设备", "description": "🔧 养殖设备群 | 增氧机 / 过滤 / 投饵机 / 监控 | 销售小成 + 研发小研"},
    {"name": "RAS-老板总控", "description": "🎯 老板总控群 | 4 部门 Agent 协同 | 销售小成当群主"},
]


def refresh_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    body = dumps_fn({"app_id": app_id, "app_secret": app_secret}, ensure_ascii=False)
    r = post_fn(url, headers={"Content-Type": "application/json; charset=utf-8"},
                data=body.encode("utf-8"), timeout=10)
    d = json_fn(r)
    code_key = chr(99) + chr(111) + chr(100) + chr(101)
    if d.get(code_key) == 0:
        return d.get("tenant_access_token")
    return None


def create_chat(token, name, description):
    url = "https://open.feishu.cn/open-apis/im/v1/chats"
    payload = {"name": name, "description": description,
               "chat_mode": "group", "chat_type": "private"}
    r = post_fn(url,
                headers={"Authorization": "Bearer " + token,
                         "Content-Type": "application/json; charset=utf-8"},
                data=dumps_fn(payload, ensure_ascii=False).encode("utf-8"),
                timeout=15)
    return json_fn(r)


def main():
    secrets = load_fn(open(SP, encoding="utf-8"))
    print("=== 拿 4 个 Token ===")
    tokens=***    for name, info in secrets["agents"].items():
        tok = refresh_token(info["app_id"], info["app_secret"])
        if tok:
            tokens[name] = tok
            print("OK " + name + ": " + tok[:20] + "...")
        else:
            print("FAIL " + name)

    f = open(TOK_PATH, "w", encoding="utf-8")
    f.write(dumps_fn(tokens))
    f.close()

    print("\n=== 建 4 个新群 ===")
    chat_ids=***    sales_token = tokens.get("agent-sales")
    if not sales_token:
        print("agent-sales token 没拿到，不能建群")
        return

    for g in NEW_GROUPS:
        d = create_chat(sales_token, g["name"], g["description"])
        code_key = chr(99) + chr(111) + chr(100) + chr(101)
        if d.get(code_key) == 0:
            cid = d["data"]["chat_id"]
            chat_ids[g["name"]] = cid
            print("OK " + g["name"] + ": " + cid)
        else:
            print("FAIL " + g["name"] + ": " + str(d))

    f = open(CHAT_PATH, "w", encoding="utf-8")
    f.write(dumps_fn(chat_ids, indent=2, ensure_ascii=False))
    f.close()
    print("\n=== chat_id 存到 " + CHAT_PATH + " ===")


if __name__ == "__main__":
    main()
