import serial
import time

def SetTarget(channel, target):
    global ser
    
    target = int(target * 4)

    print(target)
    
    serialBytes = [0,0,0,0]
    serialBytes[0] = 0x84
    serialBytes[1] = channel
    serialBytes[2] = target & 0x7f
    serialBytes[3] = (target >> 7) & 0x7f

    ser.write(serialBytes)


def calculaAeB(x1,y1,x2,y2):
    a = (y2 - y1)/(x2-x1)
    b = y2 - a * x2

    print("a = "+str(a))
    print("b = "+str(b))


'''
A(75, 2080)
B(-75, 755)
C(0, 1371)
Azimute (pan)
'''
def f(x):
    if(x > 0):
        a = 8.833333333333334
        b = 1417.5
    else:
        a = 8.213333333333333
        b = 1371.0

    return a * x + b

'''
A(90, 2240)
B(-90, 640)
Elevação (tilt)
'''
def g(x):
    a = 8.88888888888889
    b = 1440.0
    
    return a * x + b

'''
A(90, 2272)
B(-90, 720)
Rotação (rotate)
'''
def h(x):
    a = 8.622222222222222
    b = 1496.0
    
    return a * x + b


# Programa principal

ser = serial.Serial('/dev/ttyACM0')

SetTarget(6, f(0))
SetTarget(7, g(0))
SetTarget(8, h(0))

'''
posicoes = [656, 2416, 656, 2416, 656, 1536]
canal = 11


while True:
    for i in range(0, 6):
        SetTarget(canal, posicoes[i])
        print(posicoes[i])
        time.sleep(2)
    
ser.close()
'''
