#!/usr/bin/env python 

from __future__ import print_function
from Tkinter import *
from time import sleep

# This is the Font used to print Temperature and Voltage
FONT_TYPE = "Helvetica"
FONT_SIZE = 16

RECORDFILE = './test.sbr'

class Tool:

  ScaleMAX = 0
  ScaleMIN = 0
  LENGTH = 0
  SBRICK = ''

  def __init__(self, sbrick):
    self.SBRICK = sbrick

    self.file=open(RECORDFILE, 'a')

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

    self.CheckPort1=Checkbutton()
    self.CheckPort2=Checkbutton()
    self.CheckPort3=Checkbutton()
    self.CheckPort4=Checkbutton()
    self.CheckPorts=[self.CheckPort1,self.CheckPort2,self.CheckPort3,self.CheckPort4]

    self.PortScale1=Scale()
    self.PortScale2=Scale()
    self.PortScale3=Scale()
    self.PortScale4=Scale()
    self.PortScales=[self.PortScale1,self.PortScale2,self.PortScale3,self.PortScale4]

    self.checkLED=IntVar()
    self.checkLED.set(0)

    self.checkRECORD=BooleanVar()
    self.checkRECORD.set(False)

    # force the window size as we are having resizing problems
    # (not a great idea but it is a start)
    self.root.minsize(400,800)

    self.draw_elements()


  def draw_elements(self):

    LabelTemperature=Label(self.root, textvariable=self.temp, font=(FONT_TYPE, FONT_SIZE))
    LabelTemperature.place(relx=0.3, rely=0.03, anchor=CENTER)

    LabelVoltage=Label(self.root, textvariable=self.volt, font=(FONT_TYPE, FONT_SIZE))
    LabelVoltage.place(relx=0.7, rely=0.03, anchor=CENTER)

    self.draw_slides()

    Checkb_IDLED=Checkbutton(self.root, variable = self.checkLED,takefocus=1, text="ID LED", padx=10, pady=10, command=self.DriveLED)
    Checkb_IDLED.place(relx=0.25, rely=0.9, anchor=CENTER)

    Button_STOP = Button(text = "STOP ALL", command = self.ports_stop)
    Button_STOP.place(relx=0.5, rely=0.9, anchor=CENTER)

    Checkb_RECORD=Checkbutton(self.root,variable=self.checkRECORD,takefocus=1,text="REC", padx=10,pady=10, command=self.Record)
    Checkb_RECORD.place(relx=0.75,rely=0.9,anchor=CENTER)

    Button_Options=Button(self.root,text='Options',command=self.Options)
    Button_Options.place(relx=0.3,rely=0.95,anchor=CENTER)

    Button_QUIT = Button(text = "QUIT", command = self.quit)
    Button_QUIT.place(relx=0.7,rely=0.95,anchor=CENTER)

  def twoDigitHex(self,number):
      return '%02x' % number

  def DriveLED(self):
    if ( self.checkLED.get()==1):
      self.SBRICK.Led(True)
    else:
      self.SBRICK.Led(False)

  def Record(self):
     # Currently this is useless
     # print(self.checkRECORD.get())
    return

  def draw_slides(self):

    #first calculate the number of slides so we can center
    col=0
    for x in range(0,4):
      count=0
      for i in range(0,4):
        if(self.slides[x][i]==True):
          count+=1
      if(count>0):
        col+=1    

    # 1/(col+1) looks good
    if(col==1):
      RelX=0.5
    elif(col==2):
      RelX=0.33
    elif(col==3):
      RelX=0.25
    else:
      RelX=0.2

    col=0
    nChecks=0

    for x in range(0,4):
      count=0
      for i in range(0,4):
        if(self.slides[x][i]==True):
          self.CheckPorts[nChecks]=Checkbutton(self.root, variable = self.checks[i],takefocus=1, text="Port #"+str(i+1), padx=10, pady=10)
          self.CheckPorts[nChecks].place(relx=RelX+RelX*col,rely=0.05+0.03*(count+1),anchor=CENTER)
          count+=1
          nChecks+=1

      if(count>0):
       self.PortScales[col]=Scale(self.root, from_=self.ScaleMAX, to=self.ScaleMIN, digits=3, resolution=5, orient=VERTICAL,length=self.LENGTH, takefocus=1, command=self.Sync, variable=self.pwms[x])
       self.PortScales[col].place(relx=RelX+RelX*col,rely=0.5,anchor=CENTER)
       col+=1    

  def Sync(self, *ignore):
    for x in range(0,4):
      speed=self.pwms[x].get()
      for i in range(0, 4):
        # update all ports
        if (self.slides[x][i]==True):
          direction="00"
          if( (speed >= 0 and self.checks[i].get()==1) or
              (speed <  0 and self.checks[i].get()==0) ):
            direction="01"
          command="0"+ str(i) + direction + self.twoDigitHex(abs(speed))
          self.SBRICK.Drive(command)
          if(self.checkRECORD.get()==True):
            self.file.write(command+'\n')
    return
               
  def quit(self):
    self.file.close()
    self.root.destroy()
    return;

  def ports_stop(self):
    for i in range(0, 4):
 #     self.SBRICK.Stop("0"+str(i))
      self.pwms[i].set(0)

    return

  def refresh(self):

    self.temp.set(self.SBRICK.ReadTemp())
    self.volt.set(self.SBRICK.ReadVolt())
    self.root.after(self.SBRICK.GetPeriod(),self.refresh)  # reschedule event
    self.Sync()

    if(self.configchanged.get() == True):
      # remove all scales and checkbuttons
#      for r in range(2,7):
#        for slaves in self.root.grid_slaves(row=r):
#          slaves.grid_remove()   # I'm not sure if we should forget instead of remove

      for c in range(0,4):
         self.CheckPorts[c].place_forget()
         self.PortScales[c].place_forget()

      # reset al scale values - if we want "memory" we should make pwm a
      # property of the port (not a property of the scale)
      # and when redrawing scales read pwm from the ports and set the scales again
      # but don't know what to do when 2 ports with different pwm values are mapped
      # to the same scale

      #self.ports_stop()

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
    self.root.resizable(width=FALSE, height=FALSE)
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

    row=0
    for x in range(0, 4):
      row=2*x
      self.LabelSlides[x]=Label(self.root,text="Slide #"+str(x+1)+" controls which Ports?")
      self.LabelSlides[x].grid(row=row,column=0,columnspan=4)
      for i in range(0,4):
        self.RadioSlideMatrix[x][i]=Radiobutton(self.root,text=str(i+1), variable=self.Ports[i], value=x*10+i, command=self.RadioSelected)
        self.RadioSlideMatrix[x][i].grid(row=1+row,column=i)
        if(self.slides[x][i]==True):
          self.RadioSlideMatrix[x][i].select()
        else:
          self.RadioSlideMatrix[x][i].deselect()
    row+=2

    self.labelBreak2=Label(self.root, height=1, pady=13)	# just a separator
    self.labelBreak2.grid(row=row)

    self.buttonClose = Button(self.root,text='Close',command=self.close)
    self.buttonClose.grid(row=row,column=0,columnspan=4)

  def RadioSelected(self):

     self.configchanged.set(True)

     # reset all mappings as we need to redefine them all
     for x in range(0,4):
       self.slides[x]=[False,False,False,False]


     for x in range(0,4):
       if (self.Ports[x].get()==x):
         self.slides[0][x]=True
       if (self.Ports[x].get()==10+x):
         self.slides[1][x]=True
       if (self.Ports[x].get()==20+x):
         self.slides[2][x]=True
       if (self.Ports[x].get()==30+x):
         self.slides[3][x]=True

     return


  def close(self):
    self.root.destroy()

