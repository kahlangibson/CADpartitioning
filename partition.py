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
        improved = True
        print "Nets: " + str(self.numNets)
        print "Initial cost: " + str(self.calcCutSize())
        # for some number of passes
        for n in range(6):
            sols = {}
            # unlock all cells
            for cell in self.cells:
                cell.is_locked = False
            # while some nodes are unlocked
            if improved:
                numMoved = 0
                nets = {}
                for net in self.nets:
                    count = 0
                    for c in net:
                        if c.side:
                            count = count + 1
                    if 0.85 < float(count)/float(len(net)) < 1.:
                        nets[float(count)/float(len(net))] = net
                    elif 0. < float(count)/float(len(net)) < 0.15:
                        nets[float(count)/float(len(net))] = net
                if len(nets) > 0:
                    for k in nets:
                        if k > 0.5: # mostly True
                            for cell in nets[k]:
                                cell.side = True
                                cell.is_locked = True
                                numMoved = numMoved + 1
                        else:
                            for cell in nets[k]:
                                cell.side = False
                                cell.is_locked = True
                                numMoved = numMoved + 1

                while numMoved < self.numCells:
                    heavyside = self.calcBalance()
                    gains = {}
                    for cell in self.cells:
                        if not cell.is_locked and cell.side == heavyside:
                            gains[self.calcGain(cell)] = cell
                    if len(gains) != 0:
                        numMoved = numMoved + 1
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

            else:
                for _ in range(self.numCells):
                    heavyside = self.calcBalance()
                    # calculate all gains (of unlocked cells on heavyside only to make faster)
                    gains = {}
                    for cell in self.cells:
                        if not cell.is_locked and cell.side == heavyside:
                            gains[self.calcGain(cell)] = cell
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
            print "Best cut " + str(n+1) + "/6: " + str(best)
            if best not in self.solutions:
                self.solutions[best] = deepcopy(sols[best])
            # roll back and do another iteration
            for i,cell in enumerate(sols[best]):
                self.cells[i].side = cell.side
            if best == 0:
                break

        final = sorted(self.solutions)[0]
        print "***************"
        print "Best: " + str(final)


filenames = [str(f) for f in listdir(dir) if isfile(join(dir, f))]

for i,file in enumerate(filenames):
    print file + ": " + str(i+1) + "/" + str(len(filenames))
    f = open(dir + file, "r")
    print "***************"
    part = partition(f)
    part.runPartition()
