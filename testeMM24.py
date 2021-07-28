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

ser = serial.Serial('COM7')

posicoes = [656, 2416, 656, 2416, 656, 1536]
canal = 11

while True:
    for i in range(0, 6):
        SetTarget(canal, posicoes[i])
        print(posicoes[i])
        time.sleep(2)
    
ser.close()
