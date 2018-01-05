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
        indChr = []
        for i in range(int(len(ind['chr']) / 2)):  # will never be odd
            indChr.append([ind['chr'][i], ind['chr'][i + int(len(ind['chr']) / 2)]])

        indChr = list(enumerate(indChr))
        sortedIndChr = sorted(indChr, key=lambda x: x[1][1])
        assignedDemand = [0] * data['hours']
        workedHours = [0] * data['numNurses']
        workedConsec = [0] * data['numNurses']
        minWorkingHours = [-1] * data['numNurses']
        maxWorkingHours = [-1] * data['numNurses']

        for currHour in range(data['hours']):
            id_nurse = 0
            while data['demand'][currHour] > assignedDemand[currHour] and id_nurse < len(sortedIndChr):  # while the demand is not satisfied
                curr_nurse = sortedIndChr[id_nurse][0]
                hours_worked = workedHours[curr_nurse]
                consec_hours_worked = workedConsec[curr_nurse]
                min_worked_hours = minWorkingHours[curr_nurse]

                if (hours_worked < maxHours
                        and consec_hours_worked < maxConsec
                        and (min_worked_hours == -1 or ((currHour + 1 - min_worked_hours) <= maxPresence))
                        and sortedIndChr[id_nurse][1][1] > 0.5):

                    if minWorkingHours[curr_nurse] == -1:
                        minWorkingHours[curr_nurse] = currHour

                    if maxWorkingHours[curr_nurse] < currHour:
                        maxWorkingHours[curr_nurse] = currHour

                    workedHours[curr_nurse] += 1
                    ind['solution'][curr_nurse][currHour] += 1
                    assignedDemand[currHour] += 1

                    # Aquest if funca perque les hores son correlatives
                    worksPreviousHour = ind['solution'][curr_nurse][currHour - 1]
                    if currHour > 0 and worksPreviousHour:
                        workedConsec[curr_nurse] += 1
                    else:
                        workedConsec[curr_nurse] = 1
                else:
                    workedConsec[curr_nurse] = 0

                id_nurse += 1

        # FITNESS EVALUATION
        result = 0

        usedNurses = [0] * data['hours']
        for nurse in ind['solution']:
            for idHour, hour in enumerate(nurse):
                usedNurses[idHour] += hour

        for idHour, hour in enumerate(usedNurses):
            result += abs(hour - data['demand'][idHour]) * 50

        result += workMinHours(ind['solution'], data['minHours']) * 30

        result += consecutiveRests(ind['solution'], data) * 40

        ind['fitness'] = result
        # print(ind['fitness'])
    return population


'''
    ind['chr'] vector of chromosomes
    ind['solution'] solution to those chromosomes
    ind['fitness'] value of objective function of chromosomes
'''
# Use the chromosome to make the assignment to task to computers

# Need to order the chromosomes ind['chr'] so that they meet with the
# requirements / constraints.

# Fitness = costc * usedc + z (remainingCapacity c)/totalCapacityc


def workMinHours(sol, min_hours):
    """"Returns the number of nurses that work less than min hours"""
    nurses = 0
    for nurse in sol:
        hours = 0
        for i in nurse:
            hours += i
        if 0 < hours < min_hours:
            nurses += 1

    return nurses


def consecutiveRests(sol, data):
    """Returns the number of nurses that rest for more than 1 consecutive hour"""
    num_nurses = 0
    for nurse in sol:
        first_hour = data['hours'] + 1
        last_hour = -1
        consec = 0
        max_consec = 0
        works_before = False
        rests = 0
        for hour, works in enumerate(nurse):
            if works:
                consec += 1
                if not works_before:
                    works_before = True

                if max_consec < consec:
                    max_consec = consec

                if hour < first_hour:
                    first_hour = hour

                if hour > last_hour:
                    last_hour = hour

                if works_before and rests > 1:
                    num_nurses += 1

                rests = 0
            else:
                rests += works_before * 1
                consec = 0
    return num_nurses


def checkFeasible(solution, data):
    if max(solution['workedHours']) > data['maxHours']:
        solution['feasible'] = False
        solution['reason'] = 'Max Hours reached'
        return

    for workingHour in solution['workedHours']:
        if 0 < workingHour < data['minHours']:
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
            solution['reason'] = 'Max consecutive surpassed'
            break

        if lastHour != -1 and (lastHour + 1 - firstHour) > data['maxPresence']:
            solution['feasible'] = False
            solution['reason'] = 'Max Presence surpased'
            break

    if not solution['feasible']:
        return
