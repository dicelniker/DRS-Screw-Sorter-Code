import tkinter as tk
from tkinter import ttk
# from tkinter import messagebox
from apscheduler.schedulers.background import BackgroundScheduler


# MAIN WINDOW SETUP
root = tk.Tk()
# the fancy stuff centers the window (at least in theory)
root.geometry('800x600+' + str(int(root.winfo_screenwidth()/2-400)) + '+0')
root.title('DRS ScrewSort')


# ACTUAL CODE
runLoopCheck = False


# when the program starts
def setup():
    stopButton['state'] = 'disabled'


# when start button is pressed
def begin_the_action():
    # immediately disables the start button to prevent running this twice accidentally
    startButton['state'] = 'disabled'
    stopButton['state'] = 'normal'
    root.update()

    global runLoopCheck
    runLoopCheck = True


def stop_the_action():
    global runLoopCheck
    runLoopCheck = False

    startButton['state'] = 'normal'
    stopButton['state'] = 'disabled'
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

current_detected_screw = '0'
servo_angle = 0


def main_loop_AI_stuff():
    global current_detected_screw
    global data_list
    global servo_angle

    print('AI call placeholder!')
    current_detected_screw = '1'
    if current_detected_screw != '0':
        data_list[0] = current_detected_screw
        current_detected_screw = '0'

    # used for the virtual belt visualization
    for iteration in range(0, 50):
        # beltCanvas.itemconfig(beltRectList[iteration], fill=data_list[iteration])
        pass

    # figure out servo angle
    servo_angle = 30 * int(data_list[49])

    # the last-most piece "falls off" the end of the virtual belt
    data_list = ['0'] + data_list[1:50]


def main_running_loop():
    if runLoopCheck:
        main_loop_AI_stuff()



# GUI CODE
# main tab set
mainTabs = ttk.Notebook(root)
mainTabs.pack(fill='both', expand=True)

# home tab
homeTabFrame = ttk.Frame(mainTabs)
homeTabFrame.place(x=0, y=0, relwidth=1, relheight=1)

startStopFrame = ttk.Labelframe(homeTabFrame, text='Start/Stop')
startStopFrame.place(x=0, rely=0.35, relwidth=0.6, relheight=0.25)
startButton = tk.Button(startStopFrame, bg='green', text='Start',
                        font='Helvetica, 28', command=begin_the_action)
startButton.place(relx=0.3, rely=0.5, anchor='center')
stopButton = tk.Button(startStopFrame, bg='red', fg='white', text='Finish',
                       font='Helvetica, 28', command=stop_the_action)
stopButton.place(relx=0.7, rely=0.5, anchor='center')

mainTabs.add(homeTabFrame, text='    Run/Stop    ')

# log tab
lagTabFrame = ttk.Frame(mainTabs)
lagTabFrame.place(x=0, y=0, relwidth=1, relheight=1)
mainTabs.add(lagTabFrame, text='    Log    ')

# Output Setup tab
outputTabFrame = ttk.Frame(mainTabs)
outputTabFrame.place(x=0, y=0, relwidth=1, relheight=1)
mainTabs.add(outputTabFrame, text='    Output Setup    ')

# scheduler setup code!
sched = BackgroundScheduler()
sched.add_job(main_running_loop, 'interval', id='mainLoop', seconds=0.1)
sched.start()

if __name__ == '__main__':
    setup()

    root.mainloop()
    sched.shutdown()
