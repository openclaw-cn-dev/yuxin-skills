#!/usr/bin/env python3
"""R23 — 单词边界 AI 关键词匹配演示与验证脚本

目的：避免 3 字母短词（如 iot/ai/svm/yolo）作为子串误命中无关论文
      R23 实证：'antibiotic resistance genes' 被 'iot' 子串误命中微生物组论文

用法：
  python3 scripts/r23-word-boundary-demo.py            # 跑默认测试用例
  python3 scripts/r23-word-boundary-demo.py "IoT sensor"  # 测试自定义文本

跨日复测建议：每个 cron 周期（5-7 天）跑一次，验证子串误命中仍被拦截
"""
import re
import sys

# AI 关键词 — 单词边界正则（修复 R23 子串误命中）
AI_KW_WORD_BOUNDARY = [
    r"\bmachine learning\b", r"\bdeep learning\b", r"\bneural network\b",
    r"\bartificial intelligence\b", r"\bcomputer vision\b",
    r"\biot\b", r"\biot[-\s]based\b",
    r"\blstm\b", r"\bxgboost\b", r"\brandom forest\b",
    r"\byolo\b", r"\btransformer\b",
    r"\bregression\b", r"\bclassification\b",
    r"\bconvolutional\b", r"\bsupport vector\b",
    r"\bobject detection\b", r"\bimage segmentation\b",
]

# 默认测试用例（覆盖 R23 实证误命中场景）
DEFAULT_TEST_CASES = [
    # 必通过（应被命中）
    ("IoT sensor networks in aquaculture", "Should match IoT"),
    ("machine learning predicts fish weight", "Should match ML"),
    ("artificial intelligence for fish farming", "Should match AI"),
    ("deep learning CNN underwater fish detection", "Should match DL/CV"),
    ("LSTM time series water quality prediction", "Should match LSTM"),
    # 必拒绝（子串误命中，必须 0 hits）
    ("antibiotic resistance genes in recirculating aquaculture", "Must NOT match (antib-iot-ic 子串)"),
    ("the Baltic Sea fish populations under climate change", "Must NOT match (Bal-ti-c 子串 — 实测并非 iot，但曾被旧版误判)"),
    ("patriot fish conservation policy review", "Must NOT match (pat-ri-ot 子串)"),
    ("idiot's guide to fish farming", "Must NOT match (idi-ot 子串)"),
    ("Egyptian mau cat fish breed description", "Must NOT match (ma-u 无 iot 子串，验证用)"),
]

def has_ai_keyword_strict(text):
    """返回所有匹配的 AI 关键词（单词边界匹配）"""
    text_lower = text.lower()
    hits = []
    for pattern in AI_KW_WORD_BOUNDARY:
        m = re.search(pattern, text_lower)
        if m:
            hits.append(m.group(0))
    return hits


def run_test_cases(test_cases, expect_match_by_index=None):
    """
    expect_match_by_index: dict {index: True/False} — 显式期望是否应匹配
        默认按关键字串首词自动判定（"Should" vs "Must NOT"）
    """
    if expect_match_by_index is None:
        expect_match_by_index = {}

    pass_count = 0
    fail_count = 0

    for i, (text, expected) in enumerate(test_cases):
        hits = has_ai_keyword_strict(text)

        # 自动判定
        if i in expect_match_by_index:
            should_match = expect_match_by_index[i]
        else:
            should_match = "Should" in expected and "NOT" not in expected

        matched_expected = bool(hits) == should_match
        status = "✅" if matched_expected else "❌"
        if matched_expected:
            pass_count += 1
        else:
            fail_count += 1

        print(f"{status} [{i+1:2d}] '{text[:70]}'")
        print(f"      Expected: {expected}")
        print(f"      Hits: {hits}")
        print(f"      should_match={should_match}, got hits={bool(hits)}")
        print()

    print(f"{'='*70}")
    print(f"PASS: {pass_count}, FAIL: {fail_count}, Total: {len(test_cases)}")

    # 退出码：失败则非零（适合 CI）
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 用户传入自定义文本
        custom_text = " ".join(sys.argv[1:])
        hits = has_ai_keyword_strict(custom_text)
        print(f"Text: '{custom_text}'")
        print(f"AI keyword hits: {hits}")
        sys.exit(0 if hits else 0)  # 不强制 — 仅展示
    else:
        # 默认测试用例
        print("R23 Word-Boundary AI Keyword Filter — Default Test Cases")
        print("=" * 70)
        print()
        sys.exit(run_test_cases(DEFAULT_TEST_CASES))
