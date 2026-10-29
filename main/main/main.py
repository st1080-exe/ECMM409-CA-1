# code base for the ECMM409 individual assignment
# the code takes the given data and attempts to optimise it using a genetic algorithm
# the problem asks to maximise the value of the contents of a van with a weight limitation
# this program will use a genetic algorithm with linear rank selection to complete the task
# parts of the code will be written using ai assistance and will be marked accordingly

#package imports
import re
import random
import numpy as np
import pygad as pg

capacity = 0
ids = 0
bags = 0
termination = 20
currentRun = 0
bestSolution = 0
populationNumber = 15

#data conversion into workable format
#code generated using claude ai
def convertData(data):
    vanCapacity = float(re.search(r"capacity:\s*([\d.]+)", data).group(1))  

    pattern = re.compile(r"bag\s+(\d+):\s*weight:\s*([\d.]+)\s*value:\s*([\d.]+)")

    rows = pattern.findall(data)
    arr = np.array(rows, dtype=float)

    ids     = arr[:, 0].astype(int)
    weights = arr[:, 1]
    values  = arr[:, 2].astype(int)

    bags = np.zeros(len(ids), dtype=[("id", int), ("weight", float), ("value", int)])
    bags["id"], bags["weight"], bags["value"] = ids, weights, values

    return vanCapacity, bags

#main
def main():

    global capacity
    global bags

    capacity, bags = convertData(open("BankProblem.txt").read())

    firstPopulationF = populationGen(bags, populationNumber)
    firstPopulationM = populationGen(bags, populationNumber)

    geneticAlgorithm(firstPopulationF, firstPopulationM)


def geneticAlgorithm(currentGenF, currentGenM):

    fitnessF = evalFunction(currentGenF)
    parentF = selection(fitnessF, currentGenF, 7)

    fitnessM = evalFunction(currentGenM)
    parentM = selection(fitnessM, currentGenM, 7)

    newGenF, newGenM  = crossover(parentF, parentM)

    newGenF = mutate(newGenF)
    newGenM = mutate(newGenM)

    newGenF = repair(newGenF, populationNumber)
    newGenM = repair(newGenM, populationNumber)




#populates first generation
def populate(dataSet):

    weight = 0
    chosenBagIDList = []

    while True:

        #gets random bag
        newBag = dataSet[random.randint(0,len(bags) - 1)]

        #if its a dupe re roll
        while newBag[0] in chosenBagIDList:
            newBag = dataSet[random.randint(0,len(bags) - 1)]

        #if it exceeds the capacity break out of loop
        if newBag[1] + weight > capacity:
            break

        #adds weight to total and id to list
        chosenBagIDList.append(newBag[0])
        weight += newBag[1]

    return chosenBagIDList

def populationGen(dataSet, popNum):
    population = []
    for i in range(popNum):
        population.append(populate(dataSet))
    return population


#sorts the generation based on fitness
def evalFunction(generation):

    fitnessNums = []

    for j in range(len(generation)):

        total = 0
        for i in range(len(generation[j])):
            total += bags[generation[j][i]-1][2]

        fitnessNums.append([j,total])

    sortedData = sorted(fitnessNums, key=lambda x: x[1])

    return sortedData

#selects parents
def selection(fitness, data, numOfRuns):

    #sums up the total fitness score
    total = 0
    
    for i in range(len(fitness)):
        total += fitness[i][1]

    selection = []
    i = 0
    while i < numOfRuns:

        #generates a random number
        num = random.uniform(0,total)

        runTime = 0

        candidate = 0

        #gradually moves up until the total reaches the random number
        for j in range(len(fitness)):

            if runTime >= num:
                candidate = j
                break
            
            runTime += fitness[j][1]

        if candidate not in selection:
            selection.append(data[candidate])
            i += 1

    return selection

def crossover(mother, father):

    cutoff = random.randint(1,len(mother)-1)
    child1 = mother[:cutoff]
    child2 = father[:cutoff]

    for i in range(len(mother) - cutoff):
        child1.append(father[-i-1])
        child2.append(mother[-i-1])

    prune(child1)
    prune(child2)
    return child1, child2

def prune(listOg):
    length = len(listOg)
    prunedList = []
    for i in range(length):
        if listOg[i] not in prunedList:
            prunedList.append(listOg[i])

    if len(prunedList) != length:
        prunedList.append(populate(bags))

def mutate(generation, rate):

    if random.random() < rate:
        generation.remove(random.choice(generation))
        generation.append(populate(bags))

    return generation

def repair(generation, popNum):

    while len(generation) < popNum:
        generation.append(populate(bags))

    return generation

main()