# imports
import math
import matplotlib.pyplot as plt

import BRKGA as brkga  # BRKGA framework (problem independent)
import DECODER_DUMMY as decoder  # Dgcoder algorithm (problem-dependent)
# Input data (problem-dependent and instance-dependent)
from DATA_DUMMY import data
# Configuration parameters (problem-dependent and execution-dependent)
from CONFIGURATION import config
import pprint
print config
# initializations
numIndividuals = int(config['numIndividuals'])
chrLength = int(config['chromosomeLength'])
numElite = int(math.ceil(numIndividuals * config['eliteProp']))
numMutants = int(math.ceil(numIndividuals * config['mutantProp']))
numCrossover = max(numIndividuals - numElite - numMutants, 0)
maxNumGen = int(config['maxNumGen'])
ro = float(config['inheritanceProb'])
evol = []

# Main body

population = brkga.initializePopulation(numIndividuals, chrLength)

i = 0
while (i < maxNumGen):
    population = decoder.decode(population, data)
    evol.append(brkga.getBestFitness(population)['fitness'])
    if numElite > 0:
        elite, nonelite = brkga.classifyIndividuals(population, numElite)
    else:
        elite = []
        nonelite = population
    if numMutants > 0:
        mutants = brkga.generateMutantIndividuals(numMutants, chrLength)
    else:
        mutants = []
    if numCrossover > 0:
        crossover = brkga.doCrossover(elite, nonelite, ro, numCrossover)
    else:
        crossover = []
    population = elite + crossover + mutants
    i += 1

population = decoder.decode(population, data)
bestIndividual = brkga.getBestFitness(population)

#pprint.pprint(bestIndividual['solution'])

usedNurses = [0]*data['hours']
nursesPresence = [0]*data['numNurses']
for idNurse, nurse in enumerate(bestIndividual['solution']):
    maxWorkingHour = 0
    minWorkingHour = data['hours']
    for idHour, hour in enumerate(nurse):
        if hour == 1:
            if maxWorkingHour < idHour:
                maxWorkingHour = idHour
            if minWorkingHour > idHour:
                minWorkingHour = idHour
        usedNurses[idHour] += hour
        nursesPresence[idNurse] = max(maxWorkingHour - minWorkingHour + 1, 0)
    print 'Nurse ' + str(idNurse) + ' works: ' + ', '.join(map(str, nurse)) + '  Presence: ' + str(nursesPresence[idNurse]) + ' (Total ' + str(sum(nurse)) + 'h)' 

print 'Demand: ' + str(data['demand'])
print 'Assigned: ' + str(usedNurses)
print bestIndividual['fitness']

plt.plot(evol)
plt.xlabel('number of generations')
plt.ylabel('Fitness of best individual')
plt.axis([0, len(evol), 0, (chrLength + 1) * chrLength / 2])
plt.show()