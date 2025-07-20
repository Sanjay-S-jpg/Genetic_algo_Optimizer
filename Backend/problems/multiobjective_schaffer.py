import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

def get_param_fields():
    return [
        {"name": "population_size", "label": "Population Size", "type": "number", "default": 100, "min": 10, "max": 300},
        {"name": "generations", "label": "Generations", "type": "number", "default": 60, "min": 1, "max": 500},
        {"name": "mutation_rate", "label": "Mutation Rate", "type": "number", "default": 0.1, "min": 0, "max": 1, "step": 0.01},
    ]

def objectives(x):
    return x**2, (x-2)**2

def dominates(a, b):
    return (a[0]<=b[0] and a[1]<=b[1]) and (a[0]<b[0] or a[1]<b[1])

def fast_non_dominated_sort(pop_objs):
    S = [[] for _ in range(len(pop_objs))]
    n = [0]*len(pop_objs)
    rank = [0]*len(pop_objs)
    fronts = [[]]
    for p in range(len(pop_objs)):
        S[p] = []
        n[p] = 0
        for q in range(len(pop_objs)):
            if dominates(pop_objs[p], pop_objs[q]):
                S[p].append(q)
            elif dominates(pop_objs[q], pop_objs[p]):
                n[p] += 1
        if n[p] == 0:
            rank[p] = 0
            fronts[0].append(p)
    i = 0
    while fronts[i]:
        next_front = []
        for p in fronts[i]:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    rank[q] = i+1
                    next_front.append(q)
        i += 1
        fronts.append(next_front)
    return fronts[:-1]

def create_individual():
    return random.uniform(-10, 10)

def mutate(x, rate):
    if random.random() < rate:
        return x + random.gauss(0, 1)
    return x

def crossover(x1, x2):
    alpha = random.random()
    return alpha*x1 + (1-alpha)*x2

def run_problem(params):
    population_size = int(params.get("population_size", 100))
    generations = int(params.get("generations", 60))
    mutation_rate = float(params.get("mutation_rate", 0.1))
    pop = [create_individual() for _ in range(population_size)]
    pareto_hist = []

    for g in range(generations):
        objs = [objectives(x) for x in pop]
        fronts = fast_non_dominated_sort(objs)
        pareto = [pop[i] for i in fronts[0]]
        pareto_objs = [objs[i] for i in fronts[0]]
        pareto_hist.append(pareto_objs)
        # Selection: Keep only Pareto front + random fill
        selected = [pop[i] for i in fronts[0]]
        while len(selected) < population_size//2:
            selected.append(random.choice(pop))
        # Create new population by crossover and mutation
        new_pop = []
        while len(new_pop) < population_size:
            p1, p2 = random.sample(selected, 2)
            child = crossover(p1, p2)
            child = mutate(child, mutation_rate)
            child = min(10, max(-10, child))
            new_pop.append(child)
        pop = new_pop

    # Final Pareto front
    objs = [objectives(x) for x in pop]
    fronts = fast_non_dominated_sort(objs)
    pareto = [pop[i] for i in fronts[0]]
    pareto_objs = [objs[i] for i in fronts[0]]

    # Plot Pareto front
    import os
    if not os.path.exists("plots"):
        os.makedirs("plots")
    unique_id = str(int(time.time() * 1000))
    plot_path = f"plots/multiobj_schaffer_{unique_id}.png"
    plt.figure(figsize=(6,4))
    plt.scatter([x[0] for x in pareto_objs], [x[1] for x in pareto_objs], c="red", label="Pareto Front")
    plt.xlabel("Objective 1: x^2")
    plt.ylabel("Objective 2: (x-2)^2")
    plt.title("Pareto Front - Schaffer Function N.1")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    result = {
        "best": pareto,
        "pareto_objs": pareto_objs,
        "history": pareto_hist,
        "score": "Pareto front of size %d" % len(pareto),
    }
    return result, plot_path