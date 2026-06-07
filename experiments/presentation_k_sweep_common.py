"""Common-ground K-sweep for the presentation.

This reruns the selected methods in one shared MC environment:
L=200, N=8, fc=3 GHz, tau_c=150, tau_p_design=15 by default.

The goal is the presentation K-sweep, not paper-faithful reproduction.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.presentation_main_compare import build_schemes, compute_ee
from src.config import SimulationConfig
from src.mussbah_se import mussbah_uplink_se
from src.network import Network


SELECTED_SCHEMES = [
    "Random",
    "Gao matching",
    "Mussbah",
    "Hybrid#3 (TopAP N=8 adaptive)",
    "MJH weighted-count strict",
    "MJH beam-resource matching",
]

LABELS = {
    "Random": "Random",
    "Gao matching": "Gao Matching",
    "Mussbah": "Mussbah Beam Graph",
    "Hybrid#3 (TopAP N=8 adaptive)": "AP-Top-N (N=8)",
    "MJH weighted-count strict": "Beam-Weighted Threshold",
    "MJH beam-resource matching": "Beam-Resource Matching",
}

COLORS = {
    "Random": "#707070",
    "Gao matching": "#1f78b4",
    "Mussbah": "#ff7f00",
    "Hybrid#3 (TopAP N=8 adaptive)": "#e7298a",
    "MJH weighted-count strict": "#d95f02",
    "MJH beam-resource matching": "#5e3c99",
}

LINESTYLES = {
    "Random": "-",
    "Gao matching": "-",
    "Mussbah": "-",
    "Hybrid#3 (TopAP N=8 adaptive)": "--",
    "MJH weighted-count strict": "--",
    "MJH beam-resource matching": "--",
}


def run_one_k(args: argparse.Namespace, k_value: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    config = SimulationConfig(
        num_aps=args.num_aps,
        num_ues=k_value,
        tau_p=args.tau_p,
        tau_c=args.tau_c,
        bandwidth_hz=20e6,
        carrier_frequency_mhz=args.carrier_frequency_mhz,
        num_antennas_per_ap=args.num_antennas,
        one_ring_radius_m=args.one_ring_radius,
        pathloss_model="umi3gpp",
        ue_height_m=1.5,
        ap_orientation=args.ap_orientation,
        beam_detection_snr_db=args.beam_detection_snr_db,
        random_seed=args.seed + k_value,
    )
    topology_rng = np.random.default_rng(args.seed + 10_000 * k_value)
    raw_rows: list[dict] = []
    setup_rows: list[dict] = []

    for setup in range(args.setups):
        if not args.no_progress and (setup + 1) % max(1, args.progress_every) == 0:
            print(f"  K={k_value}: setup {setup + 1}/{args.setups}", flush=True)

        net = Network.random(config, topology_rng)
        channel_seed = args.seed + 100_000 + 1000 * k_value + setup * 13
        schemes = build_schemes(
            args.seed + 1_000_000 * k_value + 1000 * setup,
            args.delta,
            args.weight_threshold,
            args.top_n,
        )

        for scheme_name in SELECTED_SCHEMES:
            scheme = schemes[scheme_name]
            pilots = scheme.assign(net, args.tau_p)
            tau_p_actual = int(pilots.max()) + 1 if pilots.size else 0
            channel_rng = np.random.default_rng(channel_seed)
            se_per_ue = mussbah_uplink_se(
                net,
                pilots,
                n_channel_samples=args.channel_samples,
                delta=args.delta,
                rician_k_db=args.rician_k_db,
                one_ring_radius_m=args.one_ring_radius,
                rng=channel_rng,
            )
            sum_se = float(np.sum(se_per_ue))
            ee = compute_ee(scheme_name, scheme, net, sum_se)
            setup_rows.append(
                {
                    "K": k_value,
                    "setup": setup,
                    "scheme": scheme_name,
                    "sum_se": sum_se,
                    "mean_se": float(np.mean(se_per_ue)),
                    "tau_p_actual": tau_p_actual,
                    "ee_bps_per_hz_per_watt": ee,
                }
            )
            for ue_idx, ue_se in enumerate(se_per_ue):
                raw_rows.append(
                    {
                        "K": k_value,
                        "setup": setup,
                        "ue": ue_idx,
                        "scheme": scheme_name,
                        "se_bps_per_hz": float(ue_se),
                        "tau_p_actual": tau_p_actual,
                    }
                )

    return pd.DataFrame(raw_rows), pd.DataFrame(setup_rows)


def summarise(setup_df: pd.DataFrame, raw_df: pd.DataFrame) -> pd.DataFrame:
    se_summary = (
        raw_df.groupby(["K", "scheme"])
        .agg(
            p5_se=("se_bps_per_hz", lambda x: float(np.percentile(x, 5))),
            mean_se=("se_bps_per_hz", "mean"),
            median_se=("se_bps_per_hz", "median"),
        )
        .reset_index()
    )
    setup_summary = (
        setup_df.groupby(["K", "scheme"])
        .agg(
            mean_tau_p=("tau_p_actual", "mean"),
            mean_ee=("ee_bps_per_hz_per_watt", "mean"),
            mean_sum_se=("sum_se", "mean"),
        )
        .reset_index()
    )
    summary = se_summary.merge(setup_summary, on=["K", "scheme"])
    random_ref = summary[summary["scheme"] == "Random"][
        ["K", "mean_se", "p5_se", "mean_ee"]
    ].rename(
        columns={
            "mean_se": "random_mean_se",
            "p5_se": "random_p5_se",
            "mean_ee": "random_mean_ee",
        }
    )
    summary = summary.merge(random_ref, on="K")
    summary["mean_vs_random_pct"] = (
        100.0 * (summary["mean_se"] - summary["random_mean_se"]) / summary["random_mean_se"]
    )
    summary["p5_vs_random_pct"] = (
        100.0 * (summary["p5_se"] - summary["random_p5_se"]) / summary["random_p5_se"]
    )
    summary["ee_vs_random_pct"] = (
        100.0 * (summary["mean_ee"] - summary["random_mean_ee"]) / summary["random_mean_ee"]
    )
    order = {scheme: idx for idx, scheme in enumerate(SELECTED_SCHEMES)}
    return summary.assign(_order=summary["scheme"].map(order)).sort_values(["K", "_order"]).drop(columns="_order")


def plot_metric(summary: pd.DataFrame, metric: str, ylabel: str, title: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.8, 4.0))
    for scheme_name in SELECTED_SCHEMES:
        sub = summary[summary["scheme"] == scheme_name].sort_values("K")
        ax.plot(
            sub["K"],
            sub[metric],
            marker="o",
            linewidth=2.3 if scheme_name not in {"Random", "Gao matching", "Mussbah"} else 1.9,
            markersize=5.0,
            color=COLORS[scheme_name],
            linestyle=LINESTYLES[scheme_name],
            label=LABELS[scheme_name],
        )
    ax.set_xlabel("Number of users K")
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=12, pad=6)
    ax.set_xticks(sorted(summary["K"].unique()))
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7.2, loc="best")
    fig.tight_layout(pad=0.7)
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k-list", type=int, nargs="+", default=[30, 40, 50, 60, 70])
    parser.add_argument("--setups", type=int, default=200)
    parser.add_argument("--channel-samples", type=int, default=20)
    parser.add_argument("--tau-p", type=int, default=15)
    parser.add_argument("--tau-c", type=int, default=150)
    parser.add_argument("--delta", type=float, default=0.95)
    parser.add_argument("--rician-k-db", type=float, default=10.0)
    parser.add_argument("--one-ring-radius", type=float, default=30.0)
    parser.add_argument("--num-antennas", type=int, default=8)
    parser.add_argument("--num-aps", type=int, default=200)
    parser.add_argument("--carrier-frequency-mhz", type=float, default=3000.0)
    parser.add_argument("--ap-orientation", choices=["fixed", "random"], default="random")
    parser.add_argument("--beam-detection-snr-db", type=float, default=20.0)
    parser.add_argument("--weight-threshold", type=float, default=10.0)
    parser.add_argument("--top-n", type=int, default=8)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out-prefix", type=str, default="presentation_k_sweep_common")
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--no-progress", action="store_true")
    args = parser.parse_args()

    out_dir = PROJECT_ROOT / "figures"
    out_dir.mkdir(exist_ok=True)

    print(
        "[presentation_k_sweep_common] "
        f"L={args.num_aps}, N={args.num_antennas}, tau_c={args.tau_c}, "
        f"tau_p_design={args.tau_p}, K={args.k_list}, "
        f"{args.setups} setups x {args.channel_samples} channel samples",
        flush=True,
    )

    raw_frames = []
    setup_frames = []
    for k_value in args.k_list:
        raw_df, setup_df = run_one_k(args, k_value)
        raw_frames.append(raw_df)
        setup_frames.append(setup_df)

    raw_all = pd.concat(raw_frames, ignore_index=True)
    setup_all = pd.concat(setup_frames, ignore_index=True)
    summary = summarise(setup_all, raw_all)

    raw_path = out_dir / f"{args.out_prefix}_raw.csv"
    setup_path = out_dir / f"{args.out_prefix}_setup.csv"
    summary_path = out_dir / f"{args.out_prefix}_summary.csv"
    raw_all.to_csv(raw_path, index=False)
    setup_all.to_csv(setup_path, index=False)
    summary.to_csv(summary_path, index=False)

    plot_metric(
        summary,
        metric="mean_se",
        ylabel="Average SE [bit/s/Hz/user]",
        title="Common-ground SE under increasing user load",
        out_path=out_dir / f"{args.out_prefix}_se.png",
    )
    plot_metric(
        summary,
        metric="mean_ee",
        ylabel="Average EE [bit/s/Hz/W]",
        title="Common-ground EE under increasing user load",
        out_path=out_dir / f"{args.out_prefix}_ee.png",
    )

    print(summary[["K", "scheme", "mean_se", "mean_vs_random_pct", "mean_tau_p", "mean_ee", "ee_vs_random_pct"]].to_string(index=False))
    print(f"Raw -> {raw_path}")
    print(f"Setup -> {setup_path}")
    print(f"Summary -> {summary_path}")


if __name__ == "__main__":
    main()
