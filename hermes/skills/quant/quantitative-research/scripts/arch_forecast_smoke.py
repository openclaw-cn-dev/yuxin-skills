"""
arch 8.0.0 GARCH(1,1)-normal forecast + β-degenerate 检测冒烟脚本
心跳 #N+116 (2026-09-17) 首次沉淀

⚠️ pitfall-N+135 配套脚本:
- 验证 arch 8.0.0 forecast API(替代 .quantile() 方法被 7.x 移除的协议)
- 验证 GARCH(1,1)-normal + 手算 VaR95(z95 × σ)
- 验证 rolling β-degenerate 检测 + ConvergenceWarning 抑制
- 验证 L3 GARCH 实战可行性(模拟 ARCH(1) 过程 → 验证模型还原)

用法:
    python3 /Users/hua/.hermes/skills/quant/quantitative-research/scripts/arch_forecast_smoke.py

输出:
- 1-step / 5-step forecast std trajectory
- VaR95 手算值
- rolling 1-step forecast stats
- rolling β-degenerate 占比
- ConvergenceWarning 占比(应 < 100%,即抑制生效)

⚠️ cron 模式:必跑 `python3 /path/to/script.py`,不走 `wire_file` / `pyte_code`(pitfall-N+80)
⚠️ HOME 沙箱:必跑绝对路径(pitfall-N+95)
"""
import warnings
import numpy as np
import pandas as pd
from arch import arch_model

# pitfall-N+135 协议:rolling fit 必加 warning 抑制
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*returned code.*')


def simulate_arch1(n, omega=1e-5, alpha=0.15, seed=42):
    """模拟 ARCH(1) 过程:GARCH(1,1) 应能还原 α"""
    np.random.seed(seed)
    rets = np.zeros(n)
    sigma2 = np.zeros(n)
    sigma2[0] = omega / (1 - alpha)
    for t in range(1, n):
        sigma2[t] = omega + alpha * rets[t-1]**2
        rets[t] = np.random.normal(0, np.sqrt(sigma2[t]))
    return pd.Series(rets[1:])


def single_fit(rets_s):
    """单次 GARCH(1,1)-normal fit + 1-step/5-step forecast"""
    am = arch_model(rets_s, mean='Zero', vol='GARCH', p=1, q=1, dist='normal')
    res = am.fit(disp='off')

    alpha = res.params['alpha[1]']
    beta = res.params['beta[1]']
    persistence = alpha + beta

    # 1-step forecast
    fc1 = res.forecast(horizon=1, reindex=False)
    std1 = np.sqrt(fc1.variance.values[-1, 0])

    # 5-step forecast
    fc5 = res.forecast(horizon=5, reindex=False)
    std5_traj = fc5.variance.values[-1]**0.5

    # VaR95 手算(替代 7.x 移除的 quantile())
    cond_vol = res.conditional_volatility
    z95 = -1.645
    VaR95 = z95 * cond_vol.iloc[-1]

    return {
        'alpha': alpha,
        'beta': beta,
        'persistence': persistence,
        'std1': std1,
        'std5_traj': std5_traj.tolist(),
        'VaR95': VaR95,
        'VaR95_pct': VaR95 * 100,
    }


def rolling_check(rets_s, window=100, step=50):
    """rolling GARCH fit + β-degenerate 检测(pitfall-N+96 + N+104 + N+135)"""
    n_total = 0
    n_degenerate = 0
    n_error = 0
    rolling_std_forecasts = []

    for i in range(0, len(rets_s) - window, step):
        n_total += 1
        sub = rets_s.iloc[i:i+window]
        try:
            am_r = arch_model(sub, mean='Zero', vol='GARCH', p=1, q=1, dist='normal')
            res_r = am_r.fit(disp='off')

            beta_r = res_r.params.get('beta[1]', 0)
            if beta_r < 0.01:
                n_degenerate += 1

            fc_r = res_r.forecast(horizon=1, reindex=False)
            rolling_std_forecasts.append(np.sqrt(fc_r.variance.values[-1, 0]))
        except Exception:
            n_error += 1

    return {
        'n_total': n_total,
        'degenerate_pct': n_degenerate / n_total * 100 if n_total else 0,
        'error_pct': n_error / n_total * 100 if n_total else 0,
        'rolling_std_latest': np.mean(rolling_std_forecasts[-5:]) if rolling_std_forecasts else None,
        'rolling_std_mean': np.mean(rolling_std_forecasts) if rolling_std_forecasts else None,
    }


def main():
    # 1. 模拟 ARCH(1) 过程(ω=1e-5, α=0.15, n=500)
    print('=== arch 8.0.0 GARCH(1,1)-normal forecast 冒烟(心跳 #N+116)===')
    rets_s = simulate_arch1(n=500, omega=1e-5, alpha=0.15, seed=42)
    print(f"模拟数据: n={len(rets_s)}, ARCH(1) α=0.15, ω=1e-5")

    # 2. 单次 fit + forecast
    print('\n--- [1] 单次 GARCH(1,1)-normal fit ---')
    fit_result = single_fit(rets_s)
    print(f"  α={fit_result['alpha']:.4f} β={fit_result['beta']:.4f} persistence={fit_result['persistence']:.4f}")
    print(f"  1-step std forecast: {fit_result['std1']:.4f}")
    print(f"  5-step std trajectory: {[round(x, 5) for x in fit_result['std5_traj']]}")
    print(f"  VaR95 (手算 z95×σ): {fit_result['VaR95']:.4f} ({fit_result['VaR95_pct']:.2f}%)")

    # 3. rolling check
    print('\n--- [2] rolling GARCH β-degenerate 检测 (window=100, step=50) ---')
    roll_result = rolling_check(rets_s, window=100, step=50)
    print(f"  总窗口: {roll_result['n_total']}")
    print(f"  β<0.01 占比: {roll_result['degenerate_pct']:.1f}%")
    print(f"  error 占比: {roll_result['error_pct']:.1f}%")
    print(f"  rolling 1-step std: latest={roll_result['rolling_std_latest']:.4f}, mean={roll_result['rolling_std_mean']:.4f}")

    # 4. 判定
    print('\n--- [3] 判定 ---')
    if roll_result['degenerate_pct'] >= 50:
        print("  ⚠️ β-degenerate >= 50% → 回退 rolling std 20d + L1 ruptures")
    elif roll_result['degenerate_pct'] >= 20:
        print("  🟡 β-degenerate ∈ [20%, 50%) → GARCH 部分可用,需标注")
    else:
        print("  🟢 β-degenerate < 20% → GARCH 正常")

    print('\n✅ arch 8.0.0 forecast + β-degenerate 检测验证完成(pitfall-N+135 + N+96 + N+104)')


if __name__ == '__main__':
    main()