import time, math, odrive, Callibration
from odrive.enums import *

xDriveSerial = '20673892304E'
yDriveSerial = '2076388F304E'

driveSupport = Callibration.ODrive_Callibration()
xDrive = driveSupport.StartDrive([xDriveSerial])[0]

print(xDrive.axis0.motor.config.current_lim)

t0 = time.monotonic()
fullRotation = 8192
while True: 
    # x = int((fullRotation) * math.sin((time.monotonic() - t0) * 2))
    # y = int((fullRotation) * math.cos((time.monotonic() - t0) * 2))
    # x = x if abs(x) < fullRotation else 0
    # y = y if abs(y) < fullRotation else 0
    # #print(f'goto: {x}, {y}')
    # xDrive.axis0.controller.pos_setpoint = x
    # #xDrive.axis1.controller.pos_setpoint = y
    # time.sleep(0.01)

    #xDrive.axis0.controller.pos_setpoint = fullRotation * 4
    xDrive.axis1.controller.pos_setpoint = fullRotation * 2
    time.sleep(1)
    #xDrive.axis0.controller.pos_setpoint = 0
    xDrive.axis1.controller.pos_setpoint = 0
    time.sleep(1)