import pygame
from pygame import locals

import serial
import math
import binascii
import os.path

def initJoystick():
	pygame.init()
	pygame.joystick.init() # main joystick device system

	try:
		j = pygame.joystick.Joystick(0) # create a joystick instance
		j.init() # init instance
		print 'Enabled joystick: ' + j.get_name()
		return j
	except pygame.error:
		print 'no joystick found.'
		exit(1)

#nb_buttons = j.get_numbuttons()
#

def initSerial(devstr="/dev/ttyACM0"):
    """ Initialize the serial port and return the Serial object """
    theSer = None
    try:
        theSer = serial.Serial(devstr)
        #ser.baudrate=9600
        theSer.timeout = 1
        theSer.close()
        theSer.open()
    except serial.serialutil.SerialException:
        print "Error occurred opening %s" % (devstr)
        exit(1)
    return theSer

def reset():
    ser.write("\x00\x00\x00\x00\x00")

def testDevice():
    reset()
    setMode("test")
    result = ser.read(4)
    if ((result.startswith("V")) and (len(result) == 4)):
        print "IRToy %s, Firmware version: %s" % (result[1:2], result[3:4])
        return True
    return False

def setMode(mode):
    modedict = {
        "sample":"S",
        "irio":"X",
        "bridge":"U",
        "intruder":"E",
        "test":"T",
    }
    modesel = modedict[mode]
    if (modesel):
        ser.write(modesel)
        return True
    return False

def setSampleFrequency(byte):
    if (len(byte)==1):
        ser.write("\x05")
        ser.write(byte)
        return True
    return False

def receiveSequence(description_button=""):
    data = ""
    
    print "Press a button " + description_button

    while 1:
        d = ser.read()
        if d == '':
            pass
        else:
            data = data + d
            if len(data) >=2 and data[-2:] == '\xff\xff':
                break

    print 'received %d bytes %s' % (len(data),binascii.hexlify(data))
    return data

def transmitSequence(data):
    setSampleFrequency("\x07")
    if (data.endswith("\xff\xff")):
        ser.write("\x24")
        ser.write("\x25")
        ser.write("\x26")
        ser.write("\x03")

        print 'full data to send (%d) : %s' %(len(data),binascii.hexlify(data))
        
        for i in range(0, len(data), 62):
            chunk = data[i:i + 62]
            print 'send (%d): %s' %(len(chunk),binascii.hexlify(chunk))
            nb = ser.write(chunk)
            ser.flush()

            ret = ser.read(1)

        confirm = False
        while not confirm:
            ret = ser.read(1)
            if ret == 'C' or ret == 'F':
                confirm = True

        return True
    return False

def writeFile(fileName, data):
    try:
        file = open(fileName, "wb")
        file.write(data)
        return True
    except IOError:
        print "Error writing to file %s" % fileName
    finally:
        file.close()

def readFile(fileName):
    try:
        file = open(fileName, "rb")
        data = file.read()
        return data
    except IOError:
        print "Error reading from file %s" % fileName
    finally:
        file.close()

j = initJoystick()

ser = initSerial()
reset()

testDevice()

setMode("sample")
response = ser.read(3)
if (response == "S01"):
    print "IRToy OK"
else:
    print "Error. No response from IRToy"
    exit(2)


if not os.path.isfile("dataSTOP"):
    dataUP = receiveSequence(description_button="UP")
    writeFile("dataUP",dataUP)
    dataUP_AGAIN = receiveSequence(description_button="UP_AGAIN")
    writeFile("dataUP_AGAIN",dataUP_AGAIN)

    dataDOWN = receiveSequence(description_button="DOWN")
    writeFile("dataDOWN",dataDOWN)
    dataDOWN_AGAIN = receiveSequence(description_button="DOWN_AGAIN")
    writeFile("dataDOWN_AGAIN",dataDOWN_AGAIN)

    dataLEFT = receiveSequence(description_button="LEFT")
    writeFile("dataLEFT",dataLEFT)
    dataLEFT_AGAIN = receiveSequence(description_button="LEFT_AGAIN")
    writeFile("dataLEFT_AGAIN",dataLEFT_AGAIN)

    dataRIGHT = receiveSequence(description_button="RIGHT")
    writeFile("dataRIGHT",dataRIGHT)
    dataRIGHT_AGAIN = receiveSequence(description_button="RIGHT_AGAIN")
    writeFile("dataRIGHT_AGAIN",dataRIGHT_AGAIN)

    dataSTOP = receiveSequence(description_button="STOP")
    writeFile("dataSTOP",dataSTOP)

else:
    dataUP = readFile("dataUP")
    dataUP_AGAIN = readFile("dataUP_AGAIN")
    dataDOWN = readFile("dataDOWN")
    dataDOWN_AGAIN = readFile("dataDOWN_AGAIN")
    dataLEFT = readFile("dataLEFT")
    dataLEFT_AGAIN = readFile("dataLEFT_AGAIN")
    dataRIGHT = readFile("dataRIGHT")
    dataRIGHT_AGAIN = readFile("dataRIGHT_AGAIN")
    dataSTOP = readFile("dataSTOP")

print "You use PS3 controller now"

direction = ''

while 1:
    for e in pygame.event.get(): # iterate over event stack
        if e.type == pygame.locals.JOYBUTTONDOWN: # 10
#           for i in range(j.get_numbuttons()):
#               print "button %d: %d" % (i, j.get_button(i))'''
            if j.get_button(4):
                if direction == 'UP' or direction == 'UP_AGAIN':
                    transmitSequence(dataUP_AGAIN)
                    direction = 'UP_AGAIN'               
                else:
                    transmitSequence(dataUP)
                    direction = 'UP'               
            if j.get_button(6):
                if direction == 'DOWN' or direction == 'DOWN_AGAIN':
                    transmitSequence(dataDOWN_AGAIN)
                    direction = 'DOWN_AGAIN'               
                else:
                    transmitSequence(dataDOWN)
                    direction = 'DOWN'               
            if j.get_button(7):
                if direction == 'LEFT' or direction == 'LEFT_AGAIN':
                    transmitSequence(dataLEFT_AGAIN)
                    direction = 'LEFT_AGAIN'
                else:
                    transmitSequence(dataLEFT)
                    direction = 'LEFT'
            if j.get_button(5):
                if direction == 'RIGHT' or direction == 'RIGHT_AGAIN':
                    transmitSequence(dataRIGHT_AGAIN)
                    direction = 'RIGHT_AGAIN'
                else:
                    transmitSequence(dataRIGHT)
                    direction = 'RIGHT'
            if j.get_button(14):
                transmitSequence(dataSTOP)
                direction = 'STOP'

            if len(direction) > 0 :
                print 'sent IR for %s' % direction