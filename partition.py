from circuit import *
from copy import deepcopy
from os import listdir
from os.path import isfile, join
dir = './benchmarks/'

class partition(Circuit):
    def __init__(self, f):
        Circuit.__init__(self, f)
        # dictionary of solutions indexed by cutsize
        self.solutions = {}

    def runPartition(self):
        """ K-L Partitioning Algorithm
        """
        # for some number of passes
        print "Nets: " + str(self.numNets)
        print "Initial cost: " + str(self.calcCutSize())
        for n in range(6):
            sols = {}
            # unlock all cells
            for cell in self.cells:
                cell.is_locked = False
            # while some nodes are unlocked
            heavyside = self.calcBalance()
            for _ in range(self.numCells):
                # calculate all gains (of unlocked cells on heavyside only to make faster)
                gains = {}
                for cell in self.cells:
                    if not cell.is_locked and cell.side == heavyside:
                        gains[self.calcGain(cell)] = cell
                # i dont think it should ever need this, but just for now:
                if len(gains) == 0:
                    print "ERROR: len gains is 0"
                    for cell in self.cells:
                        if not cell.is_locked:
                            gains[self.calcGain(cell)] = cell

                # choose node with highest gain that doesn't imbalance nets
                switch = sorted(gains, reverse=True)[0]
                # move node to the other side and lock it
                gains[switch].side = not heavyside
                gains[switch].is_locked = True
                heavyside = not heavyside

                cut = self.calcCutSize()
                if cut not in sols:
                    sols[cut] = deepcopy(self.cells)

            # choose best cut in this pass (smallest cutcost) and append to solutions
            best = sorted(sols)[0]
            print "Best cut " + str(n+1) + "/6: " + str(best)
            if best not in self.solutions:
                self.solutions[best] = deepcopy(sols[best])

        final = sorted(self.solutions)[0]
        print "***************"
        print "Best: " + str(final)


filenames = [str(f) for f in listdir(dir) if isfile(join(dir, f))]

for i,f in enumerate(filenames):
    print "***************"
    print f + ": " + str(i+1) + "/" + str(len(filenames))
    f = open(dir + f, "r")
    part = partition(f)
    part.runPartition()
    