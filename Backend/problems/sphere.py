import random
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

def get_param_fields():
    return [
        {"name": "dimensions", "label": "Dimensions", "type": "number", "default": 3, "min": 1, "max": 15},
        {"name": "population_size", "label": "Population Size", "type": "number", "default": 60, "min": 10, "max": 300},
        {"name": "generations", "label": "Generations", "type": "number", "default": 60, "min": 1, "max": 1000},
        {"name": "mutation_rate", "label": "Mutation Rate", "type": "number", "default": 0.08, "min": 0, "max": 1, "step": 0.01},
    ]

def sphere(x):
    return sum(xi**2 for xi in x)

def create_individual(dim):
    return [random.uniform(-5, 5) for _ in range(dim)]

def fitness(ind):
    return -sphere(ind)  # minimize

def breed(p1, p2):
    alpha = random.random()
    return [alpha*xi + (1-alpha)*yi for xi, yi in zip(p1, p2)]

def mutate(ind, rate):
    return [xi + random.gauss(0, 0.2) if random.random() < rate else xi for xi in ind]

def run_problem(params):
    dim = int(params.get("dimensions", 3))
    population_size = int(params.get("population_size", 60))
    generations = int(params.get("generations", 60))
    mutation_rate = float(params.get("mutation_rate", 0.08))
    pop = [create_individual(dim) for _ in range(population_size)]
    history = []
    best, best_fit = None, float('-inf')
    for g in range(generations):
        fits = [fitness(ind) for ind in pop]
        gen_best = max(fits)
        if gen_best > best_fit:
            best_fit = gen_best
            best = pop[fits.index(gen_best)]
        history.append(gen_best)
        selected = [pop[i] for i in sorted(range(len(fits)), key=lambda i: fits[i], reverse=True)[:population_size//2]]
        next_pop = []
        while len(next_pop) < population_size:
            p1, p2 = random.sample(selected, 2)
            child = breed(p1, p2)
            child = mutate(child, mutation_rate)
            next_pop.append(child)
        pop = next_pop
    import os
    if not os.path.exists("plots"):
        os.makedirs("plots")
    unique_id = str(int(time.time() * 1000))
    plot_path = f"plots/sphere_{unique_id}.png"
    plt.figure()
    plt.plot(history, label="Best (Negative) Sphere")
    plt.xlabel("Generation")
    plt.ylabel("Negative Sphere Value")
    plt.title("Sphere Progress")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    result = {
        "best": best,
        "score": best_fit,
        "history": history
    }
    return result, plot_path