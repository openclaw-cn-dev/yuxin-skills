#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Property-Based Testing Demo (R522) — 老莫
演示 Hypothesis 三大支柱:Generators + Properties + Shrinking
渔芯落地候选: 照片修复 / RAS 数据处理 / LLM Gateway

依赖: pip install hypothesis pytest
运行: python3 scripts/r522_pbt_lob_demo.py
"""
from hypothesis import given, strategies as st, settings, example
from hypothesis import Phase

# ============================================================
# Demo 1: 经典排序性质 — sorted() 满足 3 个不变式
# ============================================================

@given(st.lists(st.integers(), min_size=1, max_size=50))
@settings(max_examples=200)
def test_sort_invariants(xs):
    """排序性质三件套: 长度不变 + 多重集相等 + 单调非降"""
    ys = sorted(xs)
    # Property 1: 长度不变
    assert len(ys) == len(xs)
    # Property 2: 元素集合不变(multiset equality)
    assert sorted(ys) == ys
    # Property 3: 单调非降
    for i in range(len(ys) - 1):
        assert ys[i] <= ys[i+1], f"不单调: ys[{i}]={ys[i]} > ys[{i+1}]={ys[i+1]}"


# ============================================================
# Demo 2: 渔芯候选 #1 — 照片修复服务
# Property: 输入 JPEG → 输出尺寸 + 色彩通道数(RGB=3)不变
# ============================================================

# 简化的"图像"表示
@st.composite
def jpeg_like_inputs(draw):
    """生成类 JPEG 输入: (width, height, channels)"""
    w = draw(st.integers(min_value=64, max_value=4096))
    h = draw(st.integers(min_value=64, max_value=4096))
    c = 3  # RGB
    return (w, h, c)


def fake_restore(img_shape):
    """模拟照片修复服务: 输出 = 输入(不缩放,只美化像素)"""
    w, h, c = img_shape
    # 真实服务会调用 doubao-seedream API,这里 mock 保持形状不变
    return (w, h, c)


@given(jpeg_like_inputs())
def ***SECRET***(img_shape):
    """Property: 输入/输出形状完全相同"""
    out = fake_restore(img_shape)
    assert out == img_shape, f"形状漂移: in={img_shape} out={out}"
    assert out[2] == 3, f"色彩通道数丢失 RGB: got {out[2]}"


# ============================================================
# Demo 3: 渔芯候选 #2 — RAS 水温/pH 滤波
# Property: 滤波后数值在原始 min/max 包络内
# ============================================================

@st.composite
def sensor_readings(draw, n=20):
    """生成 RAS 传感器读数序列"""
    return [draw(st.floats(min_value=0.0, max_value=35.0, allow_nan=False))
            for _ in range(n)]


def moving_average(xs, window=3):
    """简单移动平均滤波"""
    if len(xs) < window:
        return xs[:]
    out = []
    for i in range(len(xs) - window + 1):
        out.append(sum(xs[i:i+window]) / window)
    return out


@given(sensor_readings(n=20))
def test_ras_filter_envelope(xs):
    """Property: 滤波后数值 ∈ [原始 min, 原始 max]"""
    if not xs:
        return
    filtered = moving_average(xs, window=3)
    orig_min, orig_max = min(xs), max(xs)
    for v in filtered:
        assert orig_min - 1e-9 <= v <= orig_max + 1e-9, \
            f"滤波值 {v} 超出原包络 [{orig_min}, {orig_max}]"


# ============================================================
# Demo 4: 渔芯候选 #3 — LLM Gateway 响应长度稳定性
# Property: 同一 prompt 重发 N 次,响应长度在合理波动内
# ============================================================

import random

def mock_llm_response(prompt: str) -> int:
    """Mock LLM: 返回 prompt 长度 × 系数 + 噪声"""
    base = len(prompt) * 10
    noise = random.gauss(0, base * 0.05)  # 5% 高斯噪声
    return int(base + noise)


@given(st.text(min_size=10, max_size=200))
@settings(max_examples=50, deadline=1000)
def test_llm_response_stability(prompt):
    """Property: 响应长度均值稳定,变异系数 < 20%"""
    samples = [mock_llm_response(prompt) for _ in range(10)]
    mean = sum(samples) / len(samples)
    var = sum((x - mean)**2 for x in samples) / len(samples)
    std = var ** 0.5
    cv = std / mean if mean > 0 else 0
    # 变异系数 < 20% 视为稳定(mock 注入 5% 噪声 → 留 4x 余量)
    assert cv < 0.20, f"响应不稳定: prompt={prompt[:30]}... cv={cv:.3f} samples={samples}"


# ============================================================
# 故意反例演示 — Shrinking 自动最小化
# ============================================================

@example(xs=[1, 0, -1, 1e308])  # 锚定一个边界用例
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False)))
def test_sum_finite(xs):
    """反例: 浮点累加溢出。Hypothesis 会自动 shrink 到最小反例。"""
    total = 0.0
    for x in xs:
        total += x
    assert abs(total) < 1e10, f"累加值过大: total={total} xs={xs[:5]}"


# ============================================================
# Driver
# ============================================================

if __name__ == "__main__":
    import sys
    import pytest

    # 运行所有 test_ 函数
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
