import sys


# This shows two examples of real sensors attached to pins A0 and A1 of the Galileo Gen 2 board.
# It uses the lib pyGalileo (Constants, __init__, and GalileoPins) on pyGalileo folder.
#
# You can adapt those sensors to your needs.

galileo_path = "pyGalileo/";
if galileo_path not in sys.path:
    sys.path.append(galileo_path);

from Constants import *
from __init__ import *
from GalileoPins import *

sensorPinLum = A0; # A0 pin comes from pyGalileo lib
sensorValueLum = 0;

sensorPinGas = A1; # A1 pin comes from pyGalileo lib
sensorValueGas = 0;


# The name of sensors functions should be the same as in config.json
def luminositySensor():
    sensorValueLum = analogRead(sensorPinLum); # analogRead comes from pyGalileo lib
    return sensorValueLum;

def gasSensor():
    sensorValueGas = analogRead(sensorPinGas); # analogRead comes from pyGalileo lib
    return sensorValueGas;
