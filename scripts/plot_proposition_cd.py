"""
Generate proposition-grouped comparison plots for Scenario C vs D.

Layout per figure: 3 rows x 2 columns
- Row 1: Final wealth vs beta (with R_bar band/mean)
- Row 2: Aggregate risky share vs threshold
- Row 3: Crisis period
- Col 1: Scenario C
- Col 2: Scenario D

One figure is generated for each (model_number, crisis_return) pair.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


BASE_OUTPUT = Path("results/tables/ver2")
FIG_DIR = Path("results/figures/ver2/proposition_cd")
CRISIS_RETURNS = ["-0.7", "-0.5"]
MODELS = [1, 2, 3, 4]


def model_profile(model_number: int) -> str:
    mapping = {
        1: r"$w_{0,i}=100,\ \beta_i=i/N,\ i=0,\dots,N$",
        2: r"$w_{0,i}=100,\ \beta_i \sim U(0,1)$",
        3: r"$w_{0,i} \sim U(0,100),\ \beta_i=i/N,\ i=0,\dots,N$",
        4: r"$w_{0,i} \sim U(0,100),\ \beta_i \sim U(0,1)$",
    }
    return mapping[model_number]


def scenario_profile(scenario_key: str) -> str:
    if scenario_key.startswith("c_rc-"):
        return r"$\bar{R}=0.8$"
    if scenario_key.startswith("d_rc-"):
        return r"$\bar{R}_t \sim \mathcal{N}(0.8,\,0.01)$"
    raise ValueError(f"Unexpected scenario key: {scenario_key}")


def load_data(scenario_key: str, model_number: int):
    if scenario_key.startswith("c_rc-"):
        prefix = f"ModelC_Model{model_number}"
    elif scenario_key.startswith("d_rc-"):
        prefix = f"ModelD_Model{model_number}"
    else:
        raise ValueError(f"Unexpected scenario key: {scenario_key}")

    agg = BASE_OUTPUT / scenario_key / f"{prefix}_aggregated_.csv"
    beta_dist = BASE_OUTPUT / scenario_key / f"{prefix}_beta_distribution_.csv"
    final_wealth = BASE_OUTPUT / scenario_key / f"{prefix}_final_wealth_.csv"

    df = pd.read_csv(agg, index_col=0)
    beta = pd.read_csv(beta_dist, index_col=0).iloc[:, 0]
    wealth = pd.read_csv(final_wealth, index_col=0).iloc[:, 0].clip(lower=1e-300)
    return df, beta, wealth


def draw_prop1(ax, df, beta, wealth, scenario_label: str):
    r_bar_mean = float(df["r_bar_t"].mean())
    r_bar_p10 = float(df["r_bar_t"].quantile(0.10))
    r_bar_p90 = float(df["r_bar_t"].quantile(0.90))

    ax.scatter(beta, wealth, s=8, alpha=0.35, color="tab:green", edgecolors="none")
    if r_bar_p90 > r_bar_p10:
        ax.axvspan(r_bar_p10, r_bar_p90, color="tab:red", alpha=0.12, label=r"$\bar{R}_t$ p10-p90 band")
    ax.axvline(r_bar_mean, color="tab:red", linestyle="--", linewidth=1.4, label=r"mean of $\bar{R}_t$")
    ax.set_yscale("log")
    ax.set_title(f"Prop 1 | {scenario_label}: Final wealth vs $\\beta_i$")
    ax.set_xlabel(r"$\beta_i$")
    ax.set_ylabel(r"$W_{i,T}$ (log scale)")
    ax.grid(alpha=0.3)
    ax.legend()


def draw_prop2(ax, df, scenario_label: str):
    ax.plot(df["t"], df["hat_beta_t"], label=r"$\hat{\beta}_t$")
    ax.plot(df["t"], df["r_bar_t"], label=r"$\bar{R}_t$", linestyle="--", alpha=0.7)
    ax.set_title(f"Prop 2 | {scenario_label}: Aggregate risky share vs $\\bar{{R}}$ threshold")
    ax.set_xlabel(r"$t$")
    ax.grid(alpha=0.3)
    ax.legend()


def draw_prop3(ax, df, scenario_label: str):
    ax.plot(df["t"], df["gamma_period_t"], label=r"$\gamma_t=t/\Gamma_t$", color="tab:red")
    if "gamma_star_t" in df.columns:
        ax.plot(df["t"], df["gamma_star_t"], label=r"$\gamma_t^\ast$", color="tab:orange", linestyle="--")
    ax.set_title(f"Prop 3 | {scenario_label}: Crisis period ($\\gamma_t$)")
    ax.set_xlabel(r"$t$")
    ax.grid(alpha=0.3)
    ax.legend()


def make_cd_figure(model_number: int, crisis_return: str):
    scenario_c = f"c_rc{crisis_return}"
    scenario_d = f"d_rc{crisis_return}"
    scenario_specs = [
        (scenario_c, scenario_profile(scenario_c)),
        (scenario_d, scenario_profile(scenario_d)),
    ]

    fig, axes = plt.subplots(3, 2, figsize=(13, 12))
    fig.suptitle(
        f"$r_R=0.1,\ r_S=0.04,\ r_C={crisis_return}$ | {model_profile(model_number)}",
        fontsize=13,
    )

    for col, (scenario_key, label) in enumerate(scenario_specs):
        df, beta, wealth = load_data(scenario_key, model_number)
        draw_prop1(axes[0, col], df, beta, wealth, label)
        draw_prop2(axes[1, col], df, label)
        draw_prop3(axes[2, col], df, label)

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / f"Model{model_number}_rc{crisis_return}_props_cd.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    print(f"Saved {out}")


def make_cd_prop_files(model_number: int, crisis_return: str):
    scenario_c = f"c_rc{crisis_return}"
    scenario_d = f"d_rc{crisis_return}"
    label_c = scenario_profile(scenario_c)
    label_d = scenario_profile(scenario_d)
    df_c, beta_c, wealth_c = load_data(scenario_c, model_number)
    df_d, beta_d, wealth_d = load_data(scenario_d, model_number)

    # Proposition 1
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    fig.suptitle(
        f"$r_R=0.1,\ r_S=0.04,\ r_C={crisis_return}$ | {model_profile(model_number)}",
        fontsize=13,
    )
    draw_prop1(axes[0], df_c, beta_c, wealth_c, label_c)
    draw_prop1(axes[1], df_d, beta_d, wealth_d, label_d)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out = FIG_DIR / f"Model{model_number}_rc{crisis_return}_prop1_cd.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    print(f"Saved {out}")

    # Proposition 2
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    fig.suptitle(
        f"$r_R=0.1,\ r_S=0.04,\ r_C={crisis_return}$ | {model_profile(model_number)}",
        fontsize=13,
    )
    draw_prop2(axes[0], df_c, label_c)
    draw_prop2(axes[1], df_d, label_d)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out = FIG_DIR / f"Model{model_number}_rc{crisis_return}_prop2_cd.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    print(f"Saved {out}")

    # Proposition 3
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    fig.suptitle(
        f"$r_R=0.1,\ r_S=0.04,\ r_C={crisis_return}$ | {model_profile(model_number)}",
        fontsize=13,
    )
    draw_prop3(axes[0], df_c, label_c)
    draw_prop3(axes[1], df_d, label_d)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out = FIG_DIR / f"Model{model_number}_rc{crisis_return}_prop3_cd.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    print(f"Saved {out}")


def main():
    for crisis_return in CRISIS_RETURNS:
        for model_number in MODELS:
            make_cd_figure(model_number, crisis_return)
            make_cd_prop_files(model_number, crisis_return)


if __name__ == "__main__":
    main()
