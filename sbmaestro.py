#!/usr/bin/env python 

from __future__ import print_function
from Tkinter import *
from time import sleep
import sys, getopt
from sbrick import SBrick


BT_ADAPTER = ''
SBRICK_ADDR = ''
PERIOD = 100

PLAYFILE = './test.sbr'

# To Do: need to define "sbr" file format
# should include PERIOD at start but perhaps it can be changed at runtime?
# should also include STOP at end or REPLAY

# exit codes
EXIT_OK   = 0
EXIT_ARGS = 2

def print_help():
  print('')
  print('sbmaestro - SBrick Conducting Tool')
  print('Usage:')
  print('   sbmaestro.py -a <adapter> -d <device> -p <period>')
  print('')
  print('   <adapter>         HCI adapter, e.g. hci0')
  print('   <device>          SBrick Bluetooh Addres, e.g. AA:BB:CC:DD:EE:FF')
  print('   <period>          time in milliseconds, e.g. 100')
  print('')


def print_version():
  print('')
  print('SBrick Conducting Tool 0.1 - Jorge Pereira - February 2015')


def main(argv):
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

    print('')
    print('sbmaestro - SBrick Conducting Tool')
    SBRICK = SBrick(BT_ADAPTER, SBRICK_ADDR, PERIOD)

    # There seems to be a deviation in time so take 15 ms in 100
    # will see this later
    STEP=float(PERIOD-15)/1000

    playfile=open(PLAYFILE,'r')

    for line in playfile:
      command=line.strip('\n')
#      print(command)
      SBRICK.Drive(command)
      sleep(STEP)

    playfile.close()

  except Exception:
    # Oooops! Hate this part! Lot of work to do...
    traceback.print_exc(file=sys.stdout)

  # better stop all ports before exit than leaving it to the watchdog
  SBRICK.Stop()

  sys.exit(EXIT_OK)


if __name__ == '__main__':
  main(sys.argv[1:])

