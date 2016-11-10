#imports
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time
import random
import copy
import random
from random import randrange
global nosepoke
global fileName


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
    offerList = []
    entry = []
    selection = ''
    parseline = []
    parseline = list(line)
    parseline = parseline[7:]
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
    offerList = []
    selection = ''
    parseline = []
    parseline = list(line)
    parseline = parseline[7:]
    for i in parseline:
        if i == ',':
            entry = copy.deepcopy(selection)
            offerList.append(int(entry))
            selection = ''
        elif i.isdigit():
            selection = selection + i
    offerList.append(int(selection))
    return(offerList)

def DataGrab():
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
    randomList = []
    tempList = copy.deepcopy(sampleList)
    while len(tempList) > 0:
        selection = randrange(0,len(tempList))
        randomList.append(tempList[selection])
        del tempList[selection]
    return(randomList)

def LeftScreenControl(offer):
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
                State = StateFive(currentTrial)
                EventChecker()
        Count = Count + 1
        trialCount = trialCount+1
    return(trialCount)

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
    textFile = open(fileName, "w")
    textFile.close()
    while trialCount < 200:
        trialCount = BlockLoop(sampleList, itiList, Number,hold1,hold2,trialCount)
    return
MainLoop()
