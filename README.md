# WHAT IS THIS #
The purpose of this repository is to provide a program to extract data from the "Mi Sol HP-3000" weather station purchased from Chinese online retailer Aliexpress.
It also works for HP-3001 models, others might also be supported.
The work is based on reverse engineering done by Matthew Wall, https://github.com/matthewwall/weewx-hp3000
and trouble shooting and creative problem solver Olivier Guyotot, https://www.mail-archive.com/weewx-user@googlegroups.com/msg09026.htm$ .


# BUT THERE IS AN OFFICIAL SOFTWARE PACKAGE, WHY NOT USE IT? #
Because they just don't work. To be frank Weewx sucks.


# KEY FINDING #
 The output of the temperature sensors are confusing.
 These are the thresholds 
 - At temperatures between 0.1 Degrees Celcius as 25.6 Degrees celcius
 The formula becomes Raw Value / 10
 - at 0 Degrees Celcius, which becomes the raw value of 256
 The formula becomes 256-Raw Value
 - at 25.6 Degrees Celcius, which becomes the raw value of 256
 The formula becomes 256-Raw Value / 10


# HOW TO GET YOUR WEATHER STATION WORKING #

TL;DR: 
The MI SOL HP3000, HP3001 weather stations are very popular. They come in an affordable package, with 5 nice temperature and humidity sensors, 
and a main weather-station with a color screen, historical graph and so on. It supports up to 8 sensors, and can also store historical measurement data to a micro SD card. 
No wonder you might want to buy this weather station. It's even supported in Linux. In fact it is supported by a really cool project called WeeWX. Great! I'm buying!

Here are my findings:
- I managed to get it to work. I am here, to share all my findings. Code. Config and Test Code.

- This is not working well. Because of sloppy code in the drivers and in Weewx codebase.

- I will not recommend buying the Mi Sol HP3000 weather station for anyone intending to use it with Weewx and Linux. Apparently the Windows software works perfectly.

- I have wasted at least 10-15 hours over many frustrating sessions trying to get the weather station to work on Linux, over USB with WeeWX.

- WeeWX is an unorganized, poorly documented mess of a software package - Buyer beware, you are stepping into a word of hurt.
This is at least true for ewhen you are using weather stations that are not supported by the  "mainlined drivers".

- This is so convoluted that I prefer to write this text up. Gather my findings. Gather the code I've discovered. Share the config file and a zipped version of the entire project.
Hopefully it will same some people time.

In my case, I have the MI SOL weather station model: HP3001.


In order to use it:
1. Verify that the USB connection is working.
Run the script found in /Tests/VerificationOfConnection.py

It should terminate with: 
It should not terminate with 
"AttributeError: 'NoneType' object has no attribute '_ctx'"
or
"USBError: [Errno 19] No such device (it may have been disconnected)"

# WHAT'S WRONG WITH THE OFFICIAL INSTRUCTIONS AND SOFTWARE PACKAGE FROM WEEWX.COM? #

## Reason 1. The Weewx.com website looks really nice and invites to a user friendly experience. ##
This is not the case. As the package you install does not come with the "USB BRANCH".
The USB Branch? Yeah that is an undocumented branch of the code which you must yourself find on your quest.

That means that when the package from the main repository, weewx.com, is installed, it does not work with plugins/drivers/extensions that rely on USB code.


## Reason 2. The third party driver doesn't work. Weewx-hp3000 is borked. ##
The dude who wrote the "third party" driver to the weather station MI SOL HP3000 surely invested his time to write a driver.
There appears to be plenty of reverse engineering taken place, as it the code revelals bit for bit mapping of the sensor data frames.
However this really matter very little, when the driver it self is not working.


Here are the installation instructions and readme for the plugin weeewx-hp3000.

---
weewx-hp3000

This is a driver for weewx that collects data from HP-3000 temperature/humidity
sensors.  The HP-3000 is a small console that receives data wirelessly from up
to 8 temperature/humidity sensors.  It is branded as WS-3000 by Ambient.

Installation

0) install weewx (see the weewx user guide)

1) download the driver

wget -O weewx-hp3000.zip https://github.com/matthewwall/weewx-hp3000/archive/master.zip

2) install the driver

wee_extension --install weewx-hp3000.zip

3) configure the driver

wee_config --reconfigure --driver=user.hp3000

4) start weewx

sudo /etc/init.d/weewx start
---

This readme fails to mention, and still fails to mention, that in order to use the driver at all, the USB tree of the Weewx software must be used.
Therefore if a user blindly follows these instructions, then he will hit a "Weeusb Module Not Found" error. 


## Reason 3. I am frustrated. Let's file an issue. ##

Issue 1: https://github.com/matthewwall/weewx-hp3000/issues/1
Author admits that he borked the readme file.
Still hasn't updated the readme tho.


From: https://www.mail-archive.com/weewx-user@googlegroups.com/msg08945.html
"
> What's the problem? Is the station not supported, am I using the wrong 
> driver, something else?
>

you need to use the hp3000 driver, which is currently an extension to weewx:

https://github.com/matthewwall/weewx-hp3000

the fousb driver is for ws10x0/20x0/30x0 weather stations.

another complicating factor is that the hp3000 driver is currently written 
to work with the 'usb' branch of weewx.  so you must install weewx from the 
source code, specifically from the 'usb' branch:

git clone https://github.com/weewx/weewx
cd weewx
git checkout usb
./setup.py install
"


## Reason 4. The plugin still doesn't work ##
After following the advice found in the issue mentioned in #3, the driver gets installed and the Weewx engine almost starts up.
Then it ends in an error, again.
 USBError: Pipe Error

"The error message 
is slightly different but produces the exact same stack trace: USBError: 
[Errno 32] Pipe error."

Now there are no more reported issues on the github driver's issue repository, that I can use to triangulate the error and get this thing working.
Luckily there is a fat thread on the mailing lists. It bears many fruits.

## Reason 5. Many people are struggling, and getting started with Weewx is extremely difficult. ##
The documentation is very poor, since it gives inadequate advice and at times leads the user down wrong paths to try and solve problems. 


Having purchased the MI SOL weather station from a vendor in China, I was eager to install it on my Linux system and measuring, tracking and automating stuff around the house based on recorded temperatures.

Little did I know poorly it all worked.

Sure! The Weemx website looks all well calculated.
Under devices it shows a weather station identical to mine, albeit with a different name.

Ahh, but no, you cannot use that one. That is for the official one. The Chinese versions of HP-3000 need to use a separate driver.



