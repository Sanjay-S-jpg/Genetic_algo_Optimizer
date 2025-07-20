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

def create_individual(length):
    return [random.randint(0, 1) for _ in range(length)]

def fitness(individual):
    return sum(individual)

def breed(parent1, parent2):
    point = random.randint(1, len(parent1)-1)
    return parent1[:point] + parent2[point:]

def mutate(individual, mutation_rate):
    return [bit if random.random() > mutation_rate else 1-bit for bit in individual]

def run_problem(params):
    length = int(params.get("length", 50))
    population_size = int(params.get("population_size", 100))
    generations = int(params.get("generations", 100))
    mutation_rate = float(params.get("mutation_rate", 0.05))

    ga = GeneticAlgorithm(
        create_individual=lambda: create_individual(length),
        fitness=fitness,
        breed=breed,
        mutate=mutate,
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate
    )
    best, score, history = ga.run()
    # Plot
    import os
    if not os.path.exists("plots"):
        os.makedirs("plots")
    unique_id = str(int(time.time() * 1000))  # Unique per run
    plot_path = f"plots/max_ones_fitness_{unique_id}.png"
    plt.figure()
    plt.plot(history, label="Best Fitness")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("Max Ones Progress")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    
    result = {
        "best": best,
        "score": score,
        "history": history  # <--- add this!
    }
    return result, plot_path    