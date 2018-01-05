# -*- coding: utf-8 -*-
from DATA_DUMMY import data
import pprint
import copy
import random
import numpy as np
from random import randint
import sys


def grasp(alpha, maxIteration):
    bestSolution = {'gc': sys.maxint}
    iteration = 1
    infeasibleCounter = 0
    while iteration <= maxIteration:
        solution = construct(alpha)
        if solution['feasible']:
            # if feasible => check for other solutions
            # bestNeighbour = local2(solution)
            bestNeighbour = solution
            if (bestNeighbour['gc'] < bestSolution['gc']):
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

        else:
            print(solution['reason'])
            infeasibleCounter += 1
        iteration += 1

    print('gc')
    pprint.pprint(bestSolution['gc'])
    print('assignedNurses')
    pprint.pprint(bestSolution['assignedNurses'])
    print('workedHours')
    pprint.pprint(bestSolution['workedHours'])
    print('schedule')
    pprint.pprint(bestSolution['schedule'])
    print('Number of infeasibles')
    print(infeasibleCounter)
    return bestSolution


def construct(alpha):
    candidates = computeCandidateElements()
    solution = {'schedule': [[0] * data['hours'] for i in range(
        data['numNurses'])],
        'gc': 0,
        'feasible': True,
        'assignedNurses': [0] * data['hours'],
        'workedHours': [0] * data['numNurses']}

    firstIteration = True
    lastNurse = -1
    lastHour = -1
    while not demandFulfilled(solution, data['demand']) \
            and len(candidates) > 0:
        greedyCost(candidates, solution, firstIteration, lastNurse, lastHour)
        candidates = list(
            filter(lambda candidate: candidate['gc'] < 1000, candidates))
        if len(candidates) == 0:
            break
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
        lastNurse = selectedNurse
        lastHour = selectedHour
        updateSolutions(candidates, randomSelectedCandidate)
        firstIteration = False

    computeSolutionCost(solution)
    return solution


def checkFeasible(solution):
    if max(solution['workedHours']) > data['maxHours']:
        solution['feasible'] = False
        solution['reason'] = 'Max Hours reached'
        return

    for workingHour in solution['workedHours']:
        if workingHour > 0 and workingHour < data['minHours']:
            solution['feasible'] = False
            solution['reason'] = 'min Hours not fulfilled'
            break

    for index, demand in enumerate(solution['assignedNurses']):
        if demand < data['demand'][index]:
            solution['feasible'] = False
            solution['reason'] = 'No demand'
            break

    if not solution['feasible']:
        return

    for nurse in solution['schedule']:
        firstHour = data['hours'] + 1
        lastHour = -1
        consec = 0
        maxConsec = 0
        worksBefore = False
        rests = 0
        for hour, works in enumerate(nurse):
            if works:
                consec += 1
                if not worksBefore:
                    worksBefore = True

                if maxConsec < consec:
                    maxConsec = consec

                if hour < firstHour:
                    firstHour = hour

                if hour > lastHour:
                    lastHour = hour

                if worksBefore and rests > 1:
                    solution['feasible'] = False
                    solution['reason'] = 'Max rest allowed'
                    break

                rests = 0
            else:
                rests += worksBefore * 1
                consec = 0

        if maxConsec > data['maxConsec']:
            solution['feasible'] = False
            solution['reason'] = 'Max consec surpased'
            break

        if lastHour != -1 and (lastHour + 1 - firstHour) > data['maxPresence']:
            solution['feasible'] = False
            solution['reason'] = 'Max Presence surpased'
            break

    if not solution['feasible']:
        return


def computeSolutionCost(solution):
    lambdaNurse = 200
    lambdaOverDemand = 10

    # CHECK FEASIBILITY
    checkFeasible(solution)
    if not solution['feasible']:
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
    for hour in range(data['hours']):
        if (demand[hour] > solution['assignedNurses'][hour]):
            return False
    for nurseWorkedHours in solution['workedHours']:
        if nurseWorkedHours > 0 and nurseWorkedHours < data['minHours']:
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


def greedyCost(solutions, schedule, firstIteration, lastNurse, lastHour):
    lambdaNewNurse = 100
    lambdaMaxConsec = 1000
    # lambdaMinHours = 100
    lambdaMaxHours = 1000
    lambdaMaxPresence = 1000
    lambdaMaxRest = 100
    lambdaDemandAdjustment = 10 # 50 / max(data['demand'])

    for solution in solutions:

        if not firstIteration and \
            (solution['nurse'] != lastNurse and
             solution['hour'] != lastHour):
            continue

        nurseWorkedHours = schedule['workedHours'][solution['nurse']]
        # New Nurse
        solution['gc'] = lambdaNewNurse * (nurseWorkedHours < 1)

        # Max hours
        solution['gc'] += lambdaMaxHours * \
            ((nurseWorkedHours + 1) >
             min(data['maxHours'], data['maxPresence']))

        # Max Presence
        solution['gc'] += lambdaMaxPresence * \
            (computeMaxPresence(schedule, solution) > data['maxPresence'])

        # Max Consec
        solution['gc'] += lambdaMaxConsec * \
            (computeMaxConsec(schedule, solution) > data['maxConsec'])

        # MaxRest
        solution['gc'] += lambdaMaxRest * \
            (computeMaxRest(schedule, solution) > 1)

        # Cost regarding hour demand

        maxRemainingDemand = [demand - assigned for demand,
                              assigned in zip(data['demand'],
                                              schedule['assignedNurses'])]
        solution['gc'] += lambdaDemandAdjustment * \
            (max(maxRemainingDemand) - maxRemainingDemand[solution['hour']])

    return


def computeMaxConsec(schedule, solution):
    consec = 0
    nurseSchedule = schedule['schedule'][solution['nurse']]

    for indexHour, workingHour in enumerate(nurseSchedule):
        if not workingHour:
            if indexHour < solution['hour']:
                consec = 0
            elif indexHour == solution['hour']:
                consec += 1
            else:
                break
        else:
            consec += 1
    return consec


def computeMaxRest(schedule, solution):
    restingHoursBetween = 0
    restingHoursBetween2 = 0
    nurseSchedule = schedule['schedule'][solution['nurse']]

    hour = solution['hour']
    while (hour < data['hours']):
        if nurseSchedule[hour] == 1:
            restingHoursBetween = hour - solution['hour'] - 1
            break
        hour += 1
    hour = solution['hour']
    while (hour >= 0):
        if nurseSchedule[hour] == 1:
            restingHoursBetween2 = solution['hour'] - hour - 1
            break
        hour -= 1

    if (restingHoursBetween == 0 or restingHoursBetween2 == 0):
        return max(restingHoursBetween, restingHoursBetween2)
    return min(restingHoursBetween2, restingHoursBetween)


def computeMaxPresence(schedule, solution):
    firstHour = data['hours'] + 1
    lastHour = -1

    for hour, works in enumerate(schedule['schedule'][solution['nurse']]):
        if works:
            if hour < firstHour:
                firstHour = hour

            if hour > lastHour:
                lastHour = hour

    if firstHour > data['hours'] or lastHour == -1:
        return 1
    elif firstHour < solution['hour']:
        if lastHour < solution['hour']:
            return solution['hour'] + 1 - firstHour
        else:
            return lastHour - firstHour + 1
    else:
        return lastHour + 1 - solution['hour']


def local2(solution):
    initialRandomSolution = copy.deepcopy(solution)
    initialRandomSolution = {'schedule': [[np.random.rand() > .5] * data['hours'] for i in range(
        data['numNurses'])],
        'gc': 0,
        'feasible': True,
        'assignedNurses': [0] * data['hours'],
        'workedHours': [0] * data['numNurses']}
    for idNurse, nurseSchedule in enumerate(solution['schedule']):
        for idHour, worksInHour in enumerate(nurseSchedule):
            initialRandomSolution['workedHours'][idNurse] += worksInHour
            initialRandomSolution['assignedNurses'][idHour] += worksInHour
    computeSolutionCost(initialRandomSolution)
    print(initialRandomSolution)
    return solution


def local(solution):
    for idNurse, nurseSchedule in enumerate(solution['schedule']):
        for idHour, worksInHour in enumerate(nurseSchedule):
            if worksInHour == 1:
                solution['schedule'][idNurse][idHour] = 0
                solution['workedHours'][idNurse] -= 1
                solution['assignedNurses'][idHour] -= 1
                computeSolutionCost(solution)
                if not solution['feasible']:
                    solution['schedule'][idNurse][idHour] = 1
                    solution['workedHours'][idNurse] += 1
                    solution['assignedNurses'][idHour] += 1
                    solution['feasible'] = True

    return solution


def main():
    alpha = 0.0
    maxIte = 1000
    grasp(alpha, maxIte)


if __name__ == "__main__":
    main()
