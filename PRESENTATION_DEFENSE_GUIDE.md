# 발표 및 질의응답 방어 가이드

작성일: 2026-06-10

기준 파일:

- 제출본: `Beamer/main.pdf`  
- 슬라이드 소스 확인용: `Beamer/main.tex`
- 발표용 결과: `Final Figure/presentation_6method/`, `Final Figure/presentation_n_sweep_6method/`, `Final Figure/presentation_high_k_6method/`
- 구현 확인용: `MJH/all_schemes_ap_domain_hybrids_pilot_boxplot_env_fixed.py`

이 문서는 제출된 PDF를 수정하지 않고, 발표자가 내용을 이해하고 질의응답을 방어하기 위한 내부 가이드다. 숫자는 제출본에 들어간 figure directory와 CSV를 기준으로 정리했다.

---

## 0. 언어 운영 원칙

슬라이드는 영어지만 발표와 질의응답은 한국어로 한다. 따라서 발표 중에는 슬라이드의 영어 용어를 그대로 가리키고, 해석과 방어는 한국어로 말하는 것이 가장 자연스럽다.

권장 방식:

- 방법 이름은 영어 그대로 말한다: `Gao Matching`, `Mussbah Beam Graph`, `AP-Top-N`, `Beam Weighted Threshold`, `Beam Resource Matching`.
- 수식 용어도 그대로 말한다: `prelog factor`, `actual pilot count`, `resource quota`, `beam-domain overlap`.
- 설명 문장은 한국어로 말한다.
- 질문을 받으면 영어 슬라이드를 다시 읽지 말고, "이 슬라이드의 의미는..."으로 한국어 해석을 바로 제시한다.

좋은 말투:

> "여기서 핵심은 pilot 수를 줄이는 것 자체가 아니라, pilot 수를 줄였을 때 생기는 prelog 이득이 SINR 손실보다 큰지 보는 것입니다."

피해야 할 말투:

> "This means..."처럼 영어 답변으로 전환하지 않는다. 청중이 한국어 Q&A를 기대하면 오히려 방어력이 떨어진다.

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
| "Fewer pilots are always better." | pilot 수가 줄어도 SINR이 무너지면 SE가 떨어질 수 있다. | "pilot 수 감소는 useful channel structure가 보존될 때만 이득이 됩니다." |
| "Beam-domain methods always beat AP-domain methods." | Beam Weighted Threshold와 Mussbah는 load가 커지면 Random보다 낮아진다. | "beam-domain 정보는 더 정밀하지만 graph density를 제어해야 합니다." |
| "Gao is useless." | main setting에서 Random과 붙지만, AP-domain reference로 의미가 있다. | "Gao는 AP-domain reference이고, 이 evaluator에서는 Random과 크게 분리되지 않는다." |
| "Mussbah is bad." | 특정 환경에서 dense graph가 되는 것이 문제다. 알고리즘 자체를 일반적으로 부정하면 안 된다. | "Mussbah는 graph가 과도하게 dense해질 때 adaptive coloring이 어떤 한계를 갖는지 보여주는 사례입니다." |
| "We proved SINR improvement." | 제출본에는 SINR/NMSE decomposition이 없다. | "측정된 SE 개선은 overhead와 interference trade-off가 좋아진 결과로 해석할 수 있습니다." |
| "EE is a full hardware energy model." | power model은 simplified/proxy 성격이다. | "EE는 명시한 simulator power model 안에서의 상대 비교 지표입니다." |
| "The comparison proves statistical significance." | 제출본 그래프에는 confidence interval이 없다. | "200 Monte Carlo setup 평균의 trend로 설명하고, formal significance claim은 피하겠습니다." |

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

> pilot assignment는 interference만 줄이는 문제가 아니라, coherence block 안에서 pilot과 data symbol을 어떻게 나눌지 정하는 overhead allocation 문제이기도 합니다.

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

> Gao는 여기서 main contribution이 아니라 AP-domain reference 축입니다. 이 unified multi-antenna evaluator에서는 Gao의 AP-domain matching이 serving structure나 pilot-risk structure를 크게 바꾸지 못해서 Random과 평균 SE가 크게 벌어지지 않습니다.

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

> Mussbah는 더 세밀한 interference signal을 주지만, graph density가 제어되지 않으면 adaptive coloring이 pilot을 너무 많이 사용해서 prelog 이득을 잃게 됩니다.

### 5.3 AP-Top-N

UE별 strongest AP Top-N만 사용해서 conflict graph를 만든다.

절차:

1. UE `k`에 대해 strongest AP set `T_k(N_top)`을 구한다.
2. 두 UE의 Top-N AP set이 겹치면 conflict edge를 둔다.
3. sparse graph를 max-degree-first greedy coloring한다.
4. 사용된 color 수가 `tau_p_actual`이 된다.

왜 넣었나:

- beam 정보 없이 AP-domain pruning만으로도 어느 정도 graph sparsification이 가능하다는 비교점이다.
- 구현과 설명이 단순하다.
- moderate load에서 좋은 결과가 나온다.
- BRM보다 정보 요구량과 구현 복잡도가 낮다.

주의:

- `N_top=8`은 제출본 세팅이다.
- 최적 `N_top`이라고 주장하지 않는다.
- `N_top`이 adaptive한 것이 아니라, `tau_p_actual`이 coloring 결과로 adaptive하게 나온다.
- 구현상 serving/active AP mask는 AP-domain baseline과 같은 convention을 쓰고, Top-N graph는 pilot conflict graph를 만드는 데 사용한다.

### 5.3.1 AP-Top-N 발표자용 집중 정리

네가 AP-Top-N 질문을 답할 때 가장 먼저 잡아야 하는 포인트는 이거다.

> AP-Top-N은 beam 정보 없이 AP-domain large-scale fading만으로 conflict graph를 sparse하게 만드는 방법입니다. 모든 AP overlap을 conflict로 보지 않고, UE별 strongest AP Top-N이 겹치는 경우만 중요한 pilot conflict로 봅니다.

알고리즘을 말로 풀면:

1. 각 UE `k`에 대해 large-scale fading `beta_{k,l}`이 큰 AP를 `N_top`개 고른다.
2. 두 UE의 Top-N AP set이 하나라도 겹치면 둘 사이에 conflict edge를 둔다.
3. 이 sparse conflict graph를 greedy coloring한다.
4. 같은 conflict edge로 연결된 UE들은 서로 다른 pilot을 받는다.
5. greedy coloring에서 실제로 사용된 color 수가 `tau_p_actual`이 된다.

수식으로는 슬라이드 그대로:

```text
T_k(N_top) = Top_Ntop { beta_{k,1}, ..., beta_{k,L} }
A_ij = 1{ T_i(N_top) cap T_j(N_top) != empty }
```

구현 기준:

- 제출본 method label: `AP-Top-N (N=8)`
- 내부 scheme 이름: `H3TopAPAdaptive`
- 사용 정보: `stats.beta_large_scale`
- Top-N conflict graph: `topn_overlap_conflict(...)`
- coloring: `quota_free_greedy_color(...)`
- `tau_p_actual = number of used colors`

Gao와의 차이:

- Gao는 UE와 AP를 many-to-many matching하고 AP group risk를 계산한다.
- AP-Top-N은 matching을 하지 않는다.
- AP-Top-N은 "강한 AP가 겹치는가?"만 보고 sparse graph를 만든다.
- 그래서 Gao보다 단순하고, AP-domain pruning 효과가 직접적으로 나타난다.

Mussbah/BRM과의 차이:

- Mussbah/BRM은 beam-domain 정보를 사용한다.
- AP-Top-N은 beam-domain 정보가 없어도 된다.
- 따라서 AP-Top-N은 rich한 beam-level method라기보다, low-information practical method다.

왜 성능이 나왔는가:

- 모든 AP overlap을 conflict로 보면 graph가 불필요하게 dense해진다.
- 특히 weak AP overlap까지 conflict로 보면 pilot reuse가 지나치게 보수적이 된다.
- Top-N은 dominant AP overlap만 남겨 graph를 sparse하게 만든다.
- 그 결과 moderate load에서 `tau_p_actual`이 줄고 prelog 이득이 생긴다.
- 동시에 strongest AP overlap은 유지하므로 SINR-side 손실이 너무 커지지 않았다.

제출본에서 네가 외워둘 숫자:

| Setting | AP-Top-N result |
| --- | --- |
| Main K-sweep, `K=50` | mean SE `+5.35%` vs Random, P5 `+6.32%`, EE `+5.29%`, mean `tau_p_actual=7.79` |
| N-sweep, `N=8`, `K=50` | mean SE `+5.25%`, P5 `+5.13%`, EE `+5.19%`, mean `tau_p_actual=7.86` |
| High-K, `K=50` | mean SE `+5.28%`, mean `tau_p_actual=7.85` |
| High-K, `K=100` | mean SE `+1.81%`, mean `tau_p_actual=12.52` |
| High-K, `K=150` | mean SE `-1.50%`, mean `tau_p_actual=17.04` |

해석:

- AP-Top-N은 moderate load에서는 굉장히 설득력 있다.
- 하지만 high load에서 `tau_p_actual`이 design budget 15를 넘기 시작하면 성능이 Random 아래로 내려간다.
- 따라서 "AP-Top-N이 항상 좋다"가 아니라, "단순한 AP-domain sparsification만으로도 moderate load에서는 큰 이득이 가능하지만, high load에서는 pilot-count control이 더 필요하다"가 안전한 결론이다.

발표장에서 한 문장으로:

> AP-Top-N은 beam 정보 없이 strongest AP overlap만 conflict로 보는 sparse graph 방식입니다. 모든 AP overlap을 다 보지 않아서 pilot count를 줄일 수 있고, moderate load에서는 이 prelog 이득이 SINR 손실보다 커서 좋은 결과가 나왔습니다.

두 문장 버전:

> AP-Top-N은 Gao처럼 AP-domain 정보를 쓰지만, many-to-many matching까지 가지 않고 UE별 strongest AP Top-N이 겹치는지만 봅니다. 그래서 구현은 단순하지만 graph가 충분히 sparse해져서 K=50 기준 Random 대비 평균 SE가 약 5.35% 좋아졌고, actual pilot count도 약 7.79로 줄었습니다.

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

> 같은 AP를 공유한다는 것이 같은 beam을 공유한다는 뜻은 아닙니다.

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

> BRM은 Mussbah의 beam-domain resolution은 유지하되, 제어 지점을 graph coloring이 아니라 resource matching으로 옮겨 pilot count가 과도하게 커지는 문제를 줄입니다.

---

## 6. 제출본 슬라이드별 발표 가이드

### Page 1. Title

목표:

- 연구 주제를 "cell-free massive MIMO pilot assignment"로 잡는다.
- subtitle의 `Beam-Domain Resource Matching with Weighted Pilot Reuse`가 방법의 본질이다.

말할 것:

> 저희는 cell-free massive MIMO에서 pilot assignment 문제를 다룹니다. 특히 pilot overhead를 줄이는 것과 pilot contamination을 피하는 것 사이의 trade-off에 초점을 맞췄습니다.

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

> 많은 AP가 여러 UE를 동시에 관측하고 serving하기 때문입니다. 이 구조는 macro-diversity를 높이지만, 같은 pilot을 쓰는 UE들이 AP나 beam domain에서 겹칠 가능성도 같이 키웁니다.

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

> 맞습니다. 그래서 이게 trade-off입니다. 저희 simulation은 pilot assignment 이후의 final SE를 보고, actual pilot count가 channel estimation과 prelog에 들어가도록 계산합니다. 단순히 pilot 수를 줄이면 좋다고 주장하는 것은 아닙니다.

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

> Mussbah는 beam-domain conflict를 잘 잡지만 graph가 dense해질 수 있습니다. 저희의 motivation은 beam-domain resolution은 유지하면서 resource matching으로 pilot overhead를 제어하는 것입니다.

### Page 5. Core Design Concept

목표:

- 발표 전체를 한 장으로 설명한다.

말할 것:

- Gao에서 many-to-many matching을 가져온다.
- Mussbah에서 active/moderate beam structure를 가져온다.
- BRM은 AP가 아니라 AP-beam resource `(l,n)`에 대해 matching한다.

핵심 문장:

> 핵심 변화는 UE-AP matching을 UE-AP-beam-resource matching으로 바꾼 것입니다.

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

> 구현에서는 actual pilot count를 DSATUR가 사용한 color 수로 봅니다. 슬라이드의 `chi(G)`는 graph-coloring notation이지만, 엄밀하게 말하면 DSATUR color count라고 설명하는 것이 안전합니다.

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

> color 수가 많다는 것은 actual pilot 수가 많다는 뜻입니다. SE에는 `(tau_c - tau_p)/tau_c` prelog가 들어가므로, color 수가 너무 많으면 data transmission time이 직접 줄어듭니다.

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

> active-active overlap을 더 크게 보되 secondary overlap도 유지하기 위한 단순한 weighting choice입니다. 최적화된 universal parameter가 아니라, 실험에서 고정한 design setting으로 보는 것이 맞습니다.

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

> 제출본 실험에서는 `N_top=8`을 고정 비교 세팅으로 사용했습니다. 전역 최적값이라고 주장하는 것은 아니고, 해석이 쉬운 sparsification level로 고정해 비교한 것입니다.

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

> Gao는 UE를 AP에 matching하고 common AP overlap을 봅니다. BRM은 UE를 AP-beam resource에 matching하고 weighted active/moderate beam overlap을 봅니다. 그래서 conflict signal이 AP-level에서 AP-beam-level로 바뀝니다.

공격 포인트:

- "BRM이 Mussbah와 정확히 뭐가 다른가?"

답:

> Mussbah는 beam overlap으로 UE conflict graph를 먼저 만들고 graph coloring이 pilot count를 결정합니다. BRM은 먼저 AP-beam resource마다 UE concentration을 matching으로 제어하고, 그 다음 weighted beam-overlap cost로 pilot을 배정합니다. 그래서 BRM은 resource quota를 통해 actual pilot count를 제한할 수 있습니다.

공격 포인트:

- "왜 active beam을 per-UE power ranking이 아니라 matching으로 정하나?"

답:

> Per-UE power ranking은 global competition을 보지 못합니다. Matching을 쓰면 active beam이 UE preference와 resource-side capacity를 모두 통과해야 하므로, active beam set이 network-level resource competition을 반영하게 됩니다.

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

> K=50에서 BRM은 actual pilot count를 약 5.3으로 낮게 유지하면서 평균 SE와 EE를 개선합니다. 이 결과가 overhead-aware design idea를 뒷받침합니다.

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

> High-K는 stress test입니다. Adaptive pilot assignment에도 operating range가 있다는 것을 보여줍니다. BRM은 대략 K=200까지는 유효하지만, 그 이후에는 현재의 단순 resource quota rule만으로는 load가 너무 커집니다.

공격 포인트:

- "K=250부터 BRM도 Random보다 낮아지는데 이 방법이 좋은가?"

답:

> 이 결과는 universal dominance가 아니라 operating range를 보여줍니다. BRM은 moderate load와 moderately high load에서는 유효하지만, very high load에서는 더 강한 resource control이나 power control, joint optimization이 필요합니다.

### Page 28. Performance Mechanism

목표:

- 결과를 mechanism으로 정리한다.

세 가지:

1. same AP is not same beam.
2. active beams are selected through global matching.
3. conflict severity is weighted.

말할 것:

> 이득은 conflict를 AP-level이 아니라 AP-beam-level로 본 것, 그리고 pilot assignment 전에 resource concentration을 먼저 제어한 것에서 나옵니다.

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

> Gao는 AP-domain matching reference입니다. 이 unified evaluator에서는 Random과 크게 분리되지 않았고, 오히려 그 점이 AP-beam-level resource matching으로 가야 하는 동기가 됩니다.

---

## 8. 예상 질문과 모범답안

### Q1. "이 발표의 contribution이 정확히 뭔가요?"

짧은 답:

> Gao의 AP-domain matching을 AP-beam resource domain으로 확장하고, Mussbah의 active/moderate beam structure를 weighted pilot reuse cost에 결합한 BRM을 제안한 것입니다.

긴 답:

> 기존 연구에서 Gao는 many-to-many matching을 쓰지만 AP-domain까지만 보고, Mussbah는 beam-domain graph coloring을 쓰지만 graph가 dense해지면 pilot 수가 커지는 문제가 있습니다. 저희는 UE를 AP-beam resource에 먼저 matching하고, 그 matching 결과로 active beam을 정의한 다음 weighted beam-domain overlap으로 pilot reuse cost를 계산했습니다. 그래서 conflict를 보는 단위를 AP에서 AP-beam resource로 바꿨고, resource quota로 pilot count도 제어했습니다.

### Q2. "Gao와 무엇이 다르죠?"

답:

> Gao는 AP 자체를 matching resource로 봅니다. 반면 BRM은 AP-beam pair, 즉 `(l,n)`을 하나의 resource로 봅니다. 그래서 두 UE가 같은 AP를 공유하더라도 같은 beam을 쓰는지, 서로 다른 beam을 쓰는지를 구분할 수 있습니다. 이게 Gao와 가장 큰 차이입니다.

### Q3. "Mussbah와 무엇이 다르죠?"

답:

> Mussbah는 active/moderate beam overlap으로 UE conflict graph를 바로 만들고 graph coloring으로 pilot을 배정합니다. BRM은 그 전에 AP-beam resource matching으로 한 resource에 UE가 과하게 몰리는 것을 먼저 제어합니다. 그 다음 weighted overlap cost로 pilot을 배정하고, resource quota 때문에 actual pilot count가 design budget 안에 묶입니다.

### Q4. "왜 beam-domain이 AP-domain보다 더 좋은가요?"

답:

> AP-domain은 두 UE가 같은 AP를 공유한다는 정보까지만 줍니다. 그런데 같은 AP를 공유해도 beam 방향이 다르면 실제 충돌 정도가 다를 수 있습니다. Beam-domain은 그 방향성까지 보므로 더 세밀한 interference descriptor입니다. 다만 beam-domain 정보만 쓴다고 항상 좋은 것은 아니고, graph가 너무 dense해지면 pilot overhead가 커져서 오히려 손해가 날 수 있습니다.

### Q5. "그럼 beam-domain method가 항상 더 좋나요?"

답:

> 아닙니다. 제출본 결과도 오히려 그 반례를 보여줍니다. Beam-domain 정보는 더 정밀하지만, graph density와 actual pilot count가 제어될 때만 이득이 됩니다. Mussbah나 Beam Weighted Threshold는 pilot count가 커지면서 Random보다 낮아지는 구간이 있습니다.

### Q6. "왜 pilot 수가 적으면 성능이 좋아지나요?"

답:

> SE 식에 `(tau_c - tau_p)/tau_c`라는 prelog factor가 들어갑니다. pilot 수가 줄면 coherence block 안에서 data 전송에 쓸 수 있는 symbol 수가 늘어납니다. 다만 같은 pilot을 더 많이 reuse하면서 SINR 손실이 커질 수 있기 때문에, pilot 수를 줄이는 것만으로 항상 좋아진다고 말하면 안 됩니다.

### Q7. "pilot 수를 줄이면 channel estimation이 안 좋아지지 않나요?"

답:

> 맞습니다. 그래서 이 문제가 trade-off입니다. simulator에서는 actual pilot count가 channel estimation과 SE 계산에 들어갑니다. 저희 주장은 pilot 수를 무조건 줄이면 좋다는 것이 아니라, pilot overhead 감소와 SINR 손실 사이에서 좋은 균형점을 찾는 것이 중요하다는 것입니다.

### Q8. "Mussbah edge threshold 0이 active beam threshold 0이라는 뜻인가요?"

답:

> 아닙니다. active beam을 고르는 기준은 `95% cumulative power`입니다. `Mussbah edge threshold = 0`은 active/moderate beam overlap이 하나라도 있으면 graph edge를 유지한다는 뜻입니다. active beam selection threshold와 edge threshold는 다른 값입니다.

### Q9. "Beam detection SNR은 얼마인가요?"

답:

> 제출본 setup slide에는 beam detection SNR을 따로 적지 않았습니다. 구현 기본값은 0 dB이고, N-sweep과 high-K 결과 README에는 `beam_detect_snr_db=0.0`로 기록되어 있습니다. 다만 main six-method plot의 README에는 그 값이 명시되어 있지 않아서, 질문이 나왔을 때만 "코드 기본값과 후속 sweep 기록 기준으로 0 dB"라고 답하는 게 안전합니다.

### Q10. "DSATUR가 chromatic number를 정확히 구하나요?"

답:

> 구현에서는 DSATUR coloring을 사용했고, actual pilot count는 그 coloring 결과 사용된 color 수입니다. 슬라이드에서는 graph coloring notation으로 `chi(G)`를 썼지만, 엄밀하게 방어 가능한 표현은 "DSATUR color count"입니다. minimum chromatic number를 항상 정확히 구했다고 주장하지 않는 것이 맞습니다.

### Q11. "왜 Gao가 Random이랑 거의 같나요? 코드가 잘못된 것 아닌가요?"

답:

> 이 unified evaluator에서는 Gao를 AP-domain reference로 넣었습니다. 이 세팅에서는 Gao의 resource constraint가 serving structure나 pilot-risk structure를 크게 바꿀 만큼 강하게 걸리지 않아서 평균 SE가 Random과 거의 붙습니다. 이걸 Gao가 좋다는 주장으로 쓰는 게 아니라, AP-domain만으로는 구분력이 약하므로 AP-beam-level matching이 필요하다는 동기로 사용했습니다.

### Q12. "Gao original은 single-antenna 논문 아닌가요? 여기서는 N=8인데 fair한가요?"

답:

> 맞습니다. Gao original은 single-antenna 기반입니다. 제출본에서는 Gao를 original reproduction으로 주장하는 것이 아니라, multi-antenna unified evaluator 안에서 AP-domain matching reference로 가져온 것입니다. 즉 Gao paper setting을 그대로 재현했다는 주장이 아니라, 같은 simulator 안에서 AP-domain 기준점을 둔 것입니다.

### Q13. "Mussbah가 논문에서는 좋다는데 왜 여기서는 낮나요?"

답:

> 이 세팅에서는 beam-overlap graph가 너무 dense해지고 DSATUR color count가 커집니다. 그 결과 actual pilot count가 커져서 prelog 손실이 크게 발생합니다. 즉 beam-domain conflict signal은 더 정밀하지만, pilot overhead가 너무 커져서 이득이 상쇄된 것입니다.

### Q14. "Mussbah actual pilot count가 tau_c보다 커지면 물리적으로 말이 되나요?"

답:

> 그건 high load에서 unconstrained adaptive coloring이 실패하는 상황을 보여주는 것입니다. SE 계산에서는 `tau_p_actual`이 `tau_c`를 넘으면 prelog가 0 또는 거의 0이 되기 때문에 성능이 collapse합니다. 이 결과는 Mussbah를 비난하려는 게 아니라, pilot-count control이 필요하다는 근거로 보는 게 맞습니다.

### Q15. "왜 BRM은 tau_p가 design budget 안에 있나요?"

답:

> BRM은 resource quota를 `Q_res=tau_p_design`으로 둡니다. 그리고 actual pilot count를 largest resource group size로 잡기 때문에, matching quota가 pilot count를 design budget 안에 묶는 역할을 합니다.

### Q16. "Q_res=tau_p_design은 임의적인 선택 아닌가요?"

답:

> 맞습니다. 현재는 baseline pilot budget과 맞춘 단순한 design choice입니다. 핵심은 같은 pilot budget을 resource-side quota로 사용해 pilot count를 제어했다는 점입니다. `Q_res`를 최적화하는 것은 자연스러운 future work입니다.

### Q17. "AP-Top-N은 왜 N=8인가요?"

답:

> 제출본에서는 simple AP-domain sparsification rule의 고정 세팅으로 `N_top=8`을 사용했습니다. 이 값이 전역 최적이라고 주장하는 것은 아닙니다. `N_top` sensitivity sweep은 future work로 보는 게 맞습니다.

### Q17-1. "AP-Top-N에서 adaptive한 것은 N인가요, pilot count인가요?"

답:

> 제출본 AP-Top-N에서는 `N_top=8`을 고정했습니다. Adaptive한 것은 `N_top`이 아니라 graph coloring 결과로 나온 `tau_p_actual`입니다. 즉 Top-8 AP overlap graph를 만들고, 그 graph를 coloring했을 때 실제로 필요한 color 수를 pilot count로 사용합니다.

### Q17-2. "왜 Top-N AP만 보나요? 약한 AP overlap도 interference가 될 수 있지 않나요?"

답:

> 약한 AP overlap도 완전히 0이라고 말할 수는 없습니다. 다만 모든 AP overlap을 conflict로 넣으면 graph가 너무 dense해져서 pilot 수가 커지고 prelog 손실이 커집니다. AP-Top-N은 dominant AP overlap만 conflict로 남겨서 중요한 충돌은 잡고, 약한 overlap 때문에 생기는 과도한 edge는 줄이자는 접근입니다.

### Q17-3. "AP-Top-N은 Gao의 단순화인가요?"

답:

> AP-domain 정보를 쓴다는 점에서는 Gao와 같은 축에 있습니다. 하지만 Gao처럼 many-to-many matching을 하지는 않고, UE별 strongest AP Top-N set이 겹치는지만 봅니다. 그래서 Gao의 AP-overlap idea를 훨씬 단순하고 sparse한 conflict graph 방식으로 만든 것이라고 설명할 수 있습니다.

### Q17-4. "AP-Top-N과 BRM 중 뭐가 더 좋은 방법인가요?"

답:

> 목적이 조금 다릅니다. AP-Top-N은 beam 정보 없이도 쓸 수 있는 단순하고 practical한 방법이고, BRM은 beam-domain resource competition까지 쓰는 더 rich한 방법입니다. 제출본 main setting에서는 BRM이 평균 SE와 EE가 더 좋지만, AP-Top-N도 K=50에서 평균 SE `+5.35%`로 매우 강합니다. 시스템이 beam 정보를 충분히 줄 수 있으면 BRM, 간단한 AP-domain rule이 필요하면 AP-Top-N이 더 매력적입니다.

### Q17-5. "AP-Top-N이 high-K에서 무너지는 이유는 뭔가요?"

답:

> K가 커지면 Top-N set끼리 겹칠 확률이 올라가고 graph가 다시 dense해집니다. 그러면 coloring에 필요한 color 수, 즉 `tau_p_actual`이 커집니다. 실제로 high-K에서 K=150이면 AP-Top-N의 mean `tau_p_actual`이 약 17.04로 design budget 15를 넘고, 그때부터 Random보다 평균 SE가 낮아지기 시작합니다.

### Q17-6. "AP-Top-N은 beam-domain을 안 쓰는데 왜 beam-domain 방법들과 비교하나요?"

답:

> 오히려 그래서 비교 가치가 있습니다. Beam-domain 정보 없이 AP-domain large-scale fading만으로 어느 정도까지 갈 수 있는지를 보여주는 기준점입니다. 결과적으로 moderate load에서는 AP-Top-N이 상당히 강해서, 복잡한 beam-domain 방법이 항상 필요한 것은 아니라는 현실적인 메시지도 줍니다.

### Q17-7. "AP-Top-N에서 graph coloring은 exact coloring인가요?"

답:

> 구현은 max-degree-first greedy coloring입니다. 따라서 minimum chromatic number를 정확히 구했다고 주장하면 안 됩니다. 발표에서는 "greedy coloring 결과 필요한 pilot 수를 `tau_p_actual`로 사용했다"고 설명하는 것이 맞습니다.

### Q17-8. "Top-N graph가 binary라서 overlap 개수가 많은 경우와 하나만 겹치는 경우를 구분 못 하지 않나요?"

답:

> 맞습니다. 제출본 AP-Top-N은 단순한 binary conflict graph입니다. overlap 개수나 strength를 더 세밀하게 반영하는 방향은 개선 가능성이 있습니다. 다만 binary로 단순화했는데도 moderate load에서 성능이 좋았기 때문에, 강한 AP overlap만 남기는 sparsification 자체가 효과가 있다는 점을 보여줍니다.

### Q18. "BWT threshold 10은 어떻게 정했나요?"

답:

> weak weighted beam-overlap edge를 줄이기 위한 design parameter로 10을 둔 것입니다. analytically optimized threshold라고 주장하면 안 되고, 같은 실험 환경에서 비교하기 위한 고정 parameter라고 설명하면 됩니다.

### Q19. "Energy efficiency가 정확히 뭘 의미하나요?"

답:

> 제출본에서의 EE는 simulator power model 아래의 relative metric입니다. transmit, circuit, RF-chain 관련 항을 포함하지만, 실제 hardware-calibrated energy model 전체를 완벽히 반영했다고 말하면 안 됩니다. 같은 power model 안에서 상대 비교를 위한 값으로 설명하는 게 안전합니다.

### Q20. "왜 full power control만 썼나요?"

답:

> pilot assignment 효과를 분리해서 보기 위해 power control을 full power로 고정했습니다. Joint power control까지 같이 최적화하면 operating point가 달라질 수 있고, 그 부분은 future work로 두었습니다.

### Q21. "confidence interval이 없는데 유의미하다고 할 수 있나요?"

답:

> 제출본 그래프는 200 Monte Carlo setup 평균을 보여줍니다. 따라서 observed trend는 말할 수 있지만, confidence interval이나 multi-seed test가 없는 상태에서 formal statistical significance를 강하게 주장하면 안 됩니다.

### Q22. "BRM이 high-K에서 K=250부터 Random보다 낮아지는데 결론이 약한 것 아닌가요?"

답:

> 이건 BRM의 operating range를 보여주는 결과입니다. Moderate load와 moderately high load에서는 이득이 있지만, very high load에서는 현재의 단순 resource quota rule만으로는 부족합니다. 그래서 결론은 "항상 이긴다"가 아니라, "pilot-count control과 channel-structure 보존의 균형이 중요하고, 현재 BRM은 그 균형이 맞는 구간에서 효과가 있다"입니다.

### Q23. "왜 high-K plot에 Mussbah를 넣었나요? 축을 망치지 않나요?"

답:

> Mussbah를 넣은 이유는 failure mode를 보여주기 위해서입니다. Graph coloring pilot count가 커지면 어떤 일이 생기는지 명확히 보입니다. 다만 나머지 method끼리 자세히 비교하려면 Mussbah를 뺀 backup plot도 결과 디렉터리에 있습니다.

### Q24. "SE gain이 prelog 때문인지 SINR 때문인지 분리했나요?"

답:

> 제출본에는 SINR decomposition이 들어가 있지 않습니다. 따라서 직접적으로 SINR이 개선됐다고 주장하면 안 됩니다. 안전한 해석은 BRM이 pilot overhead와 interference 사이의 trade-off를 더 좋게 만든다는 것입니다. SINR이나 NMSE diagnostic은 추가 실험이 필요합니다.

### Q25. "eCDF에서 무엇을 봐야 하나요?"

답:

> eCDF는 UE throughput의 분포를 보여줍니다. 왼쪽 아래 부분은 성능이 낮은 UE, 즉 lower-tail을 의미합니다. Curve가 오른쪽으로 이동하면 전체 throughput distribution이 좋아진 것이고, 5th percentile 또는 95% likely throughput은 lower-tail behavior를 요약하는 지표입니다.

### Q26. "왜 Random을 baseline으로 쓰나요?"

답:

> Random은 channel structure를 사용하지 않는 기준점입니다. 같은 simulator 안에서 어떤 방법이 Random보다 못하면, 그 세팅에서는 추가한 channel-structure logic이 실제 성능으로 이어지지 않았다는 뜻입니다.

### Q27. "Gao paper reproduction이 완벽한가요?"

답:

> 이 발표는 Gao reproduction 발표가 아닙니다. 여기서 Gao는 unified evaluator 안의 AP-domain reference method로 사용한 것입니다. 따라서 이 발표에서 Gao paper를 완벽히 재현했다고 주장하지 않는 것이 맞습니다.

### Q28. "Mussbah paper reproduction이 완벽한가요?"

답:

> 이 발표에서는 Mussbah의 beam-domain graph idea를 reference method로 사용했습니다. 제출본의 초점은 exact reproduction이 아니라 unified comparison과 BRM입니다. Mussbah 논문의 모든 closed-form detail을 완전히 재현했다는 식으로 말하면 안 됩니다.

### Q29. "왜 conclusion에 'existing methods보다 improved'라고 되어 있는데 high-K에서는 아닌가요?"

답:

> 그 문장은 제출본의 main moderate-load와 N-sweep 결과 범위에서 해석해야 합니다. High-K sweep은 universal dominance가 아니라 limitation과 operating range를 보여주는 부분입니다. 그래서 질문이 나오면 "모든 K에서 항상 좋다는 뜻은 아니다"라고 범위를 명확히 잡아야 합니다.

### Q30. "이 방법이 실제 시스템에 바로 적용 가능한가요?"

답:

> Beam-domain information과 centralized coordination이 필요하므로 CPU가 coordination하는 cell-free architecture에 가장 자연스럽습니다. 실제 적용까지 가려면 beam reporting overhead, mobility, update periodicity 같은 practical issue를 추가로 봐야 합니다.

### Q31. "beam reporting overhead는 고려했나요?"

답:

> 제출본 결과에서는 명시적으로 고려하지 않았습니다. Simulation은 stated model 안에서 pilot assignment와 SE/EE에 초점을 맞췄습니다. Beam reporting overhead는 practical extension으로 보는 것이 맞습니다.

### Q32. "mobility가 있으면 dominant beam이 바뀌는데요?"

답:

> 맞습니다. 이동성이 있으면 dominant beam이 바뀔 수 있습니다. 그래서 conclusion에서 time-varying dominant beam과 mobility scenario를 future work로 둔 것입니다. BRM을 실제로 쓰려면 matching update 주기나 robust matching이 필요합니다.

### Q33. "BRM complexity는 어떤가요?"

답:

> AP-Top-N보다는 복잡합니다. AP-beam resource에 대해 UE-resource matching을 하고, weighted pilot assignment도 수행하기 때문입니다. 제출본에서는 성능 mechanism을 우선 설명했고, complexity analysis는 future work로 보는 것이 맞습니다.

### Q34. "왜 AP-Top-N이 BRM과 비슷하게 좋은데 더 복잡한 BRM이 필요한가요?"

답:

> AP-Top-N은 단순하고 moderate load에서 강해서 practical value가 큽니다. 다만 BRM은 beam-domain resource competition까지 사용하기 때문에 더 rich한 방법이고, 제출본 main setting에서는 평균 SE와 EE가 가장 좋습니다. 실제 시스템에서는 beam 정보가 충분한지, complexity budget이 있는지에 따라 둘 중 하나를 선택할 수 있습니다.

### Q35. "이 발표의 가장 약한 부분은 무엇인가요?"

답:

> 가장 약한 부분은 final deck에 confidence interval이 없고, SINR/NMSE decomposition이 없으며, `N_top`, edge threshold, `Q_res`에 대한 parameter sensitivity가 충분히 들어가지 않았다는 점입니다. 그래서 가장 안전한 결론은 universal optimality가 아니라, overhead-aware pilot assignment 방향이 효과적일 수 있다는 observed result입니다.

---

## 9. 공격받을 때의 운영 원칙

1. 범위를 좁혀 답한다.
   - "제출본의 unified evaluator 기준으로는..."
   - "이 simulation setting에서는..."
   - "moderate-load 구간에서는..."

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
   - "그 항목은 제출본 실험에는 포함되어 있지 않습니다."
   - "그 decomposition은 현재 deck에는 들어가 있지 않습니다."
   - "그 부분은 좋은 future work 방향입니다."

---

## 10. 30초 요약 스크립트

> Cell-free massive MIMO에서는 많은 AP가 여러 UE를 함께 serving해서 coverage와 macro-diversity는 좋아지지만, pilot reuse가 더 어려워집니다. 기존 방법은 AP-domain matching이나 beam-domain graph coloring을 사용했습니다. 저희는 이 둘을 결합해서 UE를 AP-beam resource에 matching하고, weighted beam-domain overlap으로 pilot을 배정하는 Beam Resource Matching을 제안했습니다. 핵심은 pilot assignment가 SINR-side interference와 pilot overhead 사이의 균형 문제라는 점입니다. 제출본 simulation에서는 moderate load에서 BRM이 actual pilot count를 낮게 유지하면서 평균 SE와 EE를 개선했고, high-K stress test에서는 pilot-count control의 중요성과 현재 방법의 한계도 확인했습니다.

---

## 11. 2분 결과 설명 스크립트

> Main simulation은 AP 200개, coherence block 길이 150, design pilot budget 15, Monte Carlo setup 200개로 진행했습니다. 비교한 방법은 Random, Gao Matching, Mussbah Beam Graph, AP-Top-N, Beam Weighted Threshold, Beam Resource Matching의 여섯 가지입니다.
>
> Main K-sweep의 K=50 기준으로 보면, Beam Resource Matching은 Random 대비 평균 SE를 약 6.66%, EE를 약 12.35% 개선했습니다. 동시에 평균 actual pilot count는 15에서 약 5.29로 줄었습니다. AP-Top-N도 단순한 방법임에도 평균 SE가 약 5.35% 좋아지고 actual pilot count가 약 7.79로 낮게 유지되었습니다.
>
> 반대로 Mussbah와 Beam Weighted Threshold는 중요한 비교 사례입니다. Mussbah는 beam-domain graph를 세밀하게 만들지만, graph가 dense해지면서 K=50에서 약 45.76개의 pilot을 사용합니다. 이러면 prelog factor가 크게 줄어듭니다. Beam Weighted Threshold는 weak edge를 줄이지만 pilot count가 여전히 design budget보다 커집니다. 즉 beam-domain conflict information은 유용하지만, pilot overhead가 제어될 때만 성능 이득으로 이어집니다.
>
> High-K sweep은 stress test입니다. BRM은 K=200 근처까지는 유효하지만, 더 높은 load에서는 Random 아래로 내려가는 구간이 있습니다. 그래서 결론은 BRM이 항상 최고라는 것이 아닙니다. 결론은 AP/beam pruning과 resource matching이 channel structure 보존과 pilot-count reduction 사이의 균형을 잘 맞춰야 한다는 것입니다.

---

## 12. 근거 파일 맵

수치가 어디서 나온 것인지 질문받으면 아래 파일을 근거로 보면 된다.

| 주장 / 수치 | 근거 파일 |
| --- | --- |
| 제출본이 30페이지이고 setup slide가 있음 | `Beamer/main.pdf`, `Beamer/main.tex` |
| main K=25-50 six-method 결과 | `Final Figure/presentation_6method/presentation_mjh_6method_k_sweep.csv` |
| main K=50 p5 throughput | `Final Figure/presentation_6method/presentation_latest_6method_p5_throughput_vs_k.csv` |
| N-sweep 결과 | `Final Figure/presentation_n_sweep_6method/n_sweep_6method_summary.csv` |
| High-K 결과 | `Final Figure/presentation_high_k_6method/high_k_6method_summary.csv` |
| Mussbah 제거 high-K backup plot | `Final Figure/presentation_high_k_6method_no_mussbah/high_k_5method_summary.csv` |
| figure별 simulation setting | 각 `Final Figure/*/README.md` |
| channel estimation과 SE prelog에 들어간 `tau_p` 처리 | `MJH/all_schemes_ap_domain_hybrids_pilot_boxplot_env_fixed.py` |
