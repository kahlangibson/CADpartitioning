from circuit import *
from copy import deepcopy
from os import listdir
from os.path import isfile, join
dir = './benchmarks/'

class partition(Circuit):
    def __init__(self, f, p):
        Circuit.__init__(self, f)
        # dictionary of solutions indexed by cutsize
        self.solutions = {}
        self.p = p

    def runPartition(self):
        """ K-L Partitioning Algorithm
        """
        print "Nets: " + str(self.numNets)
        print "Initial cost: " + str(self.calcCutSize())
        # for some number of passes
        for n in range(6):
            sols = {}
            # unlock all cells
            for cell in self.cells:
                cell.is_locked = False
            # while some nodes are unlocked
            for _ in range(self.numCells):
                heavyside = self.calcBalance()
                # calculate all gains (of unlocked cells on heavyside only to make faster)
                gains = {}
                for cell in self.cells:
                    if not cell.is_locked and cell.side == heavyside:
                        # gains[self.calcGain(cell)] = cell
                        gains[self.calcGainImproved(cell, self.p)] = cell
                if len(gains) != 0:
                    # choose node with highest gain that doesn't imbalance nets
                    switch = sorted(gains, reverse=True)[0]
                    # move node to the other side and lock it
                    gains[switch].side = not heavyside
                    gains[switch].is_locked = True

                    cut = self.calcCutSize()
                    if cut not in sols:
                        sols[cut] = deepcopy(self.cells)
                else:
                    break

            # choose best cut in this pass (smallest cutcost) and append to solutions
            best = sorted(sols)[0]
            # print "Best cut " + str(n+1) + "/6: " + str(best)
            if best not in self.solutions:
                self.solutions[best] = deepcopy(sols[best])
            # roll back and do another iteration
            for i,cell in enumerate(sols[best]):
                self.cells[i].side = cell.side

        final = sorted(self.solutions)[0]
        print "***************"
        print "P: " + str(self.p)
        print "Best: " + str(final)


filenames = [str(f) for f in listdir(dir) if isfile(join(dir, f))]

for i,file in enumerate(filenames):
    print file + ": " + str(i+1) + "/" + str(len(filenames))
    f = open(dir + file, "r")
    for p in [0.65,0.75,0.85,0.95]:
        print "***************"
        part = partition(f, p)
        part.runPartition()
