import RPi.GPIO as GPIO
import time
import eventHook
import datetime

class s88:
    contacts = [None] * 16 * 8  # max 64 contacts and None means that there is no specific data type to  that variable 
    contactsTime = [None] * 16 * 8

    # pin constants
    #DATA = 29
    #CLOCK = 31
    #LOAD = 32
    #RESET = 33
	
    TIME = 50 / 1000000.0  # 50 microseconds

    DenderCompensation = 0.75

   # constructor
    def __init__(self, data, clock, load, reset):
		#self means nothing in python but is more a a naming convention , and we give 
        self.DATA = data
        self.CLOCK = clock 
        self.LOAD = load
        self.RESET = reset

        GPIO.setmode(GPIO.BOARD)# setting the gpio to use the real pin numbering instead of the bcm numbering  

        GPIO.setup(self.DATA, GPIO.IN)
        GPIO.setup(self.CLOCK, GPIO.OUT)
        GPIO.setup(self.LOAD, GPIO.OUT)
        GPIO.setup(self.RESET, GPIO.OUT)
		
        for i in range(len(self.contacts)):
            self.contacts[i] = 0
            self.contactsTime[i] = datetime.datetime.now()

        self.refresh(1)

        self.onChange = eventHook.EventHook()

        print("connected to S88")

    # destructor
    def __del__(self):
        GPIO.cleanup()  # release i/o pins

    def fire(self, index, value):
        if (hasattr(self, 'onChange')): 
            self.onChange.fire(index, value)

    # private function
    def bitWrite(self, index, newValue):
        oldValue = self.contacts[index]
        if(oldValue != newValue):
            if (datetime.datetime.now() > self.contactsTime[index]):
                self.fire(index + 1, newValue)
            else:
                print(datetime.datetime.now().time(), "te rap " ,index + 1 , " op value ", newValue)
            self.contacts[index] = newValue
            self.contactsTime[index] = datetime.datetime.now() + datetime.timedelta(seconds = self.DenderCompensation)

    # private function
    def bitRead(self, v, bit):
        return ((v >> bit) & 1)

    # fetch bits from s88 shift register
    def refresh(self, aantal):
        index = 0

        GPIO.output(self.LOAD, GPIO.HIGH)
        time.sleep(self.TIME)
        GPIO.output(self.CLOCK, GPIO.HIGH)
        time.sleep(self.TIME)
        GPIO.output(self.CLOCK, GPIO.LOW)
        time.sleep(self.TIME)
        GPIO.output(self.RESET, GPIO.HIGH)
        time.sleep(self.TIME)
        GPIO.output(self.RESET, GPIO.LOW)
        time.sleep(self.TIME)
        GPIO.output(self.LOAD, GPIO.LOW)

        time.sleep(self.TIME / 2)  

        self.bitWrite(index, GPIO.input(self.DATA))
        index = index + 1

        time.sleep(self.TIME / 2)

        for i in range(1, 16 * aantal):
            GPIO.output(self.CLOCK, GPIO.HIGH)
            time.sleep(self.TIME)
            GPIO.output(self.CLOCK, GPIO.LOW)

            time.sleep(self.TIME / 2)
            self.bitWrite(index, GPIO.input(self.DATA))
            index = index + 1

            time.sleep(self.TIME / 2)


    # API to get
    def getValue(self, index):
        return self.contacts[index - 1]
