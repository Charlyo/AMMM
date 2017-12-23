from random import randint
from DATA_DUMMY import data
import pprint
import sys


def grasp(alpha, maxIteration):
    bestSolution = {'gc': sys.maxint}
    iteration = 1
    while iteration <= maxIteration:
        solution = construct(alpha)
        bestNeighbour = local(solution)
        if (bestNeighbour['gc'] < bestSolution['gc']):

            # if feasible => update best solution
            bestSolution = bestNeighbour
            print('it', iteration)
            print('gc')
            pprint.pprint(bestSolution['gc'])
            print('assignedNurses')
            pprint.pprint(bestSolution['assignedNurses'])
            print('workedHours')
            pprint.pprint(bestSolution['workedHours'])
            print('schedule')
            pprint.pprint(bestSolution['schedule'])

        iteration += 1
    return bestSolution


def construct(alpha):
    candidates = computeCandidateElements()
    solution = {'schedule': [[0] * data['hours'] for i in range(
        data['numNurses'])],
        'gc': 0,
        'assignedNurses': [0] * data['hours'],
        'workedHours': [0] * data['numNurses']}

    while not demandFulfilled(solution, data['demand']) and candidates:
        greedyCost(candidates, solution)
        sortedCandidates = sorted(
            candidates, key=lambda candidate: candidate['gc'])
        minGreedyCost = sortedCandidates[0]['gc']
        maxGreedyCost = sortedCandidates[len(sortedCandidates) - 1]['gc']
        maxGraspCost = minGreedyCost + alpha * (maxGreedyCost - minGreedyCost)
        RCL = generateRCL(sortedCandidates, maxGraspCost)
        randomSelectedCandidate = RCL[randint(0, len(RCL) - 1)]

        # UPDATE SOLUTION
        selectedNurse = randomSelectedCandidate['nurse']
        selectedHour = randomSelectedCandidate['hour']
        solution['schedule'][selectedNurse][selectedHour] = 1
        solution['assignedNurses'][selectedHour] += 1
        solution['workedHours'][selectedNurse] += 1
        updateSolutions(candidates, randomSelectedCandidate)

    computeSolutionCost(solution)
    return solution


def computeSolutionCost(solution):
    lambdaNurse = 200
    lambdaOverDemand = 20

    # CHECK FEASIBILITY
    if max(solution['workedHours']) > data['maxHours']:
        solution['gc'] = sys.maxint
        return

    for workingHour in solution['workedHours']:
        if workingHour > 0 and workingHour < data['minHours']:
            solution['gc'] = sys.maxint
            break

    if solution['gc'] == sys.maxint:
        return

    for nurse in solution['schedule']:
        firstHour = data['hours'] + 1
        lastHour = -1
        consec = 0
        maxConsec = 0
        for hour, works in enumerate(nurse):
            if works:
                consec += 1
                if hour < firstHour:
                    firstHour = hour

                elif hour > lastHour:
                    lastHour = hour
            else:
                if maxConsec < consec:
                    maxConsec = consec
                consec = 0

        if maxConsec > data['maxConsec']:
            solution['gc'] = sys.maxint
            break

        if lastHour != -1 and (lastHour + 1 - firstHour) > data['maxPresence']:
            solution['gc'] = sys.maxint
            break

    if solution['gc'] == sys.maxint:
        return

    # END CHECK FEASIBILITY
    solution['gc'] = lambdaNurse * \
        len(filter(lambda workedHour: workedHour > 0, solution['workedHours']))

    solution['gc'] += (reduce(lambda totaldemand, demand: totaldemand + demand,
                              solution['assignedNurses']) -
                       reduce(lambda totalDemand, demand: totalDemand + demand,
                              data['demand'])) * lambdaOverDemand
    return


def demandFulfilled(solution, demand):
    for k in range(data['hours']):
        if (demand[k] > solution['assignedNurses'][k]):
            return False
    return True


def generateRCL(solutions, maxGraspCost):
    return filter(lambda solution: solution['gc'] <= maxGraspCost, solutions)


def updateSolutions(solutions, randomSelectedSolution):
    solutions.pop(solutions.index(randomSelectedSolution))
    return


def computeCandidateElements():
    solutions = list(map(lambda number:
                         {'nurse': number / data['hours'],
                          'hour': number % data['hours'],
                          'gc': 0},
                         range(data['numNurses'] * data['hours'])))
    return solutions


def greedyCost(solutions, schedule):
    lambdaNewNurse = 400
    lambdaMaxConsec = 1500
    lambdaMinHours = 150
    lambdaMaxHours = 1500
    lambdaMaxPresence = 1500
    lambdaMaxRest = 1500
    lambdaDemandAdjustment = 20
    lambdaOverDemand = 100

    for solution in solutions:
        # New Nurse
        solution['gc'] = lambdaNewNurse * \
            (schedule['workedHours'][solution['nurse']] < 1)

        # Min Hours
        solution['gc'] -= lambdaMinHours * \
            ((schedule['workedHours'][solution['nurse']] + 1) <
             data['minHours'])
        # * (data['minHours'] - (schedule['workedHours'][solution['nurse']] ))

        # Max hours
        solution['gc'] += lambdaMaxHours * \
            (schedule['workedHours'][solution['nurse']] + 1 >
             min(data['maxHours'], data['maxPresence']))

        # Cost regarding hour demand
        maxRemainingDemand = [demand - assigned for demand,
                              assigned in zip(data['demand'],
                                              schedule['assignedNurses'])]
        
        maxRemainingDemand[solution['hour']] -= 1
        
        solution['gc'] += (maxRemainingDemand[solution['hour']] <= 0) * \
            lambdaOverDemand

        solution['gc'] -= lambdaDemandAdjustment * \
            abs(max(maxRemainingDemand) -
                schedule['assignedNurses'][solution['hour']])

        # Max Presence
        solution['gc'] += lambdaMaxPresence * \
            (computeMaxPresence(schedule, solution) > data['maxPresence'])

        # Max Consec
        consec = 0
        for indexHour, workingHour in enumerate(schedule['schedule'][solution['nurse']]):
            if not workingHour:
                if indexHour < solution['hour']:
                    consec = 0
                elif indexHour == solution['hour']:
                    consec += 1
                else:
                    break
            else:
                consec += 1
        solution['gc'] += lambdaMaxConsec * (consec > data['maxConsec'])

        # MaxRest

    return


def computeMaxPresence(schedule, solution):
    firstHour = data['hours'] + 1
    lastHour = -1

    for hour, works in enumerate(schedule['schedule'][solution['nurse']]):
        if works:
            if hour < firstHour:
                firstHour = hour

            elif hour > lastHour:
                lastHour = hour

    if firstHour > data['hours'] or lastHour == -1:
        return 1
    elif firstHour < solution['hour']:
        if lastHour < solution['hour']:
            return solution['hour'] + 1 - firstHour
        else:
            return 1
    else:
        return lastHour + 1 - solution['hour']


def local(solution):
    return solution


def main():
    alpha = 0.1
    maxIte = 1000
    grasp(alpha, maxIte)


if __name__ == "__main__":
    main()
