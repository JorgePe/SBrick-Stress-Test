#!/usr/bin/env python 

from __future__ import print_function
from Tkinter import *
from time import sleep
from sbrick import *

# exit codes
EXIT_OK   = 0
EXIT_ARGS = 2
#EXIT_FILE = 3

# This is the Font used to print Temperature and Voltage
FONT_TYPE = "Helvetica"
FONT_SIZE = 16



class Tool:

  ScaleMAX = 0
  ScaleMIN = 0
  LENGTH = 0
  SBRICK = ''

  def __init__(self, sbrick):
    self.SBRICK = sbrick
    self.ScaleMAX = sbrick.GetScaleMAX()
    self.ScaleMIN = -1*self.ScaleMAX
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

    self.nr_slides = IntVar()	# number of slide bars to use
    self.nr_slides.set(4)
    self.nr_slides_copy=4

    self.pwm1.set(0)
    self.pwm2.set(0)
    self.pwm3.set(0)
    self.pwm4.set(0)
    self.pwms = [self.pwm1, self.pwm2, self.pwm3, self.pwm4]
 
    self.check1=IntVar()
    self.check1.set(0)
    self.check2=IntVar()
    self.check2.set(0)
    self.check3=IntVar()
    self.check3.set(0)
    self.check4=IntVar()
    self.check4.set(0)
    self.checks = [self.check1, self.check2, self.check3, self.check4]

    LabelTemperature=Label(self.root, textvariable=self.temp, font=(FONT_TYPE, FONT_SIZE))
    LabelTemperature.grid(row=0, column=1)

    LabelVoltage=Label(self.root, textvariable=self.volt, font=(FONT_TYPE, FONT_SIZE))
    LabelVoltage.grid(row=0, column=2)

    self.draw_slides()

    LabelQuit=Label(self.root, height=1, pady=10)	# just a separator
    LabelQuit.grid(row=4)
    Button_QUIT = Button(text = "QUIT", command = self.quit)
    Button_QUIT.grid(row=5, column=1, columnspan=2)

    Button_Options=Button(self.root,text='Options',command=self.Options)
    Button_Options.grid(row=6,column=1)

  def twoDigitHex(self,number):
      return '%02x' % number


  def draw_slides(self):

    for x in range(0, self.nr_slides.get()):
      CheckPort=Checkbutton(self.root, variable = self.checks[x],takefocus=1, text="Port #"+str(x+1), padx=50, pady=10)
      CheckPort.grid(row=2,column=x)

      Port = Scale(self.root, from_=self.ScaleMAX, to=self.ScaleMIN, digits=3, resolution=5, orient=VERTICAL, length=self.LENGTH, takefocus=1, command=self.Sync, variable=self.pwms[x])
      Port.grid(row=3,column=x)

    self.nr_slides_copy=self.nr_slides.get()

  def Sync(self, *ignore):
    for x in range(0, self.nr_slides.get()):
      direction="00"
      speed=self.pwms[x].get()
      if( (speed >= 0 and self.checks[x].get()==1) or
          (speed <  0 and self.checks[x].get()==0) ):
        direction="01"
        speed=abs(speed)    
      self.SBRICK.Drive("0"+ str(x) + direction + self.twoDigitHex(speed))
    return
               
  def quit(self):
    self.root.destroy()
    return;


  def refresh(self):
    self.temp.set(self.SBRICK.ReadTemp())
    self.volt.set(self.SBRICK.ReadVolt()) 
    self.root.after(self.SBRICK.GetPeriod(),self.refresh)  # reschedule event
    self.Sync()

    if(self.nr_slides.get()<>self.nr_slides_copy):
      # remove all scales and checkbuttons
      for slaves in self.root.grid_slaves(row=2):
        slaves.grid_remove()
      for slaves in self.root.grid_slaves(row=3):
        slaves.grid_remove()

      # reset pwm of removed scales so we don't have surprises if ever put scales back
      for x in range(self.nr_slides.get(),4):
        self.SBRICK.Stop("0"+str(x))
        self.pwms[x].set(0)      

      # redraw
      self.draw_slides()


  def Options(self):
    self.newWindow = Toplevel(self.root)
    self.config = Config(self.newWindow,self.nr_slides)


class Config:
  def __init__(self, root, nr_slides):
    self.root = root

    self.num = IntVar()
    self.num = nr_slides

    OPTIONS = ['1', '2', '3', '4']
    self.labelNrSlides=Label(self.root,text="Number of Slides:")
    self.labelNrSlides.grid(row=0,column=0,columnspan=2)
    self.optionNrSlides = OptionMenu(self.root, self.num, *OPTIONS, command=self.RemapSlides)
    self.optionNrSlides.grid(row=0,column=3)

    self.Port1 = IntVar()
    self.Port2 = IntVar()
    self.Port3 = IntVar()
    self.Port4 = IntVar()

    self.labelBreak=Label(self.root, height=1, pady=10)	# just a separator
    self.labelBreak.grid(row=1)

    # Line 2 and 3: Slide1
    self.LabelSlide1=Label(self.root,text="Slide #1 controls which Ports?")
    self.LabelSlide1.grid(row=2,column=0,columnspan=4)

    self.RadioSlide1Port1=Radiobutton(self.root,text="1", variable=self.Port1,value=11)
    self.RadioSlide1Port1.grid(row=3,column=0)
    self.RadioSlide1Port2=Radiobutton(self.root,text="2", variable=self.Port2,value=12)
    self.RadioSlide1Port2.grid(row=3,column=1)
    self.RadioSlide1Port3=Radiobutton(self.root,text="3", variable=self.Port3,value=13)
    self.RadioSlide1Port3.grid(row=3,column=2)
    self.RadioSlide1Port4=Radiobutton(self.root,text="4", variable=self.Port4,value=14)
    self.RadioSlide1Port4.grid(row=3,column=3)


    # Line 4 and 5: Slide2
    self.LabelSlide2=Label(self.root,text="Slide #2 controls which Ports?")
    self.LabelSlide2.grid(row=4,column=0,columnspan=4)
    self.RadioSlide2Port1=Radiobutton(self.root,text="1", variable=self.Port1,value=21)
    self.RadioSlide2Port1.grid(row=5,column=0)
    self.RadioSlide2Port2=Radiobutton(self.root,text="2", variable=self.Port2,value=22)
    self.RadioSlide2Port2.grid(row=5,column=1)
    self.RadioSlide2Port3=Radiobutton(self.root,text="3", variable=self.Port3,value=23)
    self.RadioSlide2Port3.grid(row=5,column=2)
    self.RadioSlide2Port4=Radiobutton(self.root,text="4", variable=self.Port4,value=24)
    self.RadioSlide2Port4.grid(row=5,column=3)


    # Line 6 and 7: Slide3
    self.LabelSlide3=Label(self.root,text="Slide #3 controls which Ports?")
    self.LabelSlide3.grid(row=6,column=0,columnspan=4)
    self.RadioSlide3Port1=Radiobutton(self.root,text="1", variable=self.Port1,value=31)
    self.RadioSlide3Port1.grid(row=7,column=0)
    self.RadioSlide3Port2=Radiobutton(self.root,text="2", variable=self.Port2,value=32)
    self.RadioSlide3Port2.grid(row=7,column=1)
    self.RadioSlide3Port3=Radiobutton(self.root,text="3", variable=self.Port3,value=33)
    self.RadioSlide3Port3.grid(row=7,column=2)
    self.RadioSlide3Port4=Radiobutton(self.root,text="4", variable=self.Port4,value=34)
    self.RadioSlide3Port4.grid(row=7,column=3)

    # Line 8 and 9: Slide4
    self.LabelSlide4=Label(self.root,text="Slide #4 controls which Ports?")
    self.LabelSlide4.grid(row=8,column=0,columnspan=4)
    self.RadioSlide4Port1=Radiobutton(self.root,text="1", variable=self.Port1,value=41)
    self.RadioSlide4Port1.grid(row=9,column=0)
    self.RadioSlide4Port2=Radiobutton(self.root,text="2", variable=self.Port2,value=42)
    self.RadioSlide4Port2.grid(row=9,column=1)
    self.RadioSlide4Port3=Radiobutton(self.root,text="3", variable=self.Port3,value=43)
    self.RadioSlide4Port3.grid(row=9,column=2)
    self.RadioSlide4Port4=Radiobutton(self.root,text="4", variable=self.Port4,value=44)
    self.RadioSlide4Port4.grid(row=9,column=3)

    self.labelBreak2=Label(self.root, height=1, pady=10)	# just a separator
    self.labelBreak2.grid(row=10)

    self.buttonClose = Button(self.root,text='Close',command=self.close)
    self.buttonClose.grid(row=11,column=0,columnspan=4)

    return

  def RemapSlides(self, *ignore):	# don't know why must put *ignore here
    num_slides=self.num.get()

    if(num_slides==1):
      self.RadioSlide2Port1.config(state=DISABLED)
      self.RadioSlide2Port2.config(state=DISABLED)
      self.RadioSlide2Port3.config(state=DISABLED)
      self.RadioSlide2Port4.config(state=DISABLED)

      self.RadioSlide3Port1.config(state=DISABLED)
      self.RadioSlide3Port2.config(state=DISABLED)
      self.RadioSlide3Port3.config(state=DISABLED)
      self.RadioSlide3Port4.config(state=DISABLED)

      self.RadioSlide4Port1.config(state=DISABLED)
      self.RadioSlide4Port2.config(state=DISABLED)
      self.RadioSlide4Port3.config(state=DISABLED)
      self.RadioSlide4Port4.config(state=DISABLED)

    elif(num_slides==2):
      self.RadioSlide2Port1.config(state=NORMAL)
      self.RadioSlide2Port2.config(state=NORMAL)
      self.RadioSlide2Port3.config(state=NORMAL)
      self.RadioSlide2Port4.config(state=NORMAL)

      self.RadioSlide3Port1.config(state=DISABLED)
      self.RadioSlide3Port2.config(state=DISABLED)
      self.RadioSlide3Port3.config(state=DISABLED)
      self.RadioSlide3Port4.config(state=DISABLED)

      self.RadioSlide4Port1.config(state=DISABLED)
      self.RadioSlide4Port2.config(state=DISABLED)
      self.RadioSlide4Port3.config(state=DISABLED)
      self.RadioSlide4Port4.config(state=DISABLED)

    elif(num_slides==3):
      self.RadioSlide2Port1.config(state=NORMAL)
      self.RadioSlide2Port2.config(state=NORMAL)
      self.RadioSlide2Port3.config(state=NORMAL)
      self.RadioSlide2Port4.config(state=NORMAL)

      self.RadioSlide3Port1.config(state=NORMAL)
      self.RadioSlide3Port2.config(state=NORMAL)
      self.RadioSlide3Port3.config(state=NORMAL)
      self.RadioSlide3Port4.config(state=NORMAL)

      self.RadioSlide4Port1.config(state=DISABLED)
      self.RadioSlide4Port2.config(state=DISABLED)
      self.RadioSlide4Port3.config(state=DISABLED)
      self.RadioSlide4Port4.config(state=DISABLED)
    else:
      self.RadioSlide2Port1.config(state=NORMAL)
      self.RadioSlide2Port2.config(state=NORMAL)
      self.RadioSlide2Port3.config(state=NORMAL)
      self.RadioSlide2Port4.config(state=NORMAL)

      self.RadioSlide3Port1.config(state=NORMAL)
      self.RadioSlide3Port2.config(state=NORMAL)
      self.RadioSlide3Port3.config(state=NORMAL)
      self.RadioSlide3Port4.config(state=NORMAL)

      self.RadioSlide4Port1.config(state=NORMAL)
      self.RadioSlide4Port2.config(state=NORMAL)
      self.RadioSlide4Port3.config(state=NORMAL)
      self.RadioSlide4Port4.config(state=NORMAL)
    return



  def close(self):
    nr_slides=self.num
    self.root.destroy()

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
  print('SBrick Stress Test Tool 0.41 - Jorge Pereira - February 2015')


def main(argv):

  BT_ADAPTER = ''
  SBRICK_ADDR = ''
  PERIOD = '100'
  
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

  # better stop all ports before exit than leaving it to the watchdog
  SBRICK.Stop("01")
  SBRICK.Stop("02")
  SBRICK.Stop("03")
  SBRICK.Stop("04")

  sys.exit(EXIT_OK)


if __name__ == '__main__':
  main(sys.argv[1:])

