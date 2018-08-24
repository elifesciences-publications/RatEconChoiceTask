

#imports
import RPi.GPIO as GPIO
import os

#os.nice(-1)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

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
global house_lt

#this is where the mapping actually is, change the number to change the pin
#the names are hopefully self explanatory for the most part
nose_poke = 17
left_in = 22
right_in = 11
tone = 5
left_1 = 23
left_2 = 18
left_3 = 19
left_4 = 16
right_1 = 24
right_2 = 21
right_3 = 26
right_4 = 12
feeder_1 = 13
feeder_2 = 25
house_lt = 3

GPIO.setup(nose_poke, GPIO.IN,pull_up_down=GPIO.PUD_UP) #nosepoke
GPIO.add_event_detect(nose_poke, GPIO.BOTH)
GPIO.setup(left_in, GPIO.IN, pull_up_down=GPIO.PUD_UP) #left screen in
GPIO.add_event_detect(left_in, GPIO.FALLING)
GPIO.setup(right_in, GPIO.IN, pull_up_down=GPIO.PUD_UP) #right scr een in
GPIO.add_event_detect(right_in, GPIO.FALLING)
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
GPIO.setup(house_lt, GPIO.OUT) 

GPIO.output(tone, GPIO.LOW)
GPIO.output(left_1, GPIO.LOW)
GPIO.output(left_2, GPIO.LOW)
GPIO.output(left_3, GPIO.LOW)
GPIO.output(left_4, GPIO.LOW)
GPIO.output(right_1, GPIO.LOW)
GPIO.output(right_2, GPIO.LOW)
GPIO.output(right_3, GPIO.LOW)
GPIO.output(right_4, GPIO.LOW)
GPIO.output(feeder_1, GPIO.LOW)
GPIO.output(feeder_2, GPIO.LOW)
GPIO.output(house_lt, GPIO.LOW)

def ResetScreens():
    GPIO.output(right_4, GPIO.HIGH)
    GPIO.output(left_4, GPIO.HIGH)
    GPIO.output(right_1, GPIO.HIGH)
    GPIO.output(left_1, GPIO.HIGH)
    time.sleep(.2)
    GPIO.output(right_4, GPIO.LOW)
    GPIO.output(left_4, GPIO.LOW)
    GPIO.output(right_1, GPIO.LOW)
    GPIO.output(left_1, GPIO.LOW)
    return

def SendCueInfo(pell1, pell2):

    ResetScreens()
    time.sleep(1)

    #The first output signals to the arduino to listen for the pellet-type
    GPIO.output(left_1, GPIO.HIGH)
    GPIO.output(right_1, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(left_1, GPIO.LOW)
    GPIO.output(right_1, GPIO.LOW)
    
    #This sends the first cue
    SendCue(pell1)
    Record(['CueA:'+str(pell1)])
    #This sends the second
    SendCue(pell2)
    Record(['CueB:'+str(pell2)])
    
    ResetScreens()
    time.sleep(4)
    return

#This function makes sure that any file on that day is not overwritten
def checkfilename(filename):

    filenameuse = filename
    n = 0
    while os.path.isfile(filenameuse):
        n += 1
        filenameuse = filename + '_' + str(n)
    return(filenameuse)

def CheckCues(rat, pell1, pell2):

    pellet1 = []
    pellet2 = []
    Ratnums = [[79,6,2,3,4,1,5],
               [80,1,3,4,2,5,6],
               [81,1,4,5,3,6,2],
               [82,5,6,3,2,4,1],
               [83,3,2,4,1,6,5],
               [84,6,3,5,4,1,2],
               [85,4,3,1,5,2,6],
               [86,4,1,2,3,6,5],
               [41,5,1,3,4,6,2],
               [42,1,5,4,3,2,6],
               [43,6,4,5,2,3,1],
               [44,4,6,2,5,1,3],
               [45,3,2,6,1,5,4],
               [46,2,3,1,6,4,5],
               [47,5,1,3,4,6,2],
               [48,1,5,4,3,2,6],
               [49,6,4,5,2,3,1],
               [50,4,6,2,5,1,3]]
    PelletTypes = ['TUL', 'SALT', 'TUM', 'GRAPE', 'CHOC', 'TUW']
    for x in Ratnums:
        if rat[2:4] == str(x[0]):
            pellet1 = PelletTypes[x.index(pell1) - 1]
            pellet2 = PelletTypes[x.index(pell2) - 1]
    if pellet1 == []:
        print('This rat is not in the database')
        pellet1 = 'cue:'+str(pell1)
        pellet2 = 'cue:'+str(pell2)
    else:
       Name = input('The pellets for this rat and the current cues are '
                    + pellet1 + ' and ' + pellet2 + '. Hit enter to start')
    return(pellet1,pellet2)
     
def SendCue(pell):
    inputSignal = list(str(bin(pell)[2:]))
    output = inputSignal[::-1]
    while len(output) < 4:
        output.append('0')
    if output[0] == '1':
        GPIO.output(left_1, GPIO.HIGH)
        GPIO.output(right_1, GPIO.HIGH)
        
    if output[1] == '1':
        GPIO.output(left_2, GPIO.HIGH)
        GPIO.output(right_2, GPIO.HIGH) 
    if output[2] == '1':
        GPIO.output(left_3, GPIO.HIGH)
        GPIO.output(right_3, GPIO.HIGH)
        
    if output[3] == '1':
        GPIO.output(left_4, GPIO.HIGH)
        GPIO.output(right_4, GPIO.HIGH)
    print(output)
    delay(2)
    GPIO.output(left_1,GPIO.LOW)
    GPIO.output(left_2,GPIO.LOW)
    GPIO.output(left_3,GPIO.LOW)
    GPIO.output(left_4,GPIO.LOW)
    GPIO.output(right_1,GPIO.LOW)
    GPIO.output(right_2,GPIO.LOW)
    GPIO.output(right_3,GPIO.LOW)
    GPIO.output(right_4,GPIO.LOW)
    return

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
       pell1: The identifier for the pellet in feeder 1
       pell2: The identifier for the pellet in feeder 2
    """
    lineswitch = 0 
    hold1=0
    hold2=0
    pell1=0
    pell2=0
    Name = ''
    Date = ''
    trials = []
    ITIs = []
    TrialNumber = []
    file = open('Settings.txt', 'r')
    for line in iter(file):
        if lineswitch == 0:
            Name = input('Rat Name:')#line[7:11]
            #print(len(Name))
        elif lineswitch == 1:
            Date = input('Date:')#line[7:11]
            #print(len(Date))
        elif lineswitch == 2:
            trials = trialParse(line)
        #elif lineswitch == 3:
        #    Number = Parse(line)
        elif lineswitch == 3:
            ITIs = Parse(line)
        elif lineswitch == 4:
            hold1 = float(line[7:].rstrip())
        elif lineswitch == 5:
            hold2 = float(line[7:].rstrip())
        elif lineswitch == 6:
            pell1 = int(input('Pellet_A:'))#int(line[7:].rstrip())
        elif lineswitch == 7:
            pell2 = int(input('Pellet_B:'))#int(line[7:].rstrip())            
        lineswitch = lineswitch + 1
    laser = False    
    return(Name, Date, trials, laser, ITIs, hold1,hold2,pell1,pell2)

def EventChecker():
    """Checks for screen touches and nosepokes and unpokes.
    Lookas at the three GPIO pins associated with the left screen, the
    right screen, and the nosepoke, passing any changes or activations
    to the Record() function for storage in the data file.
    """
    eventList = []
    global nosepoke
    if GPIO.input(nose_poke) == False and nosepoke == 0:
        eventList.append('N1') #nosepoke on
        nosepoke = 1
    if GPIO.input(nose_poke) and nosepoke == 1:
        eventList.append('N0')#nosepoke off
        nosepoke = 0
##    if GPIO.event_detected(nose_poke):
##        if GPIO.input(nose_poke) == False:
##            eventList.append('N1')
##        else:
##            eventList.append('N0')
    if GPIO.event_detected(left_in):
        eventList.append('LP') #left screen
    if GPIO.event_detected(right_in):
        eventList.append('RP') #right screen
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
    if PelletNumber > 0:
        GPIO.output(control, GPIO.HIGH)
        Record(['F'+str(control)+'-1'])
        #time.sleep(PelletNumber*.8)
        delay(.1 + (PelletNumber - 1)*.7) #.8
        GPIO.output(control, GPIO.LOW)
        Record(['F'+str(control)+'-0'])
        #the script then adds an additional 1 second to the ITI for each pellet
        #delivered
        delay(PelletNumber*.5)
    else:
        delay(1)
    return

def ScreensOn():
    GPIO.output(left_4, GPIO.HIGH)
    GPIO.output(right_4,GPIO.HIGH)
    Record(['S1'])
    return

def ScreensOff():
    Record(['S0'])
    GPIO.output(left_4, GPIO.LOW)
    GPIO.output(right_4,GPIO.LOW)
    GPIO.output(left_1, GPIO.HIGH)
    GPIO.output(left_4,GPIO.HIGH)
    GPIO.output(right_1, GPIO.HIGH)
    GPIO.output(right_4,GPIO.HIGH)
    delay(.2)
    GPIO.output(left_1, GPIO.LOW)
    GPIO.output(left_4,GPIO.LOW)
    GPIO.output(right_1, GPIO.LOW)
    GPIO.output(right_4,GPIO.LOW)
    delay(.1)
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
    textFile = open(fileName, "a")
    while len(newEntry) > 0:
        textFile.write(str(time.time()) + "   " + str(newEntry[0]) + '\n')
        del(newEntry[0])
    textFile.close()
    return

def Record2(entry):
    """Writes the current choice behavior to the data file.
    """
    global fileName
    textFile = open(fileName, "a")
    newdata = ''
    for i in entry:
        newdata += '|'
        for j in i:
            newdata += str(j)
            newdata += ','
    textFile.write(str(time.time()) + "   " + newdata + '\n')
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

def ScreenControl(offerL, offerR):
    
    """Sends the signal for what is to be displayed on the screens to the arduino
    Takes a number corresponding to a given offer and converts it to binary, before
    sending each bit of the binary out through a different GPIO pin
    Args:
       offerL: A number corresponding to a cue to be displayed on the left touchscreen
       offerR: A number corresponding to a cue to be displayed on the left touchscreen
    """
 #The bit outputs don't map directly onto the number of pellets. This remaps the
    #number of pellets to the correct number to be converted to the bit output. For
    #example, binary 5 actually has the symbol for 6 pellets, likewise, binary 14,
    #not 15 (9 + 6), refers to 6 pellets for the second pellet-type
    #num2pell = [0,1 , 2, 3, 4, 6, 8, 99, 99, 99 10 11 12 13 15 17]
    num2pell = [0, 0, 2, 3, 4, 5, 0, 6, 0, 7, 10, 11, 12, 13, 0, 14, 0, 15]
    num = num2pell[offerL]

    inputSignal = list(str(bin(num)[2:]))
    outputL = inputSignal[::-1]
    while len(outputL) < 4:
        outputL.append('0')
    if outputL[0] == '1':
        GPIO.output(left_1, GPIO.HIGH)
   
    if outputL[1] == '1':
        GPIO.output(left_2, GPIO.HIGH)
     
    if outputL[2] == '1':
        GPIO.output(left_3, GPIO.HIGH)
    
    if outputL[3] == '1':
        GPIO.output(left_4, GPIO.HIGH)

    num = num2pell[offerR]
    inputSignal = list(str(bin(num)[2:]))
    outputR = inputSignal[::-1]
    while len(outputR) < 4:
        outputR.append('0')
    if outputR[0] == '1':
        GPIO.output(right_1, GPIO.HIGH)
   
    if outputR[1] == '1':
        GPIO.output(right_2, GPIO.HIGH)
     
    if outputR[2] == '1':
        GPIO.output(right_3, GPIO.HIGH)
    
    if outputR[3] == '1':
        GPIO.output(right_4, GPIO.HIGH)

    #print('Left', end=" ")
    #print(outputL)
    #print('Right', end=" ")
    #print(outputR)
    
    delay(.3)
    GPIO.output(left_1,GPIO.LOW)
    GPIO.output(left_2,GPIO.LOW)
    GPIO.output(left_3,GPIO.LOW)
    GPIO.output(left_4,GPIO.LOW)
    GPIO.output(right_1,GPIO.LOW)
    GPIO.output(right_2,GPIO.LOW)
    GPIO.output(right_3,GPIO.LOW)
    GPIO.output(right_4,GPIO.LOW)
    return

def SendtoArd(offer):
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
    #print(output)
    return

def trialList(trials,laser):
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
    Number = 1
    
##    listplace = 0
##    for x in Trials:
##        count = 0
##        while count < Number[listplace]:
##            selection = copy.deepcopy(Trials[listplace])
##            trialList.append(selection)
##            if selection[2] == 0:
##                Trials[listplace][2] = 1
##            elif selection[2] == 1:
##                Trials[listplace][2] = 0
##            count = count + 1
##        listplace = listplace + 1
##    return(trialList)
    count = 0
    for x in Trials:
        for y in range(Number):
            trialList.append([x[0], x[1], 1, 0,x[3]])
            trialList.append([x[0], x[1], 0, 0,x[3]])
            if laser:
                trialList.append([x[0], x[1], 1, 1,x[3]])
                trialList.append([x[0], x[1], 0, 1,x[3]])
        count+=1        
    return(trialList)                           

def delay(sec):
    tn = 0;
    t0 = time.time();
    while tn < sec:
        tn = time.time() - t0
        EventChecker()

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
    if currentTrial[1] == 0:
        offer2 = 1
    else:
        offer2 = currentTrial[1] + 9
    offer1 = currentTrial[0] + 1
    
    #This gives n right vs n left
    if currentTrial[2] == 0:
        #This gives laser or no laser
        if currentTrial[3] == 0: 
            Record([str(currentTrial[0])+'Bv'+str(currentTrial[1])+'A'])
        else:
            Record([str(currentTrial[0])+'Bv'+str(currentTrial[1])+'A-L'])
             
        ScreenControl(offer1, offer2) #First input is left screen, 2nd is right

    if currentTrial[2] == 1:
        if currentTrial[3] == 0: 
            Record([str(currentTrial[1])+'Av'+str(currentTrial[0])+'B'])
        else:
            Record([str(currentTrial[1])+'Av'+str(currentTrial[0])+'B-L'])
        ScreenControl(offer2, offer1)#First input is left screen, 2nd is right

    delay(6)
    State = 2
    #time.sleep(6)
    return(State)

def StateTwo(laser):
    """Second stage of a trial in the touchscreen task.
    Turns on a GPIO pin controlling a tone, then waits for a nosepoke to either pass
    to the next stage of the trial, or default back to the first.
    Returns:
       State: the current stage of the trial
    """
    State = 2
    GPIO.output(tone, GPIO.HIGH)
    Record(['T1'])

    #turn on the laser if a laser trial
    if laser == 1:
        GPIO.output(house_lt, GPIO.HIGH)
        Record(['L1'])
    t0 = time.time()
    timeout = 1
    State = 1
    while (timeout < 20): # 5 seconds for opto study
        timeout = time.time() - t0
        if (GPIO.input(nose_poke) == False):
            #print('nosepoke')
            #timout = -1
            timeout = 21
            State = 3
            
    if State == 1:
        Record(['N0'])
        GPIO.output(tone, GPIO.LOW)
        if laser == 1:
            GPIO.output(house_lt, GPIO.LOW)
            Record(['L0'])            
        Record(['T0'])
    return(State)

def StateThree(hold1,laser):
    """Third stage of a trial in the touchscreen task.
    Checks to make sure the animal nosepokes for a long enough amount of time (in
    this case 'long enough' is a user generated value in the settings file.
    Args:
       hold1: the duration for which the animal must nosepoke to turn the screen on
    Returns:
       State: the current stage of the trial
    """
    State = 4
    holdtime = hold1
    poketime = 0
    t0 = time.time()
    while poketime < holdtime:
        poketime = time.time() - t0
        EventChecker()
        #print(poketime)
        if (GPIO.input(nose_poke)) == True:
            GPIO.output(tone, GPIO.LOW)
            Record(['T0'])
            if laser == 1:
                GPIO.output(house_lt, GPIO.LOW)
                Record(['L0'])
            State = 2
            break
    return(State)

def StateFour(hold2,laser):
    """Fourth stage of a trial in the touchscreen task.
    Makes sure the animal nosepokes for long enough to keep the screen on, then
    changes the State to 5.
    Args:
       hold2: the duration for which an animal needs to nosepoke with the screens on
    Returns:
       State: the current stage of the trial
    """
    #State = 4
    t0 = time.time()
    holdTime = 0
    screenHold = hold2
    ScreensOn()
    Record(['S1'])
    State = 5
    while True: #holdTime < screenHold:
        holdTime = time.time()-t0
        if GPIO.input(nose_poke) == True:
            State = 1
            ScreensOff()
            Record(['N0', 'T0'])
            GPIO.output(tone, GPIO.LOW)
            if laser == 1:
                GPIO.output(house_lt, GPIO.LOW)
                Record(['L0'])
            #Record(['N0'])
            #Record(['T0'])
            delay(1.5)
            break
        elif holdTime >= screenHold:
            GPIO.output(tone, GPIO.LOW)
            Record(['T0'])
            break
    return(State)

def StateFive(currentTrial,trial_totals):

    reward = currentTrial
    #print(reward)
    inputWait = 20 #this is how long the screens stay on waiting for input, set to 10 for opto studies
    t0 = time.time()
    timeElapsed = 0
    while timeElapsed < inputWait:
        timeElapsed = time.time() - t0
        EventChecker()
        if GPIO.input(left_in) == False:
            #timeElapsed = inputWait + 1
            GPIO.output(house_lt, GPIO.LOW)
            ScreensOff()
            if reward[2] == 0:
                Record(['LA']) #Chose left Type 1/A
                if reward[3] == 0:
                    trial_totals[0][reward[4]*2] += 1
                else:
                    trial_totals[1][reward[4]*2] += 1
                Feeder(1,reward[0])
            elif reward[2] == 1:
                Record(['LB']) ##Chose left Type 2/B
                if reward[3] == 0:
                    trial_totals[0][reward[4]*2 +1] += 1
                else:
                    trial_totals[1][reward[4]*2 +1] += 1
                Feeder(2, reward[1])           
            State = 6
            #print("done")
            break
        elif GPIO.input(right_in) == False:
            #timeElapsed = inputWait + 1
            GPIO.output(house_lt, GPIO.LOW)
            ScreensOff()
            if reward[2] == 1:
                Record(['RA']) #Chose Right Type 1/A
                if reward[3] == 0:
                    trial_totals[0][reward[4]*2] += 1
                else:
                    trial_totals[1][reward[4]*2] += 1
                Feeder(1,reward[0])
            elif reward[2] == 0:
                Record(['RB']) #Chose Right Type 2/B
                if reward[3] == 0:
                    trial_totals[0][reward[4]*2 +1] += 1
                else:
                    trial_totals[1][reward[4]*2 +1] += 1
                Feeder(2, reward[1])
           
            State = 6
            #print("done")
            break
    if timeElapsed >= inputWait:        
        print("omitted")
        if reward[3] == 1:
                GPIO.output(house_lt, GPIO.LOW)
                Record(['L0'])
        ScreensOff()
        State = 1
        delay(7)
    return(State, trial_totals)

def BlockLoop(trial_totals,sampleList, itiList,laser,hold1,hold2,trialCount):
    endsess=False
    global State
    Hold1=hold1
    Hold2=hold2
    Count = 0
    #number = Number
    sampleList1 = copy.deepcopy(sampleList)
    itiList1 = copy.deepcopy(itiList)
    randomBlock = randomList(sampleList1)
    trialITI = randomList(itiList1)
    for i in randomBlock:
        currentTrial = i
        thisITI = trialITI[Count]
        #print(str(thisITI))
        State = 1
        while State < 6:
            if State ==1:
                State = StateOne(thisITI,currentTrial)
                EventChecker()
                #User input requires an input
                #user_input = input()
                #if user_input == "f":
                 #   endsess = True
                 #   break
            if State == 2:
                #currentTrial[3] is whether the laser is on
                State = StateTwo(currentTrial[3])
                EventChecker()
            if State == 3:
                State = StateThree(Hold1,currentTrial[3])
                EventChecker()
            if State == 4:
                State = StateFour(Hold2,currentTrial[3])
                EventChecker()
            if State == 5:
                State, trial_totals = StateFive(currentTrial,trial_totals)
                data1 = trial_totals[0][::2]
                data2 = trial_totals[0][1::2]
                data1L = trial_totals[1][::2]
                data2L = trial_totals[1][1::2]
                #readout = [data1[i]+data2[i] for i in range(len(data1))]
                #type1 = currentTrial[0]
                #type2 = currentTrial[1]
                #type 1 is pellet A
                #type 2 is pellet B
                #print('Type 1: '+ str(type1) +'  Type 2: '+ str(type2))
                print(data1)
                print(data2)
                if laser:
                    print(data1L)
                    print(data2L)
                print('\n')
                Record2([data1, data2])
                Record2([data1L, data2L])
                #print(trial_totals)
               # print(readout)
                EventChecker()
        Count = Count + 1
        trialCount = trialCount+1
    return(trialCount,trial_totals)


def MainLoop():
    global fileName
    global nosepoke
    nosepoke = 0

    identifier, date, trials,laser,itiList,hold1,hold2,pell1,pell2 = DataGrab()
    fileNameTemp = str(identifier)+'-'+str(date)
    fileName = checkfilename(fileNameTemp)
    print(fileName)

    (p1,p2) = CheckCues(identifier,pell1,pell2)
    textFile = open(fileName, "w")
    textFile.write('Pellets:   ' + p1 + '-' + p2 + '\n')
    tr = 'Trials:   '
    for x in trials:
        tr += str(x[0]) + '/'+ str(x[1]) + ','
    tr = tr[:-1]    
    textFile.write(tr + '\n')
    textFile.close()
    SendCueInfo(pell1, pell2)
    delay(1)
    #This function tells the arduinos which cues to use
    sampleList = trialList(trials,laser)
    trialCount = 0
    trial_display = []
    for x in trials:
        listcount = 0
        for g in x:
            if listcount < 2:
                trial_display.append(g)
            listcount = listcount + 1
    trial_totals  = [list(), list()]

    i = 0
    while i < len(trials):
        trial_totals[0].append(0)
        trial_totals[0].append(0)
        trial_totals[1].append(0)
        trial_totals[1].append(0)
        i = i + 1
    
    while trialCount < 400:
        print(trial_display)
        trialCount,trial_totals = BlockLoop(trial_totals,sampleList, itiList, laser,hold1,hold2,trialCount)
 
    print('Done!')
    return
MainLoop()
