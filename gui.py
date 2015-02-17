#!/usr/bin/env python 

from __future__ import print_function
from Tkinter import *
from time import sleep

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

    # port mapping:
    # each slide has a list 4 boolean values (True or False for each port it controls)
    # have to assure somewhere else that a port is only True once
    self.slide1= [True,False,False,False]
    self.slide2= [False,True,False,False]
    self.slide3= [False,False,True,False]
    self.slide4= [False,False,False,True]
    self.slides= [self.slide1,self.slide2,self.slide3,self.slide4]

    self.configchanged=BooleanVar()
    self.configchanged.set(False)

    # NOTE: pwm is a property of the slide bar (but it should be of the port)
    self.pwm1.set(0)
    self.pwm2.set(0)
    self.pwm3.set(0)
    self.pwm4.set(0)
    self.pwms = [self.pwm1, self.pwm2, self.pwm3, self.pwm4]
 
    # NOTE: check is now a property of the port, not of the slide
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

    LabelBreak=Label(self.root, height=1, pady=10)	# just a separator
    LabelBreak.grid(row=7)

    Button_Options=Button(self.root,text='Options',command=self.Options)
    Button_Options.grid(row=8,column=0)

    Button_QUIT = Button(text = "QUIT", command = self.quit)
    Button_QUIT.grid(row=8, column=1)


  def twoDigitHex(self,number):
      return '%02x' % number


  def draw_slides(self):

    col=0
    for x in range(0,4):
      count=0
      for i in range(0,4):
        if(self.slides[x][i]==True):
          CheckPort=Checkbutton(self.root, variable = self.checks[i],takefocus=1, text="Port #"+str(i+1), padx=50, pady=10)
          CheckPort.grid(row=2+count,column=col)
          count+=1

      if(count>0):
       Port = Scale(self.root, from_=self.ScaleMAX, to=self.ScaleMIN, digits=3, resolution=5, orient=VERTICAL, length=self.LENGTH, takefocus=1, command=self.Sync, variable=self.pwms[x])
       Port.grid(row=6,column=col)
       col+=1


  def Sync(self, *ignore):

    # one slide may now control several ports

    for x in range(0,4):
      speed=self.pwms[x].get()

      if (self.slides[x][0]==True):
         # port #1
        direction="00"
        if( (speed >= 0 and self.checks[0].get()==1) or
            (speed <  0 and self.checks[0].get()==0) ):
          direction="01"
        self.SBRICK.Drive("00" + direction + self.twoDigitHex(abs(speed)))

      if (self.slides[x][1]==True):
         # port #2
        direction="00"
        if( (speed >= 0 and self.checks[1].get()==1) or
            (speed <  0 and self.checks[1].get()==0) ):
          direction="01"
        self.SBRICK.Drive("01" + direction + self.twoDigitHex(abs(speed)))

      if (self.slides[x][2]==True):
         # port #3
        direction="00"
        if( (speed >= 0 and self.checks[2].get()==1) or
            (speed <  0 and self.checks[2].get()==0) ):
          direction="01"
        self.SBRICK.Drive("02" + direction + self.twoDigitHex(abs(speed)))

      if (self.slides[x][3]==True):
         # port #4
        direction="00"
        if( (speed >= 0 and self.checks[3].get()==1) or
            (speed <  0 and self.checks[3].get()==0) ):
          direction="01"
        self.SBRICK.Drive("03" + direction + self.twoDigitHex(abs(speed)))
    return
               
  def quit(self):
    self.root.destroy()
    return;


  def refresh(self):

    self.temp.set(self.SBRICK.ReadTemp())
    self.volt.set(self.SBRICK.ReadVolt())
    self.root.after(self.SBRICK.GetPeriod(),self.refresh)  # reschedule event
    self.Sync()

    if(self.configchanged.get() == True):
      # remove all scales and checkbuttons
      for r in range(2,7):
        for slaves in self.root.grid_slaves(row=r):
          slaves.grid_remove()

      # reset al scale values - if we want "memory" we should make pwm a
      # property of the port (not a property of the scale)
      # and when redrawing scales read pwm from the ports and set the scales again
      # but don't know what to do when 2 ports with different pwm values are mapped
      # to the same scale

      for x in range(0,4):
        self.SBRICK.Stop("0"+str(x))
        self.pwms[x].set(0)      

      # redraw it all
      self.draw_slides()
      self.configchanged.set(False)

  def Options(self):

    # NOTE: it is possible to open multiple new windows - it shouldn't
    self.newWindow = Toplevel(self.root)
    self.config = Config(self.newWindow,self)


class Config(Tool):
  def __init__(self, root, tool):
    self.root = root
    self.slides=tool.slides
    self.configchanged=tool.configchanged

    self.Port1 = IntVar()
    self.Port2 = IntVar()
    self.Port3 = IntVar()
    self.Port4 = IntVar()
    self.Ports = [self.Port1,self.Port2,self.Port3,self.Port4]

    self.LabelSlide1=Label()
    self.LabelSlide2=Label()
    self.LabelSlide3=Label()
    self.LabelSlide4=Label()
    self.LabelSlides=[self.LabelSlide1,self.LabelSlide2,self.LabelSlide3,self.LabelSlide4]

    self.RadioSlide11=Radiobutton()
    self.RadioSlide12=Radiobutton()
    self.RadioSlide13=Radiobutton()
    self.RadioSlide14=Radiobutton()
    self.RadioSlideRow1=[self.RadioSlide11,self.RadioSlide12,self.RadioSlide13,self.RadioSlide14]

    self.RadioSlide21=Radiobutton()
    self.RadioSlide22=Radiobutton()
    self.RadioSlide23=Radiobutton()
    self.RadioSlide24=Radiobutton()
    self.RadioSlideRow2=[self.RadioSlide21,self.RadioSlide22,self.RadioSlide23,self.RadioSlide24]

    self.RadioSlide31=Radiobutton()
    self.RadioSlide32=Radiobutton()
    self.RadioSlide33=Radiobutton()
    self.RadioSlide34=Radiobutton()
    self.RadioSlideRow3=[self.RadioSlide31,self.RadioSlide32,self.RadioSlide33,self.RadioSlide34]

    self.RadioSlide41=Radiobutton()
    self.RadioSlide42=Radiobutton()
    self.RadioSlide43=Radiobutton()
    self.RadioSlide44=Radiobutton()
    self.RadioSlideRow4=[self.RadioSlide41,self.RadioSlide42,self.RadioSlide43,self.RadioSlide44]

    self.RadioSlideMatrix=[self.RadioSlideRow1,self.RadioSlideRow2,self.RadioSlideRow3,self.RadioSlideRow4]

    for x in range(0, 4):
      self.LabelSlides[x]=Label(self.root,text="Slide #"+str(x+1)+" controls which Ports?")
      self.LabelSlides[x].grid(row=2*x,column=0,columnspan=4)
      for i in range(0,4):
        self.RadioSlideMatrix[x][i]=Radiobutton(self.root,text=str(i+1), variable=self.Ports[i], value=x*10+i, command=self.RadioSelected)
        self.RadioSlideMatrix[x][i].grid(row=1+2*x,column=i)
        if(self.slides[x][i]==True):
          self.RadioSlideMatrix[x][i].select()
        else:
          self.RadioSlideMatrix[x][i].deselect()


    self.labelBreak2=Label(self.root, height=1, pady=10)	# just a separator
    self.labelBreak2.grid(row=8)

    self.buttonClose = Button(self.root,text='Close',command=self.close)
    self.buttonClose.grid(row=9,column=0,columnspan=4)


  def RadioSelected(self):

     self.configchanged.set(True)

     # reset all mappings as we need to redefine them all
     for x in range(0,4):
       self.slides[x]=[False,False,False,False]

     # read all 16 RadioButtons and set slides port mapping, brute force method

     if (self.Ports[0].get()==0):
       print("Slide #1 uses port 0")
       self.slides[0][0]=True
     if (self.Ports[0].get()==10):
       print("Slide #2 uses port 0")
       self.slides[1][0]=True
     if (self.Ports[0].get()==20):
       print("Slide #3 uses port 0")
       self.slides[2][0]=True
     if (self.Ports[0].get()==30):
       print("Slide #4 uses port 0")
       self.slides[3][0]=True

     if (self.Ports[1].get()==1):
       print("Slide #1 uses port 1")
       self.slides[0][1]=True
     if (self.Ports[1].get()==11):
       print("Slide #2 uses port 1")
       self.slides[1][1]=True
     if (self.Ports[1].get()==21):
       print("Slide #3 uses port 1")
       self.slides[2][1]=True
     if (self.Ports[1].get()==31):
       print("Slide #4 uses port 1")
       self.slides[3][1]=True

     if (self.Ports[2].get()==2):
       print("Slide #1 uses port 2")
       self.slides[0][2]=True
     if (self.Ports[2].get()==12):
       print("Slide #2 uses port 2")
       self.slides[1][2]=True
     if (self.Ports[2].get()==22):
       print("Slide #3 uses port 2")
       self.slides[2][2]=True
     if (self.Ports[2].get()==32):
       print("Slide #4 uses port 2")
       self.slides[3][2]=True

     if (self.Ports[3].get()==3):
       print("Slide #1 uses port 3")
       self.slides[0][3]=True
     if (self.Ports[3].get()==13):
       print("Slide #2 uses port 3")
       self.slides[1][3]=True
     if (self.Ports[3].get()==23):
       print("Slide #3 uses port 3")
       self.slides[2][3]=True
     if (self.Ports[3].get()==33):
       print("Slide #4 uses port 3")
       self.slides[3][3]=True

     return


  def close(self):
#    nr_slides=self.num
    self.root.destroy()

