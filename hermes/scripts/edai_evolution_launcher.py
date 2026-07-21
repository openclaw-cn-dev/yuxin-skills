#!/usr/bin/env python3
"""
EDAI 9设备 — 统一自进化启动器 v1.0

每个设备独立运行自进化周期：
1. 扫描 RKR 知识库获取本设备领域最新知识
2. 检测知识缺口（MISSING_TOPIC / SHALLOW_COVERAGE / OUTDATED）
3. 自动向 RKR 提交 CategoryRequest 调研申请
4. RKR 转发 → FindEra 调研 → 结果回库 → 设备重新扫描（闭环）

用法:
  python3 edai_evolution_launcher.py [--device 滚筒微滤机] [--once] [--interval 6]

三项目沟通机制:
  EDAI(自进化检测缺口) → RKR(CategoryRequest API) → FindEra(调研采集)
  FindEra → 文档中转站 → RKR(扫描导入) → EDAI(重新扫描验证)
"""
import os
import sys
import json
import time
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger('EDAI')

# ── 配置 ──
RKR_BASE_URL = os.environ.get("RKR_BASE_URL", "http://localhost:8000")
RKR_API_KEY = os.environ.get("RKR_API_KEY", "")
RKR_EMAIL = os.environ.get("RKR_EMAIL", "")
RKR_PASSWORD = os.environ.get("RKR_PASSWORD", "")
RKR_TOKEN = os.environ.get("RKR_TOKEN", "")  # 直接使用已有 token 跳过登录

# 9 大设备知识域定义
EDAI_DEVICES = {
    "滚筒微滤机": {
        "id": "HW-003",
        "port": 8103,
        "topics": [
            "滚筒微滤机过滤精度", "转鼓式固液分离", "反冲洗优化",
            "微滤机筛网选型", "悬浮固体去除率", "微滤机节能降耗",
            "RAS微滤机设计标准", "微滤机故障诊断", "滤网堵塞动力学",
        ],
        "rkr_project_id": "***SECRET***",
        "category_path": "RAS设备与技术工程 > 核心处理单元 > 滚筒微滤机",
    },
    "蛋白分离器": {
        "id": "HW-001",
        "port": 8101,
        "topics": [
            "蛋白质分离器设计", "气浮分离技术", "泡沫分馏",
            "有机物去除率", "臭氧耦合蛋白分离", "蛋白分离器水力计算",
            "RAS蛋白分离器标准", "蛋白分离器优化", "微气泡生成技术",
        ],
        "rkr_project_id": "***SECRET***",
        "category_path": "RAS设备与技术工程 > 核心处理单元 > 蛋白分离器",
    },
    "生物过滤设备": {
        "id": "HW-004",
        "port": 8104,
        "topics": [
            "MBBR生物过滤", "硝化动力学", "生物膜技术",
            "填料比表面积", "氨氮去除率", "反硝化设计",
            "RAS生物滤池标准", "生物过滤优化", "移动床生物反应器",
        ],
        "rkr_project_id": "***SECRET***",
        "category_path": "RAS设备与技术工程 > 核心处理单元 > 生物过滤",
    },
    "增氧曝气系统": {
        "id": "HW-005",
        "port": 8105,
        "topics": [
            "增氧曝气系统设计", "溶解氧分布", "氧传递效率",
            "曝气盘选型", "纯氧增氧技术", "曝气能耗优化",
            "RAS增氧标准", "纳米曝气技术", "锥形氧气锥设计",
        ],
        "rkr_project_id": "***SECRET***",
        "category_path": "RAS设备与技术工程 > 辅助系统 > 增氧曝气",
    },
    "温控设备": {
        "id": "HW-006",
        "port": 8106,
        "topics": [
            "RAS温控系统设计", "加热制冷功率计算", "保温材料选型",
            "热泵技术", "温度场分布", "温控能耗优化",
            "RAS温控标准", "换热器选型", "太阳能辅助加热",
        ],
        "rkr_project_id": "***SECRET***",
        "category_path": "RAS设备与技术工程 > 辅助系统 > 温控设备",
    },
    "消毒设备": {
        "id": "HW-007",
        "port": 8107,
        "topics": [
            "UV紫外消毒系统", "臭氧消毒技术", "消毒剂量计算",
            "UV灯管选型", "臭氧发生器", "RAS消毒标准",
            "高级氧化技术", "消毒副产物控制", "紫外线穿透率",
        ],
        "rkr_project_id": "***SECRET***",
        "category_path": "RAS设备与技术工程 > 辅助系统 > 消毒设备",
    },
    "自动投喂设备": {
        "id": "HW-008",
        "port": 8108,
        "topics": [
            "自动投喂系统设计", "投喂策略优化", "饲料转化率",
            "生长模型", "投喂频率", "RAS投喂标准",
            "智能投喂算法", "饲料营养配方", "投喂量计算",
        ],
        "rkr_project_id": "***SECRET***",
        "category_path": "RAS设备与技术工程 > 辅助系统 > 自动投喂",
    },
    "智能控制": {
        "id": "HW-009",
        "port": 8109,
        "topics": [
            "PLC控制系统", "水质在线监测", "传感器选型",
            "RAS自动化控制", "远程监控系统", "控制算法优化",
            "工业物联网", "数字孪生控制", "故障预警系统",
        ],
        "rkr_project_id": "***SECRET***",
        "category_path": "RAS设备与技术工程 > 系统设计与集成 > 智能控制",
    },
    "数据采集设备": {
        "id": "HW-010",
        "port": 8110,
        "topics": [
            "水质传感器技术", "数据采集系统", "采样频率优化",
            "传感器校准", "RAS数据采集标准", "数据清洗算法",
            "多参数监测", "无线传感网络", "边缘计算",
        ],
        "rkr_project_id": "***SECRET***",
        "category_path": "RAS设备与技术工程 > 系统设计与集成 > 数据采集",
    },
}


class EDAIDeviceEvolution:
    """单个 EDAI 设备的自进化引擎"""

    def __init__(self, device_name: str, config: dict):
        self.name = device_name
        self.config = config
        self.device_id = config['id']
        self.topics = config['topics']
        self.rkr_project_id = config.get('rkr_project_id', '')
        self.category_path = config.get('category_path', '')
        self.state_file = Path.home() / '.edai_evolution' / f'{device_name}_state.json'
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()
        self._token: Optional[str] = None

    def _load_state(self) -> dict:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except Exception:
                pass
        return {
            "device": self.name,
            "cycles_completed": 0,
            "gaps_found_total": 0,
            "requests_submitted": 0,
            "last_scan_at": None,
            "known_topics": [],
        }

    def _save_state(self):
        self.state_file.write_text(json.dumps(self.state, indent=2, ensure_ascii=False))

    def _get_token(self) -> Optional[str]:
        """获取 RKR JWT Token（优先使用环境变量）"""
        if self._token:
            return self._token
        # 优先使用环境变量中的 token
        if RKR_TOKEN:
            self._token = RKR_TOKEN
            return self._token
        if not RKR_EMAIL or not RKR_PASSWORD:
            logger.warning(f"[{self.name}] 未配置 RKR 凭据，使用 API Key 模式")
            return None
        try:
            resp = requests.post(
                f"{RKR_BASE_URL}/api/v1/auth/login",
                json={"email": RKR_EMAIL, "password": RKR_PASSWORD},
                timeout=10,
            )
            if resp.status_code == 200:
                self._token = resp.json().get("access_token")
                return self._token
        except Exception as e:
            logger.warning(f"[{self.name}] RKR 登录失败: {e}")
        return None

    def _api_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        token = self._get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if RKR_API_KEY:
            headers["X-API-Key"] = RKR_API_KEY
        return headers

    def check_rkr_health(self) -> bool:
        """检查 RKR 是否可达"""
        try:
            resp = requests.get(f"{RKR_BASE_URL}/api/v1/health", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def scan_knowledge(self) -> list[dict]:
        """扫描 RKR 知识库，搜索本设备领域知识"""
        gaps = []
        headers = self._api_headers()

        for topic in self.topics:
            try:
                # 语义搜索 RKR
                resp = requests.post(
                    f"{RKR_BASE_URL}/api/v1/search",
                    headers=headers,
                    json={"query": topic, "top_k": 5},
                    timeout=15,
                )
                if resp.status_code != 200:
                    continue

                results = resp.json().get("results", [])
                scores = [r.get("score", 0) for r in results]

                if not results or max(scores) < 0.6 if scores else True:
                    # 知识缺口：搜索结果少或相关性低
                    gaps.append({
                        "topic": topic,
                        "gap_type": "MISSING_TOPIC" if not results else "SHALLOW_COVERAGE",
                        "current_results": len(results),
                        "max_score": max(scores) if scores else 0,
                    })
                    logger.info(f"[{self.name}] 🔍 缺口: {topic} ({gaps[-1]['gap_type']})")

                self.state["known_topics"].append(topic)

            except Exception as e:
                logger.error(f"[{self.name}] 搜索 '{topic}' 失败: {e}")

        return gaps

    def submit_category_request(self, gap: dict) -> bool:
        """向 RKR 提交知识域条目申请（触发调研）"""
        headers = self._api_headers()

        payload = {
            "name": gap["topic"],
            "description": f"[{self.name}] 自动检测到知识缺口: {gap['gap_type']}。"
                          f"当前搜索结果: {gap['current_results']}条，"
                          f"最高相关度: {gap['max_score']}。"
                          f"建议 FindEra 对该主题进行深度调研。",
            "requester_module": f"EDAI-{self.name}",
            "requester_contact": f"edai-{self.device_id}@yuxin.tech",
            "target_project_id": self.rkr_project_id,
            "source": "edai_auto_evolution",
            "external_ref": hashlib.md5(
                f"{self.name}_{gap['topic']}_{datetime.now().strftime('%Y%m%d')}".encode()
            ).hexdigest()[:12],
        }

        # 添加建议的分类路径
        if self.category_path:
            payload["suggested_category_path"] = self.category_path

        try:
            resp = requests.post(
                f"{RKR_BASE_URL}/api/v1/external/category-requests",
                headers=headers,
                json=payload,
                timeout=15,
            )
            if resp.status_code in (200, 201):
                logger.info(f"[{self.name}] ✅ 已提交调研申请: {gap['topic']}")
                return True
            else:
                logger.warning(f"[{self.name}] 提交失败 ({resp.status_code}): {resp.text[:100]}")
                return False
        except Exception as e:
            logger.error(f"[{self.name}] 提交异常: {e}")
            return False

    def run_evolution_cycle(self) -> dict:
        """执行一次完整自进化周期"""
        cycle_start = datetime.now(timezone.utc)
        result = {
            "device": self.name,
            "device_id": self.device_id,
            "started_at": cycle_start.isoformat(),
            "rkr_healthy": False,
            "gaps_found": 0,
            "requests_submitted": 0,
            "status": "unknown",
        }

        # 1. 检查 RKR 连通性
        if not self.check_rkr_health():
            result["status"] = "rkr_unreachable"
            logger.warning(f"[{self.name}] ⚠️ RKR 不可达")
            return result

        result["rkr_healthy"] = True

        # 2. 扫描知识缺口
        gaps = self.scan_knowledge()
        result["gaps_found"] = len(gaps)

        # 3. 提交调研申请
        for gap in gaps:
            if self.submit_category_request(gap):
                result["requests_submitted"] += 1
                time.sleep(0.5)  # 避免请求过快

        # 4. 更新状态
        self.state["cycles_completed"] += 1
        self.state["gaps_found_total"] += len(gaps)
        self.state["requests_submitted"] += result["requests_submitted"]
        self.state["last_scan_at"] = cycle_start.isoformat()
        self._save_state()

        result["status"] = "completed"
        result["total_cycles"] = self.state["cycles_completed"]
        elapsed = (datetime.now(timezone.utc) - cycle_start).total_seconds()
        result["elapsed_seconds"] = round(elapsed, 1)

        logger.info(
            f"[{self.name}] 🧬 周期#{self.state['cycles_completed']}完成: "
            f"缺口{len(gaps)}, 申请{result['requests_submitted']}, "
            f"耗时{elapsed:.0f}秒"
        )
        return result


def run_all_devices(once: bool = False, interval_hours: int = 6, specific_device: str = None):
    """运行所有/指定 EDAI 设备自进化"""
    devices = {}
    for name, config in EDAI_DEVICES.items():
        if specific_device and specific_device not in name:
            continue
        devices[name] = EDAIDeviceEvolution(name, config)

    if not devices:
        logger.error(f"未找到设备: {specific_device}")
        return

    logger.info(f"🚀 EDAI 自进化启动: {len(devices)} 个设备")
    logger.info(f"   RKR: {RKR_BASE_URL}")
    logger.info(f"   模式: {'单次' if once else f'每{interval_hours}小时'}")

    try:
        while True:
            print(f"\n{'='*60}")
            print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")

            summary = {"total": 0, "gaps": 0, "submitted": 0, "errors": 0}

            for name, device in devices.items():
                try:
                    result = device.run_evolution_cycle()
                    summary["total"] += 1
                    summary["gaps"] += result["gaps_found"]
                    summary["submitted"] += result["requests_submitted"]
                    if result["status"] != "completed":
                        summary["errors"] += 1
                except Exception as e:
                    logger.error(f"[{name}] 进化异常: {e}")
                    summary["errors"] += 1

                time.sleep(1)  # 设备间隔

            print(f"📊 汇总: {summary['total']}设备, "
                  f"缺口{summary['gaps']}, 申请{summary['submitted']}, 错误{summary['errors']}")

            if once:
                break

            # 等待下一个周期
            wait = interval_hours * 3600
            print(f"⏳ 下次扫描: {wait/3600:.0f}小时后")
            time.sleep(wait)

    except KeyboardInterrupt:
        print("\n👋 EDAI 自进化已停止")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='EDAI 9设备统一自进化')
    parser.add_argument('--device', help='只运行指定设备')
    parser.add_argument('--once', action='store_true', help='只执行一次')
    parser.add_argument('--interval', type=int, default=6, help='进化间隔(小时)')
    parser.add_argument('--rkr-url', default=RKR_BASE_URL, help='RKR API地址')
    args = parser.parse_args()

    if args.rkr_url:
        RKR_BASE_URL = args.rkr_url

    run_all_devices(once=args.once, interval_hours=args.interval, specific_device=args.device)
