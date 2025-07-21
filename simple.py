import odrive
from odrive.enums import *
import time, math

print('Searching for ODrive...')
my_drive = odrive.find_any()
print(f'ODrive Connected: {my_drive.vbus_voltage}')

my_drive.axis0.motor.config.current_lim = 20
my_drive.axis0.controller.config.vel_limit = 250000
my_drive.axis0.controller.config.vel_gain = 10 / 10000.0
my_drive.axis0.controller.config.pos_gain = 20
my_drive.axis0.controller.config.vel_integrator_gain = 0



print('starting calibration...')
my_drive.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
while my_drive.axis0.current_state != AXIS_STATE_IDLE: 
    time.sleep(0.1)

my_drive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

t0 = time.monotonic()
fullRotation = 8192
while True: 
    # setpoint = (fullRotation) * math.sin((time.monotonic() - t0) * 2) * 10
    # print("goto " + str(int(setpoint)))
    # my_drive.axis0.controller.pos_setpoint = setpoint
    # time.sleep(0.01)

    my_drive.axis0.controller.pos_setpoint = fullRotation * 10
    time.sleep(2.5)
    my_drive.axis0.controller.pos_setpoint = 0
    time.sleep(2.5)