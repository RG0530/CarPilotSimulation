import Sensor

class Car:
    carVelocityX = 0
    carVelocityY = 0
    carPositionX = 0
    carPositionY = 0

    carName = ""
    startPosX = 0
    startPosY = 0
    carColor = 'black'

    carRectangle = None
    carSensor = None

    def __init__(self, name, startX, startY=0, carWidth=0, carHeight=0, startVelocityX=0.0, startVelocityY=2.0, color='black', radius=0):
        self.carVelocityX = startVelocityX
        self.carVelocityY = startVelocityY
        self.carPositionX = startX
        self.carPositionY = startY

        self.carName = name
        self.startPosX = startX
        self.startPosY = startY
        self.carColor = color

        self.carSensor = Sensor.Sensor(radius)
