import serial
import time
import pygame
import cv2

def SetTarget(channel, target):
    global ser
    
    target = int(target * 4)

    #print(target)
    
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

url_droidcam = 'http://192.168.1.2:4747'
# Cria o objeto de captura de vídeo
video_captura = cv2.VideoCapture(url_droidcam+'/video')

posicoes_memo = [[999,999,999,0],
                 [999,999,999,0],
                 [999,999,999,0],
                 [999,999,999,0],
                 [999,999,999,0],
                 [999,999,999,0]]

gravacao_habilitada = False

fixarPosicao = False # False ou True

pygame.init()
pygame.joystick.init()

ser = serial.Serial('/dev/ttyACM0')

if ser.isOpen():
    print("Porta "+ser.name+" está aberta.")
else:
    print("Porta "+ser.name+" está fechada.")

ang_azimute = 0
ang_elevacao = 0
ang_rotacao = 0

while True:
    # Captura um quadro da câmera
    ret, frame = video_captura.read()
    
    #frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    # Mostra um quadro da câmera na janela
    cv2.imshow("Video", frame)

    k = cv2.waitKey(30) & 0xff

    if k != 255:
        if k == 27: # tecla esc
            break
    
    joystick_count = pygame.joystick.get_count()

    if (joystick_count == 0):
        print("Joystick não detectado.")
    else:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        valor_eixo_azimute = joystick.get_axis(3)
        valor_eixo_elevacao = joystick.get_axis(1)
        valor_eixo_rotacao = joystick.get_axis(0)
        # Converter o valor para ângulo
        if not fixarPosicao:
            ang_azimute = fj(valor_eixo_azimute)
            ang_elevacao = gj(valor_eixo_elevacao)
            ang_rotacao = hj(valor_eixo_rotacao)

        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                print("Botão do joystick pressionado.")
                joystick = pygame.joystick.Joystick(0)
                gatilho = joystick.get_button(0)
                botao_polegar = joystick.get_button(1)
                # Fazer algo com o gatilho
                if gatilho == 1:
                    fixarPosicao = not fixarPosicao

                if botao_polegar == 1:
                    gravacao_habilitada = not gravacao_habilitada

                if gravacao_habilitada:
                    for i in range(6, 11+1):
                        botao_pos = joystick.get_button(i)

                        if botao_pos == 1:
                            posicoes_memo[i-6][0] = ang_azimute
                            posicoes_memo[i-6][1] = ang_elevacao
                            posicoes_memo[i-6][2] = ang_rotacao

                            if posicoes_memo[i-6][3] == 0:
                                posicoes_memo[i-6][3] = 1
                            else:
                                posicoes_memo[i-6][3] = 0
                else: # gravação não habilitada
                    for i in range(6, 11+1):
                        botao_pos = joystick.get_button(i)

                        if botao_pos == 1:
                            if posicoes_memo[i-6][3] == 1:
                                ang_azimute = posicoes_memo[i-6][0]
                                ang_elevacao = posicoes_memo[i-6][1]
                                ang_rotacao = posicoes_memo[i-6][2]
                                fixarPosicao = True
                    
            elif event.type == pygame.JOYBUTTONUP:
                print("Botão do joystick liberado.")
    
        SetTarget(6, f(ang_azimute))
        SetTarget(7, g(ang_elevacao))
        SetTarget(8, h(ang_rotacao))            
        print("az: "+str(ang_azimute)+" el: "+str(ang_elevacao)+ " rot: "+str(ang_rotacao))
        
pygame.quit()
ser.close()

video_captura.release()
cv2.destroyAllWindows()
