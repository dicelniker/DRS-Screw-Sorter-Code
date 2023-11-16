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
    'None',
    'Misc./Unknown',
    'Screw Type 1',
    'Screw Type 2',
    'Screw Type 3',
    'Screw Type 4'
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
    fileSaver = filedialog.asksaveasfile(mode='w', defaultextension='.txt', title='Save Log to System')
    if fileSaver is None:
        saveLogButton['state'] = 'normal'
        return
    textToSave = logText.get(1.0, tk.END)
    fileSaver.write(textToSave)
    fileSaver.close()
    saveLogButton['state'] = 'normal'


def save_preset_to_file():
    # disabling both to avoid potential risks of multiple file dialogs at once.
    presetSaveButton['state'] = 'disabled'
    presetLoadButton['state'] = 'disabled'
    # get the file as an object.
    fileSaver = filedialog.asksaveasfile(mode='w', defaultextension='.preset', title='Save Settings Preset to System')
    # make sure a file was actually selected!
    if fileSaver is None:
        presetSaveButton['state'] = 'normal'
        presetLoadButton['state'] = 'normal'
        return
    # getting the data from each combobox
    textToSave = (outputCombo1.get() + '\n' + outputCombo2.get() + '\n' + outputCombo3.get() + '\n' +
                  outputCombo4.get() + '\n' + outputCombo5.get() + '\n' + outputCombo6.get() + '\n')
    fileSaver.write(textToSave)
    fileSaver.close()
    presetSaveButton['state'] = 'normal'
    presetLoadButton['state'] = 'normal'


def load_preset_from_file():
    # disabling both to avoid potential risks of multiple file dialogs at once.
    presetSaveButton['state'] = 'disabled'
    presetLoadButton['state'] = 'disabled'
    file = filedialog.askopenfile(mode='r', title='Select a preset file to open.',
                                  filetypes=[('Preset Files', '*.preset')])
    # make sure the opening wasn't canceled!
    if file is None:
        presetSaveButton['state'] = 'normal'
        presetLoadButton['state'] = 'normal'
        return
    # file was selected, so continue
    lines = file.readlines()
    outputCombo1.set(lines[0])
    outputCombo2.set(lines[1])
    outputCombo3.set(lines[2])
    outputCombo4.set(lines[3])
    outputCombo5.set(lines[4])
    outputCombo6.set(lines[5])

    presetSaveButton['state'] = 'normal'
    presetLoadButton['state'] = 'normal'

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
                                 text='Hello, and welcome! To begin using, first set up the outputs in the '
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

outputGuideFrame = ttk.LabelFrame(outputTabFrame, text='Output Setup Guide')
outputGuideFrame.place(relx=0.05, rely=0.05, relwidth=0.4, relheight=0.6)
outputGuideText = ttk.Label(outputGuideFrame,wraplength=300,
                            text='Use this tab to set up where to output each type of screw. '
                                 'One box must always be set up as "Misc/Unknown" or else your system will nor run. To '
                                 'choose what type of screw should go in each box, simply click on the dropdown menu '
                                 'and select the screw type.')
outputGuideText.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

outputSaveFrame = ttk.LabelFrame(outputTabFrame, text='Save & Load Presets')
outputSaveFrame.place(relx=0.05, rely=0.7, relwidth=0.4, relheight=0.25)
presetSaveButton = ttk.Button(outputSaveFrame, text='Save Current Settings to File System', command=save_preset_to_file)
presetSaveButton.place(relx=0.5, rely=0.33, anchor='center')
presetLoadButton = ttk.Button(outputSaveFrame, text='Load Settings from File System', command=load_preset_from_file)
presetLoadButton.place(relx=0.5, rely=0.67, anchor='center')


outputChooserFrame = ttk.Labelframe(outputTabFrame, text='Output Type Selection')
outputChooserFrame.place(relx=0.5, rely=0.05, relwidth=0.45, relheight=0.9)
outputLabel1 = ttk.Label(outputChooserFrame, text='Output 1:')
outputLabel1.place(relx=0.2, rely=0.4)
outputCombo1 = ttk.Combobox(outputChooserFrame)
outputCombo1['values'] = screw_types
outputCombo1['state'] = 'readonly'
outputCombo1.set('None')
outputCombo1.place(relx=0.4, rely=0.4)
outputLabel2 = ttk.Label(outputChooserFrame, text='Output 2:')
outputLabel2.place(relx=0.2, rely=0.5)
outputCombo2 = ttk.Combobox(outputChooserFrame)
outputCombo2['values'] = screw_types
outputCombo2['state'] = 'readonly'
outputCombo2.set('None')
outputCombo2.place(relx=0.4, rely=0.5)
outputLabel3 = ttk.Label(outputChooserFrame, text='Output 3:')
outputLabel3.place(relx=0.2, rely=0.6)
outputCombo3 = ttk.Combobox(outputChooserFrame)
outputCombo3['values'] = screw_types
outputCombo3['state'] = 'readonly'
outputCombo3.set('None')
outputCombo3.place(relx=0.4, rely=0.6)
outputLabel4 = ttk.Label(outputChooserFrame, text='Output 4:')
outputLabel4.place(relx=0.2, rely=0.7)
outputCombo4 = ttk.Combobox(outputChooserFrame)
outputCombo4['values'] = screw_types
outputCombo4['state'] = 'readonly'
outputCombo4.set('None')
outputCombo4.place(relx=0.4, rely=0.7)
outputLabel5 = ttk.Label(outputChooserFrame, text='Output 5:')
outputLabel5.place(relx=0.2, rely=0.8)
outputCombo5 = ttk.Combobox(outputChooserFrame)
outputCombo5['values'] = screw_types
outputCombo5['state'] = 'readonly'
outputCombo5.set('None')
outputCombo5.place(relx=0.4, rely=0.8)
outputLabel6 = ttk.Label(outputChooserFrame, text='Output 6:')
outputLabel6.place(relx=0.2, rely=0.9)
outputCombo6 = ttk.Combobox(outputChooserFrame)
outputCombo6['values'] = screw_types
outputCombo6['state'] = 'readonly'
outputCombo6.set('None')
outputCombo6.place(relx=0.4, rely=0.9)

mainTabs.add(outputTabFrame, text='    Output Setup    ')

# scheduler setup code!
scheduler = BackgroundScheduler()
scheduler.add_job(main_running_loop, 'interval', id='mainLoop', seconds=0.175)
scheduler.start()

if __name__ == '__main__':
    setup()

    root.mainloop()
    scheduler.shutdown()
