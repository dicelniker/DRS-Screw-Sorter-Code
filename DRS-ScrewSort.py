import tkinter as tk
from tkinter import ttk
# from tkinter import messagebox

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
    startButton['state'] = 'normal'
    root.update()

    global runLoopCheck
    runLoopCheck = True
    while runLoopCheck:
        main_running_loop()
        root.update()


def stop_the_action():
    global runLoopCheck
    runLoopCheck = False

    startButton['state'] = 'normal'
    stopButton['state'] = 'disabled'
    root.update()


def main_running_loop():
    # runLoopCheck = 1
    pass


# GUI CODE
# main tab set
mainTabs = ttk.Notebook(root)
mainTabs.pack(fill='both', expand=True)

# home tab
homeTabFrame = ttk.Frame(mainTabs)
homeTabFrame.place(x=0, y=0, relwidth=1, relheight=1)

startStopFrame = ttk.Labelframe(homeTabFrame, text='Start/Stop')
startStopFrame.place(x=0, rely=0.35, relwidth=0.6, relheight=0.25)
startButton = tk.Button(startStopFrame, bg='green', text='Start', font='Helvetica, 28', command=begin_the_action)
startButton.place(relx=0.3, rely=0.5, anchor='center')
stopButton = tk.Button(startStopFrame, bg='red', fg='white', text='Finish', font='Helvetica, 28')
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


if __name__ == '__main__':
    setup()
    root.mainloop()
