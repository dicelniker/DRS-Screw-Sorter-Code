import _tkinter
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog
# from tkinter import messagebox
from apscheduler.schedulers.background import BackgroundScheduler
import random


# MAIN WINDOW SETUP
root = tk.Tk()
# the fancy stuff centers the window (at least in theory)
root.geometry('800x600+' + str(int(root.winfo_screenwidth()/2-400)) + '+0')
root.resizable(False, False)
root.title('DRS ScrewSort')


# ACTUAL CODE
runLoopCheck = False

randNum = random.Random()


# when the program starts
def setup():
    stopButton['state'] = 'disabled'


# when start button is pressed
def begin_the_action():
    global logTextVar

    # immediately disables the start button to prevent running this twice accidentally
    startButton['state'] = 'disabled'
    stopButton['state'] = 'normal'
    logText.configure(state='normal')
    logText.insert(tk.INSERT, 'Starting run sequence...\n')
    logText.configure(state='disabled')

    root.update()

    global runLoopCheck
    runLoopCheck = True


def stop_the_action():
    global logTextVar
    global runLoopCheck
    runLoopCheck = False

    startButton['state'] = 'normal'
    stopButton['state'] = 'disabled'
    logText.configure(state='normal')
    logText.insert(tk.INSERT, 'RUN SEQUENCE DISABLED!\n')
    logText.configure(state='disabled')

    root.update()


# screw types list
screw_types = [
    'Hex_head_big',
    'Hex_head_small',
    'Phillips_head_medium'
]


# setup data list
data_list = []
for i in range(0, 50):
    data_list.append('0')

current_detected_screw_number = '0'
servo_angle = 0


def main_loop_ai_stuff():
    global current_detected_screw_number
    global data_list
    global servo_angle

    logText.configure(state='normal')
    logText.insert(tk.INSERT, 'AI call placeholder!\n')
    logText.configure(state='disabled')
    current_detected_screw_number = str(randNum.randint(0, 1))
    if current_detected_screw_number != '0':
        data_list[0] = current_detected_screw_number

    # figure out servo angle
    servo_angle = 30 * int(data_list[49])

    # the last-most piece "falls off" the end of the virtual belt
    data_list = ['0'] + data_list[0:49]


def main_loop_visual_stuff():
    # used for the virtual belt visualization

    if check_currentDetected.get() == '1':
        currentDetectedLabel.configure(text=current_detected_screw_number)

    if check_virtualBelt.get() == '1':
        for iteration in range(0, 50):
            try:
                virtualBeltCanvas.itemconfig(beltRepresentationList[iteration],
                                             fill=('light blue' if int(data_list[iteration]) else 'dark green'))
            except _tkinter.TclError:
                pass


def main_running_loop():
    if runLoopCheck:
        main_loop_ai_stuff()
        main_loop_visual_stuff()


def show_hide_current_detected():
    global currentDetectedFrame
    global current_detected_screw_number
    global currentDetectedLabel

    if check_currentDetected.get() == '1':
        currentDetectedFrame = ttk.Labelframe(homeTabFrame, text='Currently Detected Screw')
        currentDetectedFrame.place(relx=0.05, rely=0.65, relwidth=0.3, relheight=0.15)
        currentDetectedLabel = ttk.Label(currentDetectedFrame, text='0', font='Helvetica 24')
        currentDetectedLabel.place(relx=0.5, rely=0.5, anchor='center')
    else:
        currentDetectedFrame.destroy()


def show_hide_virtual_belt():
    global virtualBeltFrame
    global virtualBeltCanvas
    global beltRepresentationList

    if check_virtualBelt.get() == '1':
        virtualBeltFrame = ttk.Labelframe(homeTabFrame, text='Known Screws on Belt')
        virtualBeltFrame.place(relx=0.05, rely=0.825, relwidth=0.9, relheight=0.15)
        virtualBeltCanvas = tk.Canvas(virtualBeltFrame, bg='light gray')
        virtualBeltCanvas.place(x=0, y=0, relwidth=1, relheight=1)
        # generates virtual belt
        beltRepresentationList = []
        for iteration in range(0, 50):
            beltRepresentationList.append(
                virtualBeltCanvas.create_rectangle((iteration * 14, 0), (iteration * 14 + 14, 100), fill='green'))
            # make sure to fill in the color immediately or else it won't update until the next cycle; annoying if the
            # machine is paused!
            virtualBeltCanvas.itemconfig(beltRepresentationList[iteration],
                                         fill=('light blue' if int(data_list[iteration]) else 'dark green'))

    else:
        virtualBeltFrame.destroy()


def save_log_to_file():
    saveLogButton['state'] = 'disabled'
    fileSaver = filedialog.asksaveasfile(mode='w', defaultextension='.txt')
    if fileSaver is None:
        return
    textToSave = logText.get(1.0, tk.END)
    fileSaver.write(textToSave)
    fileSaver.close()
    saveLogButton['state'] = 'normal'


# GUI CODE
# main tab set
mainTabs = ttk.Notebook(root)
mainTabs.pack(fill='both', expand=True)

# home tab
homeTabFrame = ttk.Frame(mainTabs)
homeTabFrame.place(x=0, y=0, relwidth=1, relheight=1)

welcomeFrame = ttk.Labelframe(homeTabFrame, text='Welcome')
welcomeFrame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.3)
progNameLabel = ttk.Label(welcomeFrame, text='DRS ScrewSort', font='Helvetica 22')
progNameLabel.place(relx=0.2, rely=0.5, anchor='center')
progDescriptionLabel = ttk.Label(welcomeFrame, font='Helvetica 10', wraplength=400,
                                 text='Hello, and welcome to the DRS Daylight Solutions "DRS ScrewSort" software for '
                                      'your screw sorting device. To begin using, first set up the outputs in the '
                                      '"output setup" tab. For ease of troubleshooting (or just for fun!) you can '
                                      'enable and disable various visualizations below. For more in-depth '
                                      'troubleshooting, you can view the datalog in the "log" tab. Once you have set '
                                      'up the outputs and gotten familiar with the software, you can press "start" '
                                      'below to activate the machine. Press "stop" to pause operation at any time.')
progDescriptionLabel.place(relx=0.4, rely=0.05)

startStopFrame = ttk.Labelframe(homeTabFrame, text='Start/Stop')
startStopFrame.place(relx=0.05, rely=0.375, relwidth=0.55, relheight=0.25)
startButton = tk.Button(startStopFrame, bg='green', text='Start',
                        font='Helvetica, 28', command=begin_the_action)
startButton.place(relx=0.3, rely=0.5, anchor='center')
stopButton = tk.Button(startStopFrame, bg='red', fg='white', text='Finish',
                       font='Helvetica, 28', command=stop_the_action)
stopButton.place(relx=0.7, rely=0.5, anchor='center')

check_currentDetected = tk.StringVar()
check_virtualBelt = tk.StringVar()

visualsFrame = ttk.Labelframe(homeTabFrame, text='Visualizations')
visualsFrame.place(relx=0.65, rely=0.375, relwidth=0.3, relheight=0.25)
visualsCheck_detectedScrewType = ttk.Checkbutton(visualsFrame, text='Detected Screw Type',
                                                 variable=check_currentDetected, command=show_hide_current_detected)
visualsCheck_detectedScrewType.place(relx=0.1, rely=0.1)
visualsCheck_virtualBelt = ttk.Checkbutton(visualsFrame, text='Known Screws on Belt',
                                           variable=check_virtualBelt, command=show_hide_virtual_belt)
visualsCheck_virtualBelt.place(relx=0.1, rely=0.3)


mainTabs.add(homeTabFrame, text='    Run/Stop    ')

# log tab
logTabFrame = ttk.Frame(mainTabs)
logTabFrame.place(x=0, y=0, relwidth=1, relheight=1)

logText = scrolledtext.ScrolledText(logTabFrame)
logText.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.8)
logText.configure(state='disabled')

saveLogButton = ttk.Button(logTabFrame, text='Click here to save log file to system.', command=save_log_to_file)
saveLogButton.place(relx=0.5, rely=0.9, anchor='n')

mainTabs.add(logTabFrame, text='    Log    ')

# Output Setup tab
outputTabFrame = ttk.Frame(mainTabs)
outputTabFrame.place(x=0, y=0, relwidth=1, relheight=1)
mainTabs.add(outputTabFrame, text='    Output Setup    ')

# scheduler setup code!
scheduler = BackgroundScheduler()
scheduler.add_job(main_running_loop, 'interval', id='mainLoop', seconds=0.175)
scheduler.start()

if __name__ == '__main__':
    setup()

    root.mainloop()
    scheduler.shutdown()
