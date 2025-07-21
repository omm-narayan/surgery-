import pygame, Callibration, Support, socketio, subprocess


handServer = subprocess.Popen('node ../node_hand_server/index.js')
xDriveSerial = '20673892304E'
yDriveSerial = '2076388F304E'

xWidth = 700
yHeight = 600
zDepth = 400
handMinimums = (-350, -300, 200)

guiSupport = Support.GUI_Support()
driveSupport = Callibration.ODrive_Callibration()

xDrive, yDrive = driveSupport.StartDrive([xDriveSerial, yDriveSerial])

homing = Callibration.Homing_Callibration()
xBounds = homing.shrinkBounds(homing.callibrateAxis(xDrive.axis0), .2)
yBounds = homing.shrinkBounds(homing.callibrateAxis(yDrive.axis0, yDrive.axis1), .2)
zBounds = homing.shrinkBounds(homing.callibrateAxis(xDrive.axis1), .2)



movement = Callibration.MovementSupport(xBounds, yBounds, zBounds, xWidth, yHeight, zDepth)
screen = guiSupport.initDisplay((xWidth, yHeight))

def loop(screen, handPos):
    handX, handY, handZ = movement.zeroBounds(handMinimums, handPos)
    print(f'{handX}, {handY}')

    x = movement.MoveX(handX)
    y = movement.MoveY(handY)
    z = movement.MoveZ(handZ)
     
    xDrive.axis0.controller.pos_setpoint = x
    xDrive.axis1.controller.pos_setpoint = z
    
    #On second Y axis motor just invert that shit lmao 
    yDrive.axis1.controller.pos_setpoint = y
    yDrive.axis0.controller.pos_setpoint = -y
    
    guiSupport.drawGraphics((handX, handY, handZ), screen, (xWidth, yHeight))
    guiSupport.displayMetrics(f'X: {x},Y: {y},Z: ', screen)
    pygame.display.update()

#Listen for hand position from socket server
handPosition = (0, 0, 0)
sio = socketio.Client()
@sio.event
def position_update(data):
    global handPosition
    handPosition = tuple(data['handPosition'])
sio.connect('http://localhost:3000')

while 1:
    loop(screen, handPosition)
    if guiSupport.isQuit(): break
    
handServer.terminate()