from tkinter import Tk, Button
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import csv

test_file = "test_data.csv"
""" fh = open(test_file)
data = csv.reader(fh)
header = next(data)
fh.close()
 """

reader = pd.read_csv(test_file)
X_time = reader["currentTime"].tolist()
Y_totalAngle = reader["totalAngle"].tolist()
print(reader)
def plot():
    fig = Figure(figsize=(5, 5), dpi=100)

    plot1 = fig.add_subplot(111)

    plot1.plot(X_time, Y_totalAngle, label="totalAngle")
    plot1.set_title("Graf závislosti úhlu na čase")
    plot1.set_xlabel("Čas [s]")
    plot1.set_ylabel("Úhel [°]")
    plot1.legend()

    canvas = FigureCanvasTkAgg(fig, master=root)
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