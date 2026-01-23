"""
Run all scenario/model combinations and generate overview plots.

Scenarios:
- Model A: fixed R_bar, r_C = -1.0
- Model B: R_bar ~ N(0.8, 0.01), r_C = -1.0
- Model C: r_C in {-0.7, -0.5}, fixed R_bar
Models 1-4 are defined in PHD_simulation_ver2.py.
"""
import subprocess
import sys
from pathlib import Path
import shutil

import pandas as pd
import matplotlib.pyplot as plt


N = 10000
T = 2000
PROGRESS = 200
BASE_OUTPUT = Path("results/tables/ver2")
FIG_DIR = Path("results/figures/ver2")


SCENARIOS = [
    {
        "key": "a",
        "label": "ModelA",
        "args": ["--scenario", "A"],
        "params": "R_bar=0.8 | r_R_N=0.1 | r_R_C=-1.0 | r_S=0.04",
        "show_star": True,
    },
    {
        "key": "b",
        "label": "ModelB",
        "args": ["--scenario", "B", "--rbar-sigma", "0.01"],
        "params": "R_bar~N(0.8,0.01) | r_R_N=0.1 | r_R_C=-1.0 | r_S=0.04",
        "show_star": True,
    },
    {
        "key": "c_rc-0.7",
        "label": "ModelC_rc-0.7",
        "args": ["--scenario", "C", "--crisis-return", "-0.7"],
        "params": "R_bar=0.8 | r_R_N=0.1 | r_R_C=-0.7 | r_S=0.04",
        "show_star": False,
    },
    {
        "key": "c_rc-0.5",
        "label": "ModelC_rc-0.5",
        "args": ["--scenario", "C", "--crisis-return", "-0.5"],
        "params": "R_bar=0.8 | r_R_N=0.1 | r_R_C=-0.5 | r_S=0.04",
        "show_star": False,
    },
    {
        "key": "d_rc-0.7",
        "label": "ModelD_rc-0.7",
        "args": ["--scenario", "D", "--rbar-sigma", "0.01", "--crisis-return", "-0.7"],
        "params": "R_bar~N(0.8,0.01) | r_R_N=0.1 | r_R_C=-0.7 | r_S=0.04",
        "show_star": False,
    },
    {
        "key": "d_rc-0.5",
        "label": "ModelD_rc-0.5",
        "args": ["--scenario", "D", "--rbar-sigma", "0.01", "--crisis-return", "-0.5"],
        "params": "R_bar~N(0.8,0.01) | r_R_N=0.1 | r_R_C=-0.5 | r_S=0.04",
        "show_star": False,
    },
]


def run_simulation(scenario: dict):
    # Always pass the base output dir; the driver appends scenario.lower()
    output_dir = BASE_OUTPUT
    cmd = [
        sys.executable,
        "src/PHD_simulation_ver2.py",
        "--n",
        str(N),
        "--t",
        str(T),
        "--progress-every",
        str(PROGRESS),
        "--output-dir",
        str(output_dir),
    ]
    cmd += scenario["args"]
    print(f"Running {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    # Rename scenario C/D outputs to include crisis return
    if scenario["key"].startswith("c_rc-"):
        src = BASE_OUTPUT / "c"
        dst = BASE_OUTPUT / scenario["key"]
        if dst.exists():
            shutil.rmtree(dst)
        if src.exists():
            src.rename(dst)
    if scenario["key"].startswith("d_rc-"):
        src = BASE_OUTPUT / "d"
        dst = BASE_OUTPUT / scenario["key"]
        if dst.exists():
            shutil.rmtree(dst)
        if src.exists():
            src.rename(dst)


def make_plot(scenario: dict, model_number: int):
    if scenario["key"].startswith("c_rc-"):
        agg = BASE_OUTPUT / scenario["key"] / f"ModelC_Model{model_number}_aggregated_.csv"
    else:
        agg = BASE_OUTPUT / scenario["key"] / f"{scenario['label']}_Model{model_number}_aggregated_.csv"
    df = pd.read_csv(agg, index_col=0)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle(f"{scenario['label']} Model{model_number}", fontsize=12, y=0.99)

    axes[0].plot(df["t"], df["hat_beta_t"], label="hat_beta_t")
    axes[0].plot(df["t"], df["r_bar_t"], label="r_bar_t", linestyle="--", alpha=0.7)
    axes[0].set_title("Aggregate risky share vs threshold")
    axes[0].legend()

    axes[1].plot(df["t"], df["top_10p_wealth_ratio"], label="top_10p_wealth_ratio", color="tab:green")
    axes[1].set_title("Top 10% wealth ratio")
    axes[1].legend()

    axes[2].plot(df["t"], df["gamma_period_t"], label="gamma_t (t/Gamma_t)", color="tab:red")
    if scenario["show_star"] and "gamma_star_t" in df.columns:
        axes[2].plot(df["t"], df["gamma_star_t"], label="gamma_star (Prop3)", color="tab:orange", linestyle="--")
    axes[2].set_title("Crisis period")
    axes[2].legend()

    for ax in axes:
        ax.set_xlabel("t")
        ax.grid(alpha=0.3)

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
    out_name = f"{scenario['label']}_Model{model_number}_metrics.png"
    fig.savefig(FIG_DIR / out_name, dpi=200)
    plt.close(fig)
    print(f"Saved {FIG_DIR / out_name}")


def main():
    for scenario in SCENARIOS:
        run_simulation(scenario)

    for scenario in SCENARIOS:
        for model_number in [1, 2, 3, 4]:
            make_plot(scenario, model_number)


if __name__ == "__main__":
    main()
