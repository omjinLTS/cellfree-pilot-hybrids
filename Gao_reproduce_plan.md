# Gao et al. (2024) Reproduce Plan

> **Paper**: Yuan Gao, Haonan Hu, Jiming Chen, Xiaoyong Wang, Xiaoli Chu, Jie Zhang,
> *"A Matching-Based Pilot Assignment Algorithm for Cell-Free Massive MIMO Networks"*,
> **IEEE Trans. Veh. Technol.**, vol. 73, no. 1, pp. 1453–1457, Jan. 2024.

---

## 1. Overview

### 1.1 논문 요지
Cell-free Massive MIMO 환경에서 발생하는 **pilot contamination** 을 완화하기 위해
**many-to-many matching** 기반의 pilot assignment 알고리즘을 제안. 핵심은:

1. **Algorithm 1** — UE와 AP 사이의 many-to-many matching 으로 UE-grouping 생성 (그룹 크기 ≤ τ_p)
2. **Algorithm 2** — 그룹별 **common-serving-AP ratio S** 의 내림차순으로 그룹 내 orthogonal pilot 할당

복잡도가 graph-coloring [14], structured access [15] 대비 훨씬 낮으면서도 95%-likely
per-UE throughput에서 우수한 성능을 보이는 것이 주장.

### 1.2 재현 목표 (task.md 1번 항목)
1. **Fig. 2** — Per UE throughput CDF (M=200, K=500, τ_p=20)
2. **Fig. 3** — 95%-likely per UE throughput vs pilot number τ_p (M=200, K=500)
3. **Fig. 4** — 95%-likely per UE throughput vs UE number M (K=500, τ_p=20)
4. 위 결과를 향후 **Mussbah et al. (beam-domain)** 결과와 한 그래프로 통합 비교

### 1.3 설계 원칙 — Model-Centric
- 향후 Mussbah(beam-domain) scheme 및 새로운 비교 기준이 plug-in 되도록 **추상 기반 클래스(ABC)** 로 인터페이스 통일
- Pilot scheme · Power control · Metric 을 모두 독립 모듈로 분리
- 새 metric/새 scheme 추가가 1개 파일 작성만으로 끝나도록 의존성 최소화

---

## 2. System Model (수식 정리)

### 2.1 환경
- K개의 single-antenna AP: $\mathcal{AP} = \{AP_1, \dots, AP_K\}$
- M개의 single-antenna UE: $\mathcal{UE} = \{UE_1, \dots, UE_M\}$ (M ≤ K)
- Uncorrelated Rayleigh fading: $h_{mk} \sim \mathcal{CN}(0, \beta_{mk})$
- TDD coherence block 길이 $\tau_c$, pilot 길이 $\tau_p$
- $\tau_p$ 개의 orthogonal pilots $\phi_1, \dots, \phi_{\tau_p} \in \mathbb{C}^{\tau_p}$,
  $\phi_{m_1}^H \phi_{m_2} = \mathbb{1}[m_1=m_2]$

### 2.2 Uplink Pilot 수신 (식 (1))
$$\mathbf{Y}_k = \sum_{m=1}^{M} \sqrt{\eta_m}\, h_{mk}\, \phi_m + \mathbf{n}_k,\quad \mathbf{n}_k \sim \mathcal{CN}(0, \sigma^2 \mathbf{I})$$

### 2.3 MMSE 채널 추정 (식 (2)–(4))
$$\hat{h}_{mk} = c_{mk}\left(\sqrt{\eta_m} h_{mk} + \sum_{m'\neq m}\sqrt{\eta_{m'}} h_{m'k}\phi_m^H\phi_{m'} + \phi_m^H \mathbf{n}_k\right)$$
$$c_{mk} = \frac{\sqrt{\eta_m}\,\beta_{mk}}{\sum_{m'=1}^{M} \eta_{m'}\beta_{m'k} |\phi_m^H \phi_{m'}|^2 + \sigma^2}$$
$$\gamma_{mk} = \frac{\eta_m \beta_{mk}^2}{\sum_{m'=1}^{M} \eta_{m'}\beta_{m'k} |\phi_m^H \phi_{m'}|^2 + \sigma^2}$$

### 2.4 Uplink Data + MR Decoding + Use-and-then-Forget (식 (5)–(7))
$$r_m = \sum_{k\in\xi_m} y_k \hat{h}_{mk}^*$$
$$\xi_m \triangleq \text{AP set serving } UE_m$$

### 2.5 SINR (식 (8))
$$SINR_m = \frac{p_m \left(\sum_{k\in\xi_m}\gamma_{mk}\right)^2}{\sum_{k\in\xi_m}\gamma_{mk}\sigma^2 + \sum_{k=1}^{K}\sum_{m'=1}^{M} p_{m'}\gamma_{mk}\beta_{m'k} + \sum_{m'\neq m}^{M} p_{m'}\left(\sum_{k=1}^{K}\gamma_{mk}\frac{\beta_{m'k}}{\beta_{mk}}\right)^2 |\phi_m^H \phi_{m'}|^2}$$

(분모 = 노이즈 + uplink 간섭 + pilot 오염)

### 2.6 Per-UE Throughput
$$R_m^{ul} = B\cdot \frac{1 - \tau_p/\tau_c}{2} \cdot \log_2(1 + SINR_m)$$

---

## 3. Algorithms

### 3.1 Algorithm 1 — Matching-Based UE-Grouping

**Input**: $\mathcal{UE}, \mathcal{AP}, \mathcal{PL}^{UE}, \mathcal{PL}^{AP}, Q_{UE}, Q_{AP}$
**Output**: User grouping $\mathcal{G}$

- $\mathcal{PL}_m^{UE}$: UE_m이 선호하는 AP 리스트 (β_mk 내림차순)
- $\mathcal{PL}_k^{AP}$: AP_k가 선호하는 UE 리스트 (β_mk 내림차순)
- $Q_{UE}$ : UE 하나가 매칭될 수 있는 AP 수 quota
- $Q_{AP} = \tau_p$ : AP 하나가 동시에 서빙할 수 있는 UE 수 quota

**Iteration**:
1. Free UE list $\mathcal{FUE} = \mathcal{UE}$, temporary matching table $\mu = \mathbf{0}^{M\times K}$
2. `while FUE != ∅`:
   - 각 free UE_i: 본인 PL에서 다음 후보 AP들 뽑아 proposing list $\mathcal{P}$ 형성, PL에서 제거
   - 각 AP_k: 본인이 받은 proposals와 기존 매칭의 합집합 크기가 $Q_{AP}$ 이하면 모두 수락, 아니면 PL 기준 상위 $Q_{AP}$명만 수락
   - 각 UE_m: $|\mu(m,:)| = Q_{UE}$ 이거나 PL이 비면 $\mathcal{FUE}$에서 제거
3. Output: $\mathcal{G}_k = \mu(:, k)$ (AP_k에 매칭된 UE 집합)

> 주의: AP가 받은 proposal 리스트의 합집합 크기에 *기존 매칭*도 포함된다는 점 (line 9의 $|\mathcal{P}_k + \mu(:,k)|$).

### 3.2 Algorithm 2 — Pilot Assignment

**Input**: $\mathcal{G}$, common-serving-AP ratio $\mathbf{S}$, total pilot list $\mathcal{TP}$
**Output**: pilot assignment $\mathcal{PA}$

**Common-serving-AP ratio (식 (9), (10))**:
$$M_{m_1 m_2} = \frac{|\mu(m_1,:) \cap \mu(m_2,:)|}{|\mu(m_1,:)|},\quad S_k = \sum_{m_1\neq m_2,\, m_1,m_2\in \mathcal{G}_k} M_{m_1 m_2}$$

**Assignment**:
1. 그룹을 $\mathbf{S}$ 내림차순으로 정렬 ($\tilde{\mathcal{G}}_k$)
2. `for k=1..K`:
   - Pilot occupancy $\mathcal{PO} = \emptyset$
   - 그룹 내 *이미 pilot 할당된 UE* 들의 pilot을 $\mathcal{PO}$ 에 추가
   - *아직 미할당된 UE* 들에 $\mathcal{TP} \setminus \mathcal{PO}$ 에서 랜덤 pilot 할당
3. Return $\mathcal{PA}$

---

## 4. Simulation Parameters

| 항목 | 값 | 비고 |
|---|---|---|
| Bandwidth B | 20 MHz | |
| Carrier frequency | 1.9 GHz | |
| AP height $h_{AP}$ | 10 m | |
| UE height $h_{UE}$ | 1.65 m | |
| UE Tx power $p_{\max}$ | 100 mW | pilot은 full power |
| Noise PSD | −174 dBm/Hz | |
| Coherence block $\tau_c$ | 200 | |
| AP serving quota $Q_{AP}$ | $\tau_p$ | |
| UE matching quota $Q_{UE}$ | unlimited | "the maximum number of APs to serve a UE is unlimited" |
| K (AP 수) | 500 (default) | |
| M (UE 수) | 100~200 (Fig.4 sweep) | |
| $\tau_p$ | 10~30 (Fig.3 sweep) | Fig.2/4 default = 20 |
| Path loss model | Ngo 2017 3-slope | Section 4.2 참조 |
| Simulation area | 1 km × 1 km wrap-around | 표준 cell-free 가정 |
| Monte Carlo realizations | 200~500 | 가속 결과 보고 조정 |

### 4.1 Throughput 공식
$$R_m^{ul} = B \cdot \frac{1 - \tau_p/\tau_c}{2} \cdot \log_2(1 + SINR_m)$$
(downlink와 uplink가 TDD에서 절반씩 차지하므로 인자 1/2)

### 4.2 Ngo 2017 [1] 3-slope Path Loss (with shadowing)
$$PL(d) = \begin{cases} -L - 35\log_{10}(d), & d > d_1 \\ -L - 15\log_{10}(d_1) - 20\log_{10}(d), & d_0 < d \leq d_1 \\ -L - 15\log_{10}(d_1) - 20\log_{10}(d_0), & d \leq d_0 \end{cases}$$
- $d_0 = 10$ m, $d_1 = 50$ m
- $L = 46.3 + 33.9\log_{10}(f) - 13.82\log_{10}(h_{AP}) - (1.1\log_{10}(f) - 0.7) h_{UE} + (1.56 \log_{10}(f) - 0.8)$
- Shadow fading: $z_{mk} \sim \mathcal{N}(0, \sigma_{sh}^2)$ , $\sigma_{sh} = 8$ dB
- $\beta_{mk} \, [\text{dB}] = PL(d_{mk}) + z_{mk}$

---

## 5. Repository / Module 구조

```
[proj]pilot/
├── Gao_reproduce_plan.md        # 본 문서
├── requirements.txt             # numpy, scipy, matplotlib, tqdm (필요 시 cvxpy)
├── src/
│   ├── __init__.py
│   ├── config.py                # SimulationConfig (dataclass)
│   ├── network.py               # Network 클래스 (AP/UE topology + β_mk)
│   ├── channel.py               # ChannelEstimator (MMSE γ_mk)
│   ├── power_control.py         # PowerControl ABC + FullPower / MaxMin
│   ├── pilot_schemes/
│   │   ├── __init__.py
│   │   ├── base.py              # PilotAssignmentScheme ABC
│   │   ├── random_scheme.py     # RandomPilotAssignment
│   │   ├── upper_bound.py       # UpperBoundPilotAssignment (orthogonal)
│   │   ├── matching_gao.py      # ★ Gao Algorithm 1 + 2
│   │   ├── graph_coloring.py    # Liu 2020 [14] Benchmark II
│   │   └── structured_access.py # Chen 2021 [15] Benchmark I
│   ├── metrics.py               # SINR, Throughput, 95%-likely, CDF
│   └── simulator.py             # Simulator (MC 루프, scheme×power×metric 매트릭스)
├── experiments/
│   ├── fig2_cdf.py
│   ├── fig3_vs_pilot_number.py
│   ├── fig4_vs_ue_number.py
│   └── (추후) fig_compare_papers.py
├── tests/
│   ├── test_algorithm1.py       # quota·termination 검증
│   ├── test_sinr.py             # 식 (8) 항별 sanity check
│   └── test_pathloss.py
└── figures/                     # 출력 PNG
```

### 5.1 핵심 추상화

```python
# pilot_schemes/base.py
from abc import ABC, abstractmethod
import numpy as np

class PilotAssignmentScheme(ABC):
    name: str

    @abstractmethod
    def assign(self, network: "Network", tau_p: int) -> np.ndarray:
        """Return pilot index array shape (M,), dtype=int, range [0, tau_p)."""
        ...
```

```python
# power_control.py
class PowerControl(ABC):
    @abstractmethod
    def compute(self, network: "Network", assignment: np.ndarray) -> np.ndarray:
        """Return per-UE transmit power, shape (M,), unit Watt."""
        ...
```

```python
# metrics.py
class Metric(ABC):
    @abstractmethod
    def evaluate(self, throughputs: np.ndarray) -> float | np.ndarray: ...
```

> Mussbah(beam-domain)는 `BeamDomainPilotAssignment(PilotAssignmentScheme)` 한 파일만 추가하면 통합 완료.

---

## 6. 구현 순서 (Phase별 To-Do)

### Phase A — 기반 구조 (1~2일)
- [x] `SimulationConfig` dataclass (모든 파라미터를 한 곳에)
- [x] `Network` 클래스
  - [x] 정사각형 영역(1km × 1km) AP/UE 균등 랜덤 분포
  - [x] Wrap-around distance 계산
  - [x] Ngo 3-slope path loss + log-normal shadow → β_mk (M, K) 행렬
- [x] `tests/test_pathloss.py` — d ↘0/d_0/d_1/d→∞ 경계 케이스

### Phase B — Pilot Assignment Schemes (3~4일)
- [x] `RandomPilotAssignment` (가장 간단, 디버깅 기준선)
- [x] `UpperBoundPilotAssignment` (orthogonal 가정으로 contamination 0)
- [x] `MatchingBasedPilotAssignment`  ★ 핵심
  - [x] Preference list 생성 (β 내림차순)
  - [x] Algorithm 1 main loop (Free UE proposal → AP acceptance → table update)
  - [x] Common-serving-AP ratio S 계산
  - [x] Algorithm 2 (S 내림차순 그룹 처리 → 그룹별 orthogonal pilot)
- [ ] `GraphColoringPilotAssignment` (Liu 2020 [14]) — 현재는 비교용 greedy heuristic scaffold
- [ ] `StructuredPilotAccessAssignment` (Chen 2021 [15]) — 현재는 strongest-AP grouping heuristic scaffold
- [x] `tests/test_algorithm1.py` — quota constraint·종료조건·간단한 toy case (M=3, K=3, τ_p=2)

### Phase C — Channel · Power · Metric (1~2일)
- [x] `ChannelEstimator`: γ_mk (M, K) 계산 (식 (4))
- [x] SINR closed-form 계산기 (식 (8)) — 각 항 분리 가능하도록 구현
- [x] `FullPowerControl` (p_m = p_max)
- [x] `MaxMinPowerControl` — bisection 또는 cvxpy SOCP 기반 (옵션, FullPower 검증 후)
- [x] `Metric`: per-UE throughput, 95%-likely, CDF array
- [x] `tests/test_sinr.py` — 노이즈만 / 한 UE만 / 직교 pilot 등 sanity case

### Phase D — Simulation & Figures (2~3일)
- [x] `Simulator.run(scheme, power, n_realizations) -> DataFrame`
- [x] **Fig. 2** (`experiments/fig2_cdf.py`): M=200, K=500, τ_p=20, CDF
- [x] **Fig. 3** (`experiments/fig3_vs_pilot_number.py`): τ_p ∈ {10, 15, 20, 25, 30}
- [x] **Fig. 4** (`experiments/fig4_vs_ue_number.py`): M ∈ {100, ..., 200}
- [x] Style 통일 (논문 축 범위 고정, fractional=solid / max-min=dotted)
- [ ] Wall-clock time profile → 필요 시 vectorization

> 2026-05-27 note: `--quick` 산출물은 smoke test 전용이다. 논문과 축/경향을 비교할 때는
> `--quick` 없이 실행해야 한다. 현재 Benchmark I/II는 paper-exact 구현이 아니라 heuristic
> scaffold 이므로, 최종 재현 figure로 사용하기 전에 Liu [14], Chen [15] 알고리즘을 정확히
> 구현해야 한다.

---

## 7. 검증 기준

### 7.1 정성적
- Fig. 2~4의 곡선 순서/경향이 논문과 일치:
  **Upper-bound > Proposed ≳ Benchmark I [15] > Benchmark II [14] ≳ Random**

### 7.2 정량적 (논문 Section IV.B)
- Full-power 시: Proposed가 Benchmark II 대비 **+15~23%** (τ_p=10일 때 최대)
- Max-min 시: Proposed가 Benchmark II 대비 **+18~23%**
- τ_p가 커질수록 모든 scheme 간 격차가 줄어드는 경향

### 7.3 단위 테스트
- Algorithm 1: 모든 그룹의 $|\mathcal{G}_k| \leq Q_{AP}$ 보장, 모든 UE가 최소 1개 AP에 매칭
- SINR: τ_p ≥ M 인 경우 pilot 오염 항이 0이 되는지
- Throughput: τ_p → τ_c 일 때 throughput → 0

---

## 8. Mussbah et al. 통합을 위한 확장 포인트 (작업 후 후속 단계)

- 새 파일 `src/pilot_schemes/beam_domain_mussbah.py` 추가
- `Network` 에 beam-domain 정보(예: angular spectrum, AoA 가정) stub 메서드 추가
- `experiments/fig_compare_papers.py` — Gao Proposed + Mussbah BeamDomain 동일 metric으로 한 그래프

> 이 단계는 Mussbah 논문 분석이 끝난 후 별도 turn에서 진행한다.

---

## 9. 위험 요소 / 미해결 이슈

| 항목 | 영향도 | 대응 |
|---|---|---|
| Benchmark I [15] 알고리즘 본문에 없음 | 중 | 원논문(Chen 2021) 직접 참조, 우선순위 ↓ |
| Max-min power control 세부 | 중 | [1] Ngo 2017 부록 참조, 우선 FullPower로 검증 |
| MC realization 횟수 vs wall-clock | 저 | NumPy vectorization, 필요 시 multiprocessing |
| Shadow fading correlation (UE 간) | 저 | Ngo 2017은 uncorrelated 가정 → 그대로 사용 |
| Q_UE 값 명시 부재 | 저 | "unlimited" → $Q_{UE} = K$ 로 설정 |

---

## 10. 다음 액션 (이 문서 승인 후)

1. `requirements.txt` 생성 → `pip install` 검증
2. **Phase A** 부터 순차 진행
3. 각 Phase 완료 시 단위 테스트 + 작은 sanity figure로 중간 검증
4. Phase D 종료 시 Fig.2~4 PNG 출력 후 논문과 시각적 대조
5. 이후 Mussbah 논문 분석 turn으로 이동
