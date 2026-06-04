# Gao et al. Reproduction Run Analysis

Run date: 2026-05-27  
Implementation state: preliminary reproduction, not paper-exact for all benchmarks.

## Commands

```bash
python experiments/fig2_cdf.py --realizations 20 --no-progress
python experiments/fig3_vs_pilot_number.py --realizations 20 --no-progress
python experiments/fig4_vs_ue_number.py --realizations 20 --no-progress
python -m pytest -q
```

Generated outputs:

- `figures/gao_fig2_cdf.png`
- `figures/gao_fig2_cdf_summary.csv`
- `figures/gao_fig3_vs_pilot_number.png`
- `figures/gao_fig3_vs_pilot_number.csv`
- `figures/gao_fig4_vs_ue_number.png`
- `figures/gao_fig4_vs_ue_number.csv`

## Paper Axis Check

The experiment scripts now force the paper-like axes when `--quick` is not used.

| Figure | Paper axis | Current script |
|---|---:|---:|
| Fig. 2 CDF | x = 2 to 20 Mbit/s, y = 0 to 1 | matched |
| Fig. 3 vs pilot number | x = 10 to 30, y = 0 to 9 Mbit/s | matched |
| Fig. 4 vs UE number | x = 100 to 200, y = 0 to 11 Mbit/s | matched |

`--quick` output is only a smoke test and intentionally uses automatic axes because it changes
the topology size.

## Fig. 2 Summary

95%-likely throughput is the 5th percentile.

| Scheme | Power control | P5 [Mbit/s] | Median [Mbit/s] | P95 [Mbit/s] |
|---|---|---:|---:|---:|
| Upper bound | Fractional | 6.417 | 11.180 | 16.286 |
| Gao matching | Fractional | 5.343 | 10.461 | 15.729 |
| Structured access | Fractional | 1.894 | 6.736 | 11.597 |
| Graph coloring | Fractional | 5.794 | 10.663 | 15.879 |
| Random | Fractional | 5.026 | 10.215 | 15.507 |
| Upper bound | Max-min | 5.185 | 6.862 | 7.836 |
| Gao matching | Max-min | 3.978 | 6.420 | 7.043 |
| Structured access | Max-min | 2.045 | 3.296 | 3.671 |
| Graph coloring | Max-min | 5.034 | 6.609 | 7.426 |
| Random | Max-min | 4.445 | 6.094 | 6.969 |

Observation:

- Axis scale is now comparable to the paper.
- Gao matching is below upper bound, as expected.
- Current graph-coloring heuristic is stronger than Gao matching. This does not match the paper.
- Structured access heuristic is far too weak. This does not match the paper.
- Max-min curves are step-like with 20 realizations because each realization nearly equalizes all
  UE throughputs. More realizations will smooth the CDF but will not fix the benchmark mismatch.

## Fig. 3 Summary

Fractional power control, 95%-likely throughput [Mbit/s]:

| Pilot number | Upper | Gao | Structured | Graph | Random |
|---:|---:|---:|---:|---:|---:|
| 10 | 6.773 | 4.858 | 1.999 | 5.410 | 4.360 |
| 15 | 6.796 | 5.543 | 1.895 | 5.959 | 5.002 |
| 20 | 6.650 | 5.505 | 1.790 | 5.989 | 5.184 |
| 25 | 6.540 | 5.623 | 1.777 | 6.059 | 5.189 |
| 30 | 6.310 | 5.563 | 1.616 | 5.934 | 5.230 |

Gao relative gains under fractional power:

| Pilot number | Gao vs Graph | Gao vs Random | Gao / Upper |
|---:|---:|---:|---:|
| 10 | -10.20% | +11.42% | 71.72% |
| 15 | -6.98% | +10.81% | 81.57% |
| 20 | -8.08% | +6.20% | 82.78% |
| 25 | -7.20% | +8.36% | 85.97% |
| 30 | -6.25% | +6.37% | 88.17% |

Observation:

- Gao improves over random, but less than the paper reports at some pilot counts.
- Gao does not outperform graph coloring because the current `GraphColoringPilotAssignment`
  is a custom greedy heuristic, not Liu et al. [14]'s exact benchmark.
- Gao/upper-bound ratio approaches the paper's qualitative claim near larger pilot counts, but
  is too low at `tau_p=10`.

## Fig. 4 Summary

Fractional power control, 95%-likely throughput [Mbit/s]:

| UE number | Upper | Gao | Structured | Graph | Random |
|---:|---:|---:|---:|---:|---:|
| 100 | 8.663 | 8.241 | 4.068 | 8.491 | 7.983 |
| 125 | 8.429 | 7.725 | 3.186 | 8.016 | 7.269 |
| 150 | 7.595 | 6.693 | 2.527 | 7.176 | 6.384 |
| 175 | 7.135 | 6.210 | 2.193 | 6.542 | 5.726 |
| 200 | 6.931 | 5.789 | 1.910 | 6.222 | 5.418 |

Observation:

- The monotonic drop with increasing UE number matches the paper qualitatively.
- The scheme order does not match the paper because benchmark I/II are not paper-exact.
- Current graph-coloring heuristic remains too competitive.

## Diagnosis

What is currently working:

- Gao Algorithm 1/2 runs at the target topology size.
- Serving sanity at `M=200, K=500, tau_p=20`: no unserved UEs; every AP group has 20 UEs.
- Throughput scale is now in the same Mbit/s range as the paper.
- Fig. 3 and Fig. 4 x/y axis ranges are aligned with the paper.
- Test suite passes.

What is not yet paper-exact:

- Benchmark I [15] and Benchmark II [14] are heuristic scaffolds. They must be replaced by
  the actual structured-access and graph-coloring procedures before final comparison.
- The power-control naming in the paper is inconsistent across caption/body text. The current
  scripts use `FractionalPowerControl(alpha=0.5)` for solid lines and max-min for dotted lines.
  This should be verified against the referenced power-control formula before final reporting.
- `realizations=20` is enough to debug trends but not enough for final CDF smoothness. Use
  200 or more realizations for final plots after the benchmark implementations are corrected.

## Next Fix Priority

1. Replace `src/pilot_schemes/graph_coloring.py` with a paper-faithful Liu et al. [14]
   interference graph construction and coloring method.
2. Replace `src/pilot_schemes/structured_access.py` with Chen et al. [15]'s threshold-based
   structured access algorithm.
3. Verify the exact fractional/full uplink power-control policy from Gao's cited references.
4. Re-run Fig. 2-4 with `--realizations 200` and compare the reported percentage gains.
