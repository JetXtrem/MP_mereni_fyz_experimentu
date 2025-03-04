from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

def plot(): 

	fig = Figure(figsize = (5, 5), 
				dpi = 100) 

	y = [i**2 for i in range(101)] 

	plot1 = fig.add_subplot(111) 

	plot1.plot(y) 

	canvas = FigureCanvasTkAgg(fig, master = root) 
	canvas.draw() 

	canvas.get_tk_widget().pack() 

	toolbar = NavigationToolbar2Tk(canvas, root) 
	toolbar.update() 

	canvas.get_tk_widget().pack() 


root = Tk()

root.geometry("750x750")
root.title("Měření fyzikálního experimentu")

button1 = Button(root, text="Začít měření", fg="green", command=plot)
button1.pack()

root.mainloop() 