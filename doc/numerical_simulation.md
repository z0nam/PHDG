# Numerical Simulation Design

## 1. Objective

The numerical simulations implement the evolutionary portfolio model to:

- Track the dynamic behavior of the aggregate risky asset ratio β̂ₜ
- Verify convergence to the fragility threshold R̄
- Examine robustness to heterogeneity in initial wealth and risk preferences
- Illustrate endogenous boom–bust cycles

All simulations directly correspond to the analytical framework.

---

## 2. Agents and Strategy Space

- Number of investors: N = 10,000
- Each investor i is characterized by:
  - Portfolio share βᵢ ∈ [0,1]
  - Wealth Wᵢ,t ≥ 0

### Portfolio Grid
Strategies are discretized as:
βᵢ = (i−1)/(N−1), i = 1, …, N

This ensures uniform coverage of the strategy space.

---

## 3. Wealth Dynamics

At each period t:

1. Compute aggregate risky share:
   β̂ₜ = Σᵢ βᵢ Wᵢ,t / Σᵢ Wᵢ,t

2. Determine regime:
   - Normal state if β̂ₜ ≤ R̄
   - Crisis state if β̂ₜ > R̄

3. Update wealth:
   Wᵢ,t₊₁ = Wᵢ,t · [1 + (1−βᵢ) r_S + βᵢ g(β̂ₜ)]

where:
- g(β̂ₜ) = r_R in normal state
- g(β̂ₜ) = −1 in crisis state

---

## 4. Baseline Parameters

| Parameter | Value |
|---------|------|
| Number of investors | 10,000 |
| Fragility threshold (R̄) | 0.8 |
| Risky return (r_R) | 0.10 |
| Safe return (r_S) | 0.04 |
| Time horizon | 2,000 periods |

These values are chosen for clarity, not calibration.

---

## 5. Model Variations

Four simulation scenarios are considered:

| Model | Initial Wealth | Risk Preference |
|------|---------------|----------------|
| Model 1 | Equal | Uniform β |
| Model 2 | Equal | Random β |
| Model 3 | Random | Uniform β |
| Model 4 | Random | Random β |

Purpose:
- Test robustness of convergence
- Confirm irrelevance of initial heterogeneity for long-run dynamics

### Scenario toggles in `ver2`

- **Model A (`--scenario A`)**: fixed R̄, crisis return r_C = -1 (baseline).
- **Model B (`--scenario B`)**: R̄ becomes time-varying via `--rbar-sigma` shocks around `--rbar-base`, clipped to [0,1].
- **Model C (`--scenario C`)**: crisis return relaxed to `--crisis-return` (must satisfy -1 ≤ r_C < r_S = 0.04), fixed R̄.
- **Model D (`--scenario D`)**: combines stochastic R̄ (as in B) with relaxed crisis return (as in C).

Aggregated outputs (`*_aggregated_.csv`) now include:
- t, β̂ₜ, top agent βᵢ, top agent wealth share, top 10% wealth share
- state indicator (0 normal / 1 crisis), k*ₜ, cumulative crises Γₜ, crisis periodicity γₜ, theoretical γ*ₜ, realized R̄ₜ

---

## 6. Observables

The simulations record:

- Aggregate risky share β̂ₜ
- Distribution of individual wealth Wᵢ,t
- Wealth concentration measures
- Crisis frequency Γₜ and γₜ = t / Γₜ
- Time-varying optimal portfolio k*ₜ

---

## 7. Expected Outcomes

Across all models:

- β̂ₜ converges to R̄
- Wealth concentrates near the optimal β*
- Crisis cycles persist endogenously
- Initial conditions affect only transient dynamics

These outcomes confirm that:
**financial fragility emerges as an evolutionary equilibrium**, not a deviation.

---

## 8. Interpretation Guidelines

Important notes for interpretation:

- Cycles are deterministic and endogenous
- No agent “anticipates” crises
- Stability is not efficient; it is fragile by construction
- The threshold R̄ acts as an evolutionary coordination boundary

Simulation results should be read as **structural implications**
of portfolio competition under cumulative wealth dynamics.
