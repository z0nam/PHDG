import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate paper-ready figures from existing simulation CSVs."
    )
    parser.add_argument(
        "--scenario",
        default="a",
        help="Scenario directory under results/tables/ver2 (e.g., a, b, c_rc-0.7, d_rc-0.5).",
    )
    parser.add_argument(
        "--input-root",
        type=Path,
        default=Path("results/tables/ver2"),
        help="Root directory containing scenario subdirectories.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("results/figures/paper"),
        help="Root output directory for generated figures.",
    )
    parser.add_argument(
        "--max-round",
        type=int,
        default=2000,
        help="Use data up to this many rounds (default: 2000).",
    )
    return parser.parse_args()


def load_single_col_csv(path: Path) -> pd.Series:
    df = pd.read_csv(path, index_col=0)
    return df.iloc[:, 0]


def find_model_file(scenario_dir: Path, model_number: int, suffix: str) -> Path:
    pattern = f"*Model{model_number}_{suffix}"
    matches = sorted(scenario_dir.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No file found for pattern: {scenario_dir / pattern}")
    return matches[0]


def load_model_bundle(scenario_dir: Path, model_number: int, max_round: int):
    agg_path = find_model_file(scenario_dir, model_number, "aggregated_.csv")
    avg_path = find_model_file(scenario_dir, model_number, "average_beta_.csv")
    beta_path = find_model_file(scenario_dir, model_number, "beta_distribution_.csv")
    init_path = find_model_file(scenario_dir, model_number, "initial_wealth_.csv")
    final_path = find_model_file(scenario_dir, model_number, "final_wealth_.csv")

    agg = pd.read_csv(agg_path, index_col=0)
    agg = agg[agg["t"] < max_round].copy()
    agg["t"] = agg["t"].astype(int)

    avg = load_single_col_csv(avg_path).iloc[:max_round].reset_index(drop=True)
    beta = load_single_col_csv(beta_path).reset_index(drop=True)
    initial = load_single_col_csv(init_path).reset_index(drop=True)
    final = load_single_col_csv(final_path).reset_index(drop=True)

    return {
        "aggregated": agg,
        "average_beta": avg,
        "beta_distribution": beta,
        "initial_wealth": initial,
        "final_wealth": final,
    }


def plot_2x2(models_data, panel_func, out_path: Path):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    axes = axes.flatten()

    for i, ax in enumerate(axes, start=1):
        panel_func(ax, i, models_data[i])
        ax.set_title(f"Model {i}", fontsize=13)
        ax.grid(True, alpha=0.25)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    print(f"Saved {out_path}")


def main():
    args = parse_args()
    scenario_dir = args.input_root / args.scenario
    if not scenario_dir.exists():
        raise FileNotFoundError(f"Scenario directory not found: {scenario_dir}")

    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams["axes.titlesize"] = 13
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 10

    models_data = {
        i: load_model_bundle(scenario_dir=scenario_dir, model_number=i, max_round=args.max_round)
        for i in [1, 2, 3, 4]
    }

    out_dir = args.output_root / args.scenario

    def panel_avg_beta(ax, model_number, md):
        agg = md["aggregated"]
        ax.plot(agg["t"], agg["hat_beta_t"], color="tab:green", lw=1.8, label=r"$\hat{\beta}_t$")
        if agg["r_bar_t"].nunique() == 1:
            ax.axhline(float(agg["r_bar_t"].iloc[0]), color="tab:red", lw=1.8, ls="--", label=r"$\bar{R}$")
        else:
            ax.plot(agg["t"], agg["r_bar_t"], color="tab:red", lw=1.4, ls="--", label=r"$\bar{R}_t$")
        ax.set_xlabel("Round")
        ax.set_ylabel(r"Wealth-weighted average of $\beta_i$")
        ax.legend(loc="lower right")

    plot_2x2(
        models_data,
        panel_avg_beta,
        out_dir / "_average_beta__combine.png",
    )

    def panel_beta_dist(ax, model_number, md):
        beta = md["beta_distribution"].values
        ax.hist(beta, bins=35, color="tab:blue", alpha=0.85, weights=np.ones_like(beta) * 100.0 / len(beta))
        ax.set_xlabel(r"Propensity to risky asset ($\beta_i$)")
        ax.set_ylabel("Percent (%)")

    plot_2x2(
        models_data,
        panel_beta_dist,
        out_dir / "_beta_distribution__combine.png",
    )

    def panel_initial_wealth(ax, model_number, md):
        w0 = md["initial_wealth"].values
        ax.hist(w0, bins=35, color="tab:purple", alpha=0.85, weights=np.ones_like(w0) * 100.0 / len(w0))
        ax.set_xlabel(r"Initial wealth ($W_{i,0}$)")
        ax.set_ylabel("Percent (%)")

    plot_2x2(
        models_data,
        panel_initial_wealth,
        out_dir / "_initial_wealth__combine.png",
    )

    def panel_final_wealth(ax, model_number, md):
        beta = md["beta_distribution"].values
        wf = md["final_wealth"].values
        ax.scatter(beta, wf, s=8, alpha=0.4, color="tab:green", edgecolors="none")
        ax.axvline(0.8, color="tab:red", ls="--", lw=1.4)
        ax.set_xlabel(r"Propensity to risky asset ($\beta_i$)")
        ax.set_ylabel(r"Final wealth ($W_{i,T}$)")

    plot_2x2(
        models_data,
        panel_final_wealth,
        out_dir / "_final_wealth__combine.png",
    )

    def panel_log_final_wealth(ax, model_number, md):
        beta = md["beta_distribution"].values
        wf = md["final_wealth"].values
        ax.scatter(beta, np.log(np.maximum(wf, 1e-300)), s=8, alpha=0.4, color="tab:olive", edgecolors="none")
        ax.axvline(0.8, color="tab:red", ls="--", lw=1.4)
        ax.set_xlabel(r"Propensity to risky asset ($\beta_i$)")
        ax.set_ylabel(r"$\log(W_{i,T})$")

    plot_2x2(
        models_data,
        panel_log_final_wealth,
        out_dir / "log__final_wealth__combine.png",
    )

    def panel_k_ast(ax, model_number, md):
        agg = md["aggregated"]
        sub = agg[agg["t"] > 0]
        ax.plot(sub["t"], sub["k_ast_t"], lw=1.8, color="tab:blue", label=r"$k_t^\ast$")
        if sub["r_bar_t"].nunique() == 1:
            ax.axhline(float(sub["r_bar_t"].iloc[0]), color="tab:red", lw=1.8, ls="--", label=r"$\bar{R}$")
        else:
            ax.plot(sub["t"], sub["r_bar_t"], lw=1.4, color="tab:red", ls="--", label=r"$\bar{R}_t$")
        ax.set_xlabel("Round")
        ax.set_ylabel(r"$k_t^\ast$")
        ax.legend(loc="upper right")

    plot_2x2(
        models_data,
        panel_k_ast,
        out_dir / "k_ast_t_combine.png",
    )

    def panel_gamma(ax, model_number, md):
        agg = md["aggregated"]
        ax.plot(agg["t"], agg["gamma_period_t"], lw=1.8, color="tab:red", label=r"$\gamma_t=t/\Gamma_t$")
        if "gamma_star_t" in agg.columns:
            ax.plot(agg["t"], agg["gamma_star_t"], lw=1.4, ls="--", color="tab:orange", label=r"$\gamma_t^\ast$")
        ax.set_xlabel("Round")
        ax.set_ylabel(r"Crisis period ($\gamma_t$)")
        ax.legend(loc="best")

    plot_2x2(
        models_data,
        panel_gamma,
        out_dir / "gamma_t_combine.png",
    )

    def panel_top_wealth(ax, model_number, md):
        agg = md["aggregated"]
        ax.plot(agg["t"], agg["top_agent_wealth_ratio"], lw=1.8, color="tab:green")
        ax.set_xlabel("Round")
        ax.set_ylabel(r"Top-agent wealth ratio ($W_t^\ast/\widetilde{W}_t$)")

    plot_2x2(
        models_data,
        panel_top_wealth,
        out_dir / "top_agent_wealth_ratio_combine.png",
    )


if __name__ == "__main__":
    main()
