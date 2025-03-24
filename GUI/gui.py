from tkinter import Tk, Button, ttk, StringVar
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd

test_file = "DATA.csv"
reader = pd.read_csv(test_file)

X_time = reader["currentTime"].tolist()
p = 0
X_actualTime = []
for _ in X_time:
    X_actualTime.append(X_time[p] - X_time[0])
    p += 1

Y_totalAngle = reader["totalAngle"].tolist()
Y_accelY = reader["Y_val"].tolist()

Y_accelZ = reader["Z_val"].tolist()
p = 0
Y_accelZ_normalized = []
for _ in Y_accelZ:
    Y_accelZ_normalized.append(Y_accelZ[p] - 1)
    p += 1

p = 0
totalAcceleration = []
for _ in Y_accelY, Y_accelZ_normalized:
    totalAcceleration.append(((Y_accelY[p] ** 2) + (Y_accelZ_normalized[p] ** 2)) ** 0.5)
    p += 1

""" print(reader) """

def plot_1():
    fig = Figure(figsize=(6, 5), dpi=100)

    plot1 = fig.add_subplot(111)
    plot1.plot(X_actualTime, Y_totalAngle, label="totalAngle")
    plot1.set_title("Graf závislosti úhlu na čase")
    plot1.set_xlabel("Čas [ms]")
    plot1.set_ylabel("Úhel [°]")
    plot1.legend()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()

    canvas.get_tk_widget().grid(row=1, column=0)

"""     toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()

    canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True) """

def plot_2():
    fig = Figure(figsize=(6, 5), dpi=100)

    plot2 = fig.add_subplot(111)
    plot2.plot(X_actualTime, Y_accelY, label="Y_val")
    plot2.set_title("Graf závislosti accelY na čase")
    plot2.set_xlabel("Čas [ms]")
    plot2.set_ylabel("accelY")
    plot2.legend()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()

    canvas.get_tk_widget().grid(row=1, column=1)

def plot_3():
    fig = Figure(figsize=(6, 5), dpi=100)

    plot3 = fig.add_subplot(111)
    plot3.plot(X_actualTime, Y_accelZ_normalized, label="Z_val")
    plot3.set_title("Graf závislosti accelZ na čase")
    plot3.set_xlabel("Čas [ms]")
    plot3.set_ylabel("accelZ")
    plot3.legend()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()

    canvas.get_tk_widget().grid(row=1, column=2)

def plot_empty():
    fig = Figure(figsize=(6, 5), dpi=100)
    emptyPlot = fig.add_subplot(111)
    emptyPlot.plot([], [])
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=1, column=0)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=1, column=1)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=1, column=2)

def plot_all():
    plot_1()
    plot_2()
    plot_3()

""" def plot_from_combobox():
    if comboBox.get() == "data1":
        plot_1()
    elif comboBox.get() == "data2":
        plot_2()
    elif comboBox.get() == "data3":
        plot_3() """


root = Tk()

root.state("zoomed")
root.title("Měření fyzikálního experimentu")

""" dataTypes = ["data1", "data2", "data3"]
comboBox = ttk.Combobox(root, values=dataTypes)
comboBox.grid(column=0, row=0)
comboBox.set(dataTypes[0])
comboBox['state'] = 'readonly' """

button1 = Button(root, text="importovat data", fg="green", command=plot_all)
button1.grid(row=0, column=0)

plot_empty()

root.mainloop()