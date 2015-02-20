# SBrick Toolkit for Linux

This Toolkit is a set of Python scripts for controlling the SBrick, a Bluetooth Low Energy LEGO(TM)-like device from Vengit that allow the remote control of LEGO constructions.

It runs only on Linux systems because it's basesd on 'gatttool', an utility from the BlueZ 5 Linux Bluetooth stack.

Currently there are two tools:
- sbstress - SBrick Stress Tool (stable)
- smaestro - SBrick Conducting Tool (very alpha)

'sbstress' (soon to be renamed) is a GUI tool that was created to stress test the SBrick but has evolved to a multi-porpose control tool.

'sbmaestro' is a command line tool that reads a sequence of commands from a file generated with sbtress (or other 3rd party tool) and replays those commands.

Please note that I do not consider myself a good programmer (some weeks ago not even A programmer!). Improving this tools had been a fun way to teach myself Python and GUI programming but I still lack a solid background on software engineering (there were no such thing as classes, objects, exceptions or source control at my Electronics Engineering course 20 years ago). As so we all must thank [szigetigabor](https://github.com/szigetigabor) for polishing and improving my original code and still contributing to this toolkit.

That said... please do have fun :)
