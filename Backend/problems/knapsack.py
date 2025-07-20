import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

ITEMS = [
    {"weight": 12, "value": 4},
    {"weight": 2, "value": 2},
    {"weight": 1, "value": 2},
    {"weight": 1, "value": 1},
    {"weight": 4, "value": 10},
    {"weight": 1, "value": 2},
    {"weight": 2, "value": 1},
]

def get_param_fields():
    return [
        {"name": "max_weight", "label": "Max Knapsack Weight", "type": "number", "default": 15, "min": 1, "max": 30},
        {"name": "population_size", "label": "Population Size", "type": "number", "default": 80, "min": 10, "max": 300},
        {"name": "generations", "label": "Generations", "type": "number", "default": 80, "min": 1, "max": 1000},
        {"name": "mutation_rate", "label": "Mutation Rate", "type": "number", "default": 0.05, "min": 0, "max": 1, "step": 0.01},
    ]

def create_individual():
    return [random.randint(0, 1) for _ in ITEMS]

def fitness(ind, max_weight):
    weight = sum(ind[i] * ITEMS[i]["weight"] for i in range(len(ITEMS)))
    value = sum(ind[i] * ITEMS[i]["value"] for i in range(len(ITEMS)))
    if weight > max_weight:
        return 0
    return value

def breed(p1, p2):
    point = random.randint(1, len(p1) - 1)
    return p1[:point] + p2[point:]

def mutate(ind, rate):
    return [gene if random.random() > rate else 1 - gene for gene in ind]

def run_problem(params):
    max_weight = int(params.get("max_weight", 15))
    population_size = int(params.get("population_size", 80))
    generations = int(params.get("generations", 80))
    mutation_rate = float(params.get("mutation_rate", 0.05))

    pop = [create_individual() for _ in range(population_size)]
    history = []
    best, best_fit = None, 0
    for g in range(generations):
        fits = [fitness(ind, max_weight) for ind in pop]
        gen_best = max(fits)
        if gen_best > best_fit:
            best_fit = gen_best
            best = pop[fits.index(gen_best)]
        history.append(gen_best)
        # Selection
        selected = [pop[i] for i in sorted(range(len(fits)), key=lambda i: fits[i], reverse=True)[:population_size//2]]
        # Breed/mutate
        next_pop = []
        while len(next_pop) < population_size:
            p1, p2 = random.sample(selected, 2)
            child = breed(p1, p2)
            child = mutate(child, mutation_rate)
            next_pop.append(child)
        pop = next_pop

    # Plot
    import os
    if not os.path.exists("plots"):
        os.makedirs("plots")
    unique_id = str(int(time.time() * 1000))
    plot_path = f"plots/knapsack_{unique_id}.png"
    plt.figure()
    plt.plot(history, label="Best Fitness")
    plt.xlabel("Generation")
    plt.ylabel("Max Value Achieved")
    plt.title("Knapsack Progress")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    picked = [i for i, x in enumerate(best) if x]
    result = {
        "best": best,
        "score": best_fit,
        "items_picked": picked,
        "total_weight": sum(ITEMS[i]["weight"] for i in picked),
        "total_value": sum(ITEMS[i]["value"] for i in picked),
        "history": history
    }
    return result, plot_path