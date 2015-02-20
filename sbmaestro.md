'sbmaestro' - SBrick Conducting Tool

This is a (very new) command line python tool to replay previously generated SBrick commands.
Presently it reads one file 'test.sbr' that contains SBrick commands as generated with 'sbstress' tool.

The file contais groups of four lines. Each group is a Step and consists of the state of the four SBrick ports until the next Step.
Each Step follows this format:

PORT + POLARITY + DUTY CYCLE

Port can be 00, 01, 02 or 03
POLARITY can be 00 or 01
DUTY CYCLE can be any hexadecimal in the range 00..FF

An example of a Step:

00000f
010180
020000
030000

This means: «tell the SBrick that until the next step it should:
- DRIVE Port#1 with Polarity '00' and Duty Cycle '0F'
- DRIVE Port#2 with Polarity '00' and Duty Cycle '80'
- DRIVE Port#3 with Polarity '00' and Duty Cycle '00'
- DRIVE Port#4 with Polarity '00' and Duty Cycle '00'

or in other words: «tell the SBrick to apply 6% to Port#1 and -50% to Port#2, leave the other two ports quiet».

At this early stage, each Step lasts 100 ms.

The script accepts the same arguments of 'sbstress', e.g.:

./sbmaestro.py -a hci1 -d 00:07:80:2E:41:97 -p 100



