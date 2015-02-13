Just some random thoughts:

PERIOD

PERIOD is a property of the SBrick but it should be a property of the Tool itself since we can choose its value, we just shouldn't use a PERIOD bigger than the defined Watchdog.
When I have time will test how to read the defined Watchdog and set it as a property of the SBrick.

Mapping SBrick Ports to Slide Bars (Scales)

I think each Slide should have a list of associated Ports. In theory, these Ports should be objects or properties of the SBrick.
But can be just 4 boolean values (1 for each port) and use some extra logic to assure only one port is true for all Slides.

OPTIONS

Other options could be set in GUI:
- PERIOD
- MAX,MIN and RESOLUTION for the Slide Bars (perhaps even LINEAR or LOGARITHMIC scales)

Future features:
- BLE scanning and SBrick selection
- Quick Drive protocol (not available for fw 4.0) - shorter and fewer gatttool commands so (hopefully) better lattency
