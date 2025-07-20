import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

def get_param_fields():
    return [
        {"name": "list_length", "label": "List Length", "type": "number", "default": 10, "min": 2, "max": 40},
        {"name": "max_value", "label": "Max Value", "type": "number", "default": 20, "min": 2, "max": 100},
        {"name": "population_size", "label": "Population Size", "type": "number", "default": 50, "min": 10, "max": 200},
        {"name": "generations", "label": "Generations", "type": "number", "default": 50, "min": 1, "max": 200},
        {"name": "mutation_rate", "label": "Mutation Rate", "type": "number", "default": 0.08, "min": 0, "max": 1, "step": 0.01},
    ]

def create_individual(list_length, max_value):
    return [random.randint(0, max_value) for _ in range(list_length)]

def fitness(ind):
    return sum(x for x in ind if x % 2 == 0)

def breed(p1, p2):
    point = random.randint(1, len(p1) - 2)
    return p1[:point] + p2[point:]

def mutate(ind, max_value, rate):
    return [x if random.random() > rate else random.randint(0, max_value) for x in ind]

def run_problem(params):
    list_length = int(params.get("list_length", 10))
    max_value = int(params.get("max_value", 20))
    population_size = int(params.get("population_size", 50))
    generations = int(params.get("generations", 50))
    mutation_rate = float(params.get("mutation_rate", 0.08))

    pop = [create_individual(list_length, max_value) for _ in range(population_size)]
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
            child = mutate(child, max_value, mutation_rate)
            next_pop.append(child)
        pop = next_pop

    # Plot
    import os
    if not os.path.exists("plots"):
        os.makedirs("plots")
    unique_id = str(int(time.time() * 1000))
    plot_path = f"plots/even_sum_{unique_id}.png"
    plt.figure()
    plt.plot(history, label="Best Even Sum")
    plt.xlabel("Generation")
    plt.ylabel("Sum of Even Numbers")
    plt.title("Even Number Sum Progress")
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