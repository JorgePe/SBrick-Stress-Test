#!/usr/bin/env python
# -*- coding: utf-8 -*-
from subprocess import call, check_output, CalledProcessError
import sys, traceback, os
from time import sleep

EXIT_HW   = 4
EXIT_FW   = 5
EXIT_FWID = 6                                 # Unknown Firmware ID - not safe to proceed

class SBrick:

  BT_ADAPTER = ''
  SBRICK = ''
  SBRICK_HW_VS = ''
  SBRICK_FW_VS = ''

  # The SBrick firmware 4.2+ has a watchdog, after 500 ms it drops the BLE connection
  # so we need to keep talking to it
  # the value for PERIOD (in ms) is empirical - you may need to adjust
  PERIOD = 100

  ScaleMAX = 255
  ScaleMIN = 0

  def __init__(self, adapter, sbrick, period):
    self.BT_ADAPTER = adapter
    self.SBRICK = sbrick
    self.PERIOD = period
    self.handle = ''

    print(' Adapter:    ', self.BT_ADAPTER)
    print(' Device:     ', self.SBRICK)
    print(' Period:     ', self.PERIOD)

    # find SBrick hardware and firmware version
    # should return something like 'Characteristic value/descriptor: 34 2e 30'
    # 34 = '4'  2E =' .'  30 = '0'
    # can have more chars for minor versions like 4.2b2 but will use just the first 3

    try:
      result=self.GetHw()
      parsed_result=result.split(" ")
      self.SBRICK_HW_VS=(parsed_result[2]+parsed_result[3]+parsed_result[4]).decode("hex")
    except CalledProcessError:
      print("Could not read SBrick hardware version")
      exit(EXIT_HW)

    try:
      result=self.GetFw()
      parsed_result=result.split(" ")
      self.SBRICK_FW_VS=(parsed_result[2]+parsed_result[3]+parsed_result[4]).decode("hex")
    except CalledProcessError:
      print("Could not read SBrick firmware version")
      exit(EXIT_FW)

    print(' SBrick Hw:   ' + self.SBRICK_HW_VS)
    print(' SBrick Fw:   ' + self.SBRICK_FW_VS)

    if(self.SBRICK_FW_VS == "4.0"):
      print("Will use SBrick firmware 4.0 handles")
      print("Will limit values to 0..FE as FF doesn't work")
      self.ScaleMAX = 254
      self.handle = "25"
    elif(self.SBRICK_FW_VS == "4.2"):
      print("Will use SBrick firmware 4.2 handles")
      self.ScaleMAX = 255
      self.handle = "1A"
    else:
      print("Don't know how to handle this firmware version")
      sys.exit(EXIT_FWID)


  def GetFw (self):
     return check_output("gatttool --device=" + self.SBRICK + " --adapter=" + self.BT_ADAPTER + " --char-read --handle=0x000A", shell=True)

  def GetHw (self):
     return check_output("gatttool --device=" + self.SBRICK + " --adapter=" + self.BT_ADAPTER + " --char-read --handle=0x000C", shell=True)

  def GetScaleMAX (self):
     return self.ScaleMAX

  def GetScaleMIN (self):
     return self.ScaleMIN

  def GetPeriod (self):
     return self.PERIOD

  def Drive (self, Command, operation="01"):
    if (self.SBRICK_FW_VS == "4.0" and Command[-2:] == "ff"):
      Command=Command[:-1]+Command[-1:].replace("f", "e")

    call("gatttool --device=" + self.SBRICK + " --adapter=" + self.BT_ADAPTER + " --char-write --handle=0x00"+self.handle+" --value="+ operation + Command, shell=True)
    return 0

  def Stop (self, Command="all"):
    if (Command == "all"):
      for x in range(0,4):
        self.Drive("0"+str(x), "00")
      return 0;

    self.Drive(Command, "00")
    return 0

  def ReadTemp(self):
    unit = " °C"
    if(self.SBRICK_FW_VS=="4.2"):
      call("gatttool -b "+self.SBRICK+" -i "+self.BT_ADAPTER+" --char-write --handle=0x00"+self.handle+" --value=0F0E",shell=True)
      sleep(0.01)
      result=check_output("gatttool -b "+self.SBRICK+" -i "+self.BT_ADAPTER+" --char-read --handle=0x00"+self.handle,shell=True).split(" ")
      t=( int(result[3]+result[2], 16) ) * 0.008413396 - 160

      return("{0:.1f}".format(t)+unit)
    else:
      # firmware 4.0 can't read temp/volt
      return("00.0"+unit)

  def ReadVolt(self):
    if(self.SBRICK_FW_VS=="4.2"):
      call("gatttool -b "+self.SBRICK+" -i "+self.BT_ADAPTER+" --char-write --handle=0x00"+self.handle+" --value=0F00",shell=True)
      sleep(0.01)
      result=check_output("gatttool -b "+self.SBRICK+" -i "+self.BT_ADAPTER+" --char-read --handle=0x00"+self.handle,shell=True).split(" ")
      v=( int(result[3]+result[2], 16) ) * 0.000378603  

      return("{0:.1f}".format(v)+" V")
    else:
      # firmware 4.0 can't read temp/volt
      return("0.0 V")

