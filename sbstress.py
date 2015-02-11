#!/usr/bin/env python 

from __future__ import print_function
from Tkinter import *
from time import sleep
from subprocess import call, check_output
import sys, traceback, os, getopt

# exit codes
EXIT_OK   = 0
EXIT_ARGS = 2
#EXIT_FILE = 3
EXIT_HW   = 4
EXIT_FW   = 5
EXIT_FWID = 6                                 # Unknown Firmware ID - not safe to proceed


BT_ADAPTER = ''
SBRICK = ''
SBRICK_HW_VS = ''
SBRICK_FW_VS = ''

# The SBrick firmware 4.2+ has a watchdog, after 500 ms it drops the BLE connection
# so we need to keep talking to it
# the value for PERIOD (in ms) is empirical - you may need to adjust
PERIOD = 330


# This is the Font used to print Temperature and Voltage
FONT_TYPE = "Helvetica"
FONT_SIZE = 16

ScaleMAX = 255
ScaleMIN = 0

def twoDigitHex(number):
    return '%02x' % number

def SBrickGetFw ():
   return check_output("gatttool --device=" + SBRICK + " --adapter=" + BT_ADAPTER + " --char-read --handle=0x000a", shell=True)

def SBrickGetHw ():
  return check_output("gatttool --device=" + SBRICK + " --adapter=" + BT_ADAPTER + " --char-read --handle=0x000c", shell=True)

def SBrickDrive (Command):
  global BT_ADAPTER, SBRICK, SBRICK_FW_VS

  if (SBRICK_FW_VS == "4.0"):
    call("gatttool --device=" + SBRICK + " --adapter=" + BT_ADAPTER + " --char-write --handle=0x0025 --value=01" + Command, shell=True)
  elif (SBRICK_FW_VS == "4.2"):
    call("gatttool --device=" + SBRICK + " --adapter=" + BT_ADAPTER + " --char-write --handle=0x001a --value=01" + Command, shell=True)
  return 0


def SBrickReadTemp():

  global BT_ADAPTER, SBRICK, SBRICK_FW_VS

  if(SBRICK_FW_VS=="4.2"):
    call("gatttool -b "+SBRICK+" -i "+BT_ADAPTER+" --char-write --handle=0x001A --value=0F0E",shell=True)
    sleep(0.01)
    result=check_output("gatttool -b "+SBRICK+" -i "+BT_ADAPTER+" --char-read --handle=0x001A",shell=True).split(" ")
    t=( int(result[3]+result[2], 16) ) * 0.008413396 - 160

    return("{0:.1f}".format(t)+" C")
  else:
    # firmware 4.0 can't read temp/volt
    return("00.0 C")

def SBrickReadVolt():

  global BT_ADAPTER, SBRICK, SBRICK_FW_VS

  if(SBRICK_FW_VS=="4.2"):
    call("gatttool -b "+SBRICK+" -i "+BT_ADAPTER+" --char-write --handle=0x001A --value=0F00",shell=True)
    sleep(0.01)
    result=check_output("gatttool -b "+SBRICK+" -i "+BT_ADAPTER+" --char-read --handle=0x001A",shell=True).split(" ")
    v=( int(result[3]+result[2], 16) ) * 0.000378603  

    return("{0:.1f}".format(v)+" V")
  else:
    # firmware 4.0 can't read temp/volt
    return("0.0 V")


class Tool:

  global ScaleMAX,ScaleMIN

  def __init__(self):
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

    Port1 = Scale(self.root, from_=ScaleMAX, to=ScaleMIN, digits=3, resolution=5, orient=VERTICAL, length=255, takefocus=1, command=self.Sync, variable=self.pwm1)
    Port1.grid(row=2,column=0)

    CheckPort2=Checkbutton(self.root, variable = self.check2,takefocus=1, text="Port #2", padx=50, pady=10)
    CheckPort2.grid(row=1,column=1)

    Port2 = Scale(self.root, from_=255, to=0, digits=3, resolution=5, orient=VERTICAL, length=255,  takefocus=1, command=self.Sync, variable=self.pwm2)
    Port2.grid(row=2,column=1)

    CheckPort3=Checkbutton(self.root, variable = self.check3,takefocus=1, text="Port #3", padx=50, pady=10)
    CheckPort3.grid(row=1,column=2)

    Port3 = Scale(self.root, from_=255, to=0, digits=3, resolution=5, orient=VERTICAL, length=255,  takefocus=1, command=self.Sync, variable=self.pwm3)
    Port3.grid(row=2,column=2)

    CheckPort4=Checkbutton(self.root, variable = self.check4,takefocus=1, text="Port #4", padx=50, pady=10)
    CheckPort4.grid(row=1,column=3)

    Port4 = Scale(self.root, from_=255, to=0, digits=3, resolution=5, orient=VERTICAL, length=255, takefocus=1, command=self.Sync, variable=self.pwm4)
    Port4.grid(row=2,column=3)

    LabelQuit=Label(self.root, height=1, pady=10)
    LabelQuit.grid(row=3)
    Button_QUIT = Button(text = "QUIT", command = self.quit)
    Button_QUIT.grid(row=4, column=1, columnspan=2)

  def Sync(self, *ignore):
    if(self.check1.get()==0):
      SBrickDrive("0000"+twoDigitHex(self.pwm1.get()))
    else:
      SBrickDrive("0001"+twoDigitHex(self.pwm1.get()))

    if(self.check2.get()==0):
      SBrickDrive("0100"+twoDigitHex(self.pwm2.get()))
    else:
      SBrickDrive("0101"+twoDigitHex(self.pwm2.get()))

    if(self.check3.get()==0):
      SBrickDrive("0200"+twoDigitHex(self.pwm3.get()))
    else:
      SBrickDrive("0201"+twoDigitHex(self.pwm3.get()))

    if(self.check4.get()==0):
      SBrickDrive("0300"+twoDigitHex(self.pwm4.get()))
    else:
      SBrickDrive("0301"+twoDigitHex(self.pwm4.get()))

    return
               
  def quit(self):
    self.root.destroy()
    return;


  def refresh(self):

    self.temp.set(SBrickReadTemp())
    self.volt.set(SBrickReadVolt()) 
    self.root.after(PERIOD,self.refresh)  # reschedule event
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
  print('SBrick Stress Test Tool 0.3 - Jorge Pereira - February 2015')


def main(argv):

  global BT_ADAPTER, SBRICK, SBRICK_FW_VS
  global ScaleMAX,ScaleMIN

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
        SBRICK = arg
      elif opt == '-p':
        PERIOD = arg

    if( BT_ADAPTER=='')or(SBRICK=='')or(PERIOD==''):
      print_help()
      sys.exit(EXIT_ARGS)
    else:
      print('')
      print('sbstress - SBrick Stress Test Tool')
      print(' Adapter:    ', BT_ADAPTER)
      print(' Device:     ', SBRICK)
      print(' Period:     ', PERIOD)

    # find SBrick hardware and firmware version
    # should return something like 'Characteristic value/descriptor: 34 2e 30'
    # 34 = '4'  2E =' .'  30 = '0'
    # can have more chars for minor versions like 4.2b2 but will use just the first 3

    try:
      result=SBrickGetHw()
      parsed_result=result.split(" ")
      SBRICK_HW_VS=(parsed_result[2]+parsed_result[3]+parsed_result[4]).decode("hex")
    except CalledProcessError:
      print("Could not read SBrick hardware version")
      exit(EXIT_HW)

    try:
      result=SBrickGetFw()
      parsed_result=result.split(" ")
      SBRICK_FW_VS=(parsed_result[2]+parsed_result[3]+parsed_result[4]).decode("hex")
    except CalledProcessError:
      print("Could not read SBrick firmware version")
      exit(EXIT_FW)

    print(' SBrick Hw:   ' + SBRICK_HW_VS)
    print(' SBrick Fw:   ' + SBRICK_FW_VS)

    if(SBRICK_FW_VS == "4.0"):
      print("Will use SBrick firmware 4.0 handles")
      print("Will limit values to 0..FE as FF doesn't work")
      ScaleMAX = 254
      ScaleMIN = 0
    elif(SBRICK_FW_VS == "4.2"):
      print("Will use SBrick firmware 4.2 handles")
      ScaleMAX = 255
      ScaleMIN = 0
    else:
      print("Don't know how to handle this firmware version")
      sys.exit(EXIT_FWID)

    tool = Tool()
    tool.root.after(PERIOD,tool.refresh)
    tool.root.mainloop()

  except Exception:
    # Oooops! Hate this part! Lot of work to do...
    traceback.print_exc(file=sys.stdout)


  sys.exit(EXIT_OK)


if __name__ == '__main__':
  main(sys.argv[1:])

