#imports
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time
import random
import copy
import random
from random import randrange
global date
global identifier
global State
global trialCount
global nosepoke
nosepoke = 0

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
    #print('in event checker')
    event_list = []
    global nosepoke
    if GPIO.input(18) and nosepoke == 0:
        event_list.append('nosepoke on')
        nosepoke = 1
    if GPIO.input(18) == False and nosepoke == 1:
        event_list.append('nosepoke off')
        nosepoke = 0
    if GPIO.input(22):
        event_list.append('left screen')
    if GPIO.input(12):
        event_list.append('right screen')
    Record(event_list)
    return()

def Feeder(FeederNumber, PelletNumber):
    #print('in feeder')
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
    global date
    global identifier
    #print('in record entry')
    new_entry = entry
    current_time = time.time()
    text_file = open(str(identifier) + str(date), "a")
    while len(new_entry) > 0:
        text_file.write(str(current_time) + "   " + str(new_entry[0]) + '\n')
        del(new_entry[0])
    text_file.close()
    return

def randomList(sampleList):
    #print('in randomList')
    randomList = []
    tempList = copy.deepcopy(sampleList)
    while len(tempList) > 0:
        selection = randrange(0,len(tempList))
        randomList.append(tempList[selection])
        del tempList[selection]
    return(randomList)

def LeftScreenControl(offer):
    #print('in leftscreen')
    input_signal = list(str(bin(offer)[2:]))
    output = input_signal[::-1]
    while len(output) < 4:
        output.append('0')
        #print(output)
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
    #print('in rightscreen')
    input_signal = list(str(bin(offer)[2:]))
    output = input_signal[::-1]
    while len(output) < 4:
        output.append('0')
        #print(output)
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
    trial_list = []
    Trials = trials
    Number = number
    listplace = 0
    for x in Trials:
        count = 0
        while count < Number[listplace]:
            selection = copy.deepcopy(Trials[listplace])
            trial_list.append(selection)
            if selection[2] == 0:
                Trials[listplace][2] = 1
            elif selection[2] == 1:
                Trials[listplace][2] = 0
            count = count + 1
        listplace = listplace + 1
    return(trial_list)
'''
def ITIGetter():
    print('in ITIGetter')
    firstList = []
    print("Please enter at least as many ITI's as trials, even if you have to repeat. Will fix later. ")
    ITINumber = int(input("How many different ITIs would you like to use?: "))
    while ITINumber > 0:
        newITI = int(input("Please enter an ITI: "))
        firstList.append(newITI)
        ITINumber = ITINumber - 1
    return(firstList)
'''
def StateOne(thisITI,currentTrial):
    global State
    #print('in state 1')
    if currentTrial[2] == 0:
        Record(['Offer (R/L): ' + str(currentTrial[1]) +'/'+str(currentTrial[0])])
        LeftScreenControl(currentTrial[0])
        RightScreenControl(currentTrial[1])
    if currentTrial[2] == 1:
        Record(['Offer (R/L): ' + str(currentTrial[0]) +'/'+str(currentTrial[1])])
        LeftScreenControl(currentTrial[1])
        RightScreenControl(currentTrial[0])
    time.sleep(thisITI)
    State = 2
    return

def StateTwo():
    global State
    #print('in state 2')
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
    return

def StateThree(hold1):
    global State
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
    return

def StateFour(hold2):
    global State
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
    return

def StateFive(currentTrial):
    global State
    reward = currentTrial
    #print('in state 5')
    inputWait = 10 #this is how long the screens stay on waiting for input
    t0 = time.time()
    time_elapsed = 0
    State = 2
    while time_elapsed < inputWait:
        time_elapsed = time.time() - t0
        if GPIO.input(22):
            time_elapsed = inputWait + 1
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
            time_elapsed = inputWait + 1
            entry = ['Chose right']
            if reward[2] == 0:
                ScreensOff()
                Feeder(2,reward[1])
            elif reward[2] == 1:
                ScreensOff()
                Feeder(1, reward[0])
            Record(entry)
            State = 6
    return
           
def BlockLoop(sampleList, itiList,Number,hold1,hold2):
    global trialCount
    global State
    Hold1=hold1
    Hold2=hold2
    Count = 0
    number = Number
    sampleList1 = copy.deepcopy(sampleList)
    itiList1 = copy.deepcopy(itiList)
    randomBlock = randomList(sampleList1)
    #print(randomBlock)
    trialITI = randomList(itiList1)
    for i in randomBlock:
        current_input = 0
        currentTrial = i
        thisITI = trialITI[Count]
        State = 1
        while State < 6:
            if State ==1:
                StateOne(thisITI,currentTrial)
                EventChecker()
            if State == 2:
                StateTwo()
                EventChecker()
            if State == 3:
                StateThree(Hold1)
                EventChecker()
            if State == 4:
                StateFour(Hold2)
                EventChecker()
            if State == 5:
                StateFive(currentTrial)
                EventChecker()
        Count = Count + 1
        trialCount = trialCount+1
    return

def MainLoop():
    global trialCount
    global date
    global identifier
    ScreensOn()
    ScreensOff()
    identifier, date, trials,Number,itiList,hold1,hold2 = DataGrab()
    sampleList = trialList(trials,Number)
    trialCount = 0
    text_file = open(str(identifier) + str(date), "w")
    text_file.close()
    while trialCount < 200:
        BlockLoop(sampleList, itiList, Number,hold1,hold2)
    return
MainLoop()
