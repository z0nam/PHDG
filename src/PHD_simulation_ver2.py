import argparse
import sys
import random
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

# main param

N = 10000
T = 10000
r_R_N = 0.1             # risky asset return (in normal state)
r_R_C = -1.0            # risky asset return (in crisis state)
r_S = 0.04              # risk-free asset return (all state)
R_BAR = 0.8             # crisis threshold
INITIAL_WEALTH = 100    # individual initial wealth
[NORMAL, CRISIS] = [0, 1]
PROGRESS_EVERY = 1000   # print progress every N steps

# meta param

AVERAGE_BETA_FILENAME = "average_beta"
BETA_DISTRIBUTION_FILENAME = "beta_distribution"
INITIAL_WEALTH_FILENAME = "initial_wealth"
FINAL_WEALTH_FILENAME = "final_wealth"

STATE_FILENAME = "State"
T_FILENAME = "t"
GAMMA_FILENAME = "gamma"
K_AST_FILENAME = "k_ast"
TOP_AGENT_BETA_I_FILENAME = "top_beta_i"

AGGREGATED_VARS_FILENAME = "aggregated"
OUTPUT_DIR = Path("results/tables/ver2")

BETA_SETTING = [BETA_UNIFORM, BETA_RANDOM] = [0, 1]
INITIAL_WEALTH_SETTING = [INITIAL_WEALTH_SAME, INITIAL_WEALTH_RANDOM] = [0, 1]
MODEL_A, MODEL_B, MODEL_C, MODEL_D = ["A", "B", "C", "D"]

# class define


class Models:
    def __init__(self, r_bar_strategy: Callable[[int], float], crisis_return: float, model_label: str):
        self.models = []
        model_number = 1
        self.r_bar_strategy = r_bar_strategy
        self.crisis_return = crisis_return
        self.model_label = model_label

        for initial_wealth_setting in INITIAL_WEALTH_SETTING:
            for beta_setting in BETA_SETTING:
                self.models.append(Model(beta_setting=beta_setting, initial_wealth_setting=initial_wealth_setting,
                                         model_number=model_number))
                model_number += 1

    def run(self):
        for model in self.models:
            print("current setting: model: %d, beta_setting: "
                  "%d, initial_wealth_setting: %d" % (model.model_number, model.beta_setting,
                                                      model.initial_wealth_setting))
            simulation = Simulation(beta_setting=model.beta_setting,
                                    initial_wealth_setting=model.initial_wealth_setting,
                                    model_number=model.model_number,
                                    progress_every=PROGRESS_EVERY,
                                    r_bar_strategy=self.r_bar_strategy,
                                    crisis_return=self.crisis_return,
                                    model_label=self.model_label)
            simulation.run()
            simulation.save()


class Model:
    def __init__(self, beta_setting, initial_wealth_setting, model_number):
        self.beta_setting = beta_setting
        self.initial_wealth_setting = initial_wealth_setting
        self.model_number = model_number


class World:
    def __init__(self, beta_setting, initial_wealth_setting, model_number, r_bar_strategy, crisis_return):
        self.agents = []
        self.beta_history = []
        self.k_ast = []
        self.state = []
        self.total_period = []
        self.model_number = model_number
        self.top_agent_beta_i_history = []
        self.top_agent_wealth_ratio = []
        self.top_10p_wealth_ratio = []
        self.total_number_of_crisis = []
        self.gamma_period_history = []
        self.gamma_star_history = []
        self.r_bar_history = []
        self.r_bar_strategy = r_bar_strategy
        self.crisis_return = crisis_return

        for i in range(0, N + 1):
            if beta_setting == BETA_UNIFORM:
                beta = i / N                # beta: individual risky asset ratio
                self.agents.append(Agent(beta=beta, initial_wealth_setting=initial_wealth_setting))
            elif beta_setting == BETA_RANDOM:
                beta = random.random()
                self.agents.append(Agent(beta=beta, initial_wealth_setting=initial_wealth_setting))
            else:
                sys.exit("beta_setting error: current beta_setting: %d" % beta_setting)

    def update(self, t):
        global_state = self.global_state(t=t)  # set beta_t
        for agent in self.agents:
            agent.update(global_state=global_state, crisis_return=self.crisis_return)   # set Wit+1

    def global_state(self, t):

        total_wealth_r = 0              # total risky asset
        total_wealth_s = 0              # total risk-free asset

        for agent in self.agents:
            total_wealth_r += agent.wealth * agent.beta             # individual risky asset
            total_wealth_s += agent.wealth * (1 - agent.beta)       # individual risk-free asset

        wealth_list = [agent.wealth for agent in self.agents]
        top_agent_index = np.argmax(wealth_list)
        self.top_agent_beta_i_history.append(self.agents[top_agent_index].beta)
        top_agent_wealth_ratio = self.agents[top_agent_index].wealth / (total_wealth_s + total_wealth_r)
        self.top_agent_wealth_ratio.append(top_agent_wealth_ratio)
        sorted_wealth = sorted(wealth_list, reverse=True)
        top_n = max(1, int(0.1 * len(sorted_wealth)))
        top_10p_ratio = sum(sorted_wealth[:top_n]) / (total_wealth_s + total_wealth_r)
        self.top_10p_wealth_ratio.append(top_10p_ratio)

        average_beta = total_wealth_r / (total_wealth_s + total_wealth_r)
        self.beta_history.append(average_beta)

        self.total_number_of_crisis.append(sum(self.state))
        self.total_period.append(t)
        gamma_period = 0 if self.total_number_of_crisis[-1] == 0 else (t + 1) / self.total_number_of_crisis[-1]

        r_bar_t = self.r_bar_strategy(t)
        self.r_bar_history.append(r_bar_t)
        denom = (r_R_N - r_S) * (1 - r_bar_t)
        gamma_star = (1 + r_R_N) / denom if denom != 0 else float("inf")
        self.gamma_period_history.append(gamma_period)
        self.gamma_star_history.append(gamma_star)

        if t > 0:
            self.k_ast.append(1 - ((1 + r_R_N)/(r_R_N - r_S))*(self.total_number_of_crisis[-1] / self.total_period[-1])) # valid only when r_R_C = -1
        else:  # i.e., t=0
            self.k_ast.append(-1)

        if average_beta > r_bar_t:
            self.state.append(1)
            return CRISIS
        elif average_beta <= r_bar_t:
            self.state.append(0)
            return NORMAL
        else:
            sys.exit("global state error: average_beta: %d" % average_beta)

        # total_number_of_crisis = 0
        # total_period = 0
        # for beta in self.beta_history:
        #     if beta > R_BAR:
        #         total_period += 1
        #         total_number_of_crisis += 1
        #     else:
        #         total_period += 1


class Agent:
    def __init__(self, beta, initial_wealth_setting):
        if initial_wealth_setting == INITIAL_WEALTH_SAME:
            self.wealth = self.initial_wealth = INITIAL_WEALTH
        elif initial_wealth_setting == INITIAL_WEALTH_RANDOM:
            self.wealth = self.initial_wealth = INITIAL_WEALTH * random.random()
        else:
            sys.exit("initial_wealth_setting error: current initial_wealth_setting:%d" % initial_wealth_setting)
        self.beta = beta
        self.r_R = None
        self.r_S = None

    def update(self, global_state, crisis_return):
        if global_state == NORMAL:
            self.r_R = r_R_N
            self.r_S = r_S
        elif global_state == CRISIS:
            self.r_R = crisis_return
            self.r_S = r_S
        else:
            sys.exit("global state setting error:: check code")
        self.wealth = self.beta * self.wealth * (1 + self.r_R) + (1 - self.beta) * self.wealth * (1 + self.r_S)


# simulation initialization

class Simulation:
    def __init__(self, beta_setting, initial_wealth_setting, model_number, progress_every, r_bar_strategy, crisis_return, model_label):
        self.world = World(beta_setting=beta_setting, initial_wealth_setting=initial_wealth_setting,
                           model_number=model_number, r_bar_strategy=r_bar_strategy, crisis_return=crisis_return)
        self.progress_every = progress_every
        self.model_label = model_label

    def run(self):
        for t in range(0, T):
            if t == 0 or (t + 1) % self.progress_every == 0 or t == T - 1:
                print("time = %d" % t)
            self.world.update(t)

    def save(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        beta_history = pd.DataFrame(self.world.beta_history)
        beta_distribution = pd.DataFrame([agent.beta for agent in self.world.agents])
        final_wealth_distribution = pd.DataFrame([agent.wealth for agent in self.world.agents])
        initial_wealth_distribution = pd.DataFrame([agent.initial_wealth for agent in self.world.agents])

        aggregated_vars = pd.DataFrame([self.world.total_period,
                                        self.world.beta_history,
                                        self.world.top_agent_beta_i_history,
                                        self.world.top_agent_wealth_ratio,
                                        self.world.top_10p_wealth_ratio,
                                        self.world.state,
                                        self.world.k_ast,
                                        self.world.total_number_of_crisis,
                                        self.world.gamma_period_history,
                                        self.world.gamma_star_history,
                                        self.world.r_bar_history]).transpose()
        aggregated_vars.columns = ["t",
                                   "hat_beta_t",
                                   "argmax_Wit",
                                   "top_agent_wealth_ratio",
                                   "top_10p_wealth_ratio",
                                   "state_t",
                                   "k_ast_t",
                                   "Gamma_t",
                                   "gamma_period_t",
                                   "gamma_star_t",
                                   "r_bar_t"]
        # state_history = pd.DataFrame(self.world.state)
        # t_history = pd.DataFrame(self.world.total_period)
        # gamma_history = pd.DataFrame(self.world.total_number_of_crisis)
        # k_ast_history = pd.DataFrame(self.world.k_ast)
        # top_agent_beta_i_history = pd.DataFrame(self.world.top_agent_beta_i_history)

        prefix = f"{self.model_label}_Model{self.world.model_number}"

        beta_history.to_csv(OUTPUT_DIR / (f"{prefix}_{AVERAGE_BETA_FILENAME}_.csv"))
        beta_distribution.to_csv(OUTPUT_DIR / (f"{prefix}_{BETA_DISTRIBUTION_FILENAME}_.csv"))
        initial_wealth_distribution.to_csv(OUTPUT_DIR / (f"{prefix}_{INITIAL_WEALTH_FILENAME}_.csv"))
        final_wealth_distribution.to_csv(OUTPUT_DIR / (f"{prefix}_{FINAL_WEALTH_FILENAME}_.csv"))

        # state_history.to_csv("Model%s_%s_.csv" % (self.world.model_number, STATE_FILENAME))
        # t_history.to_csv("Model%s_%s_.csv" % (self.world.model_number, T_FILENAME))
        # gamma_history.to_csv("Model%s_%s_.csv" % (self.world.model_number, GAMMA_FILENAME))
        # k_ast_history.to_csv("Model%s_%s_.csv" % (self.world.model_number, K_AST_FILENAME))
        # top_agent_beta_i_history.to_csv("Model%s_%s_.csv" % (self.world.model_number, TOP_AGENT_BETA_I_FILENAME))

        aggregated_vars.to_csv(OUTPUT_DIR / (f"{prefix}_{AGGREGATED_VARS_FILENAME}_.csv"))


# Main Procedure
def make_r_bar_strategy(scenario: str, base_r_bar: float, sigma: float) -> Callable[[int], float]:
    def clipped_random():
        draw = np.random.normal(base_r_bar, sigma)
        return float(np.clip(draw, 0.0, 1.0))

    if scenario in (MODEL_B, MODEL_D):
        if sigma <= 0:
            return lambda t: base_r_bar
        return lambda t: clipped_random()
    else:
        return lambda t: base_r_bar


def parse_args():
    parser = argparse.ArgumentParser(description="Evolutionary portfolio simulation")
    parser.add_argument("--n", type=int, default=N, help="Number of investors")
    parser.add_argument("--t", type=int, default=T, help="Time horizon")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Directory for CSV outputs")
    parser.add_argument("--progress-every", type=int, default=PROGRESS_EVERY, help="Print progress every N steps")
    parser.add_argument("--scenario", choices=[MODEL_A, MODEL_B, MODEL_C, MODEL_D], default=MODEL_A,
                        help="Model A: fixed R̄, r_C=-1; Model B: variable R̄; Model C: relaxed crisis return; "
                             "Model D: variable R̄ + relaxed crisis return")
    parser.add_argument("--rbar-base", type=float, default=R_BAR, help="Base threshold R̄")
    parser.add_argument("--rbar-sigma", type=float, default=0.0,
                        help="Std dev for R̄ shocks in Model B (0 disables randomness)")
    parser.add_argument("--crisis-return", type=float, default=-0.5,
                        help="Crisis return r_C for Model C (must be <= r_S and >= -1)")
    return parser.parse_args()


def main():
    global N, T, OUTPUT_DIR, PROGRESS_EVERY, r_R_C, R_BAR

    args = parse_args()
    if args.rbar_base < 0 or args.rbar_base > 1:
        sys.exit("rbar_base must be in [0, 1]")
    if args.scenario in (MODEL_C, MODEL_D):
        if args.crisis_return < -1.0 or args.crisis_return >= r_S:
            sys.exit(f"crisis_return must satisfy -1 <= r_C < r_S ({r_S})")
        r_R_C = args.crisis_return
    else:
        r_R_C = -1.0

    N = args.n
    T = args.t
    OUTPUT_DIR = args.output_dir / f"{args.scenario.lower()}"
    PROGRESS_EVERY = args.progress_every
    R_BAR = args.rbar_base

    r_bar_strategy = make_r_bar_strategy(scenario=args.scenario, base_r_bar=args.rbar_base, sigma=args.rbar_sigma)
    model_label = f"Model{args.scenario}"

    print("Simulation Started.")
    print(f"Parameters: N={N}, T={T}, scenario={args.scenario}, R_bar_base={args.rbar_base}, "
          f"rbar_sigma={args.rbar_sigma}, r_C={r_R_C}, output_dir={OUTPUT_DIR}, progress_every={PROGRESS_EVERY}")

    models = Models(r_bar_strategy=r_bar_strategy, crisis_return=r_R_C, model_label=model_label)
    models.run()
    print("Simulation Ended.")


if __name__ == "__main__":
    main()
