from Tkinter import *
import Tkinter as tk
from math import *
from random import *
from circuit import *
from time import sleep
from copy import deepcopy

class draw(Circuit):
    def __init__(self, parent, f):
        Circuit.__init__(self, f)
        self.myParent = parent
        self.myContainer1 = tk.Frame(parent)
        self.myContainer1.pack()
        self.myCanvas = tk.Canvas(self.myContainer1)
        self.myCanvas.configure(borderwidth=0, highlightthickness=0,width=0,
                                height=0)
        # set this to True to *not* run animation
        self.fast = False

        self.cellsize = 0
        self.n = 0
        self.rect = {}
        self.text = {}
        self.celltext = {}
        self.lines = {}
        self.costy = 0
        self.costtext = 0
        self.doneText = 0
        self.initText = 0

        self.pos = {}
        self.nums = {}
        self.xy = {}

        self.solutions = {}

        self.make(self.numCells)
        self.grid = {True: [], False: []}
        for x in range(self.n/2+1):
            g = []
            for y in range(self.n):
                g.append(' ')
            self.grid[True].append(g)
        for x in range(self.n/2+1):
            g = []
            for y in range(self.n):
                g.append(' ')
            self.grid[False].append(g)
        print self.numCells
        for num in range(self.numCells):
            cell = self.cells[num]
            self.nums[cell] = num
            placed = False
            for x in range(self.n/2+1):
                for y in range(self.n):
                    if self.grid[cell.side][x][y] == ' ':
                        self.grid[cell.side][x][y] = num
                        self.place(cell.side,x,y,num)
                        self.xy[cell] = (x,y)
                        placed = True
                        break
                if placed:
                    break
        for net in self.nets:
            source = net[0]
            (x1,y1) = self.pos[source]
            for sink in net[1:]:
                (x2,y2) = self.pos[sink]
                self.draw_net(source,sink,x1,y1,x2,y2)

    def delete(self):
        self.myCanvas.delete('all')
        self.myCanvas.configure(borderwidth=0, highlightthickness=0,width=0,
                                height=0)

    def place(self, side, x, y, num):
        if side:
            x1 = x * self.cellsize
            x2 = x1 + self.cellsize
        else:
            x1 = (self.n/2 + 1) * self.cellsize + x * self.cellsize + 30
            x2 = x1 + self.cellsize
        y1 = y * self.cellsize
        y2 = y1 + self.cellsize
        self.pos[self.cells[num]] = (x1,y1)
        self.celltext[x1, y1] = self.myCanvas.create_text((x1+x2)/2, (y1+y2)/2, font=("Helvetica", self.cellsize/2), text=num)

    def make(self, numCells):
        self.n = int(pow(numCells,0.5))+5
        self.cellsize = min(1000/(self.n+10), 30)
        self.myCanvas = tk.Canvas(self.myContainer1)
        self.myCanvas.configure(borderwidth=0, highlightthickness=0,
                                width=self.cellsize*self.n+100,
                                height=self.cellsize*self.n+50)
        self.myCanvas.pack(side=tk.RIGHT)
        for x in range(self.n/2+1):
            for y in range(self.n):
                x1 = x * self.cellsize
                y1 = y * self.cellsize
                x2 = x1 + self.cellsize
                y2 = y1 + self.cellsize
                self.rect[y1, x1] = self.myCanvas.create_rectangle(x1, y1, x2, y2, fill="white")
        for x in range(self.n/2+1, self.n+1):
            for y in range(self.n):
                x1 = x * self.cellsize+30
                y1 = y * self.cellsize
                x2 = x1 + self.cellsize
                y2 = y1 + self.cellsize
                self.rect[y1, x1] = self.myCanvas.create_rectangle(x1, y1, x2, y2, fill="white")

        self.costy = self.n * self.cellsize + 20
        self.text[50,self.costy] = self.myCanvas.create_text(50, self.costy, text="Initial Cut:  ")
        self.initText = self.myCanvas.create_text(100, self.costy, text=self.calcCutSize())
        self.text[150,self.costy] = self.myCanvas.create_text(150, self.costy, text="Cut Size:  ")
        self.costtext = self.myCanvas.create_text(200, self.costy, text=self.calcCutSize())

    def remove_net(self, source, sink):
        self.myCanvas.delete(self.lines[source, sink])

    def draw_net(self, source, sink, x1, y1, x2, y2):
        startx = x1 + self.cellsize/2
        starty = y1 + self.cellsize/2
        endx = x2 + self.cellsize/2
        endy = y2 + self.cellsize/2
        self.lines[source, sink] = self.myCanvas.create_line(startx,starty,endx,endy)

    def draw_net_done(self, source, sink, x1, y1, x2, y2):
        startx = x1 + self.cellsize/2
        starty = y1 + self.cellsize/2
        endx = x2 + self.cellsize/2
        endy = y2 + self.cellsize/2
        self.lines[source, sink] = self.myCanvas.create_line(startx,starty,endx,endy,fill='green')

    def move_cell(self, cell):
        # move text from one side to other
        # find open space
        placed = False
        (x,y) = self.xy[cell]
        self.grid[cell.side][x][y] = ' '
        (x,y) = self.pos[cell]
        self.myCanvas.delete(self.celltext[x,y])

        cell.side = not cell.side
        cell.is_locked = True
        for x in range(self.n/2 + 1):
            for y in range(self.n):
                if self.grid[cell.side][x][y] == ' ':
                    self.grid[cell.side][x][y] = self.nums[cell]
                    self.place(cell.side, x, y, self.nums[cell])
                    self.xy[cell] = (x,y)
                    placed = True
                    break
            if placed:
                break
        for netNum in cell.cellNets:
            net = self.nets[netNum]
            source = net[0]
            (x1,y1) = self.pos[source]
            for sink in net[1:]:
                (x2,y2) = self.pos[sink]
                self.remove_net(source,sink)
                # self.myCanvas.delete()
                if self.crossesPart(net):
                    self.draw_net(source,sink,x1,y1,x2,y2)
                else:
                    self.draw_net_done(source,sink,x1,y1,x2,y2)

    def runPartition(self):

        """ K-L Partitioning Algorithm
        """
        print "IN DRAW"
        print "Nets: " + str(self.numNets)
        print "Initial cost: " + str(self.calcCutSize())
        # for some number of passes
        for n in range(6):
            sols = {}
            # unlock all cells
            for cell in self.cells:
                cell.is_locked = False
            # while some nodes are unlocked
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
            # move all cells in nets that are nearly all on one side
            if len(nets) > 0:
                for k in nets:
                    if k > 0.5: # mostly True
                        for cell in nets[k]:
                            if not cell.side:
                                sleep(0.0001)
                                self.move_cell(cell)
                                self.myCanvas.update()
                                numMoved = numMoved + 1
                    else: # mostly False
                        for cell in nets[k]:
                            if cell.side:
                                sleep(0.0001)
                                self.move_cell(cell)
                                self.myCanvas.update()
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
                    sleep(0.0001)
                    self.move_cell(gains[switch])
                    self.myCanvas.update()

                    cut = self.calcCutSize()
                    self.myCanvas.delete(self.costtext)
                    self.costtext = self.myCanvas.create_text(200, self.costy, text=cut)
                    self.myCanvas.update()
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
                if self.cells[i].side is not cell.side:
                    sleep(0.0001)
                    self.move_cell(self.cells[i])
                    self.myCanvas.update()
            self.myCanvas.delete(self.costtext)
            self.costtext = self.myCanvas.create_text(200, self.costy, text=best)
            self.myCanvas.update()
            if best == 0:
                break

        final = sorted(self.solutions)[0]
        for i,cell in enumerate(self.solutions[final]):
            if self.cells[i].side is not cell.side:
                sleep(0.0001)
                self.move_cell(self.cells[i])
                self.myCanvas.update()
        self.myCanvas.delete(self.costtext)
        self.costtext = self.myCanvas.create_text(200, self.costy, text=final)
        self.myCanvas.update()


        self.doneText = self.myCanvas.create_text(300, self.costy, text="PARTITION COMPLETE")
        print "***************"
        print "Best: " + str(final)