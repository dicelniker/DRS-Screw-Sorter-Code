import tkinter as tk
from tkinter import ttk
import time


# setup of main window
root = tk.Tk()
root.geometry('1200x500+0+0')
root.title('virtual belt demo')
root.resizable(False, False)

# setup data list
data_list = []
for i in range(0, 27):
    data_list.append('green')

currentDetectedColor = 'green'


def big_dropped():
    global currentDetectedColor
    currentDetectedColor = 'cyan'


def small_dropped():
    global currentDetectedColor
    currentDetectedColor = 'magenta'


def program_loop():
    global currentDetectedColor
    global data_list
    if currentDetectedColor != 'green':
        data_list[0] = currentDetectedColor
        currentDetectedColor = 'green'
    for iteration in range(0, 27):
        beltCanvas.itemconfig(beltRectList[iteration], fill=data_list[iteration])
    if data_list[26] == 'cyan':
        servoText.configure(text='Big Screw Bin')
    elif data_list[26] == 'magenta':
        servoText.configure(text='Small Screw Bin')
    # first value of list is green b/c no button presses are being checked yet
    # last value is ignored b/c it has 'fallen off' the edge
    data_list = ['green'] + data_list[:26]
    root.update()


# setup controls
screwButtonFrame = ttk.Labelframe(root, text="Input: Drop Screws on to the Belt")
screwButtonFrame.place(x=50, y=25, width=375, height=100)
smallScrewButton = tk.Button(screwButtonFrame, text="Drop Small Screw", background="magenta", command=small_dropped)
smallScrewButton.place(x=25, y=15, width=150, height=50)
bigScrewButton = tk.Button(screwButtonFrame, text="Drop Big Screw", background="cyan", command=big_dropped)
bigScrewButton.place(x=200, y=15, width=150, height=50)
beltSpeedFrame = ttk.Labelframe(root, text="Input: Belt Speed")
beltSpeedFrame.place(x=450, y=25, width=300, height=100)
beltSpeedSlider = ttk.Scale(beltSpeedFrame, from_=1, to=20, orient="horizontal")
beltSpeedSlider.place(x=25, y=25, width=250, height=25)
beltSpeedSlider.set(10)

# setup servo output
servoFrame = ttk.Labelframe(root, text="Program: Servo Position")
servoFrame.place(x=800, y=25, width=350, height=100)
servoText = ttk.Label(servoFrame, text='Start Position', font='Helvetica, 24')
servoText.place(relx=0.65, rely=0.5, relwidth=1, relheight=1, anchor='center')

# setup virtual belt
beltFrame = ttk.Labelframe(root, text="Program: Virtual Belt")
beltFrame.place(x=50, y=150, width=1100, height=150)
beltCanvas = tk.Canvas(beltFrame, bg='light gray')
beltCanvas.place(x=0, y=0, relwidth=1, relheight=1)
beltRectList = []
for i in range(0, 27):
    beltRectList.append(beltCanvas.create_rectangle((i * 40, 0), (i*40 + 40, 100), fill='green'))

while True:
    try:
        program_loop()
        time.sleep(1 / beltSpeedSlider.get())
    except tk.TclError:
        break
