'''
def decode(population, data):
    for ind in population:
        ind['solution'] = ind['chr']
        res = np.multiply(ind['chr'], range(len(ind['chr'])))
        ind['fitness'] = sum(res)
    return(population)
'''


def decode(population, data):
    maxPresence = data['maxPresence']
    maxConsec = data['maxConsec']
    minHours = data['minHours']
    maxHours = data['maxHours']
    maxConsec = data['maxConsec']

    for ind in population:

        ind['solution'] = [[0] * data['hours']
                           for i in range(data['numNurses'])]
        indChr = list(enumerate(ind['chr']))
        sortedIndChr = sorted(indChr, key=lambda x: x[1])
        assignedDemand = [0] * data['hours']
        workedHours = [0] * data['numNurses']
        workedConsec = [0] * data['numNurses']
        minWorkingHours = [-1] * data['numNurses']
        maxWorkingHours = [-1] * data['numNurses']
        maxNurses = len(ind['chr'])

        for currHour in range(data['hours']):
            idNurse = 0
            while (data['demand'][currHour] > assignedDemand[currHour] and
                    idNurse < maxNurses):
                currNurse = sortedIndChr[idNurse][0]
                hoursWorked = workedHours[currNurse]
                consecHoursWorked = workedConsec[currNurse]
                minWorkedHours = minWorkingHours[currNurse]

                if (hoursWorked < maxHours and
                    consecHoursWorked < maxConsec and
                        (minWorkedHours == -1 or
                            ((currHour + 1 - minWorkedHours) <= maxPresence))):

                    if(minWorkingHours[currNurse] == -1):
                        minWorkingHours[currNurse] = currHour
                    if(maxWorkingHours[currNurse] < currHour):
                        maxWorkingHours[currNurse] = currHour

                    workedHours[currNurse] += 1
                    ind['solution'][currNurse][currHour] += 1
                    assignedDemand[currHour] += 1

                    # Aquest if funca perque les hores son correlatives
                    worksPreviousHour = ind['solution'][currNurse][currHour - 1]
                    if (currHour > 0 and worksPreviousHour):
                        workedConsec[currNurse] += 1
                    else:
                        workedConsec[currNurse] = 1
                else:
                    workedConsec[currNurse] = 0

                idNurse += 1

        # FITNESS EVALUATION
        result = 0

        usedNurses = [0] * data['hours']
        for nurse in ind['solution']:
            for idHour, hour in enumerate(nurse):
                usedNurses[idHour] += hour

        for idHour, hour in enumerate(usedNurses):
            result += abs(hour - data['demand'][idHour]) * 50

        ind['fitness'] = result
    return(population)


'''
    ind['chr'] vector of chromosomes
    ind['solution'] solution to those chromosomes
    ind['fitness'] value of objective function of chromosomes
'''
# Use the chromosome to make the assignment to task to computers

# Need to order the chromosomes ind['chr'] so that they meet with the
# requirements / constraints.

# Fitness = costc * usedc + z (remainingCapacity c)/totalCapacityc
