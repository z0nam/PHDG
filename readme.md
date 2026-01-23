# Evolutionary Portfolio Simulation

Numerical simulation of the Hawk–Dove–style evolutionary portfolio model described in `doc/context.md` and `doc/numerical_simulation.md`.

## Setup (venv)

Use a fresh virtualenv in the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Notes:
- `env/` and `venv/` are leftover virtualenvs from earlier experiments; prefer the new `.venv` above.
- The code currently targets Python 3.9+; adjust the `python3` binary if you need a different interpreter.

## Run

Prefer the new `ver2` driver (baseline is scenario A with fixed R̄ and r_C = -1):

```bash
python src/PHD_simulation_ver2.py --scenario A
```

CSV outputs (beta history, wealth distributions, aggregated metrics) are written to `results/tables/ver2` with filenames like `Model1_*.csv`. Older outputs from the previous version live in `results/tables/ver1`.

### Quick smoke test

Run a short, lighter simulation to confirm the pipeline:

```bash
python src/PHD_simulation_ver2.py --scenario A --n 500 --t 200 --progress-every 50
```

### Scenarios (ver2)

- `--scenario A` (Model A): fixed threshold `R̄` (default 0.8), crisis return `r_C = -1`.
- `--scenario B` (Model B): threshold varies each period around `--rbar-base` with optional noise `--rbar-sigma` (clipped to [0,1]); crisis return `r_C = -1`.
- `--scenario C` (Model C): crisis return relaxed via `--crisis-return` (must satisfy -1 ≤ r_C < r_S=0.04); threshold fixed at `--rbar-base`.
- `--scenario D` (Model D): combines stochastic threshold from Model B with relaxed crisis return from Model C.

Outputs are written under `results/tables/ver2/<scenario>/` with filenames prefixed by the scenario label.

### What the run produces (ver2)

- `*_average_beta_.csv`: β̂ₜ series (wealth-weighted risky share).
- `*_aggregated_.csv`: time, β̂ₜ, top agent’s βᵢ and wealth share, top 10% wealth share, state (0/1), k*ₜ, Γₜ, γₜ, γ*ₜ, realized R̄ₜ.
- `*_beta_distribution_.csv`: grid of agent βᵢ values used in the run.
- `*_initial_wealth_.csv` and `*_final_wealth_.csv`: wealth snapshots for every agent.

Legacy runner: the previous implementation is preserved as `src/PHD_simulation_ver1.py` (fixed R̄, r_C = -1, no scenario toggles).
