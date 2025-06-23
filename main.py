"""
CircuitPython LCD display demonstration
"""

import board
import busio
import time
from lcd.lcd import LCD, CursorMode
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface
import neopixel
import digitalio
import pwmio
import random as rand

# My own shuffle function, cuz circuitpython does not have random.shuffle for some reason
def shuffle(x):
    for i in range(len(x) - 1, 0, -1):
        j = rand.randint(0, i)
        x[i], x[j] = x[j], x[i]


# setup
i2c_scl = board.GP27
i2c_sda = board.GP26
i2c_address = 0x26

cols = 16
rows = 2

i2c = busio.I2C(scl=i2c_scl, sda=i2c_sda)
interface = I2CPCF8574Interface(i2c, i2c_address)
lcd = LCD(interface, num_rows=rows, num_cols=cols)
lcd.set_cursor_mode(CursorMode.HIDE)
lcd.clear()

arrowChar: bytearray = ([
    0b00000,
    0b00100,
    0b00010,
    0b11111,
    0b11111,
    0b00010,
    0b00100,
    0b00000
])

lcd.create_char(0, arrowChar)

leftLed = digitalio.DigitalInOut(board.GP5)
leftLed.direction = digitalio.Direction.OUTPUT
leftLed.value = False

rightLed = digitalio.DigitalInOut(board.GP4)
rightLed.direction = digitalio.Direction.OUTPUT
rightLed.value = False

leftButton = digitalio.DigitalInOut(board.GP2)
leftButton.direction = digitalio.Direction.INPUT
leftButton.pull = digitalio.Pull.UP

middleButton = digitalio.DigitalInOut(board.GP6)
middleButton.direction = digitalio.Direction.INPUT
middleButton.pull = digitalio.Pull.UP

rightButton = digitalio.DigitalInOut(board.GP3)
rightButton.direction = digitalio.Direction.INPUT
rightButton.pull = digitalio.Pull.UP





middleLed = neopixel.NeoPixel(board.GP16, 1, brightness=0.15)
middleLed[0] = 0
middleLed.show()

#Settings
use_middleLed:bool = True

# 0 - Dont
# 1 - Partially
# 2 - Fully
use_backlight: int = 1

use_leds: bool = True

use_buzzer: bool = True

# 0 - Game inicialization
# 1 - Settings
# 2 - Clock

faze: int = 0

# 0 - middleLed
# 1 - backlight
# 2 - leds
# 3 - buzzer
settingsFaze:int  = 0

middleButtonMillis: int = 0

# False: Left
# True: Right
playerOnMove: bool = False

timeLeft:float
timeRight:float

MiddleStatus = 0

timer: float

startingTime: int = 1
startingClock: int = 0

# self explanatory
def BuzzerAhhFunction(lenght, freq):
    buzzer = pwmio.PWMOut(board.GP7, duty_cycle=2 ** 15, frequency=freq, variable_frequency=True)
    time.sleep(lenght)
    buzzer.deinit()

# also self explanatory
def End(whoLost):
    lcd.clear()
    if not whoLost:
        lcd.print("LEFT PLAYER LOST ON TIME")
    else:
        lcd.print("RIGHT PLAYER LOST ON TIME")
    
    while True:
        leftLed.value = False
        rightLed.value = False
        buzzer = pwmio.PWMOut(board.GP7, duty_cycle=2 ** 15, frequency=500, variable_frequency=True)
        time.sleep(0.3)
        leftLed.value = True
        rightLed.value = True
        buzzer.deinit()
        time.sleep(1)
        leftLed.value = False
        rightLed.value = False
        buzzer = pwmio.PWMOut(board.GP7, duty_cycle=2 ** 15, frequency=1000, variable_frequency=True)
        time.sleep(0.3)
        leftLed.value = True
        rightLed.value = True
        buzzer.deinit()
        time.sleep(1)

# Prints the time left on the LCD
def TimePrint():
    

    zvisokLeft = int(timeLeft) % 60
    zvisokRight = int(timeRight) % 60

    lcd.set_cursor_pos(0,0)
    lcd.print(f"Left: {int(timeLeft / 60):02d}:{zvisokLeft:02d}")
    lcd.set_cursor_pos(1,0)
    lcd.print(f"Right: {int(timeRight / 60):02d}:{zvisokRight:02d}")

# The most lazy way to pause the game ;)
def Pause():
    global timer
    while not middleButton.value:
        pass
    lcd.clear()
    lcd.print("Paused the game.")
    while middleButton.value:
        pass
    while not middleButton.value:
        pass
    lcd.clear()
    timer = time.monotonic()

# Main game function
def Game():
    # This is still first-time setup
    global playerOnMove, timer, timeLeft, timeRight, startingTime, startingClock, use_backlight, use_buzzer, use_leds, use_middleLed, MiddleStatus
    
    timeLeft = startingTime * 60
    timeRight = startingTime * 60

    zvisokLeft = int(timeLeft) % 60
    zvisokRight = int(timeRight) % 60

    lcd.clear()
    lcd.print(f"Left: {int(timeLeft / 60):02d}:{zvisokLeft:02d}")
    lcd.set_cursor_pos(1,0)
    lcd.print(f"Right: {int(timeRight / 60):02d}:{zvisokRight:02d}")

    if use_leds:
        leftLed.value = True
        rightLed.value = True
    
    while leftButton.value is True and rightButton.value is True:
        pass

    if leftButton.value is False:
        print("IN HERE")
        if use_leds:
            rightLed.value = False
        playerOnMove = True
    elif rightButton.value is False:
        print("IN OTHER HERE")
        if use_leds:
            leftLed.value = False
        playerOnMove = False
    else:
        raise(RuntimeError())

    if use_buzzer:
        BuzzerAhhFunction(0.01, 2000)

    # Here the loop starts
    timer = time.monotonic()
    while timeLeft > 0 and timeRight > 0:
        while time.monotonic() - timer <= 1:

            # Main logic with the buttons
            if leftButton.value or rightButton.value:
                if leftButton.value is False and not playerOnMove:
                    playerOnMove = True
                    timeLeft += startingClock

                    if use_leds:
                        leftLed.value = True
                        rightLed.value = False
                    
                    if use_buzzer:
                        BuzzerAhhFunction(0.01, 2000)
                    
                    timeLeft -= (time.monotonic() - timer)
                    #timer = time.monotonic()
                    
                if rightButton.value is False and playerOnMove:
                    playerOnMove = False
                    timeRight += startingClock
                    if use_leds:
                        leftLed.value = False
                        rightLed.value = True

                    if use_buzzer:
                        BuzzerAhhFunction(0.01, 2000)
                    
                    timeRight -= (time.monotonic() - timer)
                    #timer = time.monotonic()
                    print("[DEBUG] Equals: " + str(time.monotonic() - timer))
                pass

            if not middleButton.value:
                Pause()
                pass
        
        if not playerOnMove:
            timeLeft -= (time.monotonic() - timer)
        else:
            timeRight -= (time.monotonic() - timer)

        if use_middleLed:
            if MiddleStatus == 0 and (timeLeft < 5*60 or timeRight < 5*60):
                MiddleStatus += 1
                middleLed[0] = (255,128,0)
                middleLed.show()
            elif MiddleStatus == 1 and (timeLeft < 60 or timeRight < 60):
                MiddleStatus += 1
                middleLed[0] = (255,0,0)
                middleLed.show()
        pass

        timer = time.monotonic()
        print("[DEBUG] Time update " + str(timer))
        TimePrint()

    # Checking if one of the players lost on time
    if timeLeft <= 0:
        End(False)
    else:
        End(True)



# Settings, I don't think I already finished this at 100%, but I may look into it in the future
def Setting():
    global use_middleLed,use_leds,use_buzzer,use_backlight,faze,settingsFaze,middleButtonMillis
    middleButtonMillis = time.monotonic()

    lcd.clear()
    lcd.print("Settings:")
    lcd.set_cursor_pos(1, 0)

    if settingsFaze == 0:
        lcd.print("Middle Led: ")
        lcd.print(str(int(use_middleLed)))
    elif settingsFaze == 1:
        lcd.print("Backlight: ")
        lcd.print(str(int(use_backlight)))
    elif settingsFaze == 2:
        lcd.print("L&R LED: ")
        lcd.print(str(int(use_leds)))
    else:
        lcd.print("Buzzer: ")
        lcd.print(str(int(use_buzzer)))

    while time.monotonic() - middleButtonMillis <= 3:
        # print(time.monotonic() - middleButtonMillis <= 3)
        smthhappened = False
        if middleButton.value is True:
            middleButtonMillis = time.monotonic()
        else:
            smthhappened = True
            while middleButton.value is False and time.monotonic() - middleButtonMillis <= 3:
                pass

            if time.monotonic() - middleButtonMillis > 3:
                lcd.clear()
                while middleButton.value is False:
                    pass
                break

            if settingsFaze == 0:
                use_middleLed = not use_middleLed
            elif settingsFaze == 1:
                use_backlight += 1
                if use_backlight >= 3:
                    use_backlight = 0
            elif settingsFaze == 2:
                use_leds = not use_leds
            else:
                use_buzzer = not use_buzzer

            pass

        if leftButton.value is False:
            smthhappened = True
            while leftButton.value is False:
                pass

            settingsFaze -= 1

            if settingsFaze <= -1:
                settingsFaze = 3

        if rightButton.value is False:
            smthhappened = True
            while rightButton.value is False:
                pass

            settingsFaze += 1

            if settingsFaze >= 4:
                settingsFaze = 0
        
        if smthhappened:
            lcd.clear()
            lcd.print("Settings:")
            lcd.set_cursor_pos(1, 0)

            if settingsFaze == 0:
                lcd.print("Middle Led: ")
                lcd.print(str(int(use_middleLed)))
            elif settingsFaze == 1:
                lcd.print("Backlight: ")
                lcd.print(str(int(use_backlight)))
            elif settingsFaze == 2:
                lcd.print("L&R LED: ")
                lcd.print(str(int(use_leds)))
            else:
                lcd.print("Buzzer: ")
                lcd.print(str(int(use_buzzer)))
    
    if use_backlight == 0:
        lcd.set_backlight(False)
    else:
        lcd.set_backlight(True)


# self explanatory -_-
def SetupLCD():
    global startingClock, startingTime
    lcd.set_cursor_pos(0,0)
    lcd.print("     MODE:     ")
    lcd.set_cursor_pos(1, 6)
    lcd.print(str(startingTime))
    lcd.print("|")
    lcd.print(str(startingClock))

# OK, don't ask why do I have setup here, and setuping again in Game(), but who cares :D...
def Setup():
    global middleButtonMillis,faze, use_buzzer, startingTime, startingClock, MiddleStatus
    middleButtonMillis = time.monotonic()
    lcd.clear()
    lcd.print("     MODE:     ")

    while True:

        if middleButton.value is True:
            middleButtonMillis = time.monotonic()
        else:
            while middleButton.value is False and time.monotonic() - middleButtonMillis <= 3:
                #print("HERE")
                pass
            
            if time.monotonic() - middleButtonMillis > 3:
                Setting()
            else:
                break

        

        if leftButton.value is False:
            while leftButton.value is False:
                pass

            startingTime -= 1

            if startingTime < 1:
                startingTime = 1

        if rightButton.value is False:
            while rightButton.value is False:
                pass

            startingTime += 1

            if startingTime > 30:
                startingTime = 30
        SetupLCD()

    while True:

        if middleButton.value is True:
            middleButtonMillis = time.monotonic()
        else:
            while middleButton.value is False and time.monotonic() - middleButtonMillis <= 3:
                #print("HERE2")
                pass
            
            if time.monotonic() - middleButtonMillis > 3:
                Setting()
            else:
                break

        

        if leftButton.value is False:
            while leftButton.value is False:
                pass

            startingClock -= 1

            if startingClock < 0:
                startingClock = 0

        if rightButton.value is False:
            while rightButton.value is False:
                pass

            startingClock += 1

            if startingClock > 30:
                startingClock = 30
    
        SetupLCD()

    if startingTime <= 1:
        MiddleStatus = 2
    elif startingTime <= 6:
        MiddleStatus = 1

    Game()

# Chess960 function, which generates a random chess960 position
def Chess960():
    lcd.clear()
    lcd.print("   Chess960??   ")
    lcd.set_cursor_pos(1, 0)
    lcd.print("     Yes/No     ")
    while leftButton.value and rightButton.value:
        pass


    if not rightButton.value:
        lcd.clear()
        return
    else:
        lcd.clear()
        lcd.print(" Loading pos... ")

        """ Code "borrowed" from https://github.com/ElijahArsenault/chess960-position-generator, and modified a bit to fit 
        in this project. 

        Thanks Elijah Arsenault! """


        # Assigning characters to piece variables
        queen = "Q"
        king = "K"
        rook1 = "R"
        rook2 = "r"
        bishop_light = "B"
        bishop_dark = "b"
        knight1 = "n"
        knight2 = "N"


        # Loop to keep trying combinations until a legal position is reached
        while True:
            position = [queen, king, rook1, rook2, bishop_light, bishop_dark, knight1, knight2]
            shuffle(position)
            # To insure bishops are on opposite colors
            if (position.index(bishop_dark) - position.index(bishop_light)) % 2 == 0:
                continue
            # Checks if king is between rooks
            elif position.index(rook1) > position.index(king) and position.index(rook2) > position.index(king):
                continue
            elif position.index(rook1) < position.index(king) and position.index(rook2) < position.index(king):
                continue
            else:
                break

        position = str(position)
        lcd.clear()
        lcd.print("Chess960 pos:")
        lcd.set_cursor_pos(1, 0)
        lcd.print(position.strip("[").strip("]").replace("'", "").replace(",", ""))
        while middleButton.value:
            pass
        # There are 100% better fixes than this, but if it works, it works
        while not middleButton.value:
            pass







Chess960()
Setup()

# type: ignore
