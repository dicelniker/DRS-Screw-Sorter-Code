# DRS ScrewSort
# Application for DRS Daylight's screw sorting machine intern project
# add credit as you add stuff :D
# Overall program (all the tabs and such): Noam A.
# A.I. stuff: Misha S.

# main imports
import _tkinter
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import messagebox
from apscheduler.schedulers.background import BackgroundScheduler
# I have NO idea why this isn't needed despite explicitly using it... keeping it here just in case -Noam
# Misha predicts that maybe one of our AI libraries imports it inside the library
# oh. apparently tkinter comes with serial bundled. keeping the "import serial" anyhow for posterity.
# import serial
import serial.tools.list_ports

# AI imports
import tensorflow as tf
import torch
from PIL import Image
from torchvision import transforms
import cv2
import numpy as np


# MAIN WINDOW SETUP
root = tk.Tk()
# the fancy stuff centers the window (at least in theory)
root.geometry('800x600+' + str(int(root.winfo_screenwidth()/2-400)) + '+0')
root.resizable(False, False)
root.title('DRS ScrewSort')


# ACTUAL CODE
runLoopCheck = False

mobilenet = torch.hub.load('pytorch/vision:v0.10.0', 'mobilenet_v2', pretrained=True)
mobilenet.eval()

checkpoint_path = "training_1/cp.ckpt"  # not including the part after this

model = tf.keras.models.Sequential([
                                    tf.keras.Input(shape=(1000,)),
                                    tf.keras.layers.Dense(1000, activation="selu"),  # selu 75%ish accuracy
                                    tf.keras.layers.Dropout(0.3),
                                    tf.keras.layers.Dense(20),  # 20: 75%ish accuracy
                                    tf.keras.layers.Dropout(0.1),
                                    tf.keras.layers.Dense(4)  # last layer needs to be at least the num. of classes? yes
])
model.load_weights(checkpoint_path)

device_num = 1  # should be the attached webcam
cap = cv2.VideoCapture(device_num)
if not cap.isOpened():
    messagebox.showerror(title='Camera not detected',
                         message='Please make sure the USB camera is connected to this device.')
    exit()


def get_prediction(image, embedding=False):
    input_image = Image.fromarray(image)
    preprocess = transforms.Compose([
        transforms.Resize(256),  # necessary?
        # transforms.CenterCrop(224), #necessary? WAS NOT USED IN TRAINING reduces output size significantly(training is 150 mb rather than 1gb)
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(input_image)
    # create a mini-batch as expected by the model
    input_batch = input_tensor.unsqueeze(0)
    # move the input and model to GPU for speed if available
    if torch.cuda.is_available():
        input_batch = input_batch.to('cuda')
        mobilenet.to('cuda')
    with torch.no_grad():
        output = mobilenet(input_batch)[0]
    if embedding:
        return mobilenet(input_batch)[0]
    return model.predict(np.array([output]))  # list (actual python list) of length 4 with logits


# fancy code ripped off the internet for determining which port the arduino is in!
ports = list(serial.tools.list_ports.comports())
for p in ports:
    if "Arduino" in p.description:
        port = p.name
try:
    # I KNOW that it doesn't like that "port" can be undefined.
    # HOWEVER this isn't actually possible, and it's just being fooled by the way I wrote the code lol -Noam
    arduino = serial.Serial(port, 9600)
except NameError:
    messagebox.showerror(title='Arduino not detected!',
                         message='Please make sure the servo arduino is connected to this device.')
    exit()

# set the funnel to the center
# Note: idk why it's not the default one, but str.encode() makes it in the generic format expected by the arduino
arduino.write(str.encode("90\n"))


# when the program starts
def setup():
    stopButton['state'] = 'disabled'


# when start button is pressed
def begin_the_action():
    global logTextVar

    # immediately disables the start button to prevent running this twice accidentally
    startButton['state'] = 'disabled'
    stopButton['state'] = 'normal'
    # the text box is not editable while disabled, even by the program
    # since we enable it then disable it *before* the root.update(), the user only sees the final result
    logText.configure(state='normal')
    logText.insert(tk.INSERT, 'Starting run sequence...\n')
    logText.configure(state='disabled')

    # with this, we know what type of screw goes in what box.
    # We can then just run servo_rot_list.index(desired screw) to get the relative turn angle
    global servo_rot_list
    servo_rot_list = [
        outputCombo1.get(), outputCombo2.get(), outputCombo3.get(),
        outputCombo4.get(), outputCombo5.get(), outputCombo6.get()
    ]
    root.update()

    # a "Misc/Unknown" output is essential for when we add the ability to sort things based on confidence
    # i.e. low confidence results will just be directed there instead of risking it being wrong
    if 'Misc/Unknown' in servo_rot_list:
        global runLoopCheck
        runLoopCheck = True
    else:
        startButton['state'] = 'normal'
        stopButton['state'] = 'disabled'
        logText.configure(state='normal')
        logText.insert(tk.INSERT, 'Error: no "Misc/Unknown" output selected!\n')
        logText.configure(state='disabled')

        root.update()
        messagebox.showerror(title='Output Setup Error', message='Please specify an output as "Misc/Unknown"!')
         

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
# whenever you want to add new types of hardware, put them here
screw_types = [
    'None',
    '0-80 Screw',
    '4-40 Screw',
    '8-32 Screw',
    'Misc/Unknown'
]

# screw type map
# this is because the ID number of things detected by the AI model might not correspond to their ID in screw_types
screw_map = [
             1,
             3,
             2,
             0
]


# setup data list
# EXPLANATION: the data list is a "virtual belt".
# What this means is that when a screw is detected, it is placed at the current location 0.
# At each main loop iteration, we rotate the list, much like the real screws move along the belt so do the screws in
# the virtual belt.
# Each iteration takes a look at the end of the virtual belt to see where to turn the servo to make sure the screw
# about to fall off will be directed correctly by the funnel. - Noam
data_list = []
for i in range(0, 50):
    data_list.append('None')

current_detected_screw_name = 'None'
servo_rot_list = []
servo_angle = 0


# the below few functions are just splittings up of the main loop. They are split by subject.

def find_servo_pos():
    global servo_angle
    global screw_types
    # no need to do anything if nothing's detected
    # NOTE: nothing is done for the no-movement case of where the same type of screw is detected, as telling
    # the servo to go to a position it is already in should have no effect anyhow.
    if data_list[49] == 'None':
        return

    global servo_rot_list
    # if the screw type wasn't selected in outputs it'll output an error!
    try:
        servo_angle = 30 * (servo_rot_list.index(data_list[49]) + 1)
    except ValueError:
        servo_angle = 30 * (servo_rot_list.index('Misc/Unknown') + 1)


def main_loop_ai_stuff():
    global current_detected_screw_name
    global data_list

    # current_detected_screw_name = screw_types[randNum.randint(0,
                                                            # (len(screw_types) - 1)) if randNum.randint(0, 1) else 0]
    # set frame here
    success, frame = cap.read()
    # do we need to take a softmax first? only if we need the actual probabilities to compare
    index_in_ml_space = tf.math.argmax(get_prediction(frame), 1).numpy()[0]
    
    current_detected_screw_name = screw_types[screw_map[index_in_ml_space]]
    if current_detected_screw_name != 'None':
        data_list[0] = current_detected_screw_name
        logText.configure(state='normal')
        logText.insert(tk.INSERT, 'Detected screw "' + current_detected_screw_name + '"\n')
        logText.configure(state='disabled')

    # figure out servo angle
    find_servo_pos()
    # send servo angle to servo arduino
    arduino.write(str.encode(str(servo_angle) + "\n"))

    # the last-most piece "falls off" the end of the virtual belt
    data_list = ['None'] + data_list[0:49]


def main_loop_visual_stuff():

    if check_currentDetected.get() == '1':
        currentDetectedLabel.configure(text=current_detected_screw_name)

    if check_servoAngle.get() == '1':
        servoAngleLabel.configure(text=servo_angle)

    # has to iterate through every rectangle object in the canvas
    if check_virtualBelt.get() == '1':
        for iteration in range(0, 50):
            try:
                virtualBeltCanvas.itemconfig(beltRepresentationList[iteration],
                                             fill=('light blue' if (data_list[iteration] != 'None') else 'dark green'))
            except _tkinter.TclError:
                pass


def main_running_loop():
    if runLoopCheck:
        main_loop_ai_stuff()
        main_loop_visual_stuff()


def show_hide_current_detected():
    global currentDetectedFrame
    global current_detected_screw_name
    global currentDetectedLabel

    if check_currentDetected.get() == '1':
        currentDetectedFrame = ttk.Labelframe(homeTabFrame, text='Currently Detected Screw')
        currentDetectedFrame.place(relx=0.05, rely=0.65, relwidth=0.425, relheight=0.15)
        currentDetectedLabel = ttk.Label(currentDetectedFrame, text='0', font='Helvetica 24')
        currentDetectedLabel.place(relx=0.5, rely=0.5, anchor='center')
    else:
        currentDetectedFrame.destroy()


def show_hide_servo_angle():
    global servoAngleFrame
    global servo_angle
    global servoAngleLabel

    if check_servoAngle.get() == '1':
        servoAngleFrame = ttk.Labelframe(homeTabFrame, text='Current Servo Angle')
        servoAngleFrame.place(relx=0.525, rely=0.65, relwidth=0.425, relheight=0.15)
        servoAngleLabel = ttk.Label(servoAngleFrame, text='0', font='Helvetica 24')
        servoAngleLabel.place(relx=0.5, rely=0.5, anchor='center')
    else:
        servoAngleFrame.destroy()


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
                                         fill=('light blue' if int(data_list.index(data_list[iteration]))
                                               else 'dark green'))

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
check_servoAngle = tk.StringVar()
check_virtualBelt = tk.StringVar()

visualsFrame = ttk.Labelframe(homeTabFrame, text='Visualizations')
visualsFrame.place(relx=0.65, rely=0.375, relwidth=0.3, relheight=0.25)
visualsCheck_detectedScrewType = ttk.Checkbutton(visualsFrame, text='Detected Screw Type',
                                                 variable=check_currentDetected, command=show_hide_current_detected)
visualsCheck_detectedScrewType.place(relx=0.1, rely=0.1)
visualsCheck_servoAngle = ttk.Checkbutton(visualsFrame, text='Current Servo Angle',
                                          variable=check_servoAngle, command=show_hide_servo_angle)
visualsCheck_servoAngle.place(relx=0.1, rely=0.5)
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
outputGuideText = ttk.Label(outputGuideFrame, wraplength=300,
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
scheduler.add_job(main_running_loop, 'interval', id='mainLoop', seconds=0.2)
scheduler.start()

if __name__ == '__main__':
    setup()

    root.mainloop()
    scheduler.shutdown()
