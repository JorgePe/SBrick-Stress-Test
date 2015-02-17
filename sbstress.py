#!/usr/bin/env python 

import sys, getopt
from sbrick import SBrick
from gui import Tool

# exit codes
EXIT_OK   = 0
EXIT_ARGS = 2

def print_help():
  print('')
  print('sbstress - SBrick Stress Test Tool')
  print('Usage:')
  print('   sbstress.py -a <adapter> -d <device> -p <period>')
  print('')
  print('   <adapter>         HCI adapter, e.g. hci0')
  print('   <device>          SBrick Bluetooh Addres, e.g. AA:BB:CC:DD:EE:FF')
  print('   <period>          time in milliseconds, e.g. 100')
  print('')

def print_version():
  print('')
  print('SBrick Stress Test Tool 0.50 - Jorge Pereira - February 2015')


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
  SBRICK.Stop()

  sys.exit(EXIT_OK)


if __name__ == '__main__':
  main(sys.argv[1:])

