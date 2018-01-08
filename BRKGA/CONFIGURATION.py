from DATA_DUMMY import data

config = {
    'chromosomeLength': 2 * data['numNurses'],
    'numIndividuals': 50,
    'maxNumGenerations': 1000,
    'eliteProp': 0.1,
    'mutantProp': 0.2,
    'inheritanceProb': 0.7
}
