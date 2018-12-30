#!/usr/bin/env python3
# Courtesy of Olivier Guyotot
# Source: https://www.mail-archive.com/weewx-user@googlegroups.com/msg09026.html
#
#[weewx-user] Re: WS-3000
#olivier . guyotot Sun, 14 Jan 2018 03:57:07 -0800
#Hi again,
#
#I did some more troubleshooting, and I now have the feeling that the driver 
#isn't doing exactly what it should.
#
#First of all, a disclaimer: I am no developer and I know next to nothing 
#about the USB protocol, so please don't be too harsh on me if what I am 
#saying is complete BS.
#
#Now, I wrote a small python script to try to read data from the WS-3000 and 
#I actually managed to get this working fine. So I can safely confirm that 
#the problem doesn't come from the hardware or from the host. The setup I am 
#using is working fine, the issue must be coming from weewx or the HP3000 
#driver.
#
#According to the output from Wireshark and from what I've read in the 
#driver's code, I *believe* that there are two issues:
#1. one is that the driver is sending commands using the 'control' channel.
#2. probably not directly related to the error I am seeing, but I don't 
#understand the point of sending all the 0x41, 0x06, 0x08, 0x09, 0x05, 0x03, 
#0x04 commands. The only interesting ones are 0x03 (current data) and 0x05 
#(calibration, assuming it must be taken into account to get the 'corrected' 
#temperature).

#You can find the small script I wrote attached. The only problem I have is 
#that I have to unplug and replug the station between each run, I probably 
#don't reset everything properly.
#You can easily compare the output when sending each of the 0x41, 0x06, 
#0x08, 0x09, 0x05, 0x03, 0x04 commands, or when sending only 0x03 commands. 
#By the way, this also means that contrary to what is mentioned in the 
#driver, the correct way to distinguish between current data and calibration 
#data is to keep track of which command was sent...
#
#Please let me know if this makes sense or not. I am willing to do any 
#additional test you need in order to get this working correctly.
#
#Thanks a lot.
#
#-- 
#You received this message because you are subscribed to the Google Groups 
#"weewx-user" group.
#To unsubscribe from this group and stop receiving emails from it, send an email 
#to weewx-user+unsubscr...@googlegroups.com.
#For more options, visit https://groups.google.com/d/optout.
#
#

# Changelog
# v1 Original script. Written for Python2 by original author Olivier Guyotot
# v2 Tiny tweaks to make the script run with Python3. Mainly around arguments to print. 28.12.2018 Thomas Frivold
# v3 Added numpy arrays and Pandas Dataframes 28.12.2018 Thomas Frivold
# v4 Commented out all the pandas stuff. Added Time and Random number, to make it easy to see that the script is running in a loop.
# v5 Added code to calculate the proper temperature values, by dividing by 10. 30.12.2018 20:25
# The output of the temperature sensors are confusing.
# These are the thresholds 
# - At temperatures between 0.1 Degrees Celcius as 25.6 Degrees celcius
# The formula becomes Raw Value / 10
# - at 0 Degrees Celcius, which becomes the raw value of 256
# The formula becomes 256-Raw Value
# - at 25.6 Degrees Celcius, which becomes the raw value of 256
# The formula becomes 256-Raw Value / 10

import sys, traceback
import numpy as np
import pandas as pd
import random
import datetime
import usb.core, usb.util
from time import sleep

now = datetime.datetime.now()

print ("Begin transmission")
print("Time",now.hour,":",now.minute, ":", now.second,"   ","Date:",now.day,".",now.month,".",now.year)
print("Random Number:",random.randint(1,100000))
print ("------------------")
def trimbuffer(buf):
    i = 0
    while i < len(buf):
        if (i > 0 and buf[i] == 0x7d and buf[i-1] == 0x40):
            break
        i += 1
    return buf[0:i+1]

def ws3000_write(command):
    print("ws3000_write: entry")
    VENDOR = 0x0483
    PRODUCT = 0x5750
    CONFIGURATION = 0

    try:

        print ("Detecting device...")
        device = usb.core.find(idVendor=VENDOR, idProduct=PRODUCT)
        if device is None:
            print("Is the WS-3000 connected?")
            sys.exit(1)
        print("Device found")

        # Device busy if managed by the kernel
        if device.is_kernel_driver_active(CONFIGURATION):
            print("Detaching kernel driver")
            device.detach_kernel_driver(CONFIGURATION)

        # WS-3000 has only one configuration
        device.set_configuration()

        # control
        print ("Sending control packet")
        #device.ctrl_transfer(0x21, 10, 0, 0, None)
        device.ctrl_transfer(0, 9, 1, 0, None)

#        commands = [0x41, 0x06, 0x08, 0x09, 0x05, 0x03, 0x04]
        commands = [0x03]
        for command in commands:
            request = [0x7b, command, 0x40, 0x7d]
            padding = [0x0] * 60
            request.extend(padding)
            print ("Sending command: "), (request)
            device.write(0x01, request, 100)
            data = device.read(0x82, 64, 100)
#            data = np.array(device.read(0x82, 62, 100))
            data = trimbuffer(data)
            print (data)
            sleep (1)
            print ("Array size is",(len(data)))

            print ("Channel 1 - Temperature Raw: ", (data[2]))
            print ("Channel 1 - Temperature Properly:", (data[2])/10)
            print ("Channel 1 - Temperature Properly Again:", (256-data[2])/10)         
            print ("Channel 1 - Humidity Percentage:", (data[3]))

            print ("Channel 2 - Temperature Raw: ", (data[5]))
            print ("Channel 2 - Temperature Properly:", (data[5])/10)
            print ("Channel 2 - Temperature Properly Again:", (256-data[5])/10)
            print ("Channel 2 - Humidity Percentage:", (data[6]))

            
            print ("Channel 3 - Temperature: Raw:", (data[8]))
            print ("Channel 3 - Temperature Properly: ", (data[8])/10)
# note - this sensor needs a different formula than the other sensors to properly calculate.
# we have to add from 256 and not subtract from 256.
            print ("Channel 3 - Temperature Properly Again: ", (256+data[8])/10)
            print ("Channel 3 - Humidity Percentage:", (data[9]))
            
            print ("Channel 4 - Temperature Raw: ", (data[11]))
            print ("Channel 4 - Temperature Properly: ", (data[11])/10)
            print ("Channel 4 - Tmemperature Properly Again: ", (256-data[11])/10)
            print ("Channel 4 - Humidity Percentage:", (data[12]))

            print ("Channel 5 - Temperature Raw: ", (data[14]))
            print ("Channel 5 - Temperature Properly: ", (data[14])/10)
            print ("Channel 5 - Temperature Properly Again: ", (256-data[14])/10)
            print ("Channel 5 - Humidity Percentage:", (data[15]))
            print ("-------")            
            print ("Negative temperatures, below 0 degrees Celcius - Values are multiplied by 10. Negative temperatures are 256-minus-temperature")
            print ("Temperatures above 25.6 degrees Celcius, below 0 - Values are multiplied by 10. Temperatures above 25.6 degrees are calculated as (example 29.9 degrees Celcius): 299-minus-256 degrees")
            print ("-------")            

            # Creating a numpy array - that's better
            np.array(data)
# Blasting this into a Pandas Dataframe
#            dates = pd.date_range('20130101', periods=6)
#            df = pd.DataFrame(data[0])
#            idx = ['Winter', 'Spring', 'Summer', 'Fall']
#            cols = np.arange(2015,2055,5)
#            df = pd.DataFrame(data.T, index=idx, columns=cols)
#            df(head)
#            data = pd.Dataframe(data)
#            data = []
#            df = pd.DataFrame(eval(data))
##            df = df.transpose()
#            df.columns = ["Team", "Player", "Salary", "Role"]
#            df(head)
####### Unnecessary debugging
#             print type(data)
#            print len(data)
#            for value in data:
#                print hex(value)
#            sleep(1)
#
#            print ("What kind of data type are each of the array elements?")
#
#            for value in data:
#                print ("Type is", type(value))
#######
    except:
        print ("An error occurred:"), sys.exc_info()
        traceback.print_exc(file=sys.stdout)

    usb.util.dispose_resources(device)

print("Starting tests...")
ws3000_write("")
print ("------------------")
print("Time",now.hour,":",now.minute, ":", now.second,"   ","Date:",now.day,".",now.month,".",now.year)
print("Random Number:",random.randint(1,100000))
print("End of transmission")
