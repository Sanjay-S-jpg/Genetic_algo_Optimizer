import pandas as pd
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import os

def get_param_fields():
    # These will be filled from frontend after CSV upload
    return [
        {"name": "csv_filename", "label": "CSV Filename", "type": "text"},
        {"name": "objective_col", "label": "Objective Column", "type": "text"},
        {"name": "maximize", "label": "Maximize?", "type": "boolean", "default": True},
        {"name": "constraint_col", "label": "Constraint Column", "type": "text", "optional": True},
        {"name": "constraint_op", "label": "Constraint Operator", "type": "text", "optional": True}, # e.g. "<=", "=="
        {"name": "constraint_value", "label": "Constraint Value", "type": "number", "optional": True},
        {"name": "population_size", "label": "Population Size", "type": "number", "default": 50},
        {"name": "generations", "label": "Generations", "type": "number", "default": 30},
        {"name": "mutation_rate", "label": "Mutation Rate", "type": "number", "default": 0.1, "step": 0.01},
    ]

def constraint_pass(row, col, op, val):
    if not col or not op or val is None or val == "":
        return True
    if op == "<=":
        return row[col] <= val
    if op == "<":
        return row[col] < val
    if op == "==":
        return row[col] == val
    if op == ">=":
        return row[col] >= val
    if op == ">":
        return row[col] > val
    return True

def fitness(row, params):
    if not constraint_pass(
        row,
        params.get("constraint_col"),
        params.get("constraint_op"),
        params.get("constraint_value"),
    ):
        return float("-inf") if params.get("maximize", True) else float("inf")
    return row[params["objective_col"]]

def run_problem(params):
    csv_path = os.path.join("uploaded_csvs", params["csv_filename"])
    df = pd.read_csv(csv_path)
    maximize = params.get("maximize", True)
    pop_size = int(params.get("population_size", 50))
    generations = int(params.get("generations", 30))
    mutation_rate = float(params.get("mutation_rate", 0.1))
    # For simplicity, each solution is just a row index
    pop = [random.randint(0, len(df) - 1) for _ in range(pop_size)]
    history = []
    best_idx, best_fit = None, float("-inf") if maximize else float("inf")
    for g in range(generations):
        fits = [fitness(df.iloc[i], params) for i in pop]
        if maximize:
            gen_best = max(fits)
        else:
            gen_best = min(fits)
        if (maximize and gen_best > best_fit) or (not maximize and gen_best < best_fit):
            best_fit = gen_best
            best_idx = pop[fits.index(gen_best)]
        history.append(gen_best)
        # Selection: top 50%
        selected = [pop[i] for i in sorted(range(len(fits)), key=lambda i: fits[i], reverse=maximize)[: pop_size // 2]]
        # Crossover/mutation (just random for demo)
        new_pop = []
        while len(new_pop) < pop_size:
            i = random.choice(selected)
            if random.random() < mutation_rate:
                i = random.randint(0, len(df) - 1)
            new_pop.append(i)
        pop = new_pop
    # Plot
    plot_path = f"plots/csv_opt_{int(time.time() * 1000)}.png"
    if not os.path.exists("plots"):
        os.makedirs("plots")
    plt.figure()
    plt.plot(history, label="Best Fitness")
    plt.xlabel("Generation")
    plt.ylabel("Objective Value")
    plt.title("CSV Optimization Progress")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    result_row = df.iloc[best_idx]

    def convert_value(v):
        if hasattr(v, "item"):
            return v.item()  # converts numpy types to plain Python
        return v

    result = {
        "best": {k: convert_value(v) for k, v in result_row.to_dict().items()},
        "best_score": float(best_fit),
        "history": [float(x) for x in history]  # make sure history is native floats
    }
    return result, plot_path