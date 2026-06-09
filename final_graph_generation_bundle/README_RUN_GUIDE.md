# Final Graph Generation Code Bundle

This bundle contains the scripts used to generate the final presentation figures.

Important: these scripts are not standalone. They expect the original project
layout because each Python script resolves the project root from its location
under `experiments/`.

## Included Files

- `experiments/presentation_make_clean_figures.py`
- `experiments/presentation_n_sweep_6method_figures.py`
- `experiments/presentation_high_k_6method_figures.py`
- `experiments/plot_high_k_without_mussbah.py`
- `experiments/run_presentation_n_sweep_6method_200.sh`
- `experiments/run_presentation_high_k_6method_200.sh`
- `requirements.txt`

## Recommended Execution From The Project Root

Run these commands from the original repository root:

```bash
cd /home/myoungjin/03_Univ/KU/02_coursework/2026-1/이동통신시스템_신원재/proj_pilot
```

### 1. Regenerate the main six-method presentation plots

This does not rerun simulation. It reads existing MJH/result CSV files and
replots the slide-ready figures.

```bash
python experiments/presentation_make_clean_figures.py
```

Output directory:

```text
figures/presentation_6method/
```

### 2. Run the N-sweep experiment and plots

This reruns the `N=1..8`, `K=50` comparison with 200 setups.

```bash
bash experiments/run_presentation_n_sweep_6method_200.sh
```

Output directory:

```text
figures/presentation_n_sweep_6method/
```

### 3. Run the high-K experiment and plots

This reruns the `K=50,100,150,200,250,300`, `N=8` comparison with 200 setups.

```bash
bash experiments/run_presentation_high_k_6method_200.sh
```

Output directory:

```text
figures/presentation_high_k_6method/
```

### 4. Replot high-K without Mussbah

This does not rerun simulation. It reads the high-K CSV files and removes
Mussbah from the plotted comparison to avoid axis compression.

```bash
python experiments/plot_high_k_without_mussbah.py
```

Output directory:

```text
figures/presentation_high_k_6method_no_mussbah/
```

## If Using Only This Bundle

If the original scripts are missing, copy the bundled files back into the
project's `experiments/` directory first:

```bash
cp final_graph_generation_bundle/experiments/* experiments/
```

Then run the commands above from the project root.

## Data Dependencies

The main plotting script expects these source CSV files:

```text
MJH/result_200_boxplot_ap_domain_env_fixed_with_gao_parallel8/sweep_K_all_schemes.csv
MJH/result_200_boxplot_ap_domain_env_fixed_mussbah_edge0_parallel8/sweep_K_all_schemes.csv
```

The high-K no-Mussbah replot expects:

```text
figures/presentation_high_k_6method/high_k_6method_summary.csv
figures/presentation_high_k_6method/high_k_6method_ecdf_raw.csv
```

The N-sweep and high-K runner scripts require the simulator module:

```text
MJH/all_schemes_ap_domain_hybrids_pilot_boxplot_env_fixed.py
```

## Final Deck Figure Mapping

- Main K-sweep SE: `figures/presentation_6method/presentation_clean_load_crossover_se.png`
- Pilot-count mechanism: `figures/presentation_6method/presentation_clean_pilot_count_vs_k.png`
- Antenna sweep SE/EE: `figures/presentation_n_sweep_6method/n_sweep_avg_se_vs_n.png`, `n_sweep_avg_ee_vs_n.png`
- High-K stress: `figures/presentation_high_k_6method_no_mussbah/high_k_5method_avg_se_vs_k.png`
