import argparse
import sys
import random
from pathlib import Path

import numpy as np
import pandas as pd

# main param

N = 10000
T = 10000
r_R_N = 0.1             # risky asset return (in normal state)
r_R_C = -1              # risky asset return (in crisis state)
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

# class define


class Models:
    def __init__(self):
        self.models = []
        model_number = 1

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
                                    progress_every=PROGRESS_EVERY)
            simulation.run()
            simulation.save()


class Model:
    def __init__(self, beta_setting, initial_wealth_setting, model_number):
        self.beta_setting = beta_setting
        self.initial_wealth_setting = initial_wealth_setting
        self.model_number = model_number


class World:
    def __init__(self, beta_setting, initial_wealth_setting, model_number):
        self.agents = []
        self.beta_history = []
        self.k_ast = []
        self.state = []
        self.total_period = []
        self.model_number = model_number
        self.top_agent_beta_i_history = []
        self.top_agent_wealth_ratio = []
        self.total_number_of_crisis = []

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
            agent.update(global_state=global_state)   # set Wit+1

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

        average_beta = total_wealth_r / (total_wealth_s + total_wealth_r)
        self.beta_history.append(average_beta)

        self.total_number_of_crisis.append(sum(self.state))
        self.total_period.append(t)

        if t > 0:
            self.k_ast.append(1 - ((1 + r_R_N)/(r_R_N - r_S))*(self.total_number_of_crisis[-1] / self.total_period[-1]))
        else:  # i.e., t=0
            self.k_ast.append(-1)

        if average_beta > R_BAR:
            self.state.append(1)
            return CRISIS
        elif average_beta <= R_BAR:
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

    def update(self, global_state):
        if global_state == NORMAL:
            self.r_R = r_R_N
            self.r_S = r_S
        elif global_state == CRISIS:
            self.r_R = r_R_C
            self.r_S = r_S
        else:
            sys.exit("global state setting error:: check code")
        self.wealth = self.beta * self.wealth * (1 + self.r_R) + (1 - self.beta) * self.wealth * (1 + self.r_S)


# simulation initialization

class Simulation:
    def __init__(self, beta_setting, initial_wealth_setting, model_number, progress_every):
        self.world = World(beta_setting=beta_setting, initial_wealth_setting=initial_wealth_setting,
                           model_number=model_number)
        self.progress_every = progress_every

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
                                        self.world.state,
                                        self.world.k_ast,
                                        self.world.total_number_of_crisis]).transpose()
        aggregated_vars.columns = ["t",
                                   "hat_beta_t",
                                   "argmax_Wit",
                                   "top_agent_wealth_ratio",
                                   "state_t",
                                   "k_ast_t",
                                   "gamma_t"]
        # state_history = pd.DataFrame(self.world.state)
        # t_history = pd.DataFrame(self.world.total_period)
        # gamma_history = pd.DataFrame(self.world.total_number_of_crisis)
        # k_ast_history = pd.DataFrame(self.world.k_ast)
        # top_agent_beta_i_history = pd.DataFrame(self.world.top_agent_beta_i_history)

        beta_history.to_csv(OUTPUT_DIR / ("Model%s_%s_.csv" % (self.world.model_number, AVERAGE_BETA_FILENAME)))
        beta_distribution.to_csv(OUTPUT_DIR / ("Model%s_%s_.csv" % (self.world.model_number, BETA_DISTRIBUTION_FILENAME)))
        initial_wealth_distribution.to_csv(OUTPUT_DIR / ("Model%s_%s_.csv" % (self.world.model_number, INITIAL_WEALTH_FILENAME)))
        final_wealth_distribution.to_csv(OUTPUT_DIR / ("Model%s_%s_.csv" % (self.world.model_number, FINAL_WEALTH_FILENAME)))

        # state_history.to_csv("Model%s_%s_.csv" % (self.world.model_number, STATE_FILENAME))
        # t_history.to_csv("Model%s_%s_.csv" % (self.world.model_number, T_FILENAME))
        # gamma_history.to_csv("Model%s_%s_.csv" % (self.world.model_number, GAMMA_FILENAME))
        # k_ast_history.to_csv("Model%s_%s_.csv" % (self.world.model_number, K_AST_FILENAME))
        # top_agent_beta_i_history.to_csv("Model%s_%s_.csv" % (self.world.model_number, TOP_AGENT_BETA_I_FILENAME))

        aggregated_vars.to_csv(OUTPUT_DIR / ("Model%s_%s_.csv" % (self.world.model_number, AGGREGATED_VARS_FILENAME)))


# Main Procedure
def parse_args():
    parser = argparse.ArgumentParser(description="Evolutionary portfolio simulation")
    parser.add_argument("--n", type=int, default=N, help="Number of investors")
    parser.add_argument("--t", type=int, default=T, help="Time horizon")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Directory for CSV outputs")
    parser.add_argument("--progress-every", type=int, default=PROGRESS_EVERY, help="Print progress every N steps")
    return parser.parse_args()


def main():
    global N, T, OUTPUT_DIR, PROGRESS_EVERY

    args = parse_args()
    N = args.n
    T = args.t
    OUTPUT_DIR = args.output_dir
    PROGRESS_EVERY = args.progress_every

    print("Simulation Started.")
    print(f"Parameters: N={N}, T={T}, output_dir={OUTPUT_DIR}, progress_every={PROGRESS_EVERY}")

    models = Models()
    models.run()
    print("Simulation Ended.")


if __name__ == "__main__":
    main()
