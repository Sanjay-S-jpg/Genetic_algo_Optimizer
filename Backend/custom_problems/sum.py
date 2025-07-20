import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

def get_param_fields():
    return [
        {"name": "length", "label": "List Length", "type": "number", "default": 10},
        {"name": "target", "label": "Target Sum", "type": "number", "default": 50},
        {"name": "population_size", "label": "Population Size", "type": "number", "default": 100},
        {"name": "generations", "label": "Generations", "type": "number", "default": 100},
        {"name": "mutation_rate", "label": "Mutation Rate", "type": "number", "default": 0.1, "min": 0, "max": 1, "step": 0.01},
    ]

def create_individual(length):
    # Each gene is an integer between 0 and 20
    return [random.randint(0, 20) for _ in range(length)]

def fitness(individual, target):
    return -abs(sum(individual) - target)  # Closest to target is best (max fitness)

def breed(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    return parent1[:point] + parent2[point:]

def mutate(individual, mutation_rate):
    return [
        gene if random.random() > mutation_rate else random.randint(0, 20)
        for gene in individual
    ]

class GeneticAlgorithm:
    def __init__(self, create_individual, fitness, breed, mutate, population_size, generations, mutation_rate, length, target):
        self.create_individual = create_individual
        self.fitness = fitness
        self.breed = breed
        self.mutate = mutate
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.length = length
        self.target = target

    def run(self):
        population = [self.create_individual(self.length) for _ in range(self.population_size)]
        history = []
        best = None
        best_score = float("-inf")
        for gen in range(self.generations):
            scores = [self.fitness(ind, self.target) for ind in population]
            gen_best_score = max(scores)
            gen_best = population[scores.index(gen_best_score)]
            if gen_best_score > best_score:
                best = gen_best
                best_score = gen_best_score
            history.append(gen_best_score)
            # Selection (top 50%)
            selected = [population[i] for i in sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:self.population_size // 2]]
            # Create new population
            next_population = []
            while len(next_population) < self.population_size:
                parents = random.sample(selected, 2)
                child = self.breed(parents[0], parents[1])
                child = self.mutate(child, self.mutation_rate)
                next_population.append(child)
            population = next_population
        return best, best_score, history

def run_problem(params):
    length = int(params.get("length", 10))
    target = int(params.get("target", 50))
    population_size = int(params.get("population_size", 100))
    generations = int(params.get("generations", 100))
    mutation_rate = float(params.get("mutation_rate", 0.1))

    ga = GeneticAlgorithm(
        create_individual=create_individual,
        fitness=fitness,
        breed=breed,
        mutate=mutate,
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate,
        length=length,
        target=target,
    )
    best, score, history = ga.run()

    # Plotting history
    import os
    if not os.path.exists("plots"):
        os.makedirs("plots")
    unique_id = str(int(time.time() * 1000))
    plot_path = f"plots/sum_target_{unique_id}.png"
    plt.figure()
    plt.plot(history, label="Best Fitness")
    plt.xlabel("Generation")
    plt.ylabel("Best Fitness (closer to 0 is better)")
    plt.title("Sum Target GA Progress")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    result = {
        "best": best,
        "score": score,
        "history": history
    }
    return result, plot_path