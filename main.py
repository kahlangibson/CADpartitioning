from os import listdir
from os.path import isfile, join
from draw import *

dir = './benchmarks/'

startT = 80.
beta = 0.6
exitRate = 0.25
runWith0 = True

def read_infile():
    global myCircuit
    runButton.pack_forget()
    if myCircuit is not None:
        myCircuit.delete()
    filename = file.get()
    f = open(dir+filename, "r")  # gets closed inside simAnneal object
    myCircuit = draw(root, startT, beta, exitRate, runWith0, f)
    runButton.pack(side='left', padx=20, pady=10)

def runAnneal():
    global myCircuit
    myCircuit.runSimAnneal()


## main ##
root = Tk()
root.lift()
root.attributes("-topmost", True)
global runButton
runButton = tk.Button(root, text="Run Placement", command=runAnneal)

myCircuit = None

file = tk.StringVar(root)
# initial value
file.set('Choose File')
# filenames = [f for f in listdir('./benchmarks/') if isfile(join('./benchmarks/', f))]
filenames = [f for f in listdir(dir) if isfile(join(dir, f))]
drop = tk.OptionMenu(root, file, *filenames)
drop.pack(side='left', padx=10, pady=10)
go = tk.Button(root, text="Choose File", command=read_infile)
go.pack(side='left', padx=20, pady=10)

root.mainloop()