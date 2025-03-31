# Knihovny
from tkinter import Tk, Button, Label, Entry, Text, ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import math

# Konstanty
TEST_FILE = "DATA.csv"
WHEEL_RADIUS = 0.02  # poloměr kola [m]
FIG_X = 6  # šířka grafu
FIG_Y = 5  # výška grafu
DPI = 100  # rozlišení grafu
GRAVITY = 9.81  # gravitační zrychlení [m/s^2]

# Vynulování a převod času v milisekundách na sekundy
def X_actual_time(rawT):
    X_actualTime = []
    startTime = rawT[0]
    for p in range(len(rawT)):
        X_actualTime.append((rawT[p] - startTime) / 1000)
    return X_actualTime

# Převod akcelerace osy Y z G na m/s^2 (Akcelerometr)
def accelY_in_ms2(yAccel):
    accelY = []
    for x in yAccel:
        accelY.append(x * GRAVITY)
    return accelY

# Převod akcelerace osy Z z G na m/s^2 (Akcelerometr)
def accelZ_in_ms2(zAccel):
    accelZ = []
    for x in zAccel:
        accelZ.append(x * GRAVITY)
    return accelZ

# součet 2 složek zrychlení a vynulování počáteční hodnoty (Akcelerometr)
def acceleration_from_acm(yAccel, zAccel):
    accFromAcm = []
    accY0 = yAccel[0]  # počáteční hodnota akcelerace osy Y
    accZ0 = zAccel[0]  # počáteční hodnota akcelerace osy Z
    for p in range(len(yAccel)):
        if (
            yAccel[p] - accY0 < 0
        ):  # pokud je hodnota záporná, vozíček zpomaluje, takže zrychlení je záporné
            accFromAcm.append(
                -math.sqrt(((yAccel[p] - accY0) ** 2) + ((zAccel[p] - accZ0) ** 2))
            )
        else:  # pokud je hodnota kladná, vozíček zrychluje
            accFromAcm.append(
                math.sqrt(((yAccel[p] - accY0) ** 2) + ((zAccel[p] - accZ0) ** 2))
            )
    return accFromAcm

# Převod akcelerace na rychlost (Akcelerometr)
def velocity_from_acceleration(acceleration):
    velFromAcm = []
    previousTime = X_actualTime[0]
    v0 = 0
    for p in range(len(acceleration)):
        sectionTime = X_actualTime[p] - previousTime  # časový interval mezi měřeními
        velFromAcm.append(v0 + acceleration[p] * sectionTime)  # výpočet rychlosti
        v0 = velFromAcm[p]  # uložení spočtené rychlosti jako v0 pro další výpočet
        previousTime = X_actualTime[p]  # aktualizace předchozího času
    return velFromAcm

# Výpočet absolutní hodnoty úhlu, aby výsledná data nebyla záporná (Rot. enkodér)
def total_angle_corr(angleTotal):
    totalAngleCorr = []
    for x in angleTotal:
        totalAngleCorr.append(abs(x))
    return totalAngleCorr

# Výpočet úhlu v radiánech mezi jednotlivými měřeními (Rot. enkodér)
def sec_angle_in_rad(angleTotal):
    secAngleInRad = []
    previousAngle = angleTotal[0]  # počáteční hodnota úhlu
    for x in angleTotal:
        sectionAngle = x - previousAngle  # úhel mezi jednotlivými měřeními
        secAngleInRad.append(math.radians(sectionAngle))  # převod úhlu na radiány
        previousAngle = x  # aktualizace předchozího úhlu
    return secAngleInRad

# Výpočet vzdálenosti na základě úhlu (Rot. enkodér)
def distance_from_rot_enc(secAngle):
    distanceFromRotEnc = []
    for x in secAngle:
        distanceFromRotEnc.append(WHEEL_RADIUS * x)  # vzálenost = poloměr kola * úhel
    return distanceFromRotEnc

# výpočet rychlosti na základě vzdálenosti (Rot. enkodér)
def velocity_from_rot_enc(distance):
    velFromRotEnc = []
    previousTime = X_actualTime[0]  # počáteční čas
    for p in range(len(distance)):
        sectionTime = X_actualTime[p] - previousTime  # časový interval mezi měřeními
        if sectionTime == 0:
            velFromRotEnc.append(0)  # pokud je časový interval 0, rychlost je 0
        else:
            velFromRotEnc.append(distance[p] / sectionTime)  # výpočet rychlosti
        previousTime = X_actualTime[p]  # aktualizace předchozího času
    return velFromRotEnc

# výpočet zrychlení na základě rychlosti (Rot. enkodér)
def acceleration_from_rot_enc(velocity):
    accFromRotEnc = []
    previousTime = X_actualTime[0]
    for p in range(len(velocity)):
        sectionTime = X_actualTime[p] - previousTime
        if sectionTime == 0:
            accFromRotEnc.append(0)  # pokud je časový interval 0, zrychlení je 0
        else:
            accFromRotEnc.append(velocity[p] / sectionTime)  # výpočet zrychlení
            previousTime = X_actualTime[p]
    return accFromRotEnc

# Kreslení grafu
def plot(X_data, Y_data, plotLabel, plotTitle, X_label, Y_label, gridPos):
    fig = Figure(figsize=(FIG_X, FIG_Y), dpi=DPI)

    plot1 = fig.add_subplot(111)
    plot1.plot(X_data, Y_data, label=plotLabel)
    plot1.set_title(plotTitle)
    plot1.set_xlabel(X_label)
    plot1.set_ylabel(Y_label, labelpad=0)
    plot1.legend()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=2, column=gridPos)

# Vytvoření prázdného grafu
def plot_empty(column):
    fig = Figure(figsize=(FIG_X, FIG_Y), dpi=DPI)
    emptyPlot = fig.add_subplot(111)
    emptyPlot.plot([], [])
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=2, column=column)

# Výběr dat na základě comboboxu pro vytvoření grafu (pomocí slovníku)
def plot_from_combobox(gridPos, comboBoxNumber):
    plots = {
        "Rot. enkodér: Graf závislosti úhlu na čase": (
            X_actualTime,
            totalAngleCorr,
            "Celkový úhel",
            "Graf závislosti úhlu na čase",
            "Čas [s]",
            "Úhel [°]",
        ),
        "Rot. enkodér: Graf závislosti uražené vzdálenosti na čase": (
            X_actualTime,
            distFromRotEnc,
            "uražená vzdálenost",
            "Graf závislosti uražené vzdálenosti (z enkodéru) na čase",
            "Čas [s]",
            "Vzdálenost [m]",
        ),
        "Rot. enkodér: Graf závislosti rychlosti na čase": (
            X_actualTime,
            velFromRotEnc,
            "okamžitá rychlost",
            "Graf závislosti rychlosti (z enkodéru) na čase",
            "Čas [s]",
            "Rychlost [m/s]",
        ),
        "Rot. enkodér: Graf závislosti zrychlení na čase": (
            X_actualTime,
            accFromRotEnc,
            "okamžité zrychlení",
            "Graf závislosti zrychlení (z enkodéru) na čase",
            "Čas [s]",
            "Zrychlení [m/s^2]",
        ),
        "Akcelerometr: Graf závislosti zrychlení (osa Y) na čase": (
            X_actualTime,
            accelY_in_G,
            "okamžité zrychlení v ose Y",
            "Graf závislosti zrychlení v ose Y na čase",
            "Čas [s]",
            "accelY",
        ),
        "Akcelerometr: Graf závislosti zrychlení (osa Z) na čase": (
            X_actualTime,
            accelZ_in_G,
            "okamžité zrychlení v ose Z",
            "Graf závislosti zrychlení v ose Z na čase",
            "Čas [s]",
            "accelZ",
        ),
        "Akcelerometr: Graf závislosti zrychlení na čase": (
            X_actualTime,
            accFromAcm,
            "okamžité celkové zrychlení",
            "Graf závislosti celkového zrychlení na čase",
            "Čas [s]",
            "Zrychlení [m/s^2]",
        ),
        "Akcelerometr: Graf závislosti rychlosti na čase": (
            X_actualTime,
            velFromAcm,
            "okamžitá rychlost",
            "Graf závislosti rychlosti na čase",
            "Čas [s]",
            "Rychlost [m/s]",
        ),
    }

    selected_plot = comboBoxNumber.get()  # získání názvu vybraného grafu
    if selected_plot in plots:
        X_data, Y_data, plotLabel, plotTitle, X_label, Y_label = plots[
            selected_plot
        ]  # získání dat pro vybraný graf
        plot(
            X_data, Y_data, plotLabel, plotTitle, X_label, Y_label, gridPos
        )  # vykreslení grafu

# Vypočítání výsledků na základě zadaných a naměřených hodnot
def calculate_result(weight, tilt, time, accRot, velRot, accAcm, velAcm):
    weight = float(weight) / 1000  # převod hmotnosti na kg
    # teoretické výpočty
    force1 = (
        weight * GRAVITY * math.sin(math.radians(float(tilt)))
    )  # výpočet síly souběžné s nakloněnou rovinou působící na vozíček
    caclAccel = force1 / weight  # výpočet zrychlení vozíčku
    caclVel = caclAccel * float(time)  # výpočet rychlosti
    # výpočty s naměřenými hodnotami
    avgAccRot = sum(accRot) / len(accRot)  # průměrné zrychlení z rot. enkodéru
    avgVelRot = sum(velRot) / len(velRot)  # průměrná rychlost z rot. enkodéru
    avgAccAcm = sum(accAcm) / len(accAcm)  # průměrné zrychlení z akcelerometru
    avgVelAcm = sum(velAcm) / len(velAcm)  # průměrná rychlost z akcelerometru
    # Přepne widget Text do normálního stavu, aby bylo možné vpisovat, poté ho znovu nastaví na "disabled"
    text1["state"] = "normal"
    text1.delete("1.0", "end")
    text1.insert(
        "1.0",
        f"Vypočtená síla F1: {force1:.3f} N\nTeoretický výpočet:\nVypočtené zrychlení: {caclAccel:.2f} m/s^2\nVypočtená rychlost: {caclVel:.2f} m/s\n",
    )
    text1.insert(
        "2.0",
        f"Naměřené hodnoty:\nPrůměrné zrychlení (z rot. enkodéru): {avgAccRot:.2f} m/s^2\nPrůměrná rychlost (z rot. enkodéru): {avgVelRot:.2f} m/s\n",
    )
    text1.insert(
        "3.0",
        f"Průměrné zrychlení (z akcelerometru): {avgAccAcm:.2f} m/s^2\nPrůměrná rychlost (z akcelerometru): {avgVelAcm:.2f} m/s\n",
    )
    text1["state"] = "disabled"

# Načtení dat z CSV souboru
reader = pd.read_csv(TEST_FILE)
rawTime = reader["currentTime"].tolist()
totalAngle = reader["totalAngle"].tolist()
accelY_in_G = reader["Y_val"].tolist()
accelZ_in_G = reader["Z_val"].tolist()

# Kontrola platnosti dat
if len(rawTime) == 0 or len(rawTime) != (
    len(totalAngle) or len(accelY_in_G) or len(accelZ_in_G)
):
    raise ValueError("Vstupní data jsou prázdná nebo neplatná.")

# Výpočty hodnot
X_actualTime = X_actual_time(rawTime)
totalAngleCorr = total_angle_corr(totalAngle)
secAngleInRad = sec_angle_in_rad(totalAngleCorr)
distFromRotEnc = distance_from_rot_enc(secAngleInRad)
velFromRotEnc = velocity_from_rot_enc(distFromRotEnc)
accFromRotEnc = acceleration_from_rot_enc(velFromRotEnc)
accelY = accelY_in_ms2(accelY_in_G)
accelZ = accelZ_in_ms2(accelZ_in_G)
accFromAcm = acceleration_from_acm(accelY, accelZ)
velFromAcm = velocity_from_acceleration(accFromAcm)

# Vytvoření GUI
root = Tk()

root.state("zoomed")  # nastavení okna na celou obrazovku
root.title("Měření fyzikálního experimentu")

# Seznam dat pro comboboxy
dataTypes = [
    "Rot. enkodér: Graf závislosti úhlu na čase",
    "Rot. enkodér: Graf závislosti uražené vzdálenosti na čase",
    "Rot. enkodér: Graf závislosti rychlosti na čase",
    "Rot. enkodér: Graf závislosti zrychlení na čase",
    "Akcelerometr: Graf závislosti zrychlení (osa Y) na čase",
    "Akcelerometr: Graf závislosti zrychlení (osa Z) na čase",
    "Akcelerometr: Graf závislosti zrychlení na čase",
    "Akcelerometr: Graf závislosti rychlosti na čase",
]
# Vytvoření comboboxů pro výběr dat
comboBox1 = ttk.Combobox(root, values=dataTypes, width=60)
comboBox1.grid(row=0, column=0)
comboBox1.set(dataTypes[0])
comboBox1["state"] = "readonly"
comboBox2 = ttk.Combobox(root, values=dataTypes, width=60)
comboBox2.grid(row=0, column=1)
comboBox2.set(dataTypes[6])
comboBox2["state"] = "readonly"

# Vytvoření tlačítek pro vykreslení grafů
button1 = Button(
    root,
    text="importovat data",
    fg="green",
    command=lambda: plot_from_combobox(
        0, comboBox1
    ),  # zavolání funkce pomocí lambda výrazu, aby se funkce provedla po stisknutí tlačítka
)
button1.grid(row=1, column=0)
button2 = Button(
    root,
    text="importovat data",
    fg="green",
    command=lambda: plot_from_combobox(1, comboBox2),
)
button2.grid(row=1, column=1)

note1 = Label(root, text="Jako desetinnou čárku použijte tečku.")
note1.grid(row=3, column=0, sticky="n")

# Vytvoření vstupních polí pro zadání hodnot
label1 = Label(root, text="hmotnost vozíčku (v gramech):")
label1.grid(row=3, column=0, sticky="e")
entry1 = Entry(root)
entry1.grid(row=3, column=1, sticky="w")
label2 = Label(root, text="náklon roviny (ve stupních):")
label2.grid(row=4, column=0, sticky="e")
entry2 = Entry(root)
entry2.grid(row=4, column=1, sticky="w")
label3 = Label(root, text="čas pohybu vozíčku (v sekundách):")
label3.grid(row=5, column=0, sticky="e")
entry3 = Entry(root)
entry3.grid(row=5, column=1, sticky="w")

# Vytvoření tlačítek pro výpočet výsledků a resetování vstupních polí
button3 = Button(
    root,
    text="vypočítat",
    fg="green",
    command=lambda: calculate_result(
        entry1.get(),
        entry2.get(),
        entry3.get(),
        accFromRotEnc,
        velFromRotEnc,
        accFromAcm,
        velFromAcm,
    ),
)
button3.grid(row=6, column=1, sticky="nw")
button4 = Button(
    root,
    text="resetovat",
    fg="orange",
    command=lambda: (
        entry1.delete(0, "end"),
        entry2.delete(0, "end"),
        entry3.delete(0, "end"),
    ),
)
button4.grid(row=6, column=1, sticky="n")

# Vytvoření textového pole pro zobrazení výsledků
text1 = Text(root, height=10, width=50)
text1.grid(row=6, column=0, columnspan=2, sticky="w")
text1["state"] = "disabled"

# Vytvoření prázdných grafů
plot_empty(column=0)
plot_empty(column=1)

root.mainloop()
