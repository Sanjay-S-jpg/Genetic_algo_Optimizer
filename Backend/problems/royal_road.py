import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

def get_param_fields():
    return [
        {"name": "n", "label": "Number of Bits", "type": "number", "default": 64, "min": 8, "max": 512},
        {"name": "block_size", "label": "Block Size", "type": "number", "default": 8, "min": 2, "max": 32},
        {"name": "population_size", "label": "Population Size", "type": "number", "default": 100, "min": 10, "max": 500},
        {"name": "generations", "label": "Generations", "type": "number", "default": 100, "min": 1, "max": 1000},
        {"name": "mutation_rate", "label": "Mutation Rate", "type": "number", "default": 0.01, "min": 0, "max": 1, "step": 0.01},
    ]

def fitness(ind, block_size):
    score = 0
    for i in range(0, len(ind), block_size):
        block = ind[i:i+block_size]
        if all(x == 1 for x in block):
            score += block_size
    return score

def create_individual(n):
    return [random.randint(0, 1) for _ in range(n)]

def breed(p1, p2):
    point = random.randint(1, len(p1)-1)
    return p1[:point] + p2[point:]

def mutate(ind, rate):
    return [g if random.random() > rate else 1-g for g in ind]

def run_problem(params):
    n = int(params.get("n", 64))
    block_size = int(params.get("block_size", 8))
    population_size = int(params.get("population_size", 100))
    generations = int(params.get("generations", 100))
    mutation_rate = float(params.get("mutation_rate", 0.01))
    pop = [create_individual(n) for _ in range(population_size)]
    history = []
    best, best_fit = None, float('-inf')
    for g in range(generations):
        fits = [fitness(ind, block_size) for ind in pop]
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
    plot_path = f"plots/royalroad_{unique_id}.png"
    plt.figure()
    plt.plot(history, label="Best Fitness")
    plt.xlabel("Generation")
    plt.ylabel("Royal Road Score")
    plt.title("Royal Road Progress")
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