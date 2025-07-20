import random

class GeneticAlgorithm:
    def __init__(self, create_individual, fitness, breed, mutate, population_size=100, generations=100, mutation_rate=0.05):
        self.create_individual = create_individual
        self.fitness = fitness
        self.breed = breed
        self.mutate = mutate
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.history = []

    def run(self):
        population = [self.create_individual() for _ in range(self.population_size)]
        best_solution = None
        best_score = float('-inf')

        for gen in range(self.generations):
            scored_population = [(ind, self.fitness(ind)) for ind in population]
            scored_population.sort(key=lambda x: x[1], reverse=True)
            best_in_gen = scored_population[0]
            self.history.append(best_in_gen[1])

            if best_in_gen[1] > best_score:
                best_score = best_in_gen[1]
                best_solution = best_in_gen[0]

            # Selection: top 20% survive
            survivors = [ind for ind, _ in scored_population[:self.population_size // 5]]

            # Breeding
            children = []
            while len(children) < self.population_size - len(survivors):
                parent1 = random.choice(survivors)
                parent2 = random.choice(survivors)
                child = self.breed(parent1, parent2)
                child = self.mutate(child, self.mutation_rate)
                children.append(child)

            population = survivors + children

        return best_solution, best_score, self.history