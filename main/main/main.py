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

#global vars
capacity = 0
ids = 0
bags = 0

# run determining vars
termination = 10000
populationNumber = 20

#main
def main():

    global capacity
    global bags

    #opens data set
    capacity, bags = convertData(open("BankProblem.txt").read())

    #generates initial population
    firstPopulationF = populationGen(bags, populationNumber)
    firstPopulationM = populationGen(bags, populationNumber)

    #runs algorithm
    geneticAlgorithm(firstPopulationF, firstPopulationM)

# genetic algorithm loop
def geneticAlgorithm(genF, genM):

    # gets best ever to arbitrary solution
    bestEver = genF[0]

    # main algorithm loop
    for i in range(termination):

        # runs selection algorithm on parents
        parentF = selection(evalFunction(genF), genF, 10)
        parentM = selection(evalFunction(genM), genM, 10)

        newGenF, newGenM  = [], []

        # while the population isnt complete
        while len(newGenF) < populationNumber:

            # shuffles parents
            random.shuffle(parentF)
            random.shuffle(parentM)

            #performs crossover
            cross1, cross2 = crossover(parentF, parentM)

            newGenF += cross1
            newGenM += cross2

        # performs mutation
        genF = mutate(prune(newGenF[:populationNumber]), 5)
        genM = mutate(prune(newGenM[:populationNumber]), 5)

        #finds best parent from current solution
        genF[0] = list(max(parentF, key=value))
        genM[0] = list(max(parentM, key=value))
        candidate = max(genF + genM, key=value)

        # replaces best ever if the score is better
        if value(candidate) > value(bestEver):
            bestEver = list(candidate)

    # returns result
    print(value(bestEver), sum(bags[i - 1][1] for i in bestEver))
    return bestEver

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

    return vanCapacity, bags            #generated code end

# quick code to generate the value of a solution
def value(solution):
    return sum(bags[i - 1][2] for i in solution)


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

# generates a population of solutions
def populationGen(dataSet, popNum):

    population = []

    for i in range(popNum):

        population.append(populate(dataSet))

    return population


#sorts the generation based on fitness and returns the key and the total value
def evalFunction(generation):

    fitnessNums = []

    for j in range(len(generation)):

        total = value(generation[j])

        fitnessNums.append([j,total])

    sortedData = sorted(fitnessNums, key=lambda x: x[1])

    return sortedData

#selects parents based on linear ranked selection
def selection(fitness, data, numOfRuns):

    n = len(fitness)

    #list to help avoid duplicates
    available = list(range(n))

    selected = []

    for i in range(numOfRuns):

        #total rank weight of the positions still on the wheel
        total = sum(pos + 1 for pos in available)

        num = random.uniform(0, total)

        runTime = 0

        #fall back candidate
        candidate = available[-1]

        #runs through list until the random number is hit
        for pos in available:

            runTime += pos + 1

            # returns value at location
            if runTime >= num:

                candidate = pos
                break

        # removes solution to prevent duplicates
        available.remove(candidate)

        selected.append(data[fitness[candidate][0]])

    # returns best solutions
    return selected

# crossover function
# takes 2 generations and interates through the solutions and applying cross over to them
def crossover(mother, father):

    child1 = []
    child2 = []

    for i in range(len(mother)):

        #selects cutoff point
        cutOff = random.randint(1,(len(mother[i])))

        # swapws tails and heads of solutions
        kid1Sol = mother[i][:cutOff] + father[i][cutOff:]
        kid2Sol = father[i][:cutOff] + mother[i][cutOff:]

        #repairs the solutions and adds them to the children
        child1.append(fixSol(kid1Sol))
        child2.append(fixSol(kid2Sol))

    return child1, child2

# fixes the solutions
def fixSol(solution):

    ## the following section was generated by claude ai

    #gets rid of duplicates
    solution = list(dict.fromkeys(solution))

    #total solution weight
    weight = sum(bags[i - 1][1] for i in solution)

    # if heavier then prunes worst solutions
    while weight > capacity:
        worst = min(solution, key=lambda i: bags[i - 1][2] / bags[i - 1][1])
        solution.remove(worst)
        weight -= bags[worst -1][1]

    # goes through unused bags to see if any of them fit in the space leftover
    # helps fill gaps in short solutions
    unused = [int(b[0]) for b in bags if int(b[0]) not in solution]
    random.shuffle(unused)
    for i in unused:
        if weight + bags[i - 1][1] <= capacity:
            solution.append(i)
            weight += bags[i - 1][1]

    return solution         ##generated code end

# gets rid of any duplicate solutions in a generation and replaces it with a new one
def prune(listOg):

    length = len(listOg)
    prunedList = []

    for i in range(length):

        if listOg[i] not in prunedList:
            prunedList.append(listOg[i])

    if len(prunedList) != length:
        prunedList.append(populate(bags))

    return prunedList

# mutates a solution based on a given rate
def mutate(generation, rate):

    for i in range(len(generation)):

        # if the rate gets hit it removes a random bag and then repairs the solution
        if generation[i] and random.randrange(0, 100) < rate:

            generation[i].remove(random.choice(generation[i]))
            generation[i] = fixSol(generation[i])

    return generation

main()