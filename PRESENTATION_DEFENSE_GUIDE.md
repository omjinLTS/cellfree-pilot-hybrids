# Presentation Defense Guide

작성일: 2026-06-10

기준 파일:

- 제출본: `Beamer/main.pdf`  
- 슬라이드 소스 확인용: `Beamer/main.tex`
- 발표용 결과: `Final Figure/presentation_6method/`, `Final Figure/presentation_n_sweep_6method/`, `Final Figure/presentation_high_k_6method/`
- 구현 확인용: `MJH/all_schemes_ap_domain_hybrids_pilot_boxplot_env_fixed.py`

이 문서는 제출된 PDF를 수정하지 않고, 발표자가 내용을 이해하고 질의응답을 방어하기 위한 내부 가이드다. 숫자는 제출본에 들어간 figure directory와 CSV를 기준으로 정리했다.

---

## 1. 발표의 핵심 메시지

한 문장:

> Cell-free massive MIMO에서 pilot assignment는 pilot overhead를 줄이는 문제이면서, 동시에 pilot-sharing UE 사이의 AP/beam-domain interference 구조를 얼마나 보존하느냐의 trade-off 문제다.

조금 더 길게:

> Gao는 AP-domain matching으로 pilot contamination을 줄이려 하고, Mussbah는 beam-domain conflict graph로 더 세밀한 충돌을 잡는다. 우리는 이 둘을 합쳐 AP-beam resource 단위에서 matching하고, weighted beam-overlap으로 pilot reuse cost를 계산하는 Beam Resource Matching을 제안했다. 결과적으로 BRM은 moderate load에서 actual pilot count를 낮게 유지하면서 평균 SE와 EE를 개선했다.

발표에서 절대 중심에 둬야 할 말:

- 좋은 pilot assignment는 "pilot 수를 무조건 줄이는 것"이 아니다.
- SE에는 `prelog = (tau_c - tau_p) / tau_c`가 들어가므로 pilot 수가 줄면 data symbol 공간은 늘어난다.
- 하지만 pilot 수를 줄이다가 중요한 channel structure를 잃으면 SINR이 낮아질 수 있다.
- 따라서 핵심은 `pilot overhead 감소`와 `SINR-side 손실 억제` 사이의 균형이다.
- 제출본의 주력 결과는 Beam Resource Matching이고, AP-Top-N은 단순하지만 꽤 강한 practical baseline이다.

---

## 2. 발표에서 피해야 할 주장

아래 문장은 공격받기 쉽다. 말하지 않는 편이 낫다.

| 위험한 주장 | 왜 위험한가 | 대신 말할 표현 |
| --- | --- | --- |
| "Fewer pilots are always better." | pilot 수가 줄어도 SINR이 무너지면 SE가 떨어질 수 있다. | "Pilot-count reduction helps only when useful channel structure is preserved." |
| "Beam-domain methods always beat AP-domain methods." | Beam Weighted Threshold와 Mussbah는 load가 커지면 Random보다 낮아진다. | "Beam-domain information is more precise, but graph density must be controlled." |
| "Gao is useless." | main setting에서 Random과 붙지만, AP-domain reference로 의미가 있다. | "Gao is included as an AP-domain reference and is weakly differentiating in this evaluator." |
| "Mussbah is bad." | 특정 환경에서 dense graph가 되는 것이 문제다. 알고리즘 자체를 일반적으로 부정하면 안 된다. | "Mussbah shows the failure mode of an overly dense adaptive coloring graph." |
| "We proved SINR improvement." | 제출본에는 SINR/NMSE decomposition이 없다. | "The measured SE improvement is consistent with a better overhead/interference trade-off." |
| "EE is a full hardware energy model." | power model은 simplified/proxy 성격이다. | "EE is evaluated under the stated simulator power model." |
| "The comparison proves statistical significance." | 제출본 그래프에는 confidence interval이 없다. | "The trend is based on 200 Monte Carlo setups; we avoid formal significance wording here." |

---

## 3. 용어와 시스템 모델

### 3.1 Cell-free massive MIMO

Cell-free massive MIMO는 많은 분산 AP가 중앙 CPU coordination 아래 여러 UE를 공동 serving하는 구조다. 기존 cellular network처럼 cell boundary로 UE를 나누는 대신, 여러 AP가 UE 주변에서 협력한다.

장점:

- UE가 가까운 AP를 활용하므로 access distance가 줄어든다.
- macro-diversity가 생긴다.
- cell-edge 문제가 줄어든다.

문제:

- AP와 UE의 연결이 많아진다.
- 같은 pilot을 reuse하는 UE들이 같은 AP 또는 같은 beam을 공유하면 channel estimation이 섞인다.
- 이 현상이 pilot contamination이다.

### 3.2 Coherence block과 pilot overhead

TDD system에서는 coherence block 길이 `tau_c` 안에 uplink pilot과 data transmission이 함께 들어간다.

슬라이드의 핵심 식:

```text
SE_k = ((tau_c - tau_p) / tau_c) log2(1 + SINR_k)
```

의미:

- `tau_p`가 커지면 pilot contamination을 줄일 수 있는 여지가 생긴다.
- 하지만 `tau_p`가 커지면 data symbol에 쓸 수 있는 공간이 줄어든다.
- adaptive method가 `tau_p_actual`을 낮추면 prelog가 좋아진다.
- 하지만 같은 pilot을 너무 많이 reuse하면 SINR이 낮아질 수 있다.

발표용 표현:

> The pilot assignment problem is not only an interference problem. It is also an overhead allocation problem inside the coherence block.

---

## 4. 비교한 여섯 방법

| Method | Domain | Pilot count | 핵심 아이디어 | 발표에서의 역할 |
| --- | --- | --- | --- | --- |
| Random | 없음 | fixed `tau_p=15` | pilot index를 무작위 배정 | reference baseline |
| Gao Matching | AP-domain | fixed `tau_p=15` | UE-AP many-to-many matching, AP group risk 기반 pilot assignment | AP-domain reference |
| Mussbah Beam Graph | beam-domain | adaptive coloring | active/moderate beam overlap graph를 만들고 DSATUR coloring | dense graph failure case |
| AP-Top-N | AP-domain sparse graph | adaptive coloring | UE별 strongest AP Top-N이 겹치면 conflict edge | simple practical method |
| Beam Weighted Threshold | beam-domain graph | adaptive coloring | active-active overlap에 더 큰 weight를 주고 threshold로 edge 생성 | weighting만으로는 부족하다는 case |
| Beam Resource Matching | AP-beam resource | adaptive but bounded | UE와 AP-beam resource를 matching하고 weighted reuse cost로 pilot 배정 | main proposed method |

---

## 5. 방법별 설명

### 5.1 Gao AP-Domain Matching

Gao는 AP-domain large-scale fading `beta_{k,l}`를 기준으로 UE와 AP를 many-to-many matching한다.

핵심:

- UE는 좋은 AP를 선호한다.
- AP는 제한된 quota 안에서 UE를 받는다.
- AP별 group을 만들고, 같은 AP를 많이 공유하는 UE pair는 pilot reuse risk가 높다고 본다.

장점:

- AP-level large-scale fading만 있으면 된다.
- beam 정보가 없어도 동작한다.

한계:

- 같은 AP 안에서 두 UE가 서로 다른 beam을 쓰는 경우를 구분하지 못한다.
- 제출본 환경에서는 Gao와 Random의 평균 SE가 거의 붙는다.

공격 방어:

> Gao is not the main contribution here. It is the AP-domain reference axis. In this unified multi-antenna evaluator, its AP-domain matching does not change the serving and pilot-risk structure enough to create a large mean-SE separation from Random.

### 5.2 Mussbah Beam-Domain Graph

Mussbah는 AP antenna array의 beam-domain representation을 사용한다.

절차:

1. UE가 reported beam set을 가진다.
2. strongest beams가 active beam set이 된다.
3. 나머지 reported beams는 moderate set이 된다.
4. UE pair가 active-active, active-moderate, moderate-active beam overlap을 가지면 conflict edge를 둔다.
5. DSATUR coloring으로 pilot을 배정한다.

중요한 구분:

- 제출본 19페이지의 `Mussbah edge threshold = 0`은 edge를 자르지 않는다는 뜻이다.
- 이것은 active beam을 고르는 `95% power` 기준과 다르다.

한계:

- beam-domain conflict는 AP-domain보다 세밀하지만, graph가 너무 dense해질 수 있다.
- dense graph는 color 수를 키우고, actual pilot count를 크게 만든다.
- 제출본 high-K 결과에서는 Mussbah actual pilot count가 `tau_c=150`보다 커지는 구간이 생기며 SE가 거의 0으로 내려간다.

발표용 표현:

> Mussbah gives a finer interference signal, but the graph density must be controlled. Otherwise the adaptive coloring uses too many pilots and loses the prelog advantage.

### 5.3 AP-Top-N

UE별 strongest AP Top-N만 사용해서 conflict graph를 만든다.

절차:

1. UE `k`에 대해 strongest AP set `T_k(N_top)`을 구한다.
2. 두 UE의 Top-N AP set이 겹치면 conflict edge를 둔다.
3. sparse graph를 coloring한다.

왜 넣었나:

- beam 정보 없이 AP-domain pruning만으로도 어느 정도 graph sparsification이 가능하다는 비교점이다.
- 구현과 설명이 단순하다.
- moderate load에서 좋은 결과가 나온다.

주의:

- `N_top=8`은 제출본 세팅이다.
- 최적 `N_top`이라고 주장하지 않는다.

### 5.4 Beam Weighted Threshold

Mussbah식 beam graph를 그대로 쓰되, overlap type마다 weight를 다르게 둔다.

```text
W_uv = w_aa |A_u cap A_v| + w_ai |A_u cap I_v| + w_ia |I_u cap A_v|
```

제출본 세팅:

- `w_aa=2`, `w_ai=1`, `w_ia=1`
- `BWT edge threshold = 10`

의미:

- active-active overlap이 가장 강한 interference라고 보고 더 크게 본다.
- threshold로 weak conflict edge를 줄인다.

한계:

- 그래프를 weighted/thresholded해도 pilot count가 적절히 control되지 않으면 load에서 무너진다.
- K=50에서 평균 actual pilot count가 약 `17.06`으로 design `15`를 넘는다.

### 5.5 Beam Resource Matching

BRM은 이 발표의 핵심 방법이다.

핵심 차이:

- Gao: UE와 AP를 matching한다.
- BRM: UE와 AP-beam resource `r=(l,n)`을 matching한다.

왜 이게 중요한가:

> same AP does not mean same beam.

두 UE가 같은 AP를 공유해도 서로 다른 beam을 쓰면 conflict severity가 다를 수 있다. Gao의 AP-domain metric은 이 차이를 못 본다. BRM은 AP-beam resource level에서 active beam을 정한다.

절차:

1. 각 UE는 reported beam set `B_k`를 가진다.
2. reference active beam count는 Mussbah power-threshold rule에서 가져온다.
3. UE가 beam power가 큰 AP-beam resource에 proposal한다.
4. 각 resource는 quota `Q_res` 안에서 UE를 받는다.
5. matching 결과가 active beam set `A_k`가 된다.
6. unmatched reported beams는 moderate set `I_k`가 된다.
7. weighted beam-overlap ratio로 resource group risk와 pilot reuse cost를 계산한다.
8. resource group을 risk 순서로 처리하고, pilot reuse cost가 작은 pilot을 배정한다.

`Q_res = tau_p_design`의 의미:

- 각 AP-beam resource에 너무 많은 UE가 몰리지 않도록 한다.
- BRM actual pilot count는 `max_r |G_r|`로 잡히고, matching quota 때문에 design budget 안에 묶인다.

발표용 표현:

> BRM keeps the beam-domain resolution of Mussbah, but avoids unbounded graph coloring by moving the control point to resource matching.

---

## 6. 제출본 슬라이드별 발표 가이드

### Page 1. Title

목표:

- 연구 주제를 "cell-free massive MIMO pilot assignment"로 잡는다.
- subtitle의 `Beam-Domain Resource Matching with Weighted Pilot Reuse`가 방법의 본질이다.

말할 것:

> We focus on pilot assignment in cell-free massive MIMO, especially the trade-off between reducing pilot overhead and avoiding pilot contamination.

### Page 2. Cell-Free Massive MIMO

목표:

- 청중이 cell-free 구조를 몰라도 따라오게 만든다.

말할 것:

- 여러 AP가 cell boundary 없이 UE를 공동 serving한다.
- 장점은 coverage, macro-diversity, cell-edge reduction이다.
- 단점은 AP-UE link가 많아져 pilot reuse conflict가 복잡해진다는 점이다.

공격 포인트:

- "왜 cell-free에서 pilot이 더 문제인가?"

답:

> Because many APs jointly observe many UEs. This improves macro-diversity, but it also increases the chance that pilot-sharing UEs overlap in AP or beam domain.

### Page 3. The Pilot Problem

목표:

- pilot contamination과 prelog trade-off를 연결한다.

말할 것:

- `tau_p` pilot symbols 후 나머지 `tau_c - tau_p`가 data symbol이다.
- 같은 pilot을 쓰는 UE들이 MMSE channel estimate 안에서 섞인다.
- SE는 SINR뿐 아니라 pilot overhead에도 영향을 받는다.

공격 포인트:

- "pilot을 줄이면 channel estimation quality도 나빠지는 것 아닌가?"

답:

> Yes, that is exactly why this is a trade-off. Our simulation evaluates the final SE after pilot assignment, including the actual pilot count in the channel-estimation and prelog pipeline. We do not claim that simply reducing pilots is always beneficial.

### Page 4. Prior Approaches and Gap

목표:

- Gao와 Mussbah를 두 축으로 세운다.

말할 것:

- Gao는 AP-domain matching이다.
- Mussbah는 beam-domain graph coloring이다.
- 우리는 AP-domain matching의 구조와 beam-domain resolution을 합친다.

공격 포인트:

- "그럼 그냥 Mussbah 쓰면 되지 않나?"

답:

> Mussbah captures beam-domain conflicts, but its graph can become dense. Our motivation is to keep beam-domain resolution while controlling pilot overhead through resource matching.

### Page 5. Core Design Concept

목표:

- 발표 전체를 한 장으로 설명한다.

말할 것:

- Gao에서 many-to-many matching을 가져온다.
- Mussbah에서 active/moderate beam structure를 가져온다.
- BRM은 AP가 아니라 AP-beam resource `(l,n)`에 대해 matching한다.

핵심 문장:

> The key replacement is UE-AP matching to UE-AP-beam-resource matching.

### Page 6. Mussbah Beam-Domain Method

목표:

- Mussbah가 왜 세밀하고, 왜 overhead 문제가 생기는지 설명한다.

주의:

- `tau_p_actual = chi(G)`는 엄밀히 말하면 graph coloring 결과로 사용한 color count를 의미한다.
- 구현은 DSATUR coloring을 사용한다.
- 완전한 minimum chromatic number를 항상 증명했다고 말하면 안 된다.

공격 포인트:

- "DSATUR가 exact chromatic number를 구하나?"

답:

> In implementation, the actual pilot count is the number of colors produced by DSATUR. The slide uses chi(G) as graph-coloring notation, but the defensible statement is the DSATUR color count used by the assignment.

### Page 7. DSATUR Coloring

목표:

- graph coloring이 pilot assignment로 어떻게 연결되는지 설명한다.

말할 것:

- vertex는 UE다.
- edge는 같은 pilot을 쓰면 위험한 UE pair다.
- color는 pilot index다.
- 인접한 UE들은 다른 color를 받도록 한다.

공격 포인트:

- "color 수가 늘면 왜 나쁜가?"

답:

> More colors mean more actual pilots. Since SE has the prelog factor `(tau_c - tau_p)/tau_c`, too many colors directly reduce data transmission time.

### Page 8. Beam Weighted Threshold

목표:

- 동료 아이디어의 핵심을 professional하게 설명한다.

말할 것:

- active-active overlap은 더 강한 conflict로 본다.
- active-moderate, moderate-active는 secondary conflict로 본다.
- threshold `theta`로 weak edge를 줄인다.

공격 포인트:

- "왜 weights가 `(2,1,1)`인가?"

답:

> It is a simple weighting choice to emphasize active-active overlap while keeping secondary overlap terms. We treat it as a controlled design setting, not as an optimized universal parameter.

### Page 9. Gao AP-Domain Matching

목표:

- Gao를 AP-domain reference로 설명한다.

말할 것:

- Gao는 AP-level large-scale fading으로 matching한다.
- AP group 안에서 pilot assignment risk를 계산한다.
- 한계는 same AP 안의 beam direction을 구분하지 못한다는 점이다.

주의:

- 슬라이드 footer에는 2023으로 보일 수 있고 reference page에는 2024로 정리되어 있다. 질문이 나오면 논문 식별자는 `IEEE TVT 73(1):1453-1457`로 답하고, 연도 논쟁은 길게 끌지 않는다.

### Page 10. AP-Top-N Method

목표:

- 단순한 AP-domain sparsification baseline을 설명한다.

말할 것:

- UE마다 strongest AP Top-N만 본다.
- Top-N set이 겹치면 conflict로 본다.
- 정보 요구량이 적고 구현이 쉽다.

공격 포인트:

- "왜 N=8인가?"

답:

> In the submitted experiments, `N_top=8` is the fixed comparison setting. It is not claimed to be globally optimal. It was chosen as a simple, interpretable sparsification level and kept fixed for comparison.

### Pages 11-18. Beam Resource Matching

핵심 흐름:

1. resource를 AP-beam pair `r=(l,n)`로 정의한다.
2. UE-resource matching을 수행한다.
3. matching result가 active beam set을 정의한다.
4. resource group `G_r` 안에서 risk를 계산한다.
5. weighted beam-overlap ratio로 pilot reuse cost를 계산한다.
6. pilot count는 largest resource group size로 잡히며 `Q_res=tau_p_design`에 의해 bounded된다.

공격 포인트:

- "BRM이 Gao와 정확히 뭐가 다른가?"

답:

> Gao matches UEs to APs and measures common AP overlap. BRM matches UEs to AP-beam resources and measures weighted active/moderate beam overlap. So the conflict signal changes from AP-level to AP-beam-level.

공격 포인트:

- "BRM이 Mussbah와 정확히 뭐가 다른가?"

답:

> Mussbah first builds a UE conflict graph from beam overlap and lets graph coloring decide the pilot count. BRM first controls UE concentration at each AP-beam resource through matching, then assigns pilots using weighted beam-overlap cost. That is why BRM can bound the actual pilot count by the resource quota.

공격 포인트:

- "왜 active beam을 per-UE power ranking이 아니라 matching으로 정하나?"

답:

> Per-UE power ranking ignores global competition. Matching makes each active beam survive both UE preference and resource-side capacity, so active beams reflect network-level resource competition.

### Page 19. Simulation Setup

제출본 표에 있는 값:

- `L=200`
- `tau_c=150`
- `tau_p_design=15`
- Monte Carlo setups: `200`
- carrier: `3 GHz`
- power control: full power
- active-beam target: `95% power`
- beam-overlap weights: `(2,1,1)`
- low-K sweep: `K=25-50`, `N=8`
- N-sweep: `N=1-8`, `K=50`
- high-K sweep: `K=50-300`, `N=8`
- eCDF snapshot: `K=50`, `N=8`
- AP-Top-N: `N_top=8`
- BWT edge threshold: `10`
- Mussbah edge threshold: `0`
- BRM resource quota: `Q_res=tau_p_design`

주의:

- 제출본 표에는 `beam_detect_snr_db`가 적혀 있지 않다.
- `presentation_n_sweep_6method`와 `presentation_high_k_6method` README에는 `beam_detect_snr_db=0.0`가 적혀 있다.
- `presentation_6method` README에는 이 값이 명시되어 있지 않고, 구현 기본값은 `0.0`이다.
- 질문이 나오면 "submitted slide does not list it; the code default and later sweep READMEs use 0 dB"라고 답하는 것이 안전하다.

### Page 20. eCDF of Throughput

목표:

- 평균만 보지 않고 UE throughput distribution을 본다는 점을 보여준다.

말할 것:

- eCDF는 전체 UE throughput 분포를 보여준다.
- left tail이 낮으면 unlucky UE 또는 cell-edge-like UE가 손해를 본다.
- BRM/AP-Top-N은 평균뿐 아니라 lower-tail 쪽에서도 개선이 보인다.

주의:

- "95% likely throughput"은 5th percentile 성격으로 설명한다.

### Pages 21-22. N-sweep

목표:

- AP antenna count가 변해도 ranking이 완전히 우연은 아니라는 점을 보여준다.

N=8 기준 수치:

| Method | Mean SE vs Random | P5 vs Random | EE vs Random | mean `tau_p_actual` |
| --- | ---: | ---: | ---: | ---: |
| Gao Matching | `-0.07%` | `-0.15%` | `-0.07%` | `15.00` |
| AP-Top-N | `+5.25%` | `+5.13%` | `+5.19%` | `7.86` |
| Beam Weighted Threshold | `-2.14%` | `-2.72%` | `+3.02%` | `17.13` |
| Beam Resource Matching | `+6.57%` | `+5.55%` | `+12.01%` | `5.39` |
| Mussbah Beam Graph | `-22.97%` | `-22.93%` | `-18.64%` | `45.41` |

해석:

- BRM은 N=8에서 가장 강한 평균 SE/EE를 보인다.
- AP-Top-N도 단순성 대비 좋은 성능이다.
- Mussbah와 BWT는 graph density와 pilot count가 문제다.

### Pages 23-24. Low-K K-sweep

목표:

- user 수가 25에서 50까지 늘어나는 moderate-load 구간에서 성능을 보여준다.

K=50 기준 수치:

| Method | Mean SE vs Random | P5 vs Random | EE vs Random | mean `tau_p_actual` |
| --- | ---: | ---: | ---: | ---: |
| Gao Matching | `-0.02%` | `+0.43%` | `-0.02%` | `15.00` |
| Mussbah Beam Graph | `-23.24%` | `-22.26%` | `-18.75%` | `45.76` |
| AP-Top-N | `+5.35%` | `+6.32%` | `+5.29%` | `7.79` |
| Beam Weighted Threshold | `-2.09%` | `-1.29%` | `+3.30%` | `17.06` |
| Beam Resource Matching | `+6.66%` | `+7.07%` | `+12.35%` | `5.29` |

발표용 핵심:

> BRM keeps the actual pilot count low, around 5.3 at K=50, while improving mean SE and EE. This supports the overhead-aware design idea.

### Page 25. Low-K vs High-K

목표:

- method가 모든 load에서 같은 방식으로 동작하지 않는다는 점을 보여준다.

말할 것:

- low-K에서는 BRM과 AP-Top-N이 뚜렷하게 좋다.
- high-K에서는 load가 커져서 sparse/adaptive graph의 한계가 나타난다.
- 이 페이지는 "무조건 좋아진다"가 아니라 operating range를 보여주는 페이지다.

### Pages 26-27. High-K sweep

목표:

- K가 300까지 커질 때의 stress test를 보여준다.

핵심 수치:

| K | Gao SE vs Random | AP-Top-N SE vs Random | BWT SE vs Random | BRM SE vs Random |
| ---: | ---: | ---: | ---: | ---: |
| 50 | `-0.04%` | `+5.28%` | `-2.05%` | `+6.62%` |
| 100 | `-0.04%` | `+1.81%` | `-11.87%` | `+4.44%` |
| 150 | `-0.01%` | `-1.50%` | `-20.75%` | `+2.65%` |
| 200 | `+0.00%` | `-4.62%` | `-29.45%` | `+1.05%` |
| 250 | `+0.04%` | `-7.34%` | `-38.12%` | `-0.16%` |
| 300 | `+0.07%` | `-10.41%` | `-46.43%` | `-0.72%` |

Mussbah high-K actual pilot count:

| K | Mussbah mean `tau_p_actual` | 해석 |
| ---: | ---: | --- |
| 50 | `45.61` | already high |
| 100 | `86.47` | prelog loss large |
| 150 | `124.84` | almost fills coherence block |
| 200 | `160.71` | exceeds `tau_c=150`, SE nearly zero |
| 250 | `195.40` | collapse |
| 300 | `229.13` | collapse |

말할 것:

> High-K is a stress test. It shows that adaptive pilot assignment has an operating range. BRM remains useful up to around K=200, then the load becomes too high for this simple resource quota rule.

공격 포인트:

- "K=250부터 BRM도 Random보다 낮아지는데 이 방법이 좋은가?"

답:

> The result shows an operating range, not a universal dominance claim. BRM is useful under moderate and moderately high load, but under very high load we need stronger resource control, power control, or joint optimization.

### Page 28. Performance Mechanism

목표:

- 결과를 mechanism으로 정리한다.

세 가지:

1. same AP is not same beam.
2. active beams are selected through global matching.
3. conflict severity is weighted.

말할 것:

> The gain comes from moving from AP-level conflict to AP-beam-level conflict, and from controlling resource concentration before pilot assignment.

### Page 29. Conclusion

목표:

- 과장 없이 마무리한다.

말할 것:

- BRM은 Gao의 UE-AP matching을 AP-beam resource level로 확장했다.
- weighted beam-domain overlap으로 pilot reuse cost를 계산했다.
- moderate load에서 SE/EE가 좋아졌다.
- future work는 mobility, joint matching/pilot/power control이다.

주의:

- "existing methods보다 항상 좋다"라고 말하지 않는다.
- "simulation results show improved..."라고 하면 바로 high-K 반례가 있다. 질문이 오면 "in the main moderate-load and N-sweep settings"로 범위를 좁힌다.

---

## 7. 결과 해석의 핵심 논리

### 7.1 왜 BRM이 좋은가

BRM은 두 가지를 동시에 한다.

1. AP-beam resource matching으로 중요한 beam-domain structure를 유지한다.
2. `Q_res=tau_p_design`으로 resource group size를 제한해 actual pilot count를 낮게 유지한다.

K=50 main result:

- Random mean SE: `3.5257`
- BRM mean SE: `3.7607`
- gain: `+6.66%`
- Random mean `tau_p`: `15.00`
- BRM mean `tau_p`: `5.29`

즉 BRM은 pilot overhead를 크게 낮추면서도 channel structure 손실이 SE gain을 다 잡아먹지 않았다.

### 7.2 왜 AP-Top-N도 좋게 나왔나

AP-Top-N은 단순하지만 conflict graph를 sparse하게 만든다. 강한 AP만 남기면 weak AP overlap 때문에 생기는 불필요한 conflict edge가 줄어든다.

K=50 main result:

- AP-Top-N mean SE gain: `+5.35%`
- AP-Top-N mean `tau_p`: `7.79`

발표에서 AP-Top-N은 "간단한 practical method"로 설명하면 된다. 단, BRM의 main novelty와 섞어 말하면 안 된다.

### 7.3 왜 Beam Weighted Threshold는 애매한가

BWT는 active-active overlap을 더 크게 보는 방향은 타당하다. 하지만 coloring 결과 actual pilot count가 올라가면 prelog 손실이 커진다.

K=50:

- mean SE: `-2.09%` vs Random
- EE: `+3.30%` vs Random
- mean `tau_p`: `17.06`

해석:

- RF/energy 쪽 이점은 일부 보일 수 있다.
- 하지만 SE 관점에서는 pilot count control이 부족하다.
- 따라서 BWT는 main winner가 아니라 "weighted conflict alone is insufficient"라는 lesson으로 쓴다.

### 7.4 왜 Mussbah가 낮게 나왔나

Mussbah는 beam-domain graph가 너무 dense해져 color count가 커진다. K=50에서 mean actual pilot count가 `45.76`이다. `tau_c=150`일 때 prelog가 Random보다 많이 낮아진다.

Random prelog:

```text
(150 - 15) / 150 = 0.900
```

Mussbah K=50 approximate prelog:

```text
(150 - 45.76) / 150 = 0.695
```

prelog만으로도 큰 손실이다. 이 때문에 beam-domain precision이 SE gain으로 이어지지 않는다.

### 7.5 왜 Gao와 Random이 거의 붙나

제출본 main setting에서는 Gao AP-domain matching이 Random 대비 serving/pilot-risk structure를 크게 바꾸지 못한다. 결과적으로 평균 SE와 EE가 거의 같다.

K=50:

- Gao mean SE: `-0.02%` vs Random
- Gao P5: `+0.43%` vs Random
- `tau_p=15.00`

발표에서 말할 것:

> Gao is a reference AP-domain matching method. In this unified evaluator, it is weakly differentiating, which actually motivates going to AP-beam-level resource matching.

---

## 8. 예상 질문과 모범답안

### Q1. "이 발표의 contribution이 정확히 뭔가요?"

짧은 답:

> Gao의 AP-domain matching을 AP-beam resource domain으로 확장하고, Mussbah의 active/moderate beam structure를 weighted pilot reuse cost에 결합한 BRM을 제안한 것입니다.

긴 답:

> Prior work gives two useful axes: Gao uses many-to-many matching but only at the AP domain, while Mussbah uses beam-domain graph coloring but can create dense graphs. Our contribution is to match users to AP-beam resources first, define active beams from this matching outcome, and then assign pilots using weighted beam-domain overlap. This changes the conflict signal and controls pilot count through the resource quota.

### Q2. "Gao와 무엇이 다르죠?"

답:

> Gao treats APs as the matching resources. BRM treats each AP-beam pair `(l,n)` as a resource. Therefore, two UEs sharing the same AP are not automatically treated as equally conflicting; the method can distinguish whether they overlap in beam domain.

### Q3. "Mussbah와 무엇이 다르죠?"

답:

> Mussbah builds a UE conflict graph directly from active/moderate beam overlap and then uses graph coloring. BRM first controls UE concentration through AP-beam resource matching. The pilot assignment then uses weighted overlap cost, and the pilot count is bounded by the resource quota.

### Q4. "왜 beam-domain이 AP-domain보다 더 좋은가요?"

답:

> AP-domain only tells us that two UEs share an AP. Beam-domain also tells us whether they occupy similar spatial directions at that AP. That is a finer interference descriptor. However, beam-domain information by itself is not enough; if it creates a dense graph, pilot overhead can dominate.

### Q5. "그럼 beam-domain method가 항상 더 좋나요?"

답:

> No. The results show the opposite: beam-domain information is useful only when graph density and pilot count are controlled. Mussbah and Beam Weighted Threshold can lose when the actual pilot count grows too much.

### Q6. "왜 pilot 수가 적으면 성능이 좋아지나요?"

답:

> SE includes the prelog factor `(tau_c - tau_p)/tau_c`. Fewer pilots leave more coherence-block symbols for data. But this helps only if the SINR-side damage from stronger pilot reuse is not too large.

### Q7. "pilot 수를 줄이면 channel estimation이 안 좋아지지 않나요?"

답:

> Yes, that is part of the trade-off. In the simulator, the actual pilot count enters the channel-estimation and SE calculation. We are not claiming that fewer pilots alone are beneficial. The result is about finding a useful balance.

### Q8. "Mussbah edge threshold 0이 active beam threshold 0이라는 뜻인가요?"

답:

> No. The active-beam target is 95% cumulative power. The Mussbah edge threshold 0 means that once an active/moderate beam overlap exists, the graph edge is kept. These are different thresholds.

### Q9. "Beam detection SNR은 얼마인가요?"

답:

> The submitted setup slide does not list beam-detection SNR. The implementation default is 0 dB, and the N-sweep/high-K README files record `beam_detect_snr_db=0.0`. For the main six-method plot, the saved README does not explicitly list that parameter, so I would not over-emphasize it unless asked.

### Q10. "DSATUR가 chromatic number를 정확히 구하나요?"

답:

> The implementation uses DSATUR coloring and the actual pilot count is the number of colors used by that coloring. The slide uses graph-coloring notation, but the defensible implementation statement is DSATUR color count, not a proof of minimum chromatic number.

### Q11. "왜 Gao가 Random이랑 거의 같나요? 코드가 잘못된 것 아닌가요?"

답:

> In this unified evaluator, Gao is an AP-domain reference and its resource constraint is not strong enough to substantially change the serving/pilot-risk structure. So the mean SE stays very close to Random. This is not used as a positive claim; it motivates the move to AP-beam-level matching.

### Q12. "Gao original은 single-antenna 논문 아닌가요? 여기서는 N=8인데 fair한가요?"

답:

> Correct. The submitted comparison is a unified multi-antenna evaluator where Gao is transplanted as an AP-domain matching reference. It is not a claim that Gao's original single-antenna paper setting is reproduced on this slide. The role of Gao here is to represent AP-domain matching under the same simulator.

### Q13. "Mussbah가 논문에서는 좋다는데 왜 여기서는 낮나요?"

답:

> In this setting, the beam-overlap graph becomes dense and the DSATUR color count becomes large. That increases actual pilot overhead. So the finer beam-domain conflict signal is offset by prelog loss.

### Q14. "Mussbah actual pilot count가 tau_c보다 커지면 물리적으로 말이 되나요?"

답:

> It indicates a failure mode of unconstrained adaptive coloring under high load. In the SE calculation, once `tau_p_actual` exceeds `tau_c`, the prelog becomes zero or nearly zero, so the method collapses. The point of showing it is to demonstrate why pilot-count control is necessary.

### Q15. "왜 BRM은 tau_p가 design budget 안에 있나요?"

답:

> BRM sets resource quota `Q_res=tau_p_design`. Since the actual pilot count is the largest resource group size, the matching quota bounds the pilot count by the design budget.

### Q16. "Q_res=tau_p_design은 임의적인 선택 아닌가요?"

답:

> It is a simple design choice aligned with the baseline pilot budget. The point is to use the same pilot budget as a resource-side quota. Optimizing `Q_res` is a natural future-work direction.

### Q17. "AP-Top-N은 왜 N=8인가요?"

답:

> It is the fixed submitted setting for a simple AP-domain sparsification rule. We do not claim N=8 is globally optimal. A sensitivity sweep over `N_top` would be future work.

### Q18. "BWT threshold 10은 어떻게 정했나요?"

답:

> It is a controlled design setting to suppress weak weighted beam-overlap edges. It should be viewed as a parameter choice, not an analytically optimized threshold.

### Q19. "Energy efficiency가 정확히 뭘 의미하나요?"

답:

> It is the simulator's EE metric under the stated power model, including transmit/circuit/RF-related terms. It is useful for relative comparison under the same model, but it should not be sold as a complete hardware-calibrated energy model.

### Q20. "왜 full power control만 썼나요?"

답:

> The submitted comparison sets power control to full power to isolate the pilot-assignment effect. Joint power control could change the operating point and is listed as future work.

### Q21. "confidence interval이 없는데 유의미하다고 할 수 있나요?"

답:

> The slides show Monte Carlo averages over 200 setups. We can discuss observed trends, but we should avoid formal statistical-significance claims unless CI or multi-seed tests are added.

### Q22. "BRM이 high-K에서 K=250부터 Random보다 낮아지는데 결론이 약한 것 아닌가요?"

답:

> It is an operating-range result. BRM improves moderate and moderately high load, but very high load requires stronger resource control or joint optimization. This limitation is valuable because it shows the boundary of the current design.

### Q23. "왜 high-K plot에 Mussbah를 넣었나요? 축을 망치지 않나요?"

답:

> Including Mussbah makes the failure mode visible: the graph coloring pilot count grows very large. If the question is about comparing the remaining methods, the no-Mussbah replotted figures exist in the result directory, but the submitted deck keeps Mussbah to show the pilot-count collapse.

### Q24. "SE gain이 prelog 때문인지 SINR 때문인지 분리했나요?"

답:

> The submitted deck does not include a SINR decomposition. The interpretation is that BRM improves the overhead/interference trade-off. We should not claim direct SINR improvement without an additional SINR or NMSE diagnostic.

### Q25. "eCDF에서 무엇을 봐야 하나요?"

답:

> eCDF shows the distribution across UE throughput. The lower-left part corresponds to weaker users. A rightward shift means better throughput distribution, and the 5th percentile or 95% likely throughput summarizes lower-tail behavior.

### Q26. "왜 Random을 baseline으로 쓰나요?"

답:

> Random provides the structure-free reference. If a method cannot beat Random under the same simulator, its added channel-structure logic is not helpful in that setting.

### Q27. "Gao paper reproduction이 완벽한가요?"

답:

> This slide deck is not a Gao reproduction talk. Gao is used as an AP-domain reference method under a unified evaluator. I would avoid claiming full paper reproduction in this presentation.

### Q28. "Mussbah paper reproduction이 완벽한가요?"

답:

> This slide deck uses Mussbah's beam-domain graph idea as a reference method. The submitted result focuses on unified comparison and BRM, not on exact reproduction of every closed-form detail in the Mussbah paper.

### Q29. "왜 conclusion에 'existing methods보다 improved'라고 되어 있는데 high-K에서는 아닌가요?"

답:

> The statement should be interpreted for the main moderate-load and N-sweep settings shown in the deck. The high-K sweep shows the limitation and operating range, not universal dominance.

### Q30. "이 방법이 실제 시스템에 바로 적용 가능한가요?"

답:

> It requires beam-domain information and centralized coordination, so it is most natural for a CPU-coordinated cell-free architecture. Practical deployment would require overhead analysis for beam reporting, mobility, and update periodicity.

### Q31. "beam reporting overhead는 고려했나요?"

답:

> Not explicitly in the submitted result. The simulation focuses on pilot assignment and SE/EE under the stated model. Beam reporting overhead is a practical extension.

### Q32. "mobility가 있으면 dominant beam이 바뀌는데요?"

답:

> Correct. The conclusion lists mobility and time-varying dominant beams as future work. BRM would need update scheduling or robust matching under beam changes.

### Q33. "BRM complexity는 어떤가요?"

답:

> It is more complex than AP-Top-N because it performs UE-resource matching and weighted pilot assignment over AP-beam resources. The submitted deck prioritizes performance mechanism; complexity analysis is future work.

### Q34. "왜 AP-Top-N이 BRM과 비슷하게 좋은데 더 복잡한 BRM이 필요한가요?"

답:

> AP-Top-N is attractive because it is simple and strong under moderate load. BRM is the richer method because it uses beam-domain resource competition and gives the best mean SE/EE in the submitted main settings. A practical system might choose between them depending on available beam information and complexity budget.

### Q35. "이 발표의 가장 약한 부분은 무엇인가요?"

답:

> The weakest parts are missing confidence intervals in the final deck, no explicit SINR/NMSE decomposition, and parameter sensitivity for `N_top`, edge threshold, and `Q_res`. The safest conclusion is therefore not a universal optimality claim, but an observed overhead-aware design direction.

---

## 9. 공격받을 때의 운영 원칙

1. 범위를 좁혀 답한다.
   - "in the submitted unified evaluator"
   - "under the stated simulation setting"
   - "in the moderate-load regime"

2. "항상 좋다"는 표현을 피한다.
   - high-K에서 반례가 있다.

3. Gao와 Mussbah를 깎아내리지 않는다.
   - Gao: AP-domain reference.
   - Mussbah: beam-domain conflict graph reference.

4. BRM도 과장하지 않는다.
   - moderate load에서 강하다.
   - very high K에서는 한계가 보인다.

5. 그래프가 공격받으면 mechanism으로 돌아간다.
   - pilot count
   - prelog
   - beam-domain resolution
   - resource quota

6. 모르면 모른다고 답한다.
   - "That is not included in the submitted experiments."
   - "We did not include that decomposition in the current deck."
   - "That is a good future-work direction."

---

## 10. 30초 요약 스크립트

> In cell-free massive MIMO, dense AP-UE connectivity improves coverage but makes pilot reuse difficult. Existing approaches look at either AP-domain matching or beam-domain graph coloring. We combine these ideas by matching users to AP-beam resources and assigning pilots using weighted beam-domain overlap. The key lesson is that pilot assignment must balance SINR-side interference and pilot overhead. In the submitted simulations, Beam Resource Matching improves mean SE and EE under moderate load by keeping actual pilot count low while preserving useful beam-domain structure. Under very high user load, the result also shows the limitation: pilot-count control becomes even more important.

---

## 11. 2분 결과 설명 스크립트

> The main simulation uses 200 APs, coherence block length 150, design pilot budget 15, and 200 Monte Carlo setups. We compare six methods: Random, Gao Matching, Mussbah Beam Graph, AP-Top-N, Beam Weighted Threshold, and Beam Resource Matching.
>
> At K=50 in the main K-sweep, Beam Resource Matching improves mean SE by about 6.66% and EE by about 12.35% over Random, while reducing the average actual pilot count from 15 to about 5.29. AP-Top-N is also strong, with about 5.35% mean SE gain and actual pilot count around 7.79.
>
> The important contrast is Mussbah and Beam Weighted Threshold. Mussbah uses a very fine beam-domain graph, but the graph becomes dense and uses about 45.76 pilots at K=50, which heavily reduces the prelog factor. Beam Weighted Threshold reduces weak edges, but its pilot count still grows above the design budget. This shows that beam-domain conflict information is valuable only if pilot overhead is controlled.
>
> The high-K sweep is a stress test. BRM remains useful up to around K=200, but crosses below Random at heavier load. So the conclusion is not that BRM is universally best. The conclusion is that AP/beam pruning and resource matching must balance channel-structure preservation against pilot-count reduction.

---

## 12. Evidence Map

Use these files if asked where a number came from.

| Claim | Evidence |
| --- | --- |
| Submitted deck has 30 pages and setup slide | `Beamer/main.pdf`, `Beamer/main.tex` |
| Main K=25-50 six-method result | `Final Figure/presentation_6method/presentation_mjh_6method_k_sweep.csv` |
| Main K=50 p5 throughput | `Final Figure/presentation_6method/presentation_latest_6method_p5_throughput_vs_k.csv` |
| N-sweep result | `Final Figure/presentation_n_sweep_6method/n_sweep_6method_summary.csv` |
| High-K result | `Final Figure/presentation_high_k_6method/high_k_6method_summary.csv` |
| High-K without Mussbah replotted backup | `Final Figure/presentation_high_k_6method_no_mussbah/high_k_5method_summary.csv` |
| Simulation settings for figures | each `Final Figure/*/README.md` |
| `tau_p` used in channel estimation and SE prelog | `MJH/all_schemes_ap_domain_hybrids_pilot_boxplot_env_fixed.py` |
