---
name: small-llm-training
description: 在本地设备（Apple Silicon MPS / 单卡 CUDA）从零训练或微调小型 LLM 的完整工作流 — 选型调研、环境搭建、数据切片、训练、推理演示、归档复跑。触发条件：华哥说"我们也造一个/训练一个专用模型/复现 XX 开源项目"、本地跑 LLM 训练、MPS/CUDA 训练报错排查、训练类任务内存管控。macOS 训练死锁/崩溃排障（import mutex、pyarrow、DataLoader 卡死）、内存看门狗、M4/16GB MiniMind 实测参数与工作流 dashboard（2026-09-09 curator 整档收纳原 local-llm-training、local-llm-training-macos 于 references/）。
license: MIT
metadata:
  author: 渔芯科技
  version: "1.0.0"
---

# 本地小模型训练工作流（从零训练 / 微调 / 复现开源项目）

## When to Use

- 华哥要求"造一个模型看看""训练 XX 专用大模型""复现某开源训练项目"
- 需要在 Mac mini (Apple M4/MPS, 16GB) 或单卡 CUDA 上跑 LLM 训练/微调
- 训练中遇到 loss=nan、内存暴涨、进程假死、import 崩溃等典型坑

## 九步标准工作流（2026-09-07 MiniMind 实测验证）

1. **选型调研**：GitHub API 一手元数据（stars/license/pushed_at/生态仓库），不用第三方转述
2. **获取代码**：`git clone --depth 1 https://gh-proxy.com/https://github.com/<repo>`（直连 50-100kB/s，gh-proxy 2.3MB/s）
3. **环境搭建**：**永远用 uv 建干净 venv（py3.11+），禁用系统 Python**；版本对齐项目 requirements 的 pin（如 transformers==4.57.6，不要默认装 5.x）
4. **数据准备**：大数据集用 HTTP Range 切片（`curl -r 0-104857599`）取前 N MB；国内走 ModelScope resolve 直链
5. **兼容性补丁**：先小步烟雾测试（20-100 步）再正式跑
6. **预训练**：后台挂 + `python3 -u`（无缓冲）+ 日志重定向**绝对路径** + notify_on_complete
7. **SFT/微调**：衔接预训练权重；注意 checkpoint 目录与加载目录一致性
8. **推理演示**：写独立 demo 脚本（apply_chat_template + generate，temperature 0.7 / top_p 0.9），3 问实录原始输出（好与差都如实记录）
9. **归档复跑**：实测记录 md（时间线/踩坑/复跑命令）+ 工作流看板 HTML + 截图 MEDIA 发飞书

## Apple Silicon MPS 四大铁坑（每坑都实付过学费）

| # | 症状 | 根因 | 根治 |
|---|---|---|---|
| ① | `import` 模型代码即 C++ 崩溃 `mutex lock failed: Invalid argument`（faulthandler 都来不及注册） | macOS 系统 Python 3.9 + 二进制混搭 | **uv 建 py3.11 干净 venv**，一行代码不病 |
| ② | `load_dataset` 解析大 jsonl 进程假死（CPU ~3%，log 只有 mutex.cc RAW: Lock blocking） | pyarrow/leveldb 在 macOS 死锁 | 补丁：纯 `json.loads` 逐行读（try/except 跳残行），接口保持兼容 |
| ③ | 官方脚本一跑就 HFValidationError / 找不到文件 | 脚本按特定 cwd 设计（如 MiniMind 一切相对 cwd=trainer/） | 按官方预期 cwd 跑；日志重定向用绝对路径 |
| ④ | SFT 大 batch loss=nan + 内存冲到 14GB/16GB | MPS fp32 大 batch×长 seq 数值溢出 + MPS 缓存不主动释放 | **batch 减半重试**（16→8 即愈）；挂内存看门狗 |

诊断卡死进程的轻量招：脚本头部加 `faulthandler.register(signal.SIGUSR1)` → 卡时 `kill -USR1 <pid>` 打印调用栈（py-spy 在 macOS 要 root，不实用）。

## 内存纪律（华哥铁律：长任务不许把 16GB 机器搞爆）

- 训练挂后台后**必挂看门狗**：每 60s `top -l 1 -pid <pid> -stats mem` 采样，**>11GB 自动 kill -9 + 落盘告警文件**（MPS 统一内存计入 top MEM 列，ps RSS 不准——曾显示 21MB 实际 14GB）
- 注意 swap 水位（`sysctl vm.swapusage`）：used >2GB 即预警
- 大 batch 想加码前先跑 micro-run（30-100 步）看内存峰值

## MiniMind 复现配方（已验证命令级）

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python torch "transformers==4.57.6" "datasets==3.6.0" einops jsonlines -i https://pypi.tuna.tsinghua.edu.cn/simple
# 数据切片（ModelScope resolve 直链支持 Range）
curl -sL -r 0-104857599 "https://www.modelscope.cn/datasets/gongjy/minimind_dataset/resolve/master/pretrain_t2t_mini.jsonl" -o dataset/pretrain_run.jsonl
cd minimind/trainer   # 官方预期 cwd
../../.venv/bin/python -u train_pretrain.py --device mps --dtype float --epochs 1 \
  --batch_size 16 --num_workers 0 --data_path ../dataset/pretrain_run.jsonl
../../.venv/bin/python -u train_full_sft.py --device mps --dtype float --epochs 1 \
  --batch_size 8 --num_workers 0 --data_path ../dataset/sft_run.jsonl --from_weight pretrain
```

实测基准（M4/16GB，1/10 数据切片）：预训练 1,563 步 loss 8.29→4.88（36min）；SFT 1,500 步 5.49→3.20（47min，batch 8）；fp16 权重 137MB；fp32 训练 8.3GB 稳定。

## 领域专用模型改接（同一条流水线换语料）

MiniMind 类项目验证后，训练"行业专用模型"只换三件：①语料（清洗+QA 合成）②tokenizer 若领域词量大需重训 ③评测集（自建 N 题域内评测 + 微调前后对照，防自嗨式微调）。**先 RAG 后微调再从零**是成本递增的落地次序；从零小模型（<100M）定位=教学/品牌/端侧实验，不可承诺生产问答能力（benchmark 贴近随机水平是常态）。

## 交付格式（华哥已认可）

工作流看板单文件 HTML（深色主题、九步时间线、踩坑红框、官方 vs 实测对照表）→ `browser_navigate file://` + `browser_vision` 截图 → final response 带 `MEDIA:<截图路径>` 发飞书；全程日志/脚本落盘项目目录并写复跑指南。

## 关联

> 🗂️ 2026-09-09 curator 整档收纳（原独立 skill 已归档，内容原样保留）：
> - `references/local-llm-training/` — Mac/Apple Silicon 训练全流程 v1.1：环境搭建、数据切片、macOS 三大死锁/崩溃排障（import mutex 崩溃、pyarrow deadlock、DataLoader 卡死）、MPS 内存爆+loss nan 排障、内存看门狗、多阶段训练流水线串联、minimind-m4 实验档案
> - `references/local-llm-training-macos/` — M4/16GB 实测工作流：MPS 适配三大坑、MiniMind 实测参数、uv/venv 搭建、minimind-m4-run 档案 + workflow-dashboard.html 模板
>
> 本 SKILL.md 为主工作流（选型→环境→数据→训练→推理→归档）；macOS 专项排障细节与实测参数查上述两个 references 分册。

- 云端 GPU 完整复现（完整数据集/大模型）→ skill `cloud-gpu-automation`（AutoDL Token/扫码直连；**2026-09-07 5090 部署新增 7 坑已入其 Pitfalls**：规格无库存降级链 / 5090 Blackwell 需 cu128 新 torch / pip resolver 死循环换 uv / paramiko 通道超时→nohup+状态文件轮询 / paramiko 长会话脆→SSH 公钥+原生 ssh / snapshot data 包装层 / 凭证防脱敏复制）
- 渔芯已验证实例：`~/6-产品研发/渔芯独角兽/01-开发中/渔芯RAS小模型/`（看板/实测记录/RAS 方案/yuxin_demo.py）
- 渔芯 RAS 专用模型三路线（A RAG→B LoRA **Qwen3-4B**（华哥 09-07 批复）→C 从零 RAS-GPT）见该目录 00-方案；**C 路线暂不开源、对外发布暂缓（华哥同日修订）**，产出先内部评估
