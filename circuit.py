from random import *
import math


class Cell(object):
    """ Cell object
          side = "side" of partition. Boolean
          is_locked = False if unlocked
          cellnets = list of net ids that this cell is in
    """

    def __init__(self):
        self.side = sample([True,False],1)[0]
        self.is_locked = False
        self.cellNets = []


class Circuit:
    def __init__(self, f):
        [self.numCells, self.numNets, self.ny, self.nx] = [int(s) for s in f.readline().split()]

        self.cells = []
        """ Generate list of Cell objects in range numCells
        """
        for cellNum in range(self.numCells):
            self.cells.append(Cell())
            # even cells get False side of partition (keep approximately even distribution)

        right = 0
        left = 0
        for c in self.cells:
            if c.side:
                right = right + 1
            else:
                left = left + 1
        if right > left:
            for _ in range((right-left)/2):
                while True:
                    c = sample(self.cells, 1)[0]
                    if c.side:
                        break
                c.side = not c.side
        else:
            for _ in range((left-right)/2):
                while True:
                    c = sample(self.cells, 1)[0]
                    if not c.side:
                        break
                c.side = not c.side
        right = 0
        left = 0
        for c in self.cells:
            if c.side:
                right = right + 1
            else:
                left = left + 1
        # make sure evenly distributed
        assert right - left in range(-1, 2)

        self.nets = []
        """ Generate a list of all nets
            Each net is a list of cells connected to each other
            add the netNum to the cellnets list for each cell
        """
        for netNum in range(self.numNets):
            line = f.readline().split()
            if len([s for s in line]) is 0:
                # empty line, read next
                line = f.readline().split()
            # source of net
            source = int(line[1])
            assert source in range(self.numCells)
            self.cells[source].cellNets.append(netNum)

            # sinks of net
            sink_cells = []
            sinks = [int(s) for s in line[2:]]
            for sink in sinks:
                assert sink in range(self.numCells)
                self.cells[sink].cellNets.append(netNum)
                sink_cells.append(self.cells[sink])
            self.nets.append([self.cells[source]] + sink_cells)
        f.close()

    def calcGain(self, cell):
        """ method: calcGain
        calculates the gain of moving a cell from one side to the other
        :param cell: cell object of cell under consideration
        :return: gain of moving cell, #edges that cross - #num edges that do not
                to adapt for multiple nets, only count number of nets that cross the partition, not num cells
        """
        gain = 0
        for netNum in cell.cellNets:
            netcross = False
            for c in self.nets[netNum]:
                if c.side is not cell.side:
                    netcross = True
                    break
            if netcross:
                gain = gain + 1
            else:
                gain = gain - 1

        return gain

    def calcBalance(self):
        """ method calcBalance
        calculates the "heavyside" of the circuit partition, "True" or "False"
        :return: heavy side, True or False
        """
        # result = number of cells on True side
        result = 0
        for cell in self.cells:
            if cell.side:
                result = result + 1

        if result*2 > self.numCells:
            return True
        else:
            return False

    def crossesPart(self, net):
        """ method crossesPart
        determines whether or not a net spans the partition
        :param net: the net being considered
        :return: True if the net crosses the partition, False otherwise
        """
        side = net[0].side
        for each in net:
            if each.side != side:
                return True
        return False

    def calcCutSize(self):
        """ method calcCutSize
        calculates the number of nets that span the partition
        :return: cutsize of the partition
        """
        cutsize = 0
        for net in self.nets:
            if self.crossesPart(net):
                cutsize = cutsize + 1

        return cutsize