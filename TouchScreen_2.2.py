#imports
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time
import random
import copy
import random
from random import randrange
from tkinter import *
global nosepoke  #holds current state of the nosepoke
global fileName #name of the datafile, extracted from settings

GPIO.setup(18, GPIO.IN,pull_up_down=GPIO.PUD_DOWN) #nosepoke
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #left screen in
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #right screen in
GPIO.setup(4, GPIO.OUT) #tone
GPIO.setup(5, GPIO.OUT) #leftscreen1
GPIO.setup(6, GPIO.OUT) #leftscreen2
GPIO.setup(13, GPIO.OUT) #Leftscreen3
GPIO.setup(19, GPIO.OUT) #leftscreen4
GPIO.setup(16, GPIO.OUT) #rightscreen1
GPIO.setup(20, GPIO.OUT) #rightscreen2
GPIO.setup(21, GPIO.OUT) #rightscreen3
GPIO.setup(26, GPIO.OUT) #rightscreen4
GPIO.setup(23, GPIO.OUT) #feeder one
GPIO.setup(24, GPIO.OUT) #feeder two

def trialParse(line):
    """Grabs and formats the trial list from the settings file.

    Takes a line of text formatted as ratios (such as 1/2,3/4,5/6)
    and puts them into an array with a randomized binary value. In
    the example case, it might return [[1,2,0],[3,4,1],[5,6,1]].
    
    Args:
       line: the current line of settings.txt that DataGrab() is working on
    Returns:
       offerlist: a list of ratios to be ordered and passed to the touchscreens
    """
    offerList = []
    entry = []
    selection = ''
    parseline = []
    parseline = list(line)
    for i in parseline:
        if i == ',':
            entry.append(int(selection))
            sideVar = random.randint(0,1)
            entry.append(sideVar)
            offerList.append(entry)
            entry =[]
            selection = ''
        elif i.isdigit():
            selection = selection + i
        elif i == '/':
            entry.append(int(selection))
            selection = ''
    entry.append(int(selection))
    sideVar = random.randint(0,1)
    entry.append(sideVar)
    offerList.append(entry)
    return(offerList)

def Parse(line):
    """Takes in non-trial data from the settings file.

    Arranges the information in whatever line is passed into a list of integers.

    Args:
       line: One line of text presumably from settings.txt
    Returns:
       newList: A list of integers extracted from the line arg
    """
    newList = []
    selection = ''
    parseline = []
    parseline = list(line)
    for i in parseline:
        if i == ',':
            entry = copy.deepcopy(selection)
            newList.append(int(entry))
            selection = ''
        elif i.isdigit():
            selection = selection + i
    newList.append(int(selection))
    return(newList)

def dataGrab(listy1):
    global listy
    hold1 = 0
    hold2 = 0
    count = 0
    name = ''
    date = ''
    Number = []
    trials = []
    ITIs = []
    listy = listy1
    for i in listy:
        if count == 0:
            name  = copy.deepcopy(i)
        if count == 1:
            date = i
        if count == 2:
            trials = trialParse(i)
        if count == 3:
            Number = Parse(i)
        if count == 4:
            ITIs = Parse(i)
        if count == 5:
            Hold1 = copy.deepcopy(i)
        if count == 6:
            Hold2 = copy.deepcopy(i)
        count = count + 1
    listy = [name, date, trials, Number, ITIs, Hold1,Hold2]
    return(listy)


def EventChecker():
    """Checks for screen touches and nosepokes and unpokes.

    Lookas at the three GPIO pins associated with the left screen, the
    right screen, and the nosepoke, passing any changes or activations
    to the Record() function for storage in the data file.
    """
    eventList = []
    global nosepoke
    if GPIO.input(18) and nosepoke == 0:
        eventList.append('nosepoke on')
        nosepoke = 1
    if GPIO.input(18) == False and nosepoke == 1:
        eventList.append('nosepoke off')
        nosepoke = 0
    if GPIO.input(22):
        eventList.append('left screen')
    if GPIO.input(12):
        eventList.append('right screen')
    Record(eventList)
    return()

def Feeder(FeederNumber, PelletNumber):
    """Turns on a Feeder for enough time to disburse the apprpriate amount of pellets.

    Turns on one of two GPIO pins connected to feeders for a number of seconds equal to
    .8*reward size.

    Args:
       FeederNumber: Takes either 1 or 2, which in this case represent the two feeders
       with different types of reward in them.
       PelletNumber: The number of pellets that the rats are going to be rewarded with
       for their selection
    """
    if FeederNumber == 1:
        control = 23
    if FeederNumber == 2:
        control = 24
    GPIO.output(control, GPIO.HIGH)
    time.sleep(PelletNumber*.8)
    GPIO.output(control, GPIO.LOW)
    return

def ScreensOn():
    GPIO.output(19, GPIO.HIGH)
    GPIO.output(26,GPIO.HIGH)
    return

def ScreensOff():
    GPIO.output(19, GPIO.LOW)
    GPIO.output(26,GPIO.LOW)
    return

def Record(entry):
    """Writes event(s) to the data file.

    Takes a list of event(s) and writes them with a timestamp to the current working
    data file, in this case a text file named after the global str fileName.

    Args:
       entry: a list of one or more events to be written to the data file
    """
    global fileName
    newEntry = entry
    currentTime = time.time()
    textFile = open(fileName, "a")
    while len(newEntry) > 0:
        textFile.write(str(currentTime) + "   " + str(newEntry[0]) + '\n')
        del(newEntry[0])
    textFile.close()
    return

def randomList(sampleList):
    """Takes a list and randomizes the order, returning the randomized list.

    Takes a list first cloning it then randomizing it, leaving the original
    list unchanged.
    
    Args:
       sampleList: list that needs shuffling.
    Returns:
       randomList: A randomized version of the original sampleList.
    """
    randomList = []
    tempList = copy.deepcopy(sampleList)
    while len(tempList) > 0:
        selection = randrange(0,len(tempList))
        randomList.append(tempList[selection])
        del tempList[selection]
    return(randomList)

def LeftScreenControl(offer):
    """Sends the signal for what is to be displayed on the left screen to the arduino

    Takes a number corresponding to a given offer and converts it to binary, before
    sending each bit of the binary out through a different GPIO pin
    Args:
       offer: A number corresponding to a cue to be displayed on a touchscreen
    """
    inputSignal = list(str(bin(offer)[2:]))
    output = inputSignal[::-1]
    while len(output) < 4:
        output.append('0')
    if output[0] == '1':
        GPIO.output(5, GPIO.HIGH)
    if output[1] == '1':
        GPIO.output(6, GPIO.HIGH)
    if output[2] == '1':
        GPIO.output(13, GPIO.HIGH)
    if output[3] == '1':
        GPIO.output(19, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(5,GPIO.LOW)
    GPIO.output(6,GPIO.LOW)
    GPIO.output(13,GPIO.LOW)
    GPIO.output(19,GPIO.LOW)
    return

def RightScreenControl(offer):
    """Sends the signal for what is to be displayed on the right screen to the arduino.

    Takes a number corresponding to a given offer and converts it to binary, before
    sending each bit of the binary out through a different GPIO pin.
    Args:
       offer: A number corresponding to a cue to be displayed on a touchscreen
    """
    inputSignal = list(str(bin(offer)[2:]))
    output = inputSignal[::-1]
    while len(output) < 4:
        output.append('0')
    if (output[0]) == '1':
        GPIO.output(16, GPIO.HIGH)
    if (output[1]) == '1':
        GPIO.output(20, GPIO.HIGH)
    if (output[2]) == '1':
        GPIO.output(21, GPIO.HIGH)
    if (output[3]) == '1':
        GPIO.output(26, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(16,GPIO.LOW)
    GPIO.output(20,GPIO.LOW)
    GPIO.output(21,GPIO.LOW)
    GPIO.output(26,GPIO.LOW)
    return

def trialList(trials,number):
    """Builds a list of trials for a given block.

    Takes the ratios of the offers to be presented and the corresponding number of time
    each ratio is to be offered and iterates the ratio onto a list that many times, with
    a binary bit at the end randomized to counterbalance offers by screen.

    Args:
       trials: A list of the trial ratios for a given session
       number: a list of values each corresponding to one entry in trials denoting how
       many times that trial is to occur in a given block
    Returns:
       trialList: the not-yet-randomized list of offers in a block
    """
    trialList = []
    Trials = trials
    Number = number
    listplace = 0
    for x in Trials:
        count = 0
        while count < Number[listplace]:
            selection = copy.deepcopy(Trials[listplace])
            trialList.append(selection)
            if selection[2] == 0:
                Trials[listplace][2] = 1
            elif selection[2] == 1:
                Trials[listplace][2] = 0
            count = count + 1
        listplace = listplace + 1
    return(trialList)

def StateOne(thisITI,currentTrial):
    """First stage of a trial in the touchscreen task.

    Sends an output to each touchscreen telling them what the offer they are going to
    display is, then waits for a random ITI off the user inputted list of ITIs.

    Args:
       thisITI: the next value on the list of randomized user entered ITIs
       currentTrial: An array entry with what is to be displayed on each screen
    Returns:
       State: the current Stage of the trial
    """
    State = 1
    if currentTrial[2] == 0:
        Record(['Offer (R/L): ' + str(currentTrial[1]) +'/'+str(currentTrial[0])])
        LeftScreenControl(currentTrial[0])
        RightScreenControl(currentTrial[1])
    if currentTrial[2] == 1:
        Record(['Offer (R/L): ' + str(currentTrial[0]) +'/'+str(currentTrial[1])])
        LeftScreenControl(currentTrial[1])
        RightScreenControl(currentTrial[0])
    t0 = time.time()
    timer = 0
    while timer < thisITI:
        timer = time.time() - t0
        EventChecker()
    State = 2
    return(State)

def StateTwo():
    """Second stage of a trial in the touchscreen task.

    Turns on a GPIO pin controlling a tone, then waits for a nosepoke to either pass
    to the next stage of the trial, or default back to the first.

    Returns:
       State: the current stage of the trial
    """
    State = 2
    GPIO.output(4, GPIO.HIGH)
    t0 = time.time()
    timeout = 1
    State = 1
    while (timeout < 4):
        timeout = time.time() - t0
        if (GPIO.input(18)):
            timout = -1
            State = 3
    if State == 1:
        GPIO.output(4, GPIO.LOW)
    return(State)

def StateThree(hold1):
    """Third stage of a trial in the touchscreen task.

    Checks to make sure the animal nosepokes for a long enough amount of time (in
    this case 'long enough' is a user generated value in the settings file.

    Args:
       hold1: the duration for which the animal must nosepoke to turn the screen on
    Returns:
       State: the current stage of the trial
    """
    State = 3
    holdtime = hold1
    poketime = 0
    t0 = time.time()
    while (GPIO.input(18)) and poketime < holdtime:
        poketime = time.time() - t0
        EventChecker()
    if (poketime >= holdtime):
        State = 4
    else:
         State = 2
    return(State)

def StateFour(hold2):
    """Fourth stage of a trial in the touchscreen task.

    Makes sure the animal nosepokes for long enough to keep the screen on, then
    changes the State to 5.

    Args:
       hold2: the duration for which an animal needs to nosepoke with the screens on
    Returns:
       State: the current stage of the trial
    """
    State = 4
    t0 = time.time()
    holdTime = 0
    screenHold = hold2
    ScreensOn()
    while GPIO.input(18) and holdTime < screenHold:
        holdTime = time.time()-t0
        EventChecker()
    if holdTime < screenHold:
        State = 2
        ScreensOff()
    elif holdTime >= screenHold:
        State = 5
    GPIO.output(4, GPIO.LOW)
    return(State)

def StateFive(currentTrial):
    """Fifth stage of a trial in the touchscreen task.

    Waits for input from the touchscreens then records the choice and rewards the animal.

    Args:
       currentTrial: array entry containing the offers/rewards the rats are choosing between.
    Returns:
       State: the current stage of the trial
    """
    reward = currentTrial
    inputWait = 10 #this is how long the screens stay on waiting for input
    t0 = time.time()
    timeElapsed = 0
    State = 2
    while timeElapsed < inputWait:
        timeElapsed = time.time() - t0
        if GPIO.input(22):
            timeElapsed = inputWait + 1
            entry = ['Chose left']
            if reward[2] == 0:
                ScreensOff()
                Feeder(1,reward[0])
            elif reward[2] == 1:
                ScreensOff()
                Feeder(2, reward[1])
            Record(entry)
            State = 6
        if GPIO.input(12):
            timeElapsed = inputWait + 1
            entry = ['Chose right']
            if reward[2] == 0:
                ScreensOff()
                Feeder(2,reward[1])
            elif reward[2] == 1:
                ScreensOff()
                Feeder(1, reward[0])
            Record(entry)
            State = 6
    return(State)
           
def BlockLoop(sampleList, itiList,Number,hold1,hold2,trialCount):
    """Runs one block of the touchscreen task, acts as the central hub between States.

    Takes input that the MainLoop() has grabbed from settings, and then randomizes it into
    a list of trials and ITIs to be run in that new order in the block. It then runs through each
    trial in the lists, looping back on itself if the animal stops partwat through.

    Args:
       sampleList: A list of the trial ratios for a given session, to be associated with a
       value from the number arg and added into a randomized list that many times.
       itiList: list of ITIs for a given session, to be randomized
       Number: a list of values each corresponding to one entry in trials denoting how
       many times that trial is to occur in a given block
       hold1: the duration for which the animal must nosepoke to turn the screen on
       hold2: the duration for which the animal must continue to nosepoke with the screen on
       trialCount: counter keeping track of the number of trials in the current session
    Returns:
       trialCount: counter keeping track of the number of trials in the current session
    """
    global State
    Hold1=int(hold1)
    Hold2=int(hold2)
    Count = 0
    number = Number
    sampleList1 = copy.deepcopy(sampleList)
    itiList1 = copy.deepcopy(itiList)
    randomBlock = randomList(sampleList1)
    trialITI = randomList(itiList1)
    for i in randomBlock:
        print(sampleList, itiList,Number,hold1,hold2,trialCount)
        currentTrial = i
        thisITI = trialITI[Count]
        State = 1
        while State < 6:
            if State ==1:
                State = StateOne(thisITI,currentTrial)
                EventChecker()
            if State == 2:
                State = StateTwo()
                EventChecker()
            if State == 3:
                State = StateThree(Hold1)
                EventChecker()
            if State == 4:
                State = StateFour(Hold2)
                EventChecker()
            if State == 5:
                State = StateFive(currentTrial)
                EventChecker()
        Count = Count + 1
        trialCount = trialCount+1
    return(trialCount)

def MainLoop(stuff):
    """Sets up the session, and checks to see if it has run through the requisite trials.

    Clears the touchscreens, and then grabs the relevant information from the settings file. It then
    creates an appropriately named data file, and passes the task off to blockloop to run each block.
    """
    global fileName
    global nosepoke
    nosepoke = 0
    ScreensOn()
    ScreensOff()
    identifier = stuff[0]
    date = stuff[1]
    trials = stuff[2]
    Number = stuff[3]
    itiList = stuff[4]
    hold1 = stuff[5]
    hold2 = stuff[6]
    fileName = str(date)+str(identifier)
    sampleList = trialList(trials,Number)
    trialCount = 0
    textFile = open(fileName, "w")
    textFile.close()
    while trialCount < 200:
        trialCount = BlockLoop(sampleList, itiList, Number,hold1,hold2,trialCount)
    print('Done!')
    return


def show_entry_fields():
    listy1 = [line1.get(), line2.get(),line3.get(), line4.get(),line5.get(), line6.get(), line7.get()]
    MainLoop(dataGrab(listy1))

def close_window():
    window.destroy()

master = Tk()
Label(master, text="Name: ").grid(row=0)
Label(master, text="Date: ").grid(row=1)
Label(master, text="Trial: ").grid(row=2)
Label(master, text="Count: ").grid(row=3)
Label(master, text="ITIs: ").grid(row=4)
Label(master, text="Hold 1: ").grid(row=5)
Label(master, text="Hold 2: ").grid(row=6)

line1 = Entry(master)
line2 = Entry(master)
line3 = Entry(master)
line4 = Entry(master)
line5 = Entry(master)
line6 = Entry(master)
line7 = Entry(master)

line1.grid(row=0, column=1)
line2.grid(row=1, column=1)
line3.grid(row=2, column=1)
line4.grid(row=3, column=1)
line5.grid(row=4, column=1)
line6.grid(row=5, column=1)
line7.grid(row=6, column=1)

Button(master, text='Quit', command=close_window).grid(row=7, column=0, sticky=W, pady=4)
Button(master, text='Show', command=show_entry_fields).grid(row=7, column=1, sticky=W, pady=4)

