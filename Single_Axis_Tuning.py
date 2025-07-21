import pygame, time, Support, odrive, Callibration

driveSupport = Callibration.ODrive_Callibration()
homing = Callibration.Homing_Callibration()

yDrive = driveSupport.StartDrive(['2076388F304E'])[0]
yBounds = homing.shrinkBounds(homing.callibrateAxis(yDrive.axis0, yDrive.axis1), .2)

movement = Callibration.MovementSupport(yBounds=yBounds, yHeight=600)



guiSupport = Support.GUI_Support()
pygame.init()

width = 600
height = 600
screen = guiSupport.initDisplay((width, height))


z = 0
while 1:
    x, y = pygame.mouse.get_pos()
    z = guiSupport.buttonTracker(pygame.K_x, pygame.K_z, z)

    y = movement.MoveY(y)
    yDrive.axis1.controller.pos_setpoint = y
    yDrive.axis0.controller.pos_setpoint = -y

    guiSupport.drawGraphics((x, y), screen, (width, height))
    guiSupport.displayMetrics(f'X: {x},Y: {y},Z: {z}', screen)
    pygame.display.update()


    if guiSupport.isQuit(): break
    time.sleep(0.01)
