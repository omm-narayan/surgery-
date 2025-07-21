import socketio, time

class DataListener:
    def __init__(self):
        self.handPos = [0, 0, 0]

    def updateHandPos(self, newHandPos):
        self.handPos = newHandPos

    def getHandPos(self):
        return self.handPos


listener = DataListener()

sio = socketio.Client()
@sio.event
def position_update(data):
    listener.updateHandPos(data)

sio.connect('http://localhost:3000')

while 1:
    print(f'{listener.getHandPos()}')
