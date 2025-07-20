import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time  # <-- add this line
from genetic_algorithm import GeneticAlgorithm

def get_param_fields():
    return [
        {"name": "length", "label": "List Length", "type": "number", "default": 10},
        {"name": "target", "label": "Target Sum", "type": "number", "default": 50},
        {"name": "population_size", "label": "Population Size", "type": "number", "default": 100},
        {"name": "generations", "label": "Generations", "type": "number", "default": 100},
        {"name": "mutation_rate", "label": "Mutation Rate", "type": "number", "default": 0.1, "min": 0, "max": 1, "step": 0.01},
    ]

def generate_cities(num_cities, seed=42):
    random.seed(seed)
    return [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(num_cities)]

def create_individual(city_indices):
    # Shuffle a list of city indices to represent a tour
    path = city_indices[:]
    random.shuffle(path)
    return path

def total_distance(tour, cities):
    dist = 0
    for i in range(len(tour)):
        x1, y1 = cities[tour[i]]
        x2, y2 = cities[tour[(i+1) % len(tour)]]
        dist += ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    return dist

def fitness(individual, cities):
    # Lower distance is better, so invert
    dist = total_distance(individual, cities)
    return 1 / (dist + 1e-6)

def breed(parent1, parent2):
    # Order Crossover (OX)
    size = len(parent1)
    start, end = sorted([random.randint(0, size-1) for _ in range(2)])
    child = [None] * size
    child[start:end+1] = parent1[start:end+1]
    fill = [gene for gene in parent2 if gene not in child]
    ptr = 0
    for i in range(size):
        if child[i] is None:
            child[i] = fill[ptr]
            ptr += 1
    return child

def mutate(individual, mutation_rate):
    ind = individual[:]
    for i in range(len(ind)):
        if random.random() < mutation_rate:
            j = random.randint(0, len(ind)-1)
            ind[i], ind[j] = ind[j], ind[i]
    return ind

def run_problem(params):
    num_cities = int(params.get("num_cities", 10))
    population_size = int(params.get("population_size", 100))
    generations = int(params.get("generations", 100))
    mutation_rate = float(params.get("mutation_rate", 0.05))
    seed = int(params.get("seed", 42))

    cities = generate_cities(num_cities, seed)
    city_indices = list(range(num_cities))

    ga = GeneticAlgorithm(
        create_individual=lambda: create_individual(city_indices),
        fitness=lambda ind: fitness(ind, cities),
        breed=breed,
        mutate=mutate,
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate
    )
    best, score, history = ga.run()
    best_distance = total_distance(best, cities)

    import os
    if not os.path.exists("plots"):
        os.makedirs("plots")
    unique_id = str(int(time.time() * 1000))
    plot_path = f"plots/tsp_fitness_{unique_id}.png"
    plt.figure()
    plt.plot([1/(h+1e-6) for h in history], label="Best Distance")
    plt.xlabel("Generation")
    plt.ylabel("Distance")
    plt.title("TSP Progress")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    # Plot best path (optional)
    # best_path_plot = f"plots/tsp_best_path_{unique_id}.png"
    # plt.figure()
    # path = best + [best[0]]
    # xs = [cities[i][0] for i in path]
    # ys = [cities[i][1] for i in path]
    # plt.plot(xs, ys, marker='o')
    # plt.title("Best Tour")
    # plt.savefig(best_path_plot)
    # plt.close()

    
    result = {
        "best": best,
        "score": score,
        "history": history  # <--- add this!
    }
    return result, plot_path