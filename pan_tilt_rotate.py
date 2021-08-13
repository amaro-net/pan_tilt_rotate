import serial
import time
import pygame

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

'''
A(-1, 75)
B(1, -75)
'''
def fj(x):
    a = -75.0
    b = 0.0

    return a * x + b

'''
A(-1, -90)
B(1, 90)
'''
def gj(x):
    a = 90.0
    b = 0.0
    
    return a * x + b

'''
A(-1, -90)
B(1, 90)
'''
def hj(x):
    a = 90.0
    b = 0.0
    
    return a * x + b


# Programa principal

pygame.init()
pygame.joystick.init()

ser = serial.Serial('/dev/ttyACM0')

while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            print("Botão do joystick pressionado.")
        elif event.type == pygame.JOYBUTTONUP:
            print("Botão do joystick liberado.")

    joystick_count = pygame.joystick.get_count()
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        valor_eixo_azimute = joystick.get_axis(3)
        valor_eixo_elevacao = joystick.get_axis(1)
        valor_eixo_rotacao = joystick.get_axis(0)
        # Converter o valor para ângulo
        ang_azimute = fj(valor_eixo_azimute)
        ang_elevacao = gj(valor_eixo_elevacao)
        ang_rotacao = hj(valor_eixo_rotacao)

        SetTarget(6, f(ang_azimute))
        SetTarget(7, g(ang_elevacao))
        SetTarget(8, h(ang_rotacao))
        
        print("az: "+str(ang_azimute)+" el: "+str(ang_elevacao)+ "rot: "+str(ang_rotacao))
        
        gatilho = joystick.get_button(0)
        # Fazer algo com o gatilho
        #print("gatilho: "+str(gatilho))
            
pygame.quit()
ser.close()
