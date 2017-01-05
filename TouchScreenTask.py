#imports
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time
import random
import copy
from random import randrange
global nosepoke  #holds current state of the nosepoke
global fileName #name of the datafile, extracted from settings


#The following section is just a way to change the GPIO mapping quickly
#this first section makes the GPIO map avaliable to all functions
global nose_poke
global left_in
global right_in
global tone
global left_1
global left_2
global left_3
global left_4
global right_1
global right_2
global right_3
global right_4
global feeder_1
global feeder_2

#this is where the mapping actually is, change the number to change the pin
#the names are hopefully self explanatory for the most part
nose_poke = 13
left_in = 10
right_in = 9
tone = 5
left_1 = 19
left_2 = 26
left_3 = 24
left_4 = 23
right_1 = 18
right_2 = 21
right_3 = 12
right_4 = 16
feeder_1 = 13
feeder_2 = 14


GPIO.setup(nose_poke, GPIO.IN,pull_up_down=GPIO.PUD_DOWN) #nosepoke
GPIO.setup(left_in, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #left screen in
GPIO.setup(right_in, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #right scr een in
GPIO.setup(tone, GPIO.OUT) #tone
GPIO.setup(left_1, GPIO.OUT) #leftscreen1
GPIO.setup(left_2, GPIO.OUT) #leftscreen2
GPIO.setup(left_3, GPIO.OUT) #Leftscreen3
GPIO.setup(left_4, GPIO.OUT) #leftscreen4
GPIO.setup(right_1, GPIO.OUT) #rightscreen1
GPIO.setup(right_2, GPIO.OUT) #rightscreen2
GPIO.setup(right_3, GPIO.OUT) #rightscreen3
GPIO.setup(right_4, GPIO.OUT) #rightscreen4
GPIO.setup(feeder_1, GPIO.OUT) #feeder one
GPIO.setup(feeder_2, GPIO.OUT) #feeder two

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
    parseline = parseline[7:]
    count = 0
    for i in parseline:
        if i == ',':
            entry.append(int(selection))
            sideVar = random.randint(0,1)
            entry.append(sideVar)
            entry.append(count)
            offerList.append(entry)
            count = count + 1
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
    entry.append(count)
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
    parseline = parseline[7:]
    for i in parseline:
        if i == ',':
            entry = copy.deepcopy(selection)
            newList.append(int(entry))
            selection = ''
        elif i.isdigit():
            selection = selection + i
    newList.append(int(selection))
    return(newList)

def DataGrab():
    """Pulls setup data for the session from a file called settings.txt in the same directory.

    Looks through Settings.txt line by line, extracting a relevant parameter from each
    and operating on each differently according to the sequence in which they are arranged.

    Returns:
       Name: the name of the animal being run, should be 4 characters
       Date: the date, should again be 4 characters (0221 being february 21st)
       trials: a list of the desired ratios for the experimental trials
       Number: the number of each corresponding ratio that should occur in each block
       ITIs: a list of inter-trial intervals
       hold1: required nosepoke with the screens off
       hold2: required nosepoke with the screens on
    """
    lineswitch = 0 
    hold1=0
    hold2=0
    Name = ''
    Date = ''
    trials = []
    ITIs = []
    TrialNumber = []
    file = open('Settings.txt', 'r')
    for line in iter(file):
        if lineswitch == 0:
            Name = line[7:]
        elif lineswitch == 1:
            Date = line[7:]
        elif lineswitch == 2:
            trials = trialParse(line)
        elif lineswitch == 3:
            Number = Parse(line)
        elif lineswitch == 4:
            ITIs = Parse(line)
        elif lineswitch == 5:
            hold1 = float(line[7:].rstrip())
        elif lineswitch == 6:
            hold2 = float(line[7:].rstrip())
        lineswitch = lineswitch + 1
    return(Name, Date, trials, Number, ITIs, hold1,hold2)

def EventChecker():
    """Checks for screen touches and nosepokes and unpokes.

    Lookas at the three GPIO pins associated with the left screen, the
    right screen, and the nosepoke, passing any changes or activations
    to the Record() function for storage in the data file.
    """
    eventList = []
    global nosepoke
    if GPIO.input(nose_poke) and nosepoke == 0:
        eventList.append('nosepoke on')
        nosepoke = 1
    if GPIO.input(nose_poke) == False and nosepoke == 1:
        eventList.append('nosepoke off')
        nosepoke = 0
    if GPIO.input(left_in):
        eventList.append('left screen')
    if GPIO.input(right_in):
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
        control = feeder_1
    if FeederNumber == 2:
        control = feeder_2
    GPIO.output(control, GPIO.HIGH)
    time.sleep(PelletNumber*.8)
    GPIO.output(control, GPIO.LOW)
    return

def ScreensOn():
    GPIO.output(left_4, GPIO.HIGH)
    GPIO.output(right_4,GPIO.HIGH)
    return

def ScreensOff():
    GPIO.output(left_4, GPIO.LOW)
    GPIO.output(right_4,GPIO.LOW)
    GPIO.output(left_1, GPIO.HIGH)
    GPIO.output(left_4,GPIO.HIGH)
    GPIO.output(right_1, GPIO.HIGH)
    GPIO.output(right_4,GPIO.HIGH)
    GPIO.output(left_1, GPIO.LOW)
    GPIO.output(left_4,GPIO.LOW)
    GPIO.output(right_1, GPIO.LOW)
    GPIO.output(right_4,GPIO.LOW)
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
        GPIO.output(left_1, GPIO.HIGH)
    if output[1] == '1':
        GPIO.output(left_2, GPIO.HIGH)
    if output[2] == '1':
        GPIO.output(left_3, GPIO.HIGH)
    if output[3] == '1':
        GPIO.output(left_4, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(left_1,GPIO.LOW)
    GPIO.output(left_2,GPIO.LOW)
    GPIO.output(left_3,GPIO.LOW)
    GPIO.output(left_4,GPIO.LOW)
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
        GPIO.output(right_1, GPIO.HIGH)
    if (output[1]) == '1':
        GPIO.output(right_2, GPIO.HIGH)
    if (output[2]) == '1':
        GPIO.output(right_3, GPIO.HIGH)
    if (output[3]) == '1':
        GPIO.output(right_4, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(right_1,GPIO.LOW)
    GPIO.output(right_2,GPIO.LOW)
    GPIO.output(right_3,GPIO.LOW)
    GPIO.output(right_4,GPIO.LOW)
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
        LeftScreenControl(currentTrial[0]+1)
        RightScreenControl(currentTrial[1]+9)
    if currentTrial[2] == 1:
        Record(['Offer (R/L): ' + str(currentTrial[0]) +'/'+str(currentTrial[1])])
        LeftScreenControl(currentTrial[1]+9)
        RightScreenControl(currentTrial[0]+1)
    t0 = time.time()
    timer = 0
    while timer < thisITI:
        timer = time.time() - t0
        EventChecker()
    State = 2
    time.sleep(6)
    return(State)

def StateTwo():
    """Second stage of a trial in the touchscreen task.

    Turns on a GPIO pin controlling a tone, then waits for a nosepoke to either pass
    to the next stage of the trial, or default back to the first.

    Returns:
       State: the current stage of the trial
    """
    State = 2
    GPIO.output(tone, GPIO.HIGH)
    t0 = time.time()
    timeout = 1
    State = 1
    while (timeout < 4):
        timeout = time.time() - t0
        if (GPIO.input(nose_poke)):
            timout = -1
            State = 3
    if State == 1:
        GPIO.output(tone, GPIO.LOW)
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
    while (GPIO.input(nose_poke)) and poketime < holdtime:
        poketime = time.time() - t0
        EventChecker()
    if (poketime >= holdtime):
        State = 4
    else:
         State = 1
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
    while GPIO.input(nose_poke) and holdTime < screenHold:
        holdTime = time.time()-t0
        EventChecker()
    if holdTime < screenHold:
        State = 1
        ScreensOff()
    elif holdTime >= screenHold:
        State = 5
    GPIO.output(tone, GPIO.LOW)
    return(State)

def StateFive(currentTrial,trial_totals):

    reward = currentTrial
    inputWait = 10 #this is how long the screens stay on waiting for input
    t0 = time.time()
    timeElapsed = 0
    State = 2
    while timeElapsed < inputWait:
        timeElapsed = time.time() - t0
        if GPIO.input(left_in):
            timeElapsed = inputWait + 1
            if reward[2] == 0:
                entry = ['Chose left Type 1']
                trial_totals[reward[3]*2] = trial_totals[reward[3]*2] + 1
                ScreensOff()
                Feeder(1,reward[0])
            elif reward[2] == 1:
                entry = ['Chose left Type 2']
                trial_totals[reward[3]*2 +1] = trial_totals[reward[3]*2+1] + 1
                ScreensOff()
                Feeder(2, reward[1])
            Record(entry)
            State = 6
        if GPIO.input(right_in):
            timeElapsed = inputWait + 1
            if reward[2] == 0:
                entry = ['Chose Right Type 1']
                trial_totals[reward[3]*2] = trial_totals[reward[3]*2+1] + 1
                ScreensOff()
                Feeder(2,reward[0])
            elif reward[2] == 1:
                entry = ['Chose Right Type 2']
                trial_totals[reward[3]*2 +1] = trial_totals[reward[3]*2] + 1
                ScreensOff()
                Feeder(1, reward[1])
            Record(entry)
            State = 6
    return(State, trial_totals)

def BlockLoop(trial_totals,sampleList, itiList,Number,hold1,hold2,trialCount):

    global State
    Hold1=hold1
    Hold2=hold2
    Count = 0
    number = Number
    sampleList1 = copy.deepcopy(sampleList)
    itiList1 = copy.deepcopy(itiList)
    randomBlock = randomList(sampleList1)
    trialITI = randomList(itiList1)
    for i in randomBlock:
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
                State, trial_totals = StateFive(currentTrial,trial_totals)
                data1 = trial_totals[::2]
                data2 = trial_totals[1::2]
                readout = [data1[i]+data2[i] for i in range(len(data1))]
                type1 = currentTrial[0]
                type2 = currentTrial[1]
                print('Type 1: '+ str(type1) +'  Type 2: '+ str(type2))
                print(data1)
                print(readout)
                EventChecker()
        Count = Count + 1
        trialCount = trialCount+1
    return(trialCount,trial_totals)

def MainLoop():
    global fileName
    global nosepoke
    nosepoke = 0
    ScreensOn()
    ScreensOff()
    identifier, date, trials,Number,itiList,hold1,hold2 = DataGrab()
    fileName = str(date)+str(identifier)
    sampleList = trialList(trials,Number)
    trialCount = 0
    trial_display = []
    for x in trials:
        listcount = 0
        for g in x:
            if listcount < 2:
                trial_display.append(g)
            listcount = listcount + 1
    trial_totals = []
    i = 0
    while i < len(trials):
        trial_totals.append(0)
        trial_totals.append(0)
        i = i + 1
    textFile = open(fileName, "w")
    textFile.close()
    while trialCount < 200:
        print(trial_display)
        trialCount,trial_totals = BlockLoop(trial_totals,sampleList, itiList, Number,hold1,hold2,trialCount)
 
    print('Done!')
    return
MainLoop()

