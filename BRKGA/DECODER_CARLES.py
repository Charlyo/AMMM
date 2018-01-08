import math
import sys


def decode(population, data):
    for ind in population:

        ind['solution'] = [[0] * data['hours']
                           for i in range(data['numNurses'])]
        indChr = []
        for i in range(data['numNurses']):  # will never be odd
            indChr.append([ind['chr'][i],
                           ind['chr'][i + data['numNurses']]])

        indChr = list(enumerate(indChr))
        sortedIndChr = sorted(indChr, key=lambda x: x[1][0])  # By order
        assignedDemand = [0] * data['hours']
        workedHours = [0] * data['numNurses']
        workedConsec = [0] * data['numNurses']
        minWorkingHours = [-1] * data['numNurses']
        maxWorkingHours = [-1] * data['numNurses']

        for gene in sortedIndChr:
            if checkDemand(assignedDemand, data):
                curr_nurse = gene[0]
                curr_hour = int(math.floor(gene[1][1] * 24))
                while curr_hour < data['hours']:
                    # Mirar que no peti maxim
                    if workedHours[curr_nurse] >= min(data['maxHours'],
                                                      data['maxPresence']):
                        break

                    # Mirar que no peti maxConsec
                    if workedConsec[curr_nurse] >= data['maxConsec']:
                        curr_hour += 1
                        workedConsec[curr_nurse] = 0
                        continue

                    # Mirar que no peti maxPresence
                    if (maxWorkingHours[curr_nurse] -
                        minWorkingHours[curr_nurse] + 1) >= \
                            data['maxPresence']:
                        break

                    # ASSIGN HOUR

                    if workedHours[curr_nurse] < data['minHours'] or \
                       ((workedHours[curr_nurse] > 0) and
                        ind['solution'][curr_nurse][curr_hour - 1] == 0) or \
                       assignedDemand[curr_hour] < data['demand'][curr_hour]:

                        if curr_hour > 0 and \
                                ind['solution'][curr_nurse][curr_hour - 1] == 1:
                            workedConsec[curr_nurse] += 1
                        else:
                            workedConsec[curr_nurse] = 1

                        if minWorkingHours[curr_nurse] == -1:
                            minWorkingHours[curr_nurse] = curr_hour

                        if maxWorkingHours[curr_nurse] < curr_hour:
                            maxWorkingHours[curr_nurse] = curr_hour

                        workedHours[curr_nurse] += 1
                        ind['solution'][curr_nurse][curr_hour] += 1
                        assignedDemand[curr_hour] += 1

                    # END ASSIGN HOUR
                    curr_hour += 1

        # FITNESS EVALUATION
        result = 0

        for idHour, assigned in enumerate(assignedDemand):
            if assigned < data['demand'][idHour]:
                result += sys.maxint
                ind['feasible'] = 'no demand'
                break
            else:
                result += (assigned - data['demand'][idHour]) * 10

        result += get_working_nurses(ind['solution']) * 200

        conditionMinHours = checkMinHours(
            workedHours, data['minHours']) * sys.maxint
        result += conditionMinHours
        if conditionMinHours:
            ind['feasible'] = 'minHours'

        for idNurse in range(data['numNurses']):
            if (maxWorkingHours[idNurse] - minWorkingHours[idNurse] + 1) \
                    > data['maxPresence']:
                result = sys.maxint
                ind['feasible'] = 'maxPresence'
                break

        ind['fitness'] = result
    return population


def checkDemand(assigned, data):
    for hour in range(data['hours']):
        if assigned[hour] < data['demand'][hour]:
            return True
    return False


def checkMinHours(solution, minHours):
    for workedHours in solution:
        if workedHours > 0 and workedHours < minHours:
            return True
    return False


def get_working_nurses(sol):
    working_nurses = 0
    for nurse in sol:
        if all(h == 0 for h in nurse):
            continue
        working_nurses += 1

    return working_nurses
