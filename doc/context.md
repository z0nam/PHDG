# Project Context: Evolutionary Portfolio Dynamics

## 1. Purpose of the Project

This project implements numerical simulations for an evolutionary portfolio investment model
based on a modified Hawk–Dove Game (HDG). The core objective is to study how individual
portfolio choices between risky and risk-free assets generate endogenous financial fragility,
boom–bust cycles, and convergence to a systemic risk threshold.

The simulation code is designed to:
- Verify analytical propositions derived in the paper
- Explore robustness under heterogeneous initial conditions
- Provide transparent and reproducible numerical evidence for evolutionary dynamics

This repository is **not** intended as a generic agent-based market simulator.
It implements a *specific evolutionary mechanism* grounded in cumulative wealth dynamics
and threshold-driven regime switches.

---

## 2. Conceptual Background

### Evolutionary Perspective
- Investors compete through **wealth accumulation**, not direct strategic interaction.
- Wealth acts as *fitness*: strategies with higher realized returns gain influence over time.
- The system evolves via **selection**, not optimization with foresight.

### Hawk–Dove Mapping
- Hawk (H) → risky asset
- Dove (D) → risk-free asset
- High return ↔ high systemic vulnerability
- Stability breeds instability through endogenous risk concentration

### Key Departure from Standard HDG
- N-player simultaneous interaction
- Continuous portfolio choice (β ∈ [0,1])
- Cumulative payoff → next-period endowment
- Regime switch triggered by aggregate risk exposure

---

## 3. Core Mechanism

Let:
- βᵢ : fraction of wealth invested in risky asset
- Wᵢ,t : wealth of investor i at time t
- β̂ₜ : wealth-weighted aggregate risky share
- R̄ : systemic fragility threshold

The economy alternates between:
- **Normal state**: β̂ₜ ≤ R̄ → risky asset yields r_R
- **Crisis state**: β̂ₜ > R̄ → risky asset collapses (r_C = −1)

Wealth evolves multiplicatively:
Wᵢ,t₊₁ = Wᵢ,t · [1 + (1−βᵢ) r_S + βᵢ g(β̂ₜ)]

This mechanism creates:
- Endogenous convergence of β̂ₜ to R̄
- Persistent boom–bust cycles without exogenous shocks
- Concentration of wealth near optimal portfolio strategies

---

## 4. Analytical Results Implemented

The simulations correspond directly to the following theoretical results:

1. **Boundary Nash Equilibrium**
   - Aggregate risk converges to β̂ = R̄

2. **Evolutionary Convergence**
   - Wealth concentrates on portfolios near the threshold-optimal β*

3. **Endogenous Crisis Periodicity**
   - Crisis frequency is determined by (r_R, r_S, R̄)

The numerical code should be interpreted as a **verification and illustration**
of these evolutionary properties, not as a calibration exercise.

---

## 5. Modeling Philosophy

Important design principles for this repository:

- Deterministic dynamics (no exogenous stochastic shocks)
- Minimal behavioral assumptions
- No anticipatory optimization; selection operates on realized wealth
- Threshold-driven fragility as the sole non-linearity
- Transparency: outputs are simple CSVs for downstream analysis

## 6. Recent updates (January 2026)

- Added `ver2` runner with scenario toggles (A–D) for variable R̄ and relaxed crisis returns.
- Aggregated outputs now include k*ₜ, Γₜ, γₜ, γ*ₜ, top agent βᵢ and wealth concentration metrics.
- Output directories are organized by scenario under `results/tables/ver2/<scenario>/`.
