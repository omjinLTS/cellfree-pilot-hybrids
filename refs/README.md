# Reference papers and implementations

본 디렉토리는 Gao et al. (2024) 재현 작업에서 참고한 외부 자료를 모아둔다.
모두 공개 자료(arXiv preprint 또는 저자 공개 GitHub 코드)이며 연구 목적 인용으로만 사용한다.

## 1. `ngo2017.pdf`

- **Paper**: H. Q. Ngo, A. Ashikhmin, H. Yang, E. G. Larsson, T. L. Marzetta,
  "Cell-Free Massive MIMO versus Small Cells", *IEEE Trans. Wireless Commun.*,
  vol. 16, no. 3, pp. 1834–1850, Mar. 2017.
- **Source**: arXiv:1602.08232 — https://arxiv.org/abs/1602.08232 (open access)
- **본 프로젝트에서의 용도**:
  - Cell-free Massive MIMO 시스템 모델 baseline
  - Uplink SINR closed-form (Eq. 27) — Gao Eq. (8) 의 origin
  - Max-min uplink power control 공식화 (Eq. 36, 37 — bisection on common SINR)
  - 우리 코드 매핑:
    - [src/metrics.py](../src/metrics.py) SINR 계산
    - [src/power_control.py](../src/power_control.py) `MaxMinPowerControl`

## 2. `liu2020/` — Benchmark II (Graph coloring)

- **Paper**: H. Liu, J. Zhang, S. Jin, B. Ai,
  "Graph coloring based pilot assignment for cell-free massive MIMO systems",
  *IEEE Trans. Veh. Technol.*, vol. 69, no. 8, pp. 9180–9184, Aug. 2020.
- **Source**: https://github.com/BJTU-MIMO/CF-Graph-Coloring-Pilot-Assignment
  (저자 공개 MATLAB code, `.git` 제거 후 보관)
- **핵심 파일**:
  - `simulation_main.m` — 시뮬레이션 진입점
  - `functiongraph.m` — θ-bisection wrapper
  - `functionAPSelection.m` — 누적 β 기준 AP 선택 (per-UE serving set)
  - `funcnumofcolor.m` — binary conflict graph 구성 + max-degree-first greedy coloring
  - `functioninterference.m` — conflict 판정 (공통 serving AP 1개 이상)
- **본 프로젝트에서의 용도**: Benchmark II 의 paper-faithful 구현 참조.
  Python 포팅: [src/pilot_schemes/graph_coloring.py](../src/pilot_schemes/graph_coloring.py)

## 3. `chen2021/` — Benchmark I (Structured access)

- **Paper**: S. Chen, J. Zhang, E. Björnson, J. Zhang, B. Ai,
  "Structured massive access for scalable cell-free massive MIMO systems",
  *IEEE J. Sel. Areas Commun.*, vol. 39, no. 4, pp. 1086–1100, Apr. 2021.
- **Source**: https://github.com/ShuaifeiChen273/structured_access_CFmMIMO
  (저자 Shuaifei Chen 공개 MATLAB code, `.git` 제거 후 보관)
- **핵심 파일**:
  - `simulationSE.m` — 시뮬레이션 진입점
  - `functionAPselection.m` — iterative AP selection with τ_p-quota eviction
  - `functionUEgroup.m` — δ-bisection 으로 conflict-graph independent set 형성
  - `functionPowerControl.m` — fractional power: `p_k = p_max·min(B^θ)/B_k^θ`
- **본 프로젝트에서의 용도**: Benchmark I 의 paper-faithful 구현 참조.
  Python 포팅: [src/pilot_schemes/structured_access.py](../src/pilot_schemes/structured_access.py)
  Power control: [src/power_control.py](../src/power_control.py) `FractionalPowerControl`

## 4. (프로젝트 루트의) Gao et al. 원문

루트 디렉토리에 PDF로 보관:
`Gao et al. - 2024 - A Matching-Based Pilot Assignment Algorithm for Cell-Free Massive MIMO Networks.pdf`

및 비교 대상 Mussbah et al.:
`Mussbah et al. - 2024 - Beam-Domain-Based Pilot Assignment for Energy Efficient Cell-Free Massive MIMO.pdf`

## 5. 라이선스 / 인용

- 각 GitHub repo 의 원본 LICENSE 파일은 그대로 포함 (`liu2020/LICENSE`, `chen2021/LICENSE`).
- 이 코드들을 Python 으로 재구현해 본 프로젝트에 사용했으며, 결과 보고 시 원논문을 인용해야 한다.
