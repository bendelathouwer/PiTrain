#importing the used libary's 
import sys
import s88
import can
import time
import random
import datetime

waiting = []  # empty stack(array) of wa = []  # iting trains 

sectie4 = 4
mainSection = 8
sectie7 = 7

speedMin = 500
speedMax = 850

c = can.can('can0')

mainSectionTrain = -1

def main(): 
    if sys.version_info < (3, 4):  # checking the version number else error & quite 
        print ("must use python 3.4 or higher ")
        sys.exit()
	
    print("connecting to S88")
    s = s88.s88(29,31,32,33)  # pins for the s88 conections  
    s.onChange += onChange  # eventhook

    # safety implementation , if a train is on the main section raise an alarm and stop the programme
#    if (s.getValue(8) == 0):
#        mainSectionTrain = -1
#    else:
#        print ("Main section bezet, niet veilig ")
#        sys.exit()	

    print("connecting to CAN")
    c = can.can('can0')

#    c.system_stopp()
#    c.system_go()
#    c.lok_nothalt(c.loc_id('DCC', 4))
    c.lok_geschwindigkeit(trein3(), 350)
    c.lok_geschwindigkeit(trein4(), 350)
#    c.lok_richtung(c.loc_id('DCC', 3), c.vorwarts)
#    c.lok_funktion(c.loc_id('DCC', 3), 'F0', 1)
#    sys.exit()

    while True:
        s.refresh(1)
#        time.sleep(0.005)


# looking at the evenhoek and taking action (based of the parameters section and value )
def onChange(section, value):
    if (value > 0):  # if the value is greater than 0 the train must be entering the section 
        onEntering(section)
    if (value == 0):  # if the value is 0 the train must be leaving  the section 
        onLeaving(section)


def onEntering(section):
    global mainSectionTrain  # 

    if(section == sectie4):  
        print(datetime.datetime.now().time(), "onEntering ", section)
        if (mainSectionTrain > 0):
            if (mainSectionTrain != trein4()):
                c.lok_nothalt(trein4()) 
                if (waiting.count(trein4()) == 0):
                    waiting.append(trein4())
                    print(datetime.datetime.now().time(), "Main is busy, train 4 has to wait")
                else:
                    print(datetime.datetime.now().time(), "**** train 4 already waiting")
            else:
                print(datetime.datetime.now().time(), "**** main already claimed by train 4")
        else:
            mainSectionTrain = trein4()
            speed = getRandomSpeed()
            c.lok_geschwindigkeit(trein4(), speed)
            print(datetime.datetime.now().time(), "Claim main section by train 4 at speed", speed / 10 , "%")

    elif(section == sectie7): 
        print(datetime.datetime.now().time(), "onEntering ", section)
        if (mainSectionTrain > 0):
            if (mainSectionTrain != trein3()):
                c.lok_nothalt(trein3()) 
                if (waiting.count(trein3()) == 0):
                    waiting.append(trein3())
                    print(datetime.datetime.now().time(), "Main is busy, train 3 has to wait")
                else:
                    print(datetime.datetime.now().time(), "**** train 3 already waiting")
            else:
                print(datetime.datetime.now().time(), "**** main already claimed by train 3")
        else:
            mainSectionTrain = trein3() 
            speed = getRandomSpeed()
            c.lok_geschwindigkeit(trein3(), speed)
            print(datetime.datetime.now().time(), "Claim main section by train 3 at speed ", speed / 10 , "%")

def onLeaving(section):
    global mainSectionTrain  # 

    if (section == mainSection):
        print(datetime.datetime.now().time(), "onLeaving ", section)
        if (len(waiting) > 0):
            train = waiting.pop(0) 
            speed = getRandomSpeed()
            print(datetime.datetime.now().time(), "starting train ", train - 49152, " from stack at speed ", speed / 10 , "%")
            c.lok_geschwindigkeit(train, speed)
            mainSectionTrain = train
        else: 
            mainSectionTrain = -1 
            print(datetime.datetime.now().time(), "No trains waiting, freeing main section")

def getRandomSpeed():
    return random.randint(speedMin, speedMax)
		
def trein3():
    return c.loc_id('DCC', 3)
		
def trein4():
    return c.loc_id('DCC', 4)
		
def terminate():
    sys.exit()
		
# entry point
if __name__ == '__main__':
    main()
