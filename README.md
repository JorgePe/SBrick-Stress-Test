# SBrick-Stress-Test v0.41

Python script to test the limits of Vengit SBrick from linux system using BlueZ 5 gatttool

Usage:

sbstress.py -a 'adapter>' -d 'device' -p 'period'
  
- 'adapter' is the hci ID of your bluetooth 4.0+ adapter (like hci0)
-  'device'  is the SBrick Bluetooh address (like AA:BB:CC:DD:EE:FF)
-  'period'  is the time in ms that occurs between each command sent to the SBrick (like 100)
  
This  script works with the original firmware (4.0) as also with 4.2 (well, at least 4.2b2). It reads the firmware version from the SBrick and expects just these versions so if you receive a different version from Vengit you need to change the script.

Firmware 4.0 doesn't expose internal temperature and voltage values so this tools shows 0.0ºC and 0V instead.
Firmware 4.2 has a lot of new functions but also some Bluetooth Low Energy handles were changed so gatttool commands are slightly different. There are other new features including a watchdog: by default, SBrick now drops the BLE session after 500 ms so we need to keep talking to it (firmware 4.0 doesn't have this watchdog but the gatttool drops the BLE session after 2.2~2.5 seconds). I still need to address the other features.

The «period» value of 100 may be reduced a bit to achieve slightly better latencies but when testing with my laptop and PERIOD=75 noticed some commands being ignored. It can also be increased but close to 500 ms you will see the SBrick resetting all ports.

This tool also implements a checkbox for each of the 4 ports to toggle the direction of the DRIVE commands.

Please note that the temperature values are read from a sensor inside the SBrick BLE chipset - other parts of the SBrick, especially the power drivers and the electrical connection WILL BE hotter. I achieved to melt a bit of plastic around the power pins of my Stress Test SBrick with temperature readings ~70ºC (overall current ~7A)

The SBrick can work with low voltages, I've used it with 3.7V LiPo batteries without issues. But with high loads internal voltage will drop, even if you use excellent high current batteries. If internal voltage drops bellow 3.3~3.5V the SBrick turns off.

Also please note that I do not consider myself a good programmer (some weeks ago not even A programmer!). 
I want to thank [szigetigabor](https://github.com/szigetigabor) for polishing and improving the original code.

There will be future improvements to this tool so it will become more like an SBrick Controller than a Stress Tester.
We are already working in a way to chose the number of slide bars [1 to 4 instead of always 4] and which ports are controlled with which slide (so we can drive more than one LEGO 9V RC motors with just one slide)

Soon it will also be possible to associate the slide bars with keyboard keys and/or gamepad controls.

That said... please do have fun :)
