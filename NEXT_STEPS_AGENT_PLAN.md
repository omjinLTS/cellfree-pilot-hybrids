# Unified E4 Completion Note — Multi-antenna Cross-paper Benchmark

## 대상 독자

**Next LLM agent** (Claude / GPT / 기타) 가 본 project 를 이어받을 때 참고할 완료 기록.
이 문서는 원래 E4 unified benchmark 실행 계획이었고, 2026-06-04 에 E4 full run 이 완료됐다.

## 0. 배경 (왜 추가 작업이 필요한가)

기존 작업 (`PROGRESS.md`, `Mussbah_reproduce_plan.md`, `Diagnosis.md`) 에서 우리는 두
paper 의 *original environment* 에서 *각각 paper-faithful reproduce* 했고, *그 위에서 우리
hybrid algorithms (TopAP bisect, H2 Gao+greedy, Hybrid#3, Hybrid#4) 의 contribution* 을
입증했다. 그러나 **cross-paper 비교** 는 *두 paper environment 차이* (Gao = AP single-
antenna N=1, Mussbah = AP multi-antenna N=8) 때문에 *fundamentally tricky*:

- Single-antenna environment 에서는 Mussbah algorithm 의 `beam_info()` 가 작동 안 함
  (`RuntimeError`).
- Multi-antenna environment 에서는 Gao algorithm 이 *element-domain β* 만 사용해서 그대로
  작동하지만, *paper original (N=1) 과 다른 환경* 이라 *Gao paper reproduce 아님*.

우리 현재 `figures/cross_paper_full_final.png` 는 *multi-antenna 통일 (N=8) + K-density
sweep (K=30 vs K=200)* 의 *stress test*. **진정한 paper-faithful cross-paper benchmark**
는:

1. **Multi-antenna unified environment 의 정확한 spec 정의** — 두 paper environment 의
   *공통 ground* 가 무엇인지 명시.
2. **Gao matching algorithm 의 multi-antenna 확장** — *beam-domain 정보 활용* 옵션 추가
   (선택적).
3. **모든 9 schemes (paper baselines + 우리 4 hybrid)** 를 *unified env 에서 평가*.
4. **Paper figure 정량 ↔ unified env 결과* 차이 명확히 분석.

이 작업은 완료됐다. 남은 것은 E4 결과를 기반으로 더 작은 seed sanity, optional beam-domain Gao
extension, 또는 발표 문서 polish 다.

## 1. Current state 요약 (한 페이지)

### 1.1 What's already done ✓

- **Code modules** (`src/`): `config.py`, `network.py` (multi-antenna 지원),
  `pathloss_umi.py` (3GPP UMi), `mussbah_channel.py` (one-ring + Rician + DFT),
  `mussbah_se.py` (paper-faithful MC SE), `pilot_schemes/` (9 algorithms).
- **Experiment scripts** (`experiments/`): Gao Fig.2/3/4 (`fig2_cdf.py` etc.), Mussbah
  Fig.1 (`mussbah_fig1_full.py`), Mussbah Fig.3 K/τ_p sweep (`mussbah_fig3_k_sweep.py`),
  cross-paper (`cross_paper_full.py`), bootstrap CI (`bootstrap_se_ci.py`,
  `bootstrap_p5_ci.py`), envelope plots (`plot_envelopes.py`).
- **Tests**: 21 unit tests pass.
- **Results**: Gao reproduce 정량 일치 (paper +23%/우리 +21.7%, max-min τ_p=10), Mussbah
  paper-spec 구현 + enabling condition (τ_p_design > chromatic) 정량 식별.
- **Docs**: `README.md`, `Defense_summary.md`, `TUTORIAL.md`, `PROGRESS.md`,
  `Mussbah_reproduce_plan.md`, `Diagnosis.md`.

### 1.2 E4 completed status

- **E4 unified common-ground benchmark 완료**: K=50, M=200, N=8, 3 GHz, τ_c=150,
  τ_p_design=15, UMi, one-ring 30 m, random AP orientation.
- **All 9 schemes evaluated**: 200 setups × 20 channel samples, same Mussbah-style MC SE.
- **Bootstrap CI 완료**: `figures/bootstrap_ci_unified_E4.csv`.
- **3-environment plot 완료**: `figures/cross_paper_unified_3env.png`.
- **Actual τ_p diagnostic 완료**: `figures/cross_paper_unified_E4_tau_p_actual.png`.
- **Optional only**: Gao matching 의 beam-domain extension.

## 2. Unified environment spec — 권장 design

두 paper 의 *공통 ground* 정의. 권장 선택지 + tradeoff.

### Option A — *Both paper environments at N=8*

**가장 단순**. 두 paper 의 original setting 을 *각각 multi-antenna (N=8) 로 강제*.

```python
# Gao setting (modified: N=1 → N=8)
SimulationConfig(
    num_aps=500, num_ues=200, tau_p=20,
    bandwidth_hz=20e6, carrier_frequency_mhz=1900.0, tau_c=200,
    num_antennas_per_ap=8,                # ★ N=8 (modified from N=1)
    one_ring_radius_m=30.0,                # adopt Mussbah convention
    pathloss_model="ngo2017",              # keep Gao path loss
    ap_orientation="fixed",
)

# Mussbah setting (paper original)
SimulationConfig(
    num_aps=100, num_ues=30, tau_p=10,
    bandwidth_hz=20e6, carrier_frequency_mhz=5000.0, tau_c=100,
    num_antennas_per_ap=8,
    one_ring_radius_m=30.0,
    pathloss_model="umi3gpp",
    ue_height_m=1.5,
    ap_orientation="fixed",
)
```

- 장점: 우리 *현재 cross_paper_full_final 와 같은 setup* — *바로 결과 활용 가능*.
- 단점: *Gao paper original (N=1) 과 다름* — Gao reproduce 측면 *strict 하지 않음*.

### Option B — *Common ground environment* (가장 fair)

두 paper 의 *system model 의 union 또는 average*. 우리 새로 정의:

```python
SimulationConfig(
    num_aps=200, num_ues=50, tau_p=15,
    bandwidth_hz=20e6, carrier_frequency_mhz=3000.0, tau_c=150,
    num_antennas_per_ap=8,
    one_ring_radius_m=30.0,
    pathloss_model="umi3gpp",
    ue_height_m=1.5,
    ap_orientation="random",                # more realistic
)
```

- 장점: *truly common ground*, neither paper-original — *symmetric*.
- 단점: *neither paper 의 정량 reproduce 도 아님* — *우리 새 environment 의 algorithm 비교*.

### Option C — *Multi-environment matrix*

각 paper 의 original environment + common ground environment 모두 평가. 가장 thorough.

| Environment | Setting | Algorithms 평가 |
| --- | --- | --- |
| **E1: Gao paper original** | N=1, K=200, M=500, Ngo 2017, 1.9 GHz | Gao, Liu, Chen, Random, Upper + 우리 hybrid (TopAP bisect, H2). *Mussbah algorithm 평가 불가* |
| **E2: Mussbah paper original** | N=8, K=30, M=100, UMi 3GPP, 5 GHz, one-ring | 9 schemes 모두 |
| **E3: Multi-antenna Gao** | N=8, K=200, M=500, 1.9 GHz, one-ring | 9 schemes 모두 |
| **E4: Common ground** | N=4 or 8, K=50, M=200, 3 GHz, UMi | 9 schemes 모두 |

E1, E2 이미 완료. E3 이 `cross_paper_full_final.png`. **E4 도 완료**.

### 완료된 선택: **Option C (matrix)** 의 *E4 추가* + *E2/E3/E4 비교 plot*

이제 *defense narrative 정직성 + cross-paper fair benchmark* 를 동시에 확보했다.

### E4 headline result

| Scheme | P5 SE | Mean SE | Mean vs Random | Mean actual τ_p |
| --- | ---: | ---: | ---: | ---: |
| Random | 1.149 | 5.291 | 0.00% | 14.94 |
| Mussbah | 1.059 | 4.845 | -8.44% | 26.52 |
| Hybrid#3 | **1.234** | **5.572** | **+5.31%** | **7.90** |
| TopAP bisect | 1.159 | 5.295 | +0.08% | 14.91 |
| Hybrid#4 | 1.161 | 5.292 | +0.01% | 15.00 |

Bootstrap mean SE CI:

- Hybrid#3: 5.572 [5.515, 5.627]
- Random: 5.291 [5.237, 5.347]
- Mussbah: 4.845 [4.794, 4.898]

Conclusion: E4 common-ground 에서는 Hybrid#3 만 Random 대비 명확한 advantage. Mussbah 는
actual τ_p 평균 26.5 로 training overhead 손실이 커져 Random 보다 낮다.

## 3. 작업 phases (8-12 시간 estimate)

### Phase 1 (1-2 시간) — Unified environment 정의 + verification

1. `src/config.py` 검토 — Option B/C 의 새 environment 정의. Memory:

   ```python
   # E4 common ground
   UNIFIED_CONFIG_E4 = SimulationConfig(
       num_aps=200, num_ues=50, tau_p=15,
       bandwidth_hz=20e6, carrier_frequency_mhz=3000.0, tau_c=150,
       num_antennas_per_ap=8, one_ring_radius_m=30.0,
       pathloss_model="umi3gpp", ue_height_m=1.5,
       ap_orientation="random", random_seed=7,
   )
   ```

2. *Smoke test* — Network 생성 + 모든 9 algorithm 동작 verify:

   ```bash
   python -c "
   from src.config import SimulationConfig
   from src.network import Network
   from src.pilot_schemes import *
   import numpy as np

   config = SimulationConfig(
       num_aps=200, num_ues=50, tau_p=15,
       num_antennas_per_ap=8, one_ring_radius_m=30.0,
       pathloss_model='umi3gpp', carrier_frequency_mhz=3000.0,
       tau_c=150, ue_height_m=1.5, random_seed=7,
   )
   net = Network.random(config, np.random.default_rng(7))
   for cls_name in ['RandomPilotAssignment', 'MatchingBasedPilotAssignment',
                    'GraphColoringPilotAssignment', 'StructuredPilotAccessAssignment',
                    'BeamDomainPilotAssignment', 'TopAPGraphColoringPilotAssignment',
                    'HybridGaoColoringPilotAssignment', 'Hybrid4TopAPGreedyPilotAssignment']:
       cls = globals()[cls_name]
       # Mussbah needs adaptive_tau_p; TopAP best with adaptive
       if cls_name == 'BeamDomainPilotAssignment':
           scheme = cls(seed=0, delta=0.95, adaptive_tau_p=True)
       elif cls_name == 'TopAPGraphColoringPilotAssignment':
           scheme = cls(seed=0, top_n=8, adaptive_tau_p=True)
       else:
           scheme = cls(seed=0)
       pilots = scheme.assign(net, tau_p=15)
       print(f'{cls_name}: pilots range=[{pilots.min()}, {pilots.max()}], distinct={len(np.unique(pilots))}')
   "
   ```

   Expected: 모든 9 schemes 가 *오류 없이* pilots 출력. Mussbah chromatic ≈ K/3 정도 (K=50).

3. *Diagnostic* — `experiments/diagnose_algorithms.py` 의 새 환경에서 D1-D5 metric 확인.

### Phase 2 (completed) — Multi-antenna unified experiment script

새 script `experiments/cross_paper_unified_E4.py` (또는 `experiments/cross_paper_unified.py`)
— E4 environment 에서 paper-faithful MC SE (Mussbah Eq.3-9) 로 9 schemes 모두 평가.

Template (copy from `experiments/mussbah_fig1_full.py`):

```python
"""Multi-antenna unified cross-paper benchmark (E4 common ground environment).

E4 spec: K=50, M=200, N=8, carrier 3 GHz, τ_c=150, UMi, one-ring 30m.
Common-ground 환경 — neither Gao nor Mussbah paper original. Paper-faithful SE.
9 schemes all evaluated, 200 setups × 20 channel samples.
"""

# Copy mussbah_fig1_full.py의 main() structure, change SimulationConfig to E4.
# Same SCHEME_ORDER (9 schemes), same mussbah_uplink_se MC.
# Output: figures/cross_paper_unified_E4_summary.csv, _raw.csv, _cdf.png
```

완료 실행:

```bash
setsid python experiments/cross_paper_unified_E4.py --setups 200 --channel-samples 20 \
    --out-suffix _E4 > logs/unified_E4.log 2>&1 < /dev/null &
```

산출물: `figures/cross_paper_unified_E4_{summary,raw}_E4.csv`, `_cdf_E4.png`.

### Phase 3 (completed) — Bootstrap CI + comparison

```bash
python experiments/bootstrap_se_ci.py \
    --input cross_paper_unified_E4_raw_E4.csv \
    --out bootstrap_ci_unified_E4.csv
```

비교 table (E2 Mussbah + E3 multi-antenna Gao + E4 unified):

- Mussbah_reproduce_plan.md §11 의 E2 결과 reuse: `bootstrap_ci_mussbah_fig1_full_raw_200setups_umi.csv`.
- §20 의 E3 결과 reuse: `bootstrap_ci_cross_paper_full_gao_raw_final.csv`.
- 새 E4 결과: `bootstrap_ci_unified_E4.csv`.

Cross-environment table:

| Algorithm | E2 (Mussbah K=30) | E3 (multi-ant K=200) | E4 (unified K=50) |
| --- | --- | --- | --- |
| Random | ... | ... | ... |
| Mussbah | ... | ... | ... |
| Hybrid#3 | ... | ... | ... |
| TopAP bisect | ... | ... | ... |

### Phase 4 (completed) — Visualization + interpretation

생성된 figure: `figures/cross_paper_unified_3env.png` — 3 environments × 9 schemes comparison.
추가 diagnostic: `figures/cross_paper_unified_E4_tau_p_actual.png`.

Plot script template (copy from `experiments/plot_envelopes.py` or `cross_paper_full.py`):

```python
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, env, summary_path in [
    (axes[0], "E2 Mussbah K=30", "mussbah_fig1_full_summary_200setups_umi.csv"),
    (axes[1], "E3 Multi-ant K=200", "cross_paper_full_gao_summary_final.csv"),
    (axes[2], "E4 Unified K=50", "cross_paper_unified_E4_summary_E4.csv"),
]:
    # bar chart per scheme...
```

### Phase 5 (completed) — Documentation + defense narrative update

1. `Mussbah_reproduce_plan.md` §22 — Unified E4 결과 정량
2. `Defense_summary.md` 의 cross-paper section update — E4 결과 추가
3. `README.md` 의 cross-paper section update
4. `TUTORIAL.md` 의 §2, §3 의 cross-paper narrative update — optional polish

핵심 narrative:

> "우리 *paper-environment paper-faithful reproduce* (E1 Gao, E2 Mussbah) + *algorithm
> cross-transferability stress test* (E3 multi-ant Gao environment) + *unified common-
> ground environment* (E4) — 세 measurement axis 로 contribution 다각도 검증."

### Phase 6 (completed) — Final verification

- `python -m pytest -q tests/` → 21 passed
- `python -c "from src.pilot_schemes import *"` → no error
- `ls figures/cross_paper_unified_*` → expected files exist
- Memory update: `~/.claude/projects/.../memory/cross_paper_claim.md` 에 E4 결과 추가.

## 4. Optional advanced — Gao matching multi-antenna extension

(시간 남으면) Gao matching algorithm 의 *beam-domain extension*. 현재 Gao matching 은
*element-domain β_{m,k}* 사용. Multi-antenna environment 에서도 그대로 작동 but *beam-
domain 정보 미활용*. Mussbah 와 *fair head-to-head* 위해:

```python
class MatchingBasedPilotAssignmentMultiAntenna(MatchingBasedPilotAssignment):
    """Gao matching extended to beam-domain.

    Use per-beam β = beam_powers (K, M, N) instead of element-domain β.
    Top-τ_p UEs *per beam* (not per AP) for matching quota.
    """
    def match_users_to_aps(self, network, tau_p):
        # Flatten to (K, M*N) virtual APs
        virtual_network = network.beam_flattened()
        return super().match_users_to_aps(virtual_network, tau_p)
```

이게 *진정한 multi-antenna Gao* — beam-domain conflict 회피. 이게 우리 Hybrid#3 + Mussbah
와 *fair head-to-head* 가능.

Expected: 우리 Hybrid#3 (TopAP N=8 adaptive 가 multi-antenna 환경에서도 leading) 와 비교
시 Gao multi-antenna 가 *어느 정도 advantage 따라잡는지*.

## 5. Known pitfalls (next agent 가 피해야 할 함정)

1. **Mussbah algorithm 의 `adaptive_tau_p=True` 사용 확인** — `BeamDomainPilotAssignment(adaptive_tau_p=True)`. 안 그러면 *modulo wrap* 으로 advantage 사라짐.
2. **`mussbah_uplink_se` 의 `tau_p` parameter 처리** — `pilots.max() + 1` (현재 implementation) — adaptive τ_p 살림. 변경 시 *Random 만 spurious effect*.
3. **`one_ring_radius_m`** — Mussbah default 30 m. 다른 환경에서도 동일 사용 (channel covariance sparsity 의 source).
4. **`Network.beam_info` 의 `snr_threshold_db`** — default 0 dB (paper "SNR > 0" 의 literal). *환경 specific tuning* 필요 가능 (`Mussbah_reproduce_plan.md` §18 의 +6dB → chromatic 8 → paper-likely).
5. **Bootstrap CI 의 P5 high variance** — *mean SE* 가 statistical defense 에 더 robust.
6. **Cross-paper figure 의 fairness** — *환경 통일 강제 명시* 필요. *Gao paper original (N=1) 과 다름* 정직 표현.

## 6. Suggested file organization (output)

```
figures/
├── cross_paper_unified_E4_summary_E4.csv      # 새 결과
├── cross_paper_unified_E4_raw_E4.csv
├── cross_paper_unified_E4_cdf_E4.png
├── bootstrap_ci_unified_E4.csv
├── cross_paper_3env.png                       # 3-environment 비교
└── cross_paper_3env_advantage.png             # vs Random advantage

docs/
├── PROGRESS.md                                # E1 (Gao single-antenna)
├── Mussbah_reproduce_plan.md                  # E2, E3 + 새 §22 (E4)
├── Defense_summary.md                         # 3 environments narrative
└── README.md                                  # entry point updated
```

## 7. Time-budget summary (completed)

| Phase | Activity | Time |
| --- | --- | --- |
| 1 | Unified env config + smoke test | 1-2 h |
| 2 | New experiment script + 200×20 MC | 2-3 h (mostly wait) |
| 3 | Bootstrap CI on E4 + comparison | 1-2 h |
| 4 | Figure (3-env comparison) | 1-2 h |
| 5 | Docs update (5 markdown files) | 2-3 h |
| 6 | Tests + cleanup | 1 h |
| **Total** | | **8-12 h** |

## 8. Success criteria (defense-defendable result)

next agent 가 이 plan 완료 시:

- ✓ `figures/cross_paper_unified_3env.png` — 3 environments × 9 schemes 비교
- ✓ Bootstrap CI 로 Hybrid#3 의 *E4 unified env 우위* 및 Mussbah disadvantage 통계 확인
- ✓ Defense_summary.md 의 cross-paper section — *paper-faithful (E1 + E2) + unified (E4)* 두 정직한 narrative
- ✓ 모든 tests pass

이게 *true cross-paper defendable contribution*.

## 9. Quick reference — 핵심 file paths

- Config: `src/config.py`
- Network: `src/network.py` (beam_info, beam_flattened)
- SE module: `src/mussbah_se.py`
- Algorithms: `src/pilot_schemes/*.py`
- Existing experiments: `experiments/mussbah_fig1_full.py`, `cross_paper_full.py`
- Bootstrap CI: `experiments/bootstrap_se_ci.py`
- Plot envelopes: `experiments/plot_envelopes.py`
- Tests: `tests/`
- Logs (background runs): `logs/`

## 10. 시작 명령 한 줄

```bash
cd ~/03_Univ/KU/02_coursework/2026-1/이동통신시스템_신원재/proj_pilot
cat NEXT_STEPS_AGENT_PLAN.md   # 이 문서
python -m pytest -q tests/     # baseline 21 passed
# Phase 1 시작...
```

Good luck. *Honest assessment + bootstrap CI* 면 defense 안전.
