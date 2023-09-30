from tkinter import *
import Car
import random

# Input variables
carSizeX = 20
carSizeY = 40
goingLeftRight = False  # Whether the lanes are going up/down or left/right


# Sets up the canvas
canvasXSize = 1500
canvasYSize = 600
canvasExtension = 50  # Extending space outside of canvas for cars to continue travelling on before teleporting
screenRefreshRate = 10

# Sets up variables for the environment (Not important)
carCount = 11
change = 50  # Distance between lanes

Tspeed = 2  # input in km/h
Lspeed = 1  # ^
carsdx = 500  # input in m
sensorRadius = 200
passNum = 0  # input in integer


# screen where user inputs their values
class InputScreen:

    root = None
    labels = None
    entries = None

    # defines and adds the labels and entries to the input screen
    def __init__(self, root2):
        self.root = root2

        self.labelNames = ['Trailing car velocity', 'Leading car velocity', 'Number of passengers', 'Starting distance between cars', 'Radar distance']
        self.labelUnits = ['km/h', ' km/h ', 'people', 'meters', ' meters ']
        self.labels = [Label(self.root, text=name).grid(row=self.labelNames.index(name), column=0) for name in self.labelNames]
        self.unitLabels = [Label(self.root, text=name).grid(row=self.labelUnits.index(name), column=3) for name in self.labelUnits]

        self.entries = [Entry(self.root) for i in range(len(self.labelNames))]
        [self.entries[i].grid(row=i, column=1) for i in range(len(self.entries))]

        # creates the button used to assign the inputted values to the variables
        self.submitButton = Button(self.root, text='Submit', command=self.enter_values).grid(row=len(self.labelNames), column=0)

    # function used by the submit button to assign inputted values to the variables
    def enter_values(self):
        global Tspeed, Lspeed, sensorRadius, carsdx, passNum
        Tspeed = int(self.entries[0].get()) / 50
        Lspeed = int(self.entries[1].get()) / 50
        passNum = int(self.entries[2].get())
        carsdx = int(self.entries[3].get()) * 15 / 2
        sensorRadius = (int(self.entries[4].get()) + 2*passNum) * 15 / 2

        # after the button is pressed, the screen gets destroyed in order to make room for the next screen
        self.root.destroy()


# canvas that hosts the simulation
class ScreenCanvas:

    canvas = None

    # code that runs when the canvas is created
    def __init__(self, root):

        self.brakingForce = 0

        # creates funny variables because text labels don't like normal strings for some reason
        self.velocityLabelVariable = StringVar()
        self.distanceLabelVariable = StringVar()
        self.brakingForceLabelVariable = StringVar()

        # puts the string variables into a list to make them easier to work with
        self.textVar = [self.velocityLabelVariable, self.distanceLabelVariable, self.brakingForceLabelVariable]

        # creates a dictionary with the label assigned to its respective label name
        self.labels = {
            'Velocity': Label(self.canvas, textvariable=self.velocityLabelVariable),
            'Distance': Label(self.canvas, textvariable=self.distanceLabelVariable),
            'Braking Force': Label(self.canvas, textvariable=self.brakingForceLabelVariable)
        }

        # creates the canvas that the simulation runs on
        self.canvas = Canvas(root, height=canvasYSize, width=canvasXSize)

        # creates an empty car list that all the cars will be added to eventually
        self.carList = []

        # creates the first two cars: the leading and trailing cars
        self.create_car('Trailing', 0, (canvasYSize + canvasExtension) // 2, carSizeY, carSizeX, Tspeed, 0, 'green', sensorRadius)
        self.create_car('Leading', carsdx, (canvasYSize + canvasExtension) // 2, carSizeY, carSizeX, Lspeed, 0, 'red')

        # creates varibales to hold the coordinates of the cars that will be used to calculate velocity and distance
        self.trailingCoords = self.canvas.coords(self.carList[0].carRectangle)
        self.leadingCoords = self.canvas.coords(self.carList[1].carRectangle)

        # gets the distance between the cars using the front x coordinate of the trailing car and the back x coordinate of the trailing car
        self.dx = int(self.leadingCoords[0]) - int(self.trailingCoords[2])

        # Creates vanity cars
        for i in range(carCount):
            self.create_car(f'Car V{i}', (canvasXSize + canvasExtension) - (i * ((canvasXSize + canvasExtension) / carCount)) + (10 - random.randrange(20)), (canvasYSize + canvasExtension) // 2 - change, carSizeY, carSizeX, 2, 0, "yellow")

        # Opposing Vanity Cars
        for j in range(2):  # Lane 1 and 2
            for i in range(carCount):
                self.create_car(f'Car V-{i + (j * carCount)}', (canvasXSize + canvasExtension) - (i * ((canvasXSize + canvasExtension) / carCount)) + (10 - random.randrange(20)),(canvasYSize + canvasExtension) // 2 + (2 * change) + (j * change), carSizeY, carSizeX, -2, 0, "yellow")

        # packs the labes to the canvas
        for key in self.labels:
            self.labels[key].pack(side=TOP)

        # packs the canvas itself
        self.canvas.pack()

        # calls the function to move the cars for the first time
        self.move_cars()

    # updates the text variables used when displaying tha labels
    def update_label_variables(self):
        self.dx = int(self.leadingCoords[0]) - int(self.trailingCoords[2]) if self.trailingCoords[2] < self.leadingCoords[0] else int(canvasXSize + canvasExtension - self.trailingCoords[2] + canvasExtension + self.leadingCoords[0])
        self.textVar[0].set(f'Velocity: {self.carList[0].carVelocityX * 50:.2f}')
        self.textVar[1].set(f'Distance: {self.dx * 2 / 15:.2f}')

    # applies the brakes to the car
    def automatic_braking(self, bf, isBraking):

        # if the car is braking, sets the braking force to the inputted force and subtracts it from the trailing car's velocity
        if isBraking:
            self.brakingForce = bf
            self.carList[0].carVelocityX -= self.brakingForce

        # if the car is not braking, subtracts from the braking force so the text variable for the label goes down
        elif self.brakingForce > 0.000001:
            self.brakingForce -= 0.000001

        # updates the text variable for the braking force label
        self.textVar[2].set(f'Braking Force: {self.brakingForce * 1000:.2f}')

    # function that creates the car and adds it to the list of cars
    def create_car(self, name, startX, startY=0, carWidth=0, carHeight=0, startVelocityX=0, startVelocityY=0, color='black', radius=0):

        # Creates a Car object and adds it to the carList.
        car = Car.Car(name, startX, startY, carWidth, carHeight, startVelocityX, startVelocityY, color, radius)
        self.carList.append(car)

        # Adds the rectangle to the canvas
        # Changes texture depending on whether it is a vanity car or not
        stipple = ''
        if (name.__contains__('V')):
            stipple = 'gray25'
        car.carRectangle = self.canvas.create_rectangle(startX, startY, startX + carWidth, startY + carHeight, fill=color, stipple=stipple)

        # creates a 'sensor' for the car if it is the trailing car
        if car.carSensor.radius > 0:
            posx = car.carPositionX - car.carSensor.radius + carWidth
            posy = car.carPositionY - car.carSensor.radius + carHeight / 2
            car.carSensor.sensorCircle = self.canvas.create_oval(posx, posy, car.carSensor.radius * 2 + posx, car.carSensor.radius * 2 + posy)

    def move_cars(self):

        # Moves the rectangle/car according to the x/y velocities currently assigned.
        for car in self.carList:
            self.canvas.move(car.carRectangle, car.carVelocityX, car.carVelocityY)
            if car.carSensor.radius > 0:
                self.canvas.move(car.carSensor.sensorCircle, car.carVelocityX, car.carVelocityY)

            # if distance between cars is less than the sensor radius
            if self.dx <= car.carSensor.radius:

                # if trailing car speed > leading car speed
                if self.carList[0].carVelocityX > self.carList[1].carVelocityX:
                    self.automatic_braking(1 / (self.dx + 10 * (passNum ** 2)), True)

                # once the trailing car matches the leading car's speed, slow down to 80% of the leading car's speed to create desired buffer between cars
                elif self.carList[0].carVelocityX > self.carList[1].carVelocityX * 0.8 and self.dx < sensorRadius:
                    self.automatic_braking(self.brakingForce - 0.0000001, True)

                # brakes are not applied so this function lowers the text variable for the braking force label
                else:
                    self.automatic_braking(0, False)
            # read previous comment
            else:
                self.automatic_braking(0, False)

            # trailing car speed < leading car speed | && | distance between cars > radius + 5
            if self.carList[0].carVelocityX < self.carList[1].carVelocityX and self.dx > sensorRadius + 1:
                self.carList[0].carVelocityX += 0.001


            car.carPositionX += car.carVelocityX
            car.carPositionY += car.carVelocityY

            # Wraps around canvas if position exceeds canvas bounds.
            if car.carPositionX > canvasXSize + canvasExtension:
                car.carPositionX = 0 - canvasExtension
                self.canvas.move(car.carRectangle, -canvasXSize - (2 * canvasExtension), car.carVelocityY)
                if (car.carSensor.radius > 0):
                    self.canvas.move(car.carSensor.sensorCircle, -canvasXSize - (2 * canvasExtension), car.carVelocityY)
            elif car.carPositionX < 0 - canvasExtension:
                car.carPositionX = canvasXSize + canvasExtension
                self.canvas.move(car.carRectangle, car.carPositionX + canvasExtension, car.carVelocityY)
                if (car.carSensor.radius > 0):
                    self.canvas.move(car.carSensor.sensorCircle, car.carPositionX, car.carVelocityY)

            if car.carPositionY > canvasYSize + canvasExtension:
                car.carPositionY = 0 - canvasExtension
                self.canvas.move(car.carRectangle, car.carVelocityX, -canvasYSize - (2 * canvasExtension))
                if (car.carSensor.radius > 0):
                    self.canvas.move(car.carSensor.sensorCircle, car.carVelocityX, -canvasYSize - (2 * canvasExtension))
            elif car.carPositionY < 0 - canvasExtension:
                car.carPositionY = canvasYSize + canvasExtension
                self.canvas.move(car.carRectangle, car.carVelocityX, car.carPositionY + canvasExtension)
                if (car.carSensor.radius > 0):
                    self.canvas.move(car.carSensor.sensorCircle, car.carVelocityX, car.carPositionY)

        # updates the coordinates of the cars
        self.trailingCoords = self.canvas.coords(self.carList[0].carRectangle)
        self.leadingCoords = self.canvas.coords(self.carList[1].carRectangle)

        # runs the update label variables by running the function
        self.update_label_variables()

        # Loops over itself every .1 seconds.
        self.canvas.after(screenRefreshRate, self.move_cars)

# runs everything
def run():

    root2 = Tk()
    root2.geometry('400x200')

    inputScreen = InputScreen(root2)

    root2.mainloop()

    root = Tk()
    root.geometry('1500x800')

    canvas = ScreenCanvas(root)

    root.mainloop()

run()