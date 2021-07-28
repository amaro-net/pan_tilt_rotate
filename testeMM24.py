import serial
import time


def SetTarget(channel, target):
    global ser
    
    target = target * 4

    serialBytes = [0,0,0,0]
    serialBytes[0] = 0x84
    serialBytes[1] = channel
    serialBytes[2] = target & 0x7f
    serialBytes[3] = (target >> 7) & 0x7f

    ser.write(serialBytes)

# Programa principal

ser = serial.Serial('/dev/ttyACM0')

posicoes = [1000, 2000, 1000, 2000, 1000, 1500]
canal = 2

for i in range(0, 6):
    SetTarget(2, posicoes[i])
    print(posicoes[i])
    time.sleep(1)
    
ser.close()
