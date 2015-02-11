# SBrick-Stress-Test v0.3

Python script to test the limits of Vengit SBrick from linux system using BlueZ 5 gatttool

Usage:

sbstress.py -a 'adapter>' -d 'device' -p 'period'
  
- 'adapter' is the hci ID of your bluetooth 4.0+ adapter (like hci0)
-  'device'  is the SBrick Bluetooh address (like AA:BB:CC:DD:EE:FF)
-  'period'  is the time in ms that occurs between each command sent to the SBrick (like 330)
  
This  script works with the original firmware (4.0) as also with 4.2 (well, at least 4.2b2).
Firmware 4.0 doesn't allow to read temperature and voltage values. Firmware 4.2 allows it but some Bluetooth Low Energy handles changed so gatttool commands need to be changed. There are other new features like one extremely relevant for my scripts - a watchdog: by default, SBrick now drops the BLE session after 500 ms so we need to keep talking to it.

The «period> value of 330 may be reduced to achieve better latencies. But if to short exceptions will occur as the SBrick will receive to much commands.

This version of the script also implements a checkbox for each port. When checked the direction of the commands to that port will change.

A temperature of 70ºC is to dangerous - I melted a bit of plastic around the power pins.
A voltage of less than 3.5V may force a reboot of the SBrick.

I do not consider myself a good programmer. This version has lots of global variables, poor comments, almost none exception handling. You've been warned.

Have fun.
