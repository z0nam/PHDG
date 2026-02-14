"""
Generate overview plots from existing simulation CSV outputs.

This script does not run simulations.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from run_all_simulations import BASE_OUTPUT, SCENARIOS


FIG_DIR = Path("results/figures/ver2")


def model_profile_math(model_number: int) -> str:
    mapping = {
        1: r"$w_{0,i}=100,\ \beta_i=i/N,\ i=0,\dots,N$",
        2: r"$w_{0,i}=100,\ \beta_i \sim U(0,1)$",
        3: r"$w_{0,i} \sim U(0,100),\ \beta_i=i/N,\ i=0,\dots,N$",
        4: r"$w_{0,i} \sim U(0,100),\ \beta_i \sim U(0,1)$",
    }
    return mapping[model_number]


def scenario_math(scenario: dict) -> str:
    if scenario["key"].startswith("a"):
        return r"$r_R=0.1,\ r_S=0.04,\ r_C=-1,\ \bar{R}=0.8$"
    if scenario["key"].startswith("b"):
        return r"$r_R=0.1,\ r_S=0.04,\ r_C=-1,\ \bar{R}_t \sim \mathcal{N}(0.8,\,0.01)$"
    if scenario["key"].startswith("c_rc-0.7"):
        return r"$r_R=0.1,\ r_S=0.04,\ r_C=-0.7,\ \bar{R}=0.8$"
    if scenario["key"].startswith("c_rc-0.5"):
        return r"$r_R=0.1,\ r_S=0.04,\ r_C=-0.5,\ \bar{R}=0.8$"
    if scenario["key"].startswith("d_rc-0.7"):
        return r"$r_R=0.1,\ r_S=0.04,\ r_C=-0.7,\ \bar{R}_t \sim \mathcal{N}(0.8,\,0.01)$"
    if scenario["key"].startswith("d_rc-0.5"):
        return r"$r_R=0.1,\ r_S=0.04,\ r_C=-0.5,\ \bar{R}_t \sim \mathcal{N}(0.8,\,0.01)$"
    return r"$r_R=0.1,\ r_S=0.04$"


def make_plot(scenario: dict, model_number: int):
    if scenario["key"].startswith("c_rc-"):
        prefix = f"ModelC_Model{model_number}"
    elif scenario["key"].startswith("d_rc-"):
        prefix = f"ModelD_Model{model_number}"
    else:
        prefix = f"{scenario['csv_label']}_Model{model_number}"

    agg = BASE_OUTPUT / scenario["key"] / f"{prefix}_aggregated_.csv"
    beta_dist = BASE_OUTPUT / scenario["key"] / f"{prefix}_beta_distribution_.csv"
    final_wealth = BASE_OUTPUT / scenario["key"] / f"{prefix}_final_wealth_.csv"

    df = pd.read_csv(agg, index_col=0)
    beta = pd.read_csv(beta_dist, index_col=0).iloc[:, 0]
    wealth = pd.read_csv(final_wealth, index_col=0).iloc[:, 0].clip(lower=1e-300)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle(
        f"{scenario_math(scenario)} | {model_profile_math(model_number)}",
        fontsize=12,
        y=0.99,
    )

    r_bar_mean = float(df["r_bar_t"].mean())
    r_bar_p10 = float(df["r_bar_t"].quantile(0.10))
    r_bar_p90 = float(df["r_bar_t"].quantile(0.90))
    axes[0].scatter(beta, wealth, s=8, alpha=0.35, color="tab:green", edgecolors="none")
    if r_bar_p90 > r_bar_p10:
        axes[0].axvspan(r_bar_p10, r_bar_p90, color="tab:red", alpha=0.12, label=r"$\bar{R}_t$ p10-p90 band")
    axes[0].axvline(r_bar_mean, color="tab:red", linestyle="--", linewidth=1.4, label=r"mean of $\bar{R}_t$")
    axes[0].set_yscale("log")
    axes[0].set_title(r"Final wealth vs $\beta_i$")
    axes[0].set_xlabel(r"$\beta_i$")
    axes[0].set_ylabel(r"$W_{i,T}$ (log scale)")
    axes[0].legend()

    axes[1].plot(df["t"], df["hat_beta_t"], label=r"$\hat{\beta}_t$")
    axes[1].plot(df["t"], df["r_bar_t"], label=r"$\bar{R}_t$", linestyle="--", alpha=0.7)
    axes[1].set_title(r"Aggregate risky share vs $\bar{R}$ threshold")
    axes[1].legend()

    axes[2].plot(df["t"], df["gamma_period_t"], label=r"$\gamma_t=t/\Gamma_t$", color="tab:red")
    if scenario["show_star"] and "gamma_star_t" in df.columns:
        axes[2].plot(df["t"], df["gamma_star_t"], label=r"$\gamma_t^\ast$", color="tab:orange", linestyle="--")
    axes[2].set_title(r"Crisis period ($\gamma_t$)")
    axes[2].legend()

    for ax in axes[1:]:
        ax.set_xlabel(r"$t$")
        ax.grid(alpha=0.3)
    axes[0].grid(alpha=0.3)

    fig.subplots_adjust(top=0.8)
    fig.text(
        0.5,
        0.92,
        scenario["params"],
        ha="center",
        va="top",
        fontsize=9,
        bbox=dict(facecolor="white", alpha=0.9, edgecolor="gray"),
    )

    fig.tight_layout(rect=[0, 0, 1, 0.87])
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out_name = f"{scenario['key']}_model{model_number}_metrics.png"
    fig.savefig(FIG_DIR / out_name, dpi=200)
    plt.close(fig)
    print(f"Saved {FIG_DIR / out_name}")


def main():
    for scenario in SCENARIOS:
        for model_number in [1, 2, 3, 4]:
            make_plot(scenario, model_number)


if __name__ == "__main__":
    main()
