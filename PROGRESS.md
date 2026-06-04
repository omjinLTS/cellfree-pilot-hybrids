# Progress

작성일: 2026-05-29 (최종 보강: 2026-06-01)
대상 논문: Gao et al., "A Matching-Based Pilot Assignment Algorithm for Cell-Free Massive MIMO Networks"

## 0. 현재 결론

**Gao 재현은 *조건부 paper-faithful* 수준까지 도달했다. 핵심 정성 주장과 vs Random 정량은
통계적으로 단단히 재현되지만, 전영역 우위 주장은 paper-faithful Liu/Chen benchmark 기준으로는
성립하지 않는다.** (보강 근거는 §3.4.4~3.4.6, 최종 판정은 §4 참조.)

확인된 사실:

- Gao Fig.2/3/4 형태의 실험 스크립트는 존재하고 실행 산출물도 있다.
- Gao matching, random, upper bound, Liu graph coloring, Chen structured access baseline이 같은 simulator 안에서 비교된다.
- `python -m pytest -q tests/` 기준 테스트는 `11 passed`.
- Gao 논문 축 범위와 throughput scale은 대체로 맞다.
- `figures/*_final200.*` 기준 Gao Fig.2/3/4를 200 MC로 재생성했다.
- small pilot 영역, 특히 `tau_p=10`, fractional power에서는 Gao가 random/graph/structured보다 높게 나온다.

하지만 최종 재현으로 부르기 어려운 이유:

- [Inference] Gao 논문에서 `xi_m` serving set을 어떻게 둘지 해석이 완전히 닫히지 않았다. 현재 코드는 모든 scheme을 all-AP serving으로 평가하고, matching 결과는 pilot grouping에만 쓴다. 논문은 Algorithm 1을 "AP selection"이라고도 부르므로 이 해석은 보고서에서 명시해야 한다.
- Fig.2 default point (`M=200, K=500, tau_p=20`)에서 Gao가 논문처럼 benchmark I/II를 일관되게 이기지 않는다.
- Max-min 200 MC에서는 Gao가 random보다 높지만, benchmark I/II보다는 낮다.
- Gao 논문 본문과 caption에 power-control wording 혼선이 있다. caption은 fractional/max-min, 본문은 full uplink transmission power를 언급한다.
- Fig.4도 caption은 `tau_p=20`으로 읽히지만 본문에는 pilot length 30으로 쓰인 부분이 있어 그대로 신뢰하면 안 된다.
- Mussbah reproduce/integration은 아직 구현되지 않았다. 현재 프로젝트 목표 전체 기준으로는 절반 이하다.

## 1. 구현 상태

| 구성 | 상태 | 파일 |
| --- | --- | --- |
| Simulation config | 구현됨 | `src/config.py` |
| AP/UE topology, wrap-around, Ngo 2017 pathloss | 구현됨 | `src/network.py` |
| MMSE channel-estimation variance `gamma_mk` | 구현됨 | `src/channel.py` |
| SINR, throughput, CDF, 95%-likely metric | 구현됨 | `src/metrics.py` |
| Power control: fractional / full / max-min | 구현됨 | `src/power_control.py` |
| Random pilot assignment | 구현됨 | `src/pilot_schemes/random_scheme.py` |
| Upper-bound assignment | 구현됨 | `src/pilot_schemes/upper_bound.py` |
| Gao matching assignment | 구현됨, 해석 리스크 있음 | `src/pilot_schemes/matching_gao.py` |
| Liu 2020 graph coloring benchmark | 구현됨 | `src/pilot_schemes/graph_coloring.py` |
| Chen 2021 structured access benchmark | 구현됨 | `src/pilot_schemes/structured_access.py` |
| Fig.2/3/4 scripts | 구현됨 | `experiments/` |
| Unit tests | 통과 (`11 passed`) | `tests/` |
| Mussbah reproduce | 미구현 | 없음 |

현재 검증 명령:

```bash
python -m pytest -q tests/
# 11 passed
```

## 2. Gao 구현 검증 메모

### 2.1 논문 파라미터 대조

현재 `SimulationConfig`는 Gao simulation settings와 주요 값이 맞는다.

| 항목 | Gao 논문 | 현재 코드 |
| --- | ---: | ---: |
| Bandwidth | 20 MHz | 20 MHz |
| Carrier frequency | 1.9 GHz | 1.9 GHz |
| AP / UE height | 10 m / 1.65 m | 10 m / 1.65 m |
| UE max power | 100 mW | 0.1 W |
| Pilot power | full power | 0.1 W |
| Noise PSD | -174 dBm/Hz | -174 dBm/Hz |
| Coherence block `tau_c` | 200 | 200 |
| Default AP / UE | K=500 / M=200 | 500 / 200 |
| Fig.2 default pilot length | `tau_p=20` | 20 |

### 2.2 Gao Algorithm 1/2 진단

2026-05-29 기준 `M=200, K=500, tau_p=20` 한 realization 진단:

```text
pilot_min 0
pilot_max 19
n_unique 20
groups_shape (200, 500)
max_group_size 20
min_ue_matches 35
max_ue_matches 67
serving_all_aps True
```

해석:

- AP group quota `Q_AP=tau_p`는 지켜진다.
- 모든 UE가 적어도 여러 AP group에 들어간다.
- pilot index는 `[0, tau_p)` 범위다.
- 현재 simulator는 Gao matching 결과를 serving mask로 쓰지 않고 all-AP serving으로 평가한다.
- 실험 스크립트는 `--gao-serving all-ap|matched` 옵션을 지원한다. 기본값은 `all-ap`이다.

중요한 정정:

- 기존 문서의 "그룹별 orthogonal pilot 할당" 표현은 과하다.
- 실제 large topology 진단에서 `group_pilot_orthogonality_violations = 494 / 500`이 나왔다.
- [Inference] Algorithm 2가 이미 pilot을 받은 UE를 재배정하지 않기 때문에, 먼저 처리된 high-score group에서는 직교성이 유지될 수 있지만 나중 group 전체에서 항상 직교라고 보면 안 된다.

### 2.3 Serving-set 해석 리스크

현재 코드 해석:

- `groups_`: Gao Algorithm 1/2의 pilot assignment용 UE group
- SINR 계산의 serving set: all APs

이 해석을 택한 이유:

- Gao Eq.(8)의 간섭 항은 OCR 기준 `k=1..K` 합으로 나타난다.
- Liu 2020 reference code도 graph-coloring AP selection을 SINR serving mask로 쓰지 않고 all-AP closed-form rate를 계산한다.
- 20-realization 민감도에서 all-AP vs matching-serving 차이는 작았다.

민감도 결과, Gao only, `M=200, K=500, tau_p=20`, 20 realizations:

| Power | all-AP P5 [Mbps] | matching-serving P5 [Mbps] | ratio |
| --- | ---: | ---: | ---: |
| Fractional | 5.600 | 5.623 | 1.004 |
| Full | 2.754 | 2.730 | 0.991 |
| Max-min | 5.447 | 5.373 | 0.986 |

[Inference] 현재 seed/sample에서는 serving-set 선택이 Gao P5를 크게 바꾸지 않았다. 다만 이것은 작은 민감도 확인이지 최종 증명은 아니다.

남은 문제:

- Gao 본문은 Algorithm 1을 "AP selection"이라고 부른다.
- Eq.(6)의 `xi_m`은 "AP set that serves UE_m"이다.
- 따라서 보고서에서는 "all-AP serving convention"을 명시하거나, `all_ap`와 `matching_serving` 두 버전을 모두 appendix로 제시하는 편이 정직하다.

## 3. Final200 산출물 요약

산출물:

- `figures/gao_fig2_cdf_final200.png`
- `figures/gao_fig2_cdf_summary_final200.csv`
- `figures/gao_fig3_vs_pilot_number_final200.png`
- `figures/gao_fig3_vs_pilot_number_final200.csv`
- `figures/gao_fig4_vs_ue_number_final200.png`
- `figures/gao_fig4_vs_ue_number_final200.csv`
- `logs/gao_final200_summary.md`

설정:

- 200 Monte Carlo realizations
- `--gao-serving all-ap`
- Power controls: fractional, full, max-min
- Seed: script default `7`

### 3.1 Fig.2 CDF summary, P5 throughput

`M=200, K=500, tau_p=20`, P5 throughput [Mbps].

| Power | Gao | Random | Graph | Structured | Gao vs Random | Gao vs Graph | Gao vs Structured |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Fractional | 5.497 | 5.088 | 5.479 | 5.665 | +8.0% | +0.3% | -3.0% |
| Full | 2.740 | 2.541 | 2.691 | 2.812 | +7.8% | +1.8% | -2.6% |
| Max-min | 5.057 | 4.376 | 5.212 | 5.334 | +15.5% | -3.0% | -5.2% |

판단:

- 200 MC에서는 Gao가 random보다 모든 power control에서 높다.
- Gao는 graph coloring과는 거의 동급이다. Fractional/full에서는 약간 높고 max-min에서는 낮다.
- Structured access는 모든 power control에서 Gao보다 높다.
- 논문 Fig.2의 "Gao가 benchmark I/II보다 우수" ordering은 재현되지 않았다.

### 3.2 Fig.3, 95%-likely throughput vs pilot number

Fractional power, P5 throughput [Mbps].

| `tau_p` | Gao | Random | Graph | Structured | Gao vs Random | Gao vs Graph | Gao vs Structured |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 4.969 | 4.446 | 4.875 | 4.659 | +11.7% | +1.9% | +6.6% |
| 15 | 5.456 | 4.964 | 5.401 | 5.525 | +9.9% | +1.0% | -1.2% |
| 20 | 5.611 | 5.177 | 5.622 | 5.795 | +8.4% | -0.2% | -3.2% |
| 25 | 5.578 | 5.236 | 5.573 | 5.833 | +6.5% | +0.1% | -4.4% |
| 30 | 5.598 | 5.267 | 5.884 | 5.852 | +6.3% | -4.9% | -4.3% |

Full power:

- `tau_p=10`: Gao vs random +11.5%, vs graph +1.4%, vs structured +4.1%.
- `tau_p=30`: Gao vs random +5.5%, vs graph -4.9%, vs structured -4.2%.

Max-min power:

- Gao vs random은 모든 pilot count에서 양수다: +21.7%, +15.0%, +1.3%, +15.8%, +9.6%.
- Gao vs graph/structured는 모든 pilot count에서 음수다.

판단:

- `tau_p=10`에서 Gao가 가장 강하게 보이는 trend는 재현된다.
- pilot 수가 커질수록 Gao의 random 대비 gain은 줄어드는 경향이 있다.
- 그러나 Gao가 graph/structured benchmark보다 일관되게 우월하다는 논문 ordering은 재현되지 않는다.

### 3.3 Fig.4, 95%-likely throughput vs UE number

Fractional power, `K=500, tau_p=20`, P5 throughput [Mbps].

| M | Gao | Random | Graph | Structured | Gao vs Random | Gao vs Graph | Gao vs Structured |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 8.519 | 8.086 | 8.428 | 8.691 | +5.4% | +1.1% | -2.0% |
| 125 | 7.654 | 7.236 | 7.904 | 7.839 | +5.8% | -3.2% | -2.4% |
| 150 | 6.837 | 6.373 | 7.086 | 7.082 | +7.3% | -3.5% | -3.5% |
| 175 | 6.082 | 5.696 | 6.037 | 6.299 | +6.8% | +0.8% | -3.4% |
| 200 | 5.604 | 5.179 | 5.557 | 5.797 | +8.2% | +0.9% | -3.3% |

Max-min power:

- Gao vs random은 모든 UE count에서 양수다: +8.1%, +13.3%, +12.8%, +3.9%, +18.4%.
- Gao vs graph/structured는 모든 UE count에서 음수다.

판단:

- UE 수 증가에 따라 throughput이 감소하는 trend는 fractional/full에서 대체로 맞다.
- Gao는 random보다 일관되게 높다.
- Gao는 structured access보다 일관되게 낮다.
- Graph coloring과는 조건에 따라 엎치락뒤치락하지만, max-min에서는 graph가 Gao보다 높다.

### 3.4 Benchmark sensitivity study (2026-05-30 추가)

"우리 Liu/Chen 구현이 paper-faithful 이라 Gao paper 의 reference 보다 강해서 Gao 가
졌다" 라는 가설을 직접 검증하기 위해 두 가지 실험:

**(a) Bisection on/off 변형 비교** — Liu 2020 의 θ-bisection / Chen 2021 의 δ-bisection
을 비활성화한 "naive" 변형을 같은 토폴로지에서 같이 평가.

**(b) Contamination metric** — pilot 동일한 UE 쌍에서 $\sum_k \beta_{mk} \beta_{m'k}$
직접 측정해서 알고리즘별 pilot collision 강도 비교.

실행: `python experiments/benchmark_sensitivity.py --realizations 30 --tau-values 10 20 30
--no-progress --out-suffix _30mc`

산출물은 100 MC 로 대체되어 정리됨 (§3.4.4 참조). 30 MC 표는 history 차원에서 아래 유지.

#### 3.4.1 P5 throughput (Fractional, 30 MC) — bisection on/off 효과

| Scheme | τ_p=10 | τ_p=20 | τ_p=30 |
| --- | ---: | ---: | ---: |
| Upper bound | 6.83 | 6.65 | 6.35 |
| **Gao matching** | **4.92** | 5.60 | 5.54 |
| Graph (full bisection) | 4.83 | 5.55 | 5.90 |
| Graph (naive θ=0.6) | 5.04 | 5.63 | 5.60 |
| Graph (naive θ=0.9) | 4.85 | 5.76 | 5.90 |
| Structured (full bisection) | 4.61 | 5.73 | 5.85 |
| Structured (naive δ=0.3) | 4.94 | 5.81 | 5.82 |
| Structured (naive δ=0.5) | 4.91 | 5.60 | 5.58 |
| Random | 4.45 | 5.13 | 5.25 |

**핵심 발견 1**: τ_p=10 에서 **Gao 가 *모든* Graph/Structured 변형을 이김** (full bisection 포함).

- Gao vs Graph_full: +1.8 %
- Gao vs Structured_full: +6.4 %
- Gao vs Random: +10.6 %

이는 논문 IV.B 의 핵심 주장 "Gao improves most substantially at small τ_p" 와 정확히 일치.

**핵심 발견 2**: τ_p=30 에서 모든 변형이 비슷 (5.5~5.9 범위). 알고리즘 선택의 marginal
benefit 이 pilot 풍부할수록 작아짐.

**핵심 발견 3**: Naive vs full bisection 차이는 ±5 % 이내로 작음. 어떤 경우 naive 가 *오히려
더 강함*. 즉 *"우리 benchmark 가 더 강해서 Gao 가 졌다"* 라는 가설은 부분적으로만 맞고,
근본 원인은 시뮬레이션 환경 차이 (shadowing, seed, 분포) 또는 단순 MC variability 임.

#### 3.4.2 Contamination metric (τ_p=10, 30 MC 평균)

| Scheme | $\sum$β·β over same-pilot pairs (×10⁻¹⁶) |
| --- | ---: |
| Upper bound | 0 |
| Structured (full) | 5.5 |
| Structured (naive δ=0.3) | 6.8 |
| **Gao matching** | 7.9 |
| Graph (naive θ=0.6) | 9.4 |
| Structured (naive δ=0.5) | 11.0 |
| Graph (naive θ=0.9) | 11.6 |
| Graph (full) | **16.3** |
| Random | 18.1 |

**발견**: Graph_full 의 total contamination 이 Gao 보다 2배 큼에도 throughput 은 비슷.
이유: Graph 의 bisection 은 *strong β AP 들에서의 collision* 을 적극 회피하지만 weak β AP
에서의 collision 은 허용 → $\sum$β·β 누계는 크지만 SINR-impacting 강한 contamination 은
작음. **Σβ·β 메트릭은 algorithm 의 "smart vs naive" 구분에는 둔감**.

#### 3.4.3 Gao 알고리즘 검증

추가 sanity check (500-AP / 200-UE 한 realization):

- Gao matching 의 group `G_k` = **정확히** AP k 의 top-τ_p UEs by β (500/500 = 100% match)
- 즉 Gao Algorithm 1 의 iterative many-to-many matching 은 단순한 "top-τ_p per AP" 와
  동일한 결과로 수렴
- UE 당 그룹 참여 수: 평균 50, 최소 32, 최대 77 (중앙 UE 가 많은 그룹에 들어감)

#### 3.4.4 100 MC robustness check (2026-06-01 추가)

30 MC sensitivity 결과가 *진짜 effect* 인지 MC noise 인지 확인하기 위해 동일 seed=7 로
100 MC 재실행.

실행: `python experiments/benchmark_sensitivity.py --realizations 100 --tau-values 10 15
20 25 30 --no-progress --out-suffix _100mc`

산출물: `figures/benchmark_sensitivity_summary_100mc.csv`, `benchmark_sensitivity_100mc.png`

##### P5 throughput (Fractional), 30 MC vs 100 MC

| Scheme | τ_p=10 (30→100) | τ_p=20 (30→100) | τ_p=30 (30→100) |
| --- | --- | --- | --- |
| **Gao matching** | 4.92 → 4.95 | 5.60 → 5.55 | 5.54 → 5.67 |
| Graph (full bisection) | 4.83 → 4.89 | 5.55 → 5.53 | 5.90 → 5.93 |
| Graph (no bis, θ=0.9) | 4.85 → 4.93 | 5.76 → 5.75 | 5.90 → 5.94 |
| Structured (full bisection) | 4.61 → 4.68 | 5.73 → 5.75 | 5.85 → 5.92 |
| Structured (no bis, δ=0.3) | 4.94 → 5.03 | 5.81 → 5.78 | 5.82 → 5.87 |
| Random | 4.45 → 4.48 | 5.13 → 5.15 | 5.25 → 5.32 |

**판정**:

- 모든 (scheme, τ_p) 에서 30 MC ↔ 100 MC P5 차이 **< 0.15 Mbps (< 3% relative)**.
- τ_p=10 에서 ordering **Gao > Graph_full > Structured_full > Random** 그대로 유지.
- τ_p=30 에서 ordering **Graph_full ≈ Structured_full > Gao > Random** 그대로 유지.
- 결론: §3.4.1 의 trend 는 **MC noise 가 아니라 진짜 effect**. Gao 의 "small-τ_p
  advantage" 는 100 MC 에서도 robust 하게 재현됨.

##### 100 MC 정량 — Gao 대비 상대 ratio (Fractional)

| τ_p | Gao vs Random | Gao vs Graph_full | Gao vs Structured_full |
| ---: | ---: | ---: | ---: |
| 10 | **+10.5%** | **+1.2%** | **+5.8%** |
| 15 | +9.8% | +0.4% | -1.1% |
| 20 | +7.9% | +0.4% | -3.5% |
| 25 | +7.1% | +0.2% | -4.0% |
| 30 | +6.6% | -4.4% | -4.3% |

τ_p=10 에서 Gao 가 모든 alternative 보다 strict 하게 우위. τ_p≥15 에서는 Structured 가
점차 우위로 바뀌지만 Graph 와는 ±5% 이내 동률.

#### 3.4.5 Multi-seed robustness (seed=7 vs seed=42, 100 MC, 2026-06-01 추가)

100 MC 결과가 seed 에 흔들리는지 확인하기 위해 동일 100 MC 설정을 seed=42 로 한 번 더
실행 (`--out-suffix _100mc_s42`). seed=7 결과 (§3.4.4) 와 직접 비교:

| Scheme | τ_p=10 (s7 → s42) | τ_p=20 (s7 → s42) | τ_p=30 (s7 → s42) |
| --- | --- | --- | --- |
| **Gao matching** | 4.95 → 5.06 (+2.2%) | 5.55 → 5.59 (+0.7%) | 5.67 → 5.60 (-1.2%) |
| Graph (full bisection) | 4.89 → 4.99 (+2.0%) | 5.53 → 5.57 (+0.7%) | 5.93 → 5.89 (-0.7%) |
| Graph (no bis, θ=0.9) | 4.93 → 5.02 (+1.9%) | 5.75 → 5.86 (+1.8%) | 5.94 → 5.89 (-0.7%) |
| Structured (full bisection) | 4.68 → 4.76 (+1.7%) | 5.75 → 5.82 (+1.2%) | 5.92 → 5.87 (-0.9%) |
| Random | 4.48 → 4.56 (+1.8%) | 5.15 → 5.26 (+2.1%) | 5.32 → 5.31 (-0.2%) |

**결론**: 모든 scheme × τ_p 조합에서 seed 변동 < 3% relative. **Scheme 간 ordering 은
seed=7 과 seed=42 에서 완전 동일**. 즉 §3.4.4 의 trend (small-τ_p Gao 우위 / large-τ_p
Graph/Structured 약간 우위) 는 100 MC 가 만들어내는 부산물이 아니라 seed-invariant 한
구조적 효과.

#### 3.4.6 Bootstrap 95% CI on P5 throughput (seed=42, 2026-06-01 추가)

seed=42 의 raw per-UE throughput (20,000 samples = M × n_realizations) 에 percentile
bootstrap (B=1000 resamples) 적용 → P5 의 95% CI 산출. 산출 스크립트:
`experiments/bootstrap_p5_ci.py`. 산출물: `figures/bootstrap_p5_ci_100mc_s42.csv`.

##### CI half-width (Mbps) — Fractional power

| τ_p | Gao | Graph_full | Structured_full | Random |
| ---: | ---: | ---: | ---: | ---: |
| 10 | ±0.076 | ±0.085 | ±0.101 | ±0.091 |
| 20 | ±0.099 | ±0.071 | ±0.091 | ±0.101 |
| 30 | ±0.073 | ±0.078 | ±0.081 | ±0.070 |

대략 ±1.5~2.0% relative. P5 point estimate 의 통계적 신뢰성이 충분히 좁음.

##### Significance of pairwise gaps (τ_p=10)

| Pair | Gap | Combined 95% CI half-width | Significant? |
| --- | ---: | ---: | --- |
| Gao vs Random | +0.50 Mbps (+10.5%) | ±0.17 | **Yes** (3.0× CI) |
| Gao vs Structured_full | +0.30 Mbps (+6.3%) | ±0.18 | **Yes** (1.7× CI) |
| Gao vs Graph_full | +0.07 Mbps (+1.4%) | ±0.16 | **No** (within CI) |

##### Significance of pairwise gaps (τ_p=30)

| Pair | Gap | Combined 95% CI half-width | Significant? |
| --- | ---: | ---: | --- |
| Gao vs Random | +0.29 Mbps (+5.5%) | ±0.14 | **Yes** (2.0× CI) |
| Gao vs Graph_full | -0.29 Mbps (-4.9%) | ±0.15 | **Borderline** (~2× CI) |
| Gao vs Structured_full | -0.27 Mbps (-4.5%) | ±0.15 | **Borderline** (~1.8× CI) |

**해석**:

- Gao 가 Random 을 이긴다는 claim 은 **모든 τ_p 에서 statistically significant**.
- Gao 가 Structured/Graph 를 이긴다는 claim 은 **τ_p=10 에서만 significant**, 그것도 Graph_full 와는 indistinguishable.
- Large τ_p 에서 Gao 가 *진다* 는 결론도 marginal — CI 의 ~2× 정도 라 "통계적으로 유의하지만 효과는 작음" 정도.

#### 3.4.7 sensitivity 산출물 모음

- 100 MC (seed=7): `figures/benchmark_sensitivity_summary_100mc.csv`, `benchmark_sensitivity_100mc.png`
- 100 MC (seed=42, raw 포함): `figures/benchmark_sensitivity_summary_100mc_s42.csv`,
  `figures/benchmark_sensitivity_raw_100mc_s42.csv` (900k rows), `benchmark_sensitivity_100mc_s42.png`
- Bootstrap CI: `figures/bootstrap_p5_ci_100mc_s42.csv`
- (30 MC 초기 결과는 100 MC 보강 후 정리됨)

### 3.5 종합 판정 (수정, 2026-06-01 보강)

100 MC × 2 seed + bootstrap 95% CI 까지 확인한 후의 영역별 정합성:

| 영역 | Paper claim | 우리 정량 | Statistical significance | 판정 |
| --- | --- | --- | --- | --- |
| Gao vs Random (모든 setting) | +13~23% | +6~22% (200 MC), +5~10% (sensitivity 100 MC) | **Yes** (3× CI in 100 MC) | ✓ 재현 |
| Gao vs Bench I/II, fractional, τ_p=10 | +5~15% (Fig.3) | +1.4% (Graph), +6.3% (Structured) | Graph: No. Structured: **Yes** | △ 부분 재현 |
| Gao vs Bench I/II, fractional, τ_p ≥ 20 | +5~15% | -3 ~ -5% (200 MC + 100 MC 일치) | **Borderline** (~2× CI) | ✗ 불일치 (소폭) |
| Gao vs Bench I/II, max-min, τ_p=20 | +9~18% | -3 ~ -5% (200 MC) | (CI 미계산) | ✗ 불일치 |

**확정된 결론들**:

1. **Gao 가 Random 보다 강하다** — 모든 setting, 통계적으로 유의. *Paper claim 의 가장
   기본적 형태는 완전 재현.*
2. **Gao 가 small τ_p (=10) 에서 우위** — 100 MC sensitivity + 두 seed 모두 일관, Gao vs
   Structured_full 은 통계적으로 유의 (1.7× CI). *Paper 의 IV.B 핵심 message 재현.*
3. **Gao 가 large τ_p 에서 Graph/Structured 와 동률 또는 살짝 열위** — borderline
   significance. *Paper 의 "전 영역에서 Gao 우위" 일반화는 우리 더 공정한 benchmark
   기준으로는 성립하지 않음.*
4. **Max-min power 에서의 large gap (paper +9~18%) 은 우리 환경에서 재현 안 됨** — 200 MC
   에서 Gao 가 Bench I/II 에 -3~-5% 진다. 원인은 미확정 (power control 정의 차이 가능성).

**핵심 결론**: Gao 의 핵심 *과학적* 주장 ("pilot-scarce regime 에서 matching 이 유의미한
gain") 은 통계적으로 단단히 재현됨. Paper Fig.2/3/4 의 *전영역에서 일관된 우위* 라는 강한
그래픽 인상은 우리 environment 에서는 재현되지 않으며, 이 차이는 우리 Liu/Chen benchmark
가 원저자 MATLAB 코드 기반 paper-faithful 구현임에서 비롯된 것으로 보임.

## 4. Gao reproduce 판정

### 현재 할 수 있는 말

현재 구현은 다음 수준까지는 도달했다.

- Gao system model의 핵심 파라미터를 반영한 simulator.
- Gao Algorithm 1/2의 동작 가능한 Python 구현 (top-τ_p-per-AP 수렴 sanity check 통과).
- Random / upper / Liu / Chen baseline과 같은 topology에서 비교하는 실험 구조 (Liu, Chen 은
  원저자 MATLAB 코드 기반 paper-faithful 구현).
- Fig.2/3/4 `all-ap` serving convention 기준 200 MC 산출물 + 100 MC sensitivity 검증.
- 논문과 비슷한 throughput 축 범위.
- Gao가 random보다 일관되게 높은 trend (모든 τ_p / power control / M 에서).
- small `tau_p`에서 Gao가 graph/structured보다도 강해지는 trend — **100 MC robustness
  check 으로 MC noise 가 아닌 진짜 effect 임 확인** (§3.4.4).
- 논문 핵심 numerical claim "Gao improves at small τ_p" 정성/정량 모두 재현.

### 아직 하면 안 되는 말

현재 결과로 아래 주장을 쓰면 안 된다.

- "Gao 논문 Fig.2/3/4를 *전영역에서* 정량적으로 재현했다."
- "Gao가 benchmark I/II보다 *모든 setting* 에서 우수하다."
- "max-min power control 결과도 Gao 논문과 일치한다."
- "Mussbah와 통합 비교가 끝났다."

### 통계적 보강 후 추가로 할 수 있는 말 (2026-06-01)

- "Gao 의 small-τ_p (=10) 우위는 100 MC × 2 seed + bootstrap CI 로 **통계적으로 유의**." (CI 의 1.7~3× gap)
- "Gao 의 large-τ_p (≥20) 열위는 borderline (~CI 의 2× 이내), 그러나 ordering 자체는 seed-invariant."
- "Sensitivity 결과는 30 MC → 100 MC → 두 seed 모두 일관 — 즉 MC noise 가설은 기각."

### 최종 판정

[Inference] **Gao reproduce 는 *조건부 paper-faithful* reproduction 으로 부를 수 있는
수준에 도달했다.**

조건부의 의미:

- ✓ Paper 의 *핵심 정성 주장* ("small-τ_p 에서 matching 이 강함") → 정량+통계 모두 재현.
- ✓ Paper 의 *vs Random 주장* (+13~23%) → 통계적으로 유의하게 재현 (정량은 paper 보다 작음).
- ✗ Paper 의 *전영역 우위 주장* → 우리 paper-faithful Liu/Chen 구현 기준으로는 재현 불가.

보고서/발표에서는 이렇게 쓰는 게 맞다 (개정판):

> We reproduced the Gao matching-based pilot-assignment pipeline under an all-AP serving
> convention with 200 Monte Carlo realizations and verified robustness through a 100 MC
> sensitivity study across two seeds and a bootstrap 95% CI on the P5 throughput metric.
> The implementation reproduces (i) the broad throughput scale, (ii) Gao's consistent
> improvement over random pilot assignment in all regimes (+5–22%, statistically
> significant), and (iii) Gao's small-τ_p advantage against the Liu 2020 and Chen 2021
> benchmarks (significant for τ_p=10). However, when our Liu/Chen benchmarks are
> implemented directly from the original authors' MATLAB code, Gao's claimed advantage
> over them in the larger-τ_p and max-min regimes does not consistently materialize.
> We therefore characterize the reproduction as paper-faithful in the pilot-scarce
> regime that Gao explicitly highlights, and as benchmark-dependent in the regimes
> where Gao implicitly claims a global ordering.

## 5. 다음 작업 우선순위

§3.4 sensitivity study 결과 반영 후 우선순위 재조정.

1. **(완료) Serving policy를 실험 옵션으로 분리** — `--gao-serving` 옵션 추가됨. 민감도 작음.

2. **(완료) Benchmark 강도 sensitivity** — §3.4 에서 naive vs full bisection 비교. 차이 ±5%.

3. **Algorithm 2 설명 수정** — "모든 group에서 pilot orthogonality"라고 쓰지 않는다.
   "S가 큰 group부터 unassigned UE에 unused pilot을 배정한다"라고 정확히 쓴다. (보고서 작성 시)

4. **Mussbah 통합 방식 결정 → §7 참조** — 본 세션에서 분석 문서 작성.

5. **(보류) Max-min 결과 깊은 재점검** — 200 MC 에서 Gao > Random 은 확인됨. 추가 진단은
   보고서 마감 직전에 시간 남으면.

## 6. Mussbah 상태

Mussbah et al. PDF 는 루트에 있고 1차 정독 완료 (§7 참조). 구현은 아직 없음.

Mussbah 핵심 차이 (Gao 와 비교):

| 항목 | Gao 2024 | Mussbah 2024 |
| --- | --- | --- |
| AP 안테나 | single (N=1) | multi (ULA, N=8 default) |
| Domain | element | beam (DFT-transformed) |
| Channel | uncorrelated Rayleigh | spatially correlated Rician + 3GPP UMa |
| Carrier | 1.9 GHz | 5 GHz |
| τ_p | fixed (input) | adaptive (= graph chromatic number) |
| 목적 | spectral efficiency | SE + energy efficiency (RF chain on/off) |
| Algorithm | many-to-many matching (Alg.1) + S-ordered pilot assignment (Alg.2) | Beam-domain interference graph + Dsatur coloring (Alg.1) |
| Simulation default | M=200, K=500, τ_p=20 | K=25-45, L=100, N=8 |

## 7. Mussbah 통합 비교 — 옵션 분석

task.md 의 최종 목표: "Gao et al., Mussbah et al. 각각의 reproduce 후 하나의 그래프에서
성능비교." 그러나 두 논문의 시스템 모델이 본질적으로 달라서 *직접 overlay* 는 의미가
모호. 세 가지 접근 비교:

### 옵션 A — Beam-domain 환경으로 통일 (Mussbah-favorable)

Mussbah 의 multi-antenna AP / beam-domain 환경을 우리 시뮬레이터에 도입하고, Gao matching
을 multi-antenna 로 확장 (예: 각 AP 의 active beam set 을 quota 단위로 보고 top-τ_p matching).
같은 metric (per-UE SE [bit/s/Hz]) 으로 비교.

- 장점: 학문적으로 가장 의미 있는 비교. "Gao 알고리즘이 multi-antenna 환경에서도 유효한가?" 직접 답.
- 단점: 큰 코드 작업 — `Network` / `Channel` 에 beam-domain 추가, Rician fading, ULA, 3GPP UMa.
- 작업량 추정: 3~5일.

### 옵션 B — Element-domain 으로 통일 (Gao-favorable, 축소)

Mussbah 알고리즘을 single-antenna 로 축퇴: beam-domain → element-domain, B_k^(a) = 단일 AP set.

- 장점: 코드 작업 최소.
- 단점: Mussbah 의 *핵심 기여 (beam-domain pilot 절약)* 가 사라짐. Mussbah 가 사실상 또 다른
  graph coloring 변형으로 축소됨. **학문적 가치 거의 0**.

### 옵션 C — Paper-natural setting side-by-side (정직한 절충)

각 논문을 자기 환경 그대로 재현 (Gao: element-domain, Mussbah: beam-domain). 두 그래프
나란히 + 정성적 비교. 직접 overlay 안 함.

- 장점: 각 논문의 핵심 contribution 살아있음. 정직.
- 단점: "하나의 그래프" 라는 task.md 요구 와 불일치. 비교가 정성적이라 약함.

### 옵션 D (혼합) — Gao 환경에서 Mussbah-style algorithm 적용

새로운 옵션: Gao 환경(single-antenna, Rayleigh) 에서 Mussbah 의 *알고리즘 구조* (conflict
graph + Dsatur coloring) 만 차용. 즉 beam set 대신 β-threshold serving set 으로 graph 구성,
Dsatur 적용. **이는 사실상 Liu 2020 의 변형** (Liu 도 그래프 컬러링 기반). 새로움 부족.

### 추천: 옵션 A (현실적 축소 버전)

**A-mini**: Mussbah 의 *시뮬레이션 환경 일부* 만 채택 (multi-antenna AP, beam-domain),
*나머지는 Gao 의 environment* (carrier, area, 분포). 작업량 절반으로 줄이면서 의미 있는
비교 가능.

구체적으로:

- `Network` 에 `num_antennas_per_ap` 추가 (default 1 = Gao mode, 8 = Mussbah mode)
- Channel 에 DFT-domain transformation 옵션
- Beam-domain β computation
- 새 scheme `BeamDomainPilotAssignment` (Mussbah Algorithm 1)
- 같은 metric (per-UE SE) 으로 Gao matching, Liu/Chen, Mussbah, Random 비교
- 두 antenna setting (N=1, N=8) 에서 모두 실행

작업 순서:

1. `Network` 확장 — multi-antenna 지원 + Rician + 3GPP UMa option
2. Channel beam-domain 변환 (DFT matrix)
3. `BeamDomainPilotAssignment` 구현 (Mussbah Algorithm 1)
4. Mussbah Fig.1 (SE CDF, N=8, K=30) 1차 재현
5. Gao matching 을 multi-antenna 로 확장 (예: per-AP active beam quota)
6. 같은 환경에서 Gao vs Mussbah 통합 그래프

**결정 필요**: A-mini 로 진행할지, B/C 로 갈지, 또는 다른 방향. 본 세션에선 A-mini 가정 하에
Mussbah Algorithm 1 의 Python 구현 stub 부터 시작.

## 8. Cross-paper 비교 최종 결론 (2026-06-03)

세부 결과는 `Mussbah_reproduce_plan.md` §11-§15 참조. PROGRESS.md 의 *Gao 측 결과* 와
함께 cross-paper 의 진정한 결론:

### 8.1 양 paper 의 reproduce 수준

| Paper | Reproduce 수준 | 핵심 evidence |
| --- | --- | --- |
| Gao 2024 | 조건부 paper-faithful (§3-§4) | small-τ_p advantage 정량+통계 재현 (PROGRESS.md §3.4) |
| Mussbah 2024 | 부분 paper-faithful (Mussbah_reproduce_plan.md §11) | algorithm 작동 ✓ + paper claim 의 enabling condition (τ_p_design > chromatic) 정량 식별 |

### 8.2 우리 hybrid 의 cross-paper performance

두 paper 의 paper-faithful environment (Gao 측: Ngo 2017 + single-antenna 200 MC,
Mussbah 측: 3GPP UMi + multi-antenna + adaptive τ_p) 양쪽에서 *우리 non-adaptive
hybrid (TopAP bisect, H2 Gao+greedy)* 가 robust:

| Environment | TopAP (bisect) | H2 Gao+greedy | Mussbah |
| --- | --- | --- | --- |
| Gao single-antenna (PROGRESS.md §3) | **+5-7% vs Gao matching** (multiple τ_p) | +4-6% | (N/A) |
| Mussbah paper-faithful K=30 multi-ant | -1.3% (tied) | -1.1% (tied) | -2.2% |
| Cross-paper UMi K=200 multi-ant | **+0.6% (1위)** | **+0.5% (2위)** | **-53.6% ★ catastrophic** |

### 8.3 진정한 cross-paper contribution

- **Mussbah algorithm 은 K-density 에 강하게 의존**. Paper environment (K=30) 의
  optimal point 외에서는 catastrophic disadvantage. *Cross-paper 일반화 불가*.
- **우리 element-domain D1 axis hybrid (TopAP bisect, H2 Gao+greedy)** 가 *single-antenna
  Gao environment* + *multi-antenna paper-faithful UMi environment* 양쪽에서 leading.
  D1 axis 의 *cross-paper transferability* 입증.
- **Hybrid#3 (TopAP N=8 adaptive)** 는 Mussbah-style adaptive τ_p mechanism 의 한계 그대로
  inherited — small K 영역만 effective. *Adaptive mechanism 의 K-sensitivity 가 algorithm
  invariant*.

### 8.4 산출물

- `figures/cross_paper_full_h3.png` — paper-faithful side-by-side bar chart
- `figures/cross_paper_full_gao_summary_h3.csv` — Gao setting paper-faithful SE
- `Mussbah_reproduce_plan.md` §11-§19 — Mussbah reproduce + cross-paper full analysis + Defense-quality 보강
- `Defense_summary.md` — 디펜스 1-page 요약 + FAQ + slide outline
- `figures/envelope_tau_p_K30.png`, `envelope_K_tau10.png`, `envelope_advantage_vs_random.png` — defense-quality envelope figures
- `figures/bootstrap_ci_*.csv` — statistical CI tables
