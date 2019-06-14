# DB imodules
import trio_stat
import sqlite3
# Search modules
import random
import numpy
from deap import base
from deap import creator
from deap import tools
from deap import algorithms

DB_PATH = 'input/trios.sqlite'
conn = sqlite3.connect(DB_PATH)
curs = conn.cursor() # cursor for executing SQL queries

OVERALL_LIMIT = 99

"""Calculate score for given trio"""
def evaluate(trio):
    # trio = [player1, player2, player3]
    goals = [0,0,0] # goals scored by each player in the trio

    #check overall
    for player in trio:
        if numpy.mean(player) > OVERALL_LIMIT:
            return (-100000,) # return big negative number if overall doesn't fit limit
    MAX_TOLERANCE = 5
    for t in range(0,MAX_TOLERANCE+1):
        if 0 not in goals: 
            break
        for p in[ (0,1,2), (1,0,2), (2,1,0)]:
            if goals[p[0]] == 0:
                g = trio_stat.goals(trio[p[0]], trio[p[1]], trio[p[2]], curs, t) # get goals scored by each player in trio
                if g is not None:
                    goals[p[0]] = g
    return (sum(goals),) # evalute must return a tuple


#Setup DEAP toolbox
creator.create("GoalsMax", base.Fitness, weights=(1.0,))
creator.create("Player", list, fitness=creator.GoalsMax)
creator.create("Trio", list, fitness=creator.GoalsMax)

ATTRIBUTES_COUNT = len(trio_stat.attr_columns)

#Population
toolbox = base.Toolbox()
toolbox.register("player_attr", random.randint, 20, 99)
toolbox.register("player", tools.initRepeat, creator.Player,
                 toolbox.player_attr, n=ATTRIBUTES_COUNT)
toolbox.register("players_trio", tools.initRepeat, creator.Trio,
                 toolbox.player, n=3)
toolbox.register("population", tools.initRepeat, list, toolbox.players_trio)          

# Decorators
def checkBounds(min, max):
    def decorator(func):
        def wrapper(*args, **kargs):
            offspring = func(*args, **kargs)
            for trio in offspring:
                for player in trio:
                    for attr in player:
                        attr = round(attr)
                        if attr > max:
                            attr = max
                        elif attr < min:
                            attr = min
            return offspring
        return wrapper
    return decorator


def trioMutGaussian(trio, mu, sigma, indpb):
    """This function applies a gaussian mutation of mean *mu* and standard
    deviation *sigma* on the input trio. This mutation expects a
    :term:`sequence` trio composed of real valued attributes.
    The *indpb* argument is the probability of each attribute to be mutated.
    :param trio: Trio to be mutated.
    :param mu: Mean or :term:`python:sequence` of means for the
               gaussian addition mutation.
    :param sigma: Standard deviation or :term:`python:sequence` of
                  standard deviations for the gaussian addition mutation.
    :param indpb: Independent probability for each attribute to be mutated.
    :returns: A tuple of one trio.
    """
    
    for player in trio:        
        player = tools.mutGaussian(player, mu, sigma, indpb)
    
    return (trio,)

def trioCrossover(trio1, trio2):
    for i in range(0, len(trio1)):
        if random.randint(0,1) == 0:
            trio1[i] = trio2[i]
        else:
            trio2[i] = trio1[i]
    return trio1, trio2           



#Algorithm
toolbox.register("evaluate", evaluate) #Score function
toolbox.register("mate", trioCrossover) #Crossover
toolbox.register("mutate", trioMutGaussian, mu=1.0, sigma=0.2, indpb=0.2) # Mutation
#toolbox.register("select", tools.selTournament, tournsize=3) #Selection
toolbox.register("select",tools.selRoulette)
#toolbox.register("select", tools.selBest)

toolbox.decorate("mate", checkBounds(20,99))
toolbox.decorate("mutate", checkBounds(20,99))

"""
Run GA
Parameters:
    overall_limit - maximum overall of each player in a trio
    population – A list of individuals.
    toolbox – A Toolbox that contains the evolution operators.
    cxpb – The probability of mating two individuals.
    mutpb – The probability of mutating an individual.
    ngen – The number of generation.
    stats – A Statistics object that is updated inplace, optional.
    halloffame – A HallOfFame object that will contain the best individuals, optional.
    verbose – Whether or not to log the statistics.
"""
def run(overall_limit = 99, population = 300, cxpb = 0.5, mtpb = 0.2 , ngen = 40):
    OVERALL_LIMIT = overall_limit
    pop = toolbox.population(n=population)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
        
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mtpb, ngen=ngen, 
                                    stats=stats, halloffame=hof, verbose=True)
    return (pop, log, stats, hof)
