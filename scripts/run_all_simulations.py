"""
Run all scenario/model combinations (simulation only).

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


N = 10000
T = 2000
PROGRESS = 200
BASE_OUTPUT = Path("results/tables/ver2")


SCENARIOS = [
    {
        "key": "a",
        "csv_label": "ModelA",
        "scenario_display": "R_bar fixed",
        "args": ["--scenario", "A"],
        "params": "R_bar=0.8 | r_R_N=0.1 | r_R_C=-1.0 | r_S=0.04",
        "show_star": True,
    },
    {
        "key": "b",
        "csv_label": "ModelB",
        "scenario_display": "R_bar stochastic",
        "args": ["--scenario", "B", "--rbar-sigma", "0.01"],
        "params": "R_bar~N(0.8,0.01) | r_R_N=0.1 | r_R_C=-1.0 | r_S=0.04",
        "show_star": True,
    },
    {
        "key": "c_rc-0.7",
        "csv_label": "ModelC",
        "scenario_display": "R_bar fixed",
        "args": ["--scenario", "C", "--crisis-return", "-0.7"],
        "params": "R_bar=0.8 | r_R_N=0.1 | r_R_C=-0.7 | r_S=0.04",
        "show_star": True,
    },
    {
        "key": "c_rc-0.5",
        "csv_label": "ModelC",
        "scenario_display": "R_bar fixed",
        "args": ["--scenario", "C", "--crisis-return", "-0.5"],
        "params": "R_bar=0.8 | r_R_N=0.1 | r_R_C=-0.5 | r_S=0.04",
        "show_star": True,
    },
    {
        "key": "d_rc-0.7",
        "csv_label": "ModelD",
        "scenario_display": "R_bar stochastic",
        "args": ["--scenario", "D", "--rbar-sigma", "0.01", "--crisis-return", "-0.7"],
        "params": "R_bar~N(0.8,0.01) | r_R_N=0.1 | r_R_C=-0.7 | r_S=0.04",
        "show_star": True,
    },
    {
        "key": "d_rc-0.5",
        "csv_label": "ModelD",
        "scenario_display": "R_bar stochastic",
        "args": ["--scenario", "D", "--rbar-sigma", "0.01", "--crisis-return", "-0.5"],
        "params": "R_bar~N(0.8,0.01) | r_R_N=0.1 | r_R_C=-0.5 | r_S=0.04",
        "show_star": True,
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


def main():
    for scenario in SCENARIOS:
        run_simulation(scenario)
    print("Simulation completed. Run `python scripts/plot_all_simulations.py` to generate figures.")


if __name__ == "__main__":
    main()
