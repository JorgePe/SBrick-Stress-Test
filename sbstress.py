#!/usr/bin/env python 

from __future__ import print_function
from Tkinter import *
from time import sleep
from subprocess import call, check_output, CalledProcessError
import sys, traceback, os, getopt

# exit codes
EXIT_OK   = 0
EXIT_ARGS = 2
#EXIT_FILE = 3
EXIT_HW   = 4
EXIT_FW   = 5
EXIT_FWID = 6                                 # Unknown Firmware ID - not safe to proceed

# This is the Font used to print Temperature and Voltage
FONT_TYPE = "Helvetica"
FONT_SIZE = 16

class SBrick:

  BT_ADAPTER = ''
  SBRICK = ''
  SBRICK_HW_VS = ''
  SBRICK_FW_VS = ''

  # The SBrick firmware 4.2+ has a watchdog, after 500 ms it drops the BLE connection
  # so we need to keep talking to it
  # the value for PERIOD (in ms) is empirical - you may need to adjust
  PERIOD = 330

  ScaleMAX = 255
  ScaleMIN = 0

  def __init__(self, adapter, sbrick, period):
    self.BT_ADAPTER = adapter
    self.SBRICK = sbrick
    self.PERIOD = period

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
    elif(self.SBRICK_FW_VS == "4.2"):
      print("Will use SBrick firmware 4.2 handles")
      self.ScaleMAX = 255
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

  def Drive (self, Command):
    if (self.SBRICK_FW_VS == "4.0"):
      call("gatttool --device=" + self.SBRICK + " --adapter=" + self.BT_ADAPTER + " --char-write --handle=0x0025 --value=01" + Command, shell=True)
    elif (self.SBRICK_FW_VS == "4.2"):
      call("gatttool --device=" + self.SBRICK + " --adapter=" + self.BT_ADAPTER + " --char-write --handle=0x001A --value=01" + Command, shell=True)
    return 0


  def ReadTemp(self):
    if(self.SBRICK_FW_VS=="4.2"):
      call("gatttool -b "+self.SBRICK+" -i "+self.BT_ADAPTER+" --char-write --handle=0x001A --value=0F0E",shell=True)
      sleep(0.01)
      result=check_output("gatttool -b "+self.SBRICK+" -i "+self.BT_ADAPTER+" --char-read --handle=0x001A",shell=True).split(" ")
      t=( int(result[3]+result[2], 16) ) * 0.008413396 - 160

      return("{0:.1f}".format(t)+" C")
    else:
      # firmware 4.0 can't read temp/volt
      return("00.0 C")

  def ReadVolt(self):
    if(self.SBRICK_FW_VS=="4.2"):
      call("gatttool -b "+self.SBRICK+" -i "+self.BT_ADAPTER+" --char-write --handle=0x001A --value=0F00",shell=True)
      sleep(0.01)
      result=check_output("gatttool -b "+self.SBRICK+" -i "+self.BT_ADAPTER+" --char-read --handle=0x001A",shell=True).split(" ")
      v=( int(result[3]+result[2], 16) ) * 0.000378603  

      return("{0:.1f}".format(v)+" V")
    else:
      # firmware 4.0 can't read temp/volt
      return("0.0 V")


class Tool:

  ScaleMAX = 0
  ScaleMIN = 0
  LENGTH = 0
  SBRICK = ''

  def __init__(self, sbrick):
    self.SBRICK = sbrick
    self.ScaleMAX = sbrick.GetScaleMAX()
    self.ScaleMIN = sbrick.GetScaleMIN()
    self.LENGTH = abs(self.ScaleMAX - self.ScaleMIN)

    self.root=Tk()
    self.root.title("SBrick Stress Test")

    self.temp = StringVar()
    self.volt = StringVar()
    self.pwm1 = IntVar()
    self.pwm2 = IntVar()
    self.pwm3 = IntVar()
    self.pwm4 = IntVar()

    self.temp.set("00.0")
    self.volt.set("0.0")
    self.pwm1.set(0)
    self.pwm2.set(0)
    self.pwm3.set(0)
    self.pwm4.set(0)
 
    self.check1=IntVar()
    self.check1.set(0)
    self.check2=IntVar()
    self.check2.set(0)
    self.check3=IntVar()
    self.check3.set(0)
    self.check4=IntVar()
    self.check4.set(0)

    LabelTemperature=Label(self.root, textvariable=self.temp, font=(FONT_TYPE, FONT_SIZE))
    LabelTemperature.grid(row=0, column=1)

    LabelVoltage=Label(self.root, textvariable=self.volt, font=(FONT_TYPE, FONT_SIZE))
    LabelVoltage.grid(row=0, column=2)

    CheckPort1=Checkbutton(self.root, variable = self.check1,takefocus=1, text="Port #1", padx=50, pady=10)
    CheckPort1.grid(row=1,column=0)

    Port1 = Scale(self.root, from_=self.ScaleMAX, to=self.ScaleMIN, digits=3, resolution=1, orient=VERTICAL, length=self.LENGTH, takefocus=1, command=self.Sync, variable=self.pwm1)
    Port1.grid(row=2,column=0)

    CheckPort2=Checkbutton(self.root, variable = self.check2,takefocus=1, text="Port #2", padx=50, pady=10)
    CheckPort2.grid(row=1,column=1)

    Port2 = Scale(self.root, from_=self.ScaleMAX, to=self.ScaleMIN, digits=3, resolution=1, orient=VERTICAL, length=self.LENGTH,  takefocus=1, command=self.Sync, variable=self.pwm2)
    Port2.grid(row=2,column=1)

    CheckPort3=Checkbutton(self.root, variable = self.check3,takefocus=1, text="Port #3", padx=50, pady=10)
    CheckPort3.grid(row=1,column=2)

    Port3 = Scale(self.root, from_=self.ScaleMAX, to=self.ScaleMIN, digits=3, resolution=1, orient=VERTICAL, length=self.LENGTH,  takefocus=1, command=self.Sync, variable=self.pwm3)
    Port3.grid(row=2,column=2)

    CheckPort4=Checkbutton(self.root, variable = self.check4,takefocus=1, text="Port #4", padx=50, pady=10)
    CheckPort4.grid(row=1,column=3)

    Port4 = Scale(self.root, from_=self.ScaleMAX, to=self.ScaleMIN, digits=3, resolution=1, orient=VERTICAL, length=self.LENGTH, takefocus=1, command=self.Sync, variable=self.pwm4)
    Port4.grid(row=2,column=3)

    LabelQuit=Label(self.root, height=1, pady=10)
    LabelQuit.grid(row=3)
    Button_QUIT = Button(text = "QUIT", command = self.quit)
    Button_QUIT.grid(row=4, column=1, columnspan=2)

  def twoDigitHex(self,number):
      return '%02x' % number

  def Sync(self, *ignore):
    if(self.check1.get()==0):
      self.SBRICK.Drive("0000"+self.twoDigitHex(self.pwm1.get()))
    else:
      self.SBRICK.Drive("0001"+self.twoDigitHex(self.pwm1.get()))

    if(self.check2.get()==0):
      self.SBRICK.Drive("0100"+self.twoDigitHex(self.pwm2.get()))
    else:
      self.SBRICK.Drive("0101"+self.twoDigitHex(self.pwm2.get()))

    if(self.check3.get()==0):
      self.SBRICK.Drive("0200"+self.twoDigitHex(self.pwm3.get()))
    else:
      self.SBRICK.Drive("0201"+self.twoDigitHex(self.pwm3.get()))

    if(self.check4.get()==0):
      self.SBRICK.Drive("0300"+self.twoDigitHex(self.pwm4.get()))
    else:
      self.SBRICK.Drive("0301"+self.twoDigitHex(self.pwm4.get()))

    return
               
  def quit(self):
    self.root.destroy()
    return;


  def refresh(self):

    self.temp.set(self.SBRICK.ReadTemp())
    self.volt.set(self.SBRICK.ReadVolt()) 
    self.root.after(self.SBRICK.GetPeriod(),self.refresh)  # reschedule event
    self.Sync()

def print_help():
  print('')
  print('sbstress - SBrick Stress Test Tool')
  print('Usage:')
  print('   sbstress.py -a <adapter> -d <device> -p <period>')
  print('')
  print('   <adapter>         HCI adapter, e.g. hci0')
  print('   <device>          SBrick Bluetooh Addres, e.g. AA:BB:CC:DD:EE:FF')
  print('   <period>          time in milliseconds, e.g. 330')
  print('')

def print_version():
  print('')
  print('SBrick Stress Test Tool 0.4 - Jorge Pereira - February 2015')


def main(argv):

  BT_ADAPTER = ''
  SBRICK_ADDR = ''
  PERIOD = ''
  
  try:
    opts, args = getopt.getopt(argv,"hva:d:p:")

  except getopt.GetoptError:
    print_help()
    sys.exit(EXIT_ARGS)

  try:
    for opt, arg in opts:
      if opt == '-h':
        print_help()
        sys.exit(EXIT_OK)
      if opt == '-v':
        print_version()
        sys.exit(EXIT_OK)
      elif opt == '-a':
        BT_ADAPTER = arg
      elif opt == '-d':
        SBRICK_ADDR = arg
      elif opt == '-p':
        PERIOD = arg

    if( BT_ADAPTER=='')or(SBRICK_ADDR=='')or(PERIOD==''):
      print_help()
      sys.exit(EXIT_ARGS)
    else:
      print('')
      print('sbstress - SBrick Stress Test Tool')
      SBRICK = SBrick(BT_ADAPTER, SBRICK_ADDR, PERIOD)

    tool = Tool(SBRICK)
    tool.root.after(PERIOD,tool.refresh)
    tool.root.mainloop()

  except Exception:
    # Oooops! Hate this part! Lot of work to do...
    traceback.print_exc(file=sys.stdout)


  sys.exit(EXIT_OK)


if __name__ == '__main__':
  main(sys.argv[1:])

