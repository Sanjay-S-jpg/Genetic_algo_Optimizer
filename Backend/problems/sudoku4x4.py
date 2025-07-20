import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

def get_param_fields():
    return [
        {"name": "population_size", "label": "Population Size", "type": "number", "default": 100, "min": 10, "max": 300},
        {"name": "generations", "label": "Generations", "type": "number", "default": 150, "min": 1, "max": 1000},
        {"name": "mutation_rate", "label": "Mutation Rate", "type": "number", "default": 0.1, "min": 0, "max": 1, "step": 0.01},
    ]

def create_individual():
    # 4x4 grid, flatten to list
    ind = []
    for _ in range(4):
        row = [1,2,3,4]
        random.shuffle(row)
        ind.extend(row)
    return ind

def fitness(ind):
    grid = [ind[i*4:(i+1)*4] for i in range(4)]
    score = 0
    # Row uniqueness
    for row in grid:
        score += len(set(row))
    # Column uniqueness
    for c in range(4):
        score += len(set(grid[r][c] for r in range(4)))
    # 2x2 box uniqueness
    for br in [0,2]:
        for bc in [0,2]:
            box = [grid[r][c] for r in range(br,br+2) for c in range(bc,bc+2)]
            score += len(set(box))
    return score

def breed(p1, p2):
    point = random.randint(1, len(p1)-1)
    return p1[:point] + p2[point:]

def mutate(ind, rate):
    ind = ind[:]
    for i in range(len(ind)):
        if random.random() < rate:
            ind[i] = random.randint(1,4)
    return ind

def run_problem(params):
    population_size = int(params.get("population_size", 100))
    generations = int(params.get("generations", 150))
    mutation_rate = float(params.get("mutation_rate", 0.1))

    pop = [create_individual() for _ in range(population_size)]
    history = []
    best, best_fit = None, 0
    for g in range(generations):
        fits = [fitness(ind) for ind in pop]
        gen_best = max(fits)
        if gen_best > best_fit:
            best_fit = gen_best
            best = pop[fits.index(gen_best)]
        history.append(gen_best)
        # Selection
        selected = [pop[i] for i in sorted(range(len(fits)), key=lambda i: fits[i], reverse=True)[:population_size//2]]
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
    plot_path = f"plots/sudoku4x4_{unique_id}.png"
    plt.figure()
    plt.plot(history, label="Best Fitness")
    plt.xlabel("Generation")
    plt.ylabel("Total Row/Col/Box Uniqueness")
    plt.title("Sudoku 4x4 Progress")
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