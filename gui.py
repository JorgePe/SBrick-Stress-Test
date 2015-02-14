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

    self.nr_slides = IntVar()	# number of slide bars to use
    self.nr_slides.set(4)
    self.nr_slides_copy=4

    # each slide has a list 4 boolean values (True or False for each port it controls)
    # have to assure somewhere else that a port is only True once
    self.slide1= [True,False,False,False]
    self.slide2= [False,True,False,False]
    self.slide3= [False,False,True,False]
    self.slide4= [False,False,False,True]
    self.slides= [self.slide1,self.slide2,self.slide3,self.slide4]

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

    LabelBreak=Label(self.root, height=1, pady=10)	# just a separator
    LabelBreak.grid(row=7)

    Button_Options=Button(self.root,text='Options',command=self.Options)
    Button_Options.grid(row=8,column=0)

    Button_QUIT = Button(text = "QUIT", command = self.quit)
    Button_QUIT.grid(row=8, column=1)


  def twoDigitHex(self,number):
      return '%02x' % number


  def draw_slides(self):

    for x in range(0, self.nr_slides.get()):
      count=0
      for i in range(0,4):
        if(self.slides[x][i]==True):
          CheckPort=Checkbutton(self.root, variable = self.checks[x],takefocus=1, text="Port #"+str(x+1), padx=50, pady=10)
          CheckPort.grid(row=2+count,column=x)
          count+=1

      Port = Scale(self.root, from_=self.ScaleMAX, to=self.ScaleMIN, digits=3, resolution=5, orient=VERTICAL, length=self.LENGTH, takefocus=1, command=self.Sync, variable=self.pwms[x])
      Port.grid(row=6,column=x)

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
      for r in range(2,7):
        for slaves in self.root.grid_slaves(row=r):
          slaves.grid_remove()

      # reset pwm of removed scales so we don't have surprises if ever put scales back
      for x in range(self.nr_slides.get(),4):
        self.SBRICK.Stop("0"+str(x))
        self.pwms[x].set(0)      

      # redraw
      self.draw_slides()


  def Options(self):

    # NOTE: at this moment it is possible to open multiple new windows
    self.newWindow = Toplevel(self.root)
    self.config = Config(self.newWindow,self.nr_slides,self.slides)


class Config:
  def __init__(self, root, nr_slides, slides):
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
    self.Ports = [self.Port1,self.Port2,self.Port3,self.Port4]

    self.labelBreak=Label(self.root, height=1, pady=10)	# just a separator
    self.labelBreak.grid(row=1)


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

    for x in range(0, self.num.get()):
      self.LabelSlides[x]=Label(self.root,text="Slide #"+str(x+1)+" controls which Ports?")
      self.LabelSlides[x].grid(row=2+2*x,column=0,columnspan=4)
      for i in range(0,4):
        self.RadioSlideMatrix[x][i]=Radiobutton(self.root,text=str(i), variable=self.Ports[i], value=x*10+i)
        self.RadioSlideMatrix[x][i].grid(row=3+2*x,column=i)
        if(slides[x][i]==True):
          self.RadioSlideMatrix[x][i].select()
        else:
#          print("Uh!")
          self.RadioSlideMatrix[x][i].deselect()
#        self.RadioSlideMatrix[x][i].deselect()



    self.labelBreak2=Label(self.root, height=1, pady=10)	# just a separator
    self.labelBreak2.grid(row=10)

    self.buttonClose = Button(self.root,text='Close',command=self.close)
    self.buttonClose.grid(row=11,column=0,columnspan=4)

    return

  def RemapSlides(self, *ignore):	# don't know why must put *ignore here
    num_slides=self.num.get()

    for i in range(0,4):
      if(num_slides==1):
        self.RadioSlideRow1[i].config(state=NORMAL)
        self.RadioSlideRow2[i].config(state=DISABLED)
        self.RadioSlideRow3[i].config(state=DISABLED)
        self.RadioSlideRow4[i].config(state=DISABLED)
      elif(num_slides==2):
        self.RadioSlideRow1[i].config(state=NORMAL)
        self.RadioSlideRow2[i].config(state=NORMAL)
        self.RadioSlideRow3[i].config(state=DISABLED)
        self.RadioSlideRow4[i].config(state=DISABLED)
      elif(num_slides==3):
        self.RadioSlideRow1[i].config(state=NORMAL)
        self.RadioSlideRow2[i].config(state=NORMAL)
        self.RadioSlideRow3[i].config(state=NORMAL)
        self.RadioSlideRow4[i].config(state=DISABLED)
      else:
        self.RadioSlideRow1[i].config(state=NORMAL)
        self.RadioSlideRow2[i].config(state=NORMAL)
        self.RadioSlideRow3[i].config(state=NORMAL)
        self.RadioSlideRow4[i].config(state=NORMAL)
    return



  def close(self):
    nr_slides=self.num
    self.root.destroy()

