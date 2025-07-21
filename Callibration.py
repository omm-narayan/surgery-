import odrive
from odrive.enums import *
import time, math, json
from queue import Queue

#X Connection_Serial: 20673892304E
#Y Connection_Serial: 2076388F304E

#X Board_Serial: 35627702825038
#Y Board_Serial: 35692127137870

class ODrive_Callibration:

    def AssignAxisParameters(self, axis, pidSettings):
        axis.motor.config.current_lim = pidSettings['current_lim']
        axis.controller.config.vel_limit = pidSettings['vel_limit']
        axis.controller.config.vel_gain = pidSettings['vel_gain']
        axis.controller.config.pos_gain = pidSettings['pos_gain']
        axis.controller.config.vel_integrator_gain = pidSettings['vel_integrator_gain']


    def DetermineDriveParameters(self, drive):
        xBoardSerial = '35627702825038'
        yBoardSerial = '35692127137870'

        with open('pid_tuning.json') as f:
            pidSettings = json.load(f)

        if str(drive.serial_number) == xBoardSerial:
            self.AssignAxisParameters(drive.axis0, pidSettings['axisX'])
            self.AssignAxisParameters(drive.axis1, pidSettings['axisZ'])

        if str(drive.serial_number) == yBoardSerial:
            self.AssignAxisParameters(drive.axis0, pidSettings['axisY_Main'])
            self.AssignAxisParameters(drive.axis1, pidSettings['axisY_Slave'])
        return drive

    def StartDrive(self, serialNumbers):
        drives = []

        #Apply PID settings to each axis
        for i in range(len(serialNumbers)):
            print('Searching for ODrive...')
            drives.append(self.DetermineDriveParameters(odrive.find_any(serial_number=serialNumbers[i])))
            print(f'({i + 1}/{len(serialNumbers)}) ODrives Connected...')


        print('starting calibration...')
        for drive in drives:
            drive.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
            drive.axis1.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        
        while 1:
            drivesNotCallibrated = 0
            for drive in drives:
                if drive.axis0.current_state != AXIS_STATE_IDLE or drive.axis1.current_state != AXIS_STATE_IDLE:
                    drivesNotCallibrated += 1
            if drivesNotCallibrated == 0:
                break
            time.sleep(0.1)
            
        for drive in drives:
            drive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            drive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

        return tuple(drives)

class Homing_Callibration:
    def withinAmperageRange(self, currentAmps, endstopMaxAmps, odriveMaxAmps):
        return abs(currentAmps) >= endstopMaxAmps * .8 or abs(currentAmps) >= odriveMaxAmps * .8
    
    def withinStartingTouque(self, startTime):
        return time.monotonic() - startTime > .5

    def callibrateAxis(self, axis, parallelAxis=None):
        steps = 1000
        ticks = 0
        #Rough heuristic for determining stopping amperage
        endstopMaxAmps = ((steps / 100) * 2.4)
        odriveMaxAmps = axis.motor.config.current_lim

        #Max position detection
        startTime = time.monotonic()
        initialEncoderPos = int(axis.encoder.pos_estimate)
        while True:
            currentPos = int(axis.encoder.pos_estimate)
            #Step Odrive forward
            axis.controller.pos_setpoint = currentPos + steps
            if parallelAxis is not None:
                parallelAxis.controller.pos_setpoint = -(currentPos + steps)
            

            #Do not read starting torque amperage value
            currentUsage = axis.motor.current_control.Iq_measured if self.withinStartingTouque(startTime) else 0

            #Filter amp reading outliers with above amperage threshold
            ticks = ticks + 1 if self.withinAmperageRange(currentUsage, endstopMaxAmps, odriveMaxAmps) else ticks - 1
            ticks = ticks if ticks >= 0 else 0
            if ticks >= 3:
                break

            time.sleep(0.01)

        MaxPos = currentPos - steps
        axis.controller.pos_setpoint = initialEncoderPos
        if parallelAxis is not None:
            parallelAxis.controller.pos_setpoint = -initialEncoderPos

        time.sleep(1.5)

        #Min position detection
        startTime = time.monotonic()
        initialEncoderPos = int(axis.encoder.pos_estimate)
        while True:
            currentPos = int(axis.encoder.pos_estimate)
            #Step Odrive forward
            axis.controller.pos_setpoint = currentPos - steps
            if parallelAxis is not None:
                parallelAxis.controller.pos_setpoint = -(currentPos - steps)
            
            #Do not read starting torque amperage value
            currentUsage = axis.motor.current_control.Iq_measured if self.withinStartingTouque(startTime) else 0

            #Filter amp reading outliers with above amperage threshold
            ticks = ticks + 1 if self.withinAmperageRange(currentUsage, endstopMaxAmps, odriveMaxAmps) else ticks - 1
            ticks = ticks if ticks >= 0 else 0
            if ticks >= 3:
                break

            time.sleep(0.01)
        
        MinPos = currentPos - steps
        axis.controller.pos_setpoint = initialEncoderPos
        if parallelAxis is not None:
            parallelAxis.controller.pos_setpoint = -initialEncoderPos
            
        time.sleep(1.5)
        return((MaxPos, MinPos, int(axis.encoder.pos_estimate)))
    
    def shrinkBounds(self, bounds, shrinkBy):
        max, min, initial = bounds
        max = int(max * (1 - shrinkBy))
        min = int(min * (1 - shrinkBy))
        return((max, min, initial))

class MovementSupport:
    def __init__(self, xBounds=None, yBounds=None, zBounds=None, xWidth=None, yHeight=None, zDepth=None):
        if xBounds is not None and xWidth is not None:
            self.calculateXScaling(xBounds, xWidth)
        if yBounds is not None and yHeight is not None:
            self.calculateYScaling(yBounds, yHeight)
        if zBounds is not None and zDepth is not None:
            self.calculateZScaling(zBounds, zDepth)

    def zeroBounds(self, handMinimums, handPosition):
        xMin, yMin, zMin = handMinimums
        xHand, zHand, yHand = handPosition
        
        xHand += -xMin
        yHand += -yMin
        zHand += -zMin
        
        xHand = int(xHand)
        yHand = int(yHand)
        zHand = int(zHand)

        return (xHand, yHand, zHand)


    def calculateXScaling(self, xBounds, xWidth):
        self.xBounds = xBounds
        xMax, xMin, xInitial = xBounds
        self.scaleX = (xMax - xMin) / xWidth
    
    def calculateYScaling(self, yBounds, yHeight):
        self.yBounds = yBounds
        yMax, yMin, yInitial = yBounds
        self.scaleY = (yMax - yMin) / yHeight

    def calculateZScaling(self, zBounds, zDepth):
        self.zBounds = zBounds
        zMax, zMin, zInitial = zBounds
        self.scaleZ = (zMax - zMin) / zDepth


    #Must flip X
    def MoveX(self, xPosition):
        xPosition *= self.scaleX
        max, min, initial = self.xBounds
        offsetX = max - xPosition
        offsetX = offsetX if offsetX > min else min
        offsetX = offsetX if offsetX < max else max
        return int(offsetX)

    
    def MoveY(self, yPosition):
        yPosition *= self.scaleY
        max, min, initial = self.yBounds
        offsetY = min + yPosition
        offsetY = offsetY if offsetY > min else min
        offsetY = offsetY if offsetY < max else max
        return int(offsetY)

    def MoveZ(self, zPosition):
        zPosition *= self.scaleZ
        max, min, initial = self.zBounds
        offsetZ = min + zPosition
        offsetZ = offsetZ if offsetZ > min else min
        offsetZ = offsetZ if offsetZ < max else max
        return int(offsetZ)
    