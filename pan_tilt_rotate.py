import serial
import pygame
import cv2
import requests
from datetime import timedelta, datetime as dt

#### Dados iniciais ####

url_droidcam = 'http://192.168.1.4:4747'
porta_serial = '/dev/ttyACM0'

intervalo_autofoco_continuo = 2 # Em segundos
intervalo_zoom_continuo = 125000 # Em microssegundos

autofoco_continuo_ativado = False
zoom_acionado = False

fonte = cv2.FONT_HERSHEY_COMPLEX_SMALL
x_texto = 20
y_texto = 65
cor_texto = (0,0,255) # Azul, verde, vermelho

#### Definições de funções ####

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


def SetMultipleTargets(num_targets, first_channel, targets):
    global ser

    serialBytes = [0, 0, 0]

    serialBytes[0] = 0x9f
    serialBytes[1] = num_targets
    serialBytes[2] = first_channel
    
    for i in range(0, num_targets):
        target = int(targets[i] * 4)        
        bytesTarget = [0, 0]
        bytesTarget[0] = target & 0x7f
        bytesTarget[1] = (target >> 7) & 0x7f

        serialBytes.extend(bytesTarget)

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



def printPosicoesGravadas():
    global texto
    global textos_posicoes
    print("=============")
    print(texto)
    for i in range(0, len(textos_posicoes)):
        if textos_posicoes[i] != '':
            print(textos_posicoes[i])
        else:
            print("")


############################
#### Programa principal ####
############################


droidcam_led_toggle = url_droidcam+'/cam/1/led_toggle'
droidcam_fpslimit = url_droidcam+'/cam/1/fpslimit'
droidcam_zoomout = url_droidcam+'/cam/1/zoomout'
droidcam_zoomin = url_droidcam+'/cam/1/zoomin'
droidcam_autofocus = url_droidcam+'/cam/1/af'

droidcam_comando_zoom = ''

tempo_inicio_autofoco_continuo = 0
tempo_inicio_mudanca_zoom = 0

# Cria o objeto de captura de vídeo
video_captura = cv2.VideoCapture(url_droidcam+'/video')

video_habilitado = not (video_captura is None) and video_captura.isOpened()

if not video_habilitado:
    print("Câmera não disponível.")

posicoes_memo = [[999,999,999,0],
                 [999,999,999,0],
                 [999,999,999,0],
                 [999,999,999,0],
                 [999,999,999,0],
                 [999,999,999,0]]

gravacao_habilitada = False

fixarPosicao = False

pygame.init()
pygame.joystick.init()

ser = serial.Serial(porta_serial)

if ser.isOpen():
    print("Porta "+ser.name+" está aberta.")
else:
    print("Porta "+ser.name+" está fechada.")

ang_azimute = 0
ang_elevacao = 0
ang_rotacao = 0

texto = 'Gravacao habilitada'
textos_posicoes = ['',
                   '',
                   '',
                   '',
                   '',
                   '']
encerrar = False

while not encerrar:
    
    ### Tratamento do vídeo ###    
    if video_habilitado:
        # Captura um quadro da câmera
        ret, frame = video_captura.read()
        
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        #frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        if gravacao_habilitada:
            y_t = y_texto
            cv2.putText(frame, texto, (x_texto,y_t), fonte, 1,cor_texto,1,cv2.LINE_AA)
            
            for j in range(0,6):
                y_t = y_t + 20
                if textos_posicoes[j] != '':
                    cv2.putText(frame, textos_posicoes[j], (x_texto,y_t), fonte, 1,cor_texto,1,cv2.LINE_AA)
                
        
        # Mostra um quadro da câmera na janela
        cv2.imshow("Video", frame)

        k = cv2.waitKey(30) & 0xff

        if k != 255:
            if k == 27: # tecla esc
                break
            elif k == ord('L') or k == ord('l'): # L ou l
                requests.get(droidcam_led_toggle)
                print("Acionamento do LED da câmera")
            elif k == ord('F') or k == ord('f'): # F ou f
                requests.get(droidcam_fpslimit)
                print('Acionamento de limite de fps (frame por segundo)')
            elif k == ord('-'): # - (menos)
                r = requests.get(droidcam_zoomout)
                print("Diminuindo zoom")
                #print(r.content)
            elif k == ord('+'): # + (mais)
                r = requests.get(droidcam_zoomin)
                print("Aumentando zoom")
                #print(r.content)
            elif k == ord('A') or k == ord('a'): # A ou a para autofoco contínuo
                r = requests.get(droidcam_autofocus)
                autofoco_continuo_ativado = not autofoco_continuo_ativado
                tempo_inicio_autofoco_continuo = dt.utcnow()
                if autofoco_continuo_ativado:
                    print("Autofoco contínuo ativado")
                else:
                    print("Autofoco contínuo desativado")


    ### Tratamento de eventos temporizados ###

    if autofoco_continuo_ativado:
        if (dt.utcnow() - tempo_inicio_autofoco_continuo).total_seconds() >= intervalo_autofoco_continuo:
            requests.get(droidcam_autofocus)
            tempo_inicio_autofoco_continuo = dt.utcnow()

    if zoom_acionado:
        if (dt.utcnow() - tempo_inicio_mudanca_zoom)/timedelta(microseconds = 1) >= intervalo_zoom_continuo:
            requests.get(droidcam_comando_zoom)
            tempo_inicio_mudanca_zoom = dt.utcnow()
        

    ### Tratamento do joystick ###
            
    joystick_count = pygame.joystick.get_count()

    if (joystick_count == 0):
        print("Joystick não detectado.")
        if not video_habilitado:
            encerrar = True
    else:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        valor_eixo_azimute = joystick.get_axis(3)
        valor_eixo_elevacao = joystick.get_axis(1)
        valor_eixo_rotacao = joystick.get_axis(0)
        
        if not fixarPosicao:
            ang_azimute = fj(valor_eixo_azimute)
            ang_elevacao = gj(valor_eixo_elevacao)
            ang_rotacao = hj(valor_eixo_rotacao)

        for event in pygame.event.get():
            if event.type == pygame.JOYHATMOTION:
                chapeu = joystick.get_hat(0)

                x, y = chapeu
                
                if (y == 1):
                    r = requests.get(droidcam_zoomin)
                    droidcam_comando_zoom = droidcam_zoomin
                    tempo_inicio_mudanca_zoom = dt.utcnow()
                    zoom_acionado = True
                    print("Aumentando zoom")
                elif (y == -1):
                    r = requests.get(droidcam_zoomout)
                    droidcam_comando_zoom = droidcam_zoomout
                    tempo_inicio_mudanca_zoom = dt.utcnow()
                    zoom_acionado = True
                    print("Diminuindo zoom")
                else:
                    droidcam_comando_zoom = ''
                    zoom_acionado = False
                    
                
            if event.type == pygame.JOYBUTTONDOWN:
                print("Botão do joystick pressionado.")
                gatilho = joystick.get_button(0)
                botao_polegar = joystick.get_button(1)
                botao3 = joystick.get_button(2)
                botao4 = joystick.get_button(3)
                botao5 = joystick.get_button(4)
                botao6 = joystick.get_button(5)
                
                if gatilho == 1:
                    fixarPosicao = not fixarPosicao

                if botao_polegar == 1:
                    gravacao_habilitada = not gravacao_habilitada
                    texto = 'Gravacao habilitada'
                    if not video_habilitado and gravacao_habilitada:
                        printPosicoesGravadas()
                    
                if botao3 == 1:
                    requests.get(droidcam_led_toggle)
                    print("Acionamento do LED da câmera")

                if botao4 == 1:
                    requests.get(droidcam_fpslimit)
                    print('Acionamento de limite de fps (frame por segundo)')

                if botao5 == 1:
                    r = requests.get(droidcam_autofocus)
                    autofoco_continuo_ativado = not autofoco_continuo_ativado
                    tempo_inicio_autofoco_continuo = dt.utcnow()
                    if autofoco_continuo_ativado:
                        print("Autofoco contínuo ativado")
                    else:
                        print("Autofoco contínuo desativado")

                if botao6 == 1:
                    print("Fechando...")
                    encerrar = True
                    break
                
                if gravacao_habilitada:
                    for i in range(6, 11+1):
                        botao_pos = joystick.get_button(i)

                        if botao_pos == 1:
                            posicoes_memo[i-6][0] = ang_azimute
                            posicoes_memo[i-6][1] = ang_elevacao
                            posicoes_memo[i-6][2] = ang_rotacao

                            if posicoes_memo[i-6][3] == 0:
                                posicoes_memo[i-6][3] = 1
                                textos_posicoes[i-6] = str(i+1)+": ("\
                                                       +str(round(posicoes_memo[i-6][0], ndigits = 1))+', '\
                                                       +str(round(posicoes_memo[i-6][1], ndigits = 1))+', '\
                                                       +str(round(posicoes_memo[i-6][2], ndigits = 1))+')'
                            else:
                                posicoes_memo[i-6][3] = 0
                                textos_posicoes[i-6] = ''

                            if not video_habilitado:
                                printPosicoesGravadas()
                                
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


        ### Tratamento de acionamento dos servomotores ###
        '''
        SetTarget(6, f(ang_azimute))
        SetTarget(7, g(ang_elevacao))
        SetTarget(8, h(ang_rotacao))
        '''
        SetMultipleTargets(3, 6, [f(ang_azimute), g(ang_elevacao), h(ang_rotacao)])
        #print("az: "+str(ang_azimute)+" el: "+str(ang_elevacao)+ " rot: "+str(ang_rotacao))
        
pygame.quit()
ser.close()

if not (video_captura is None):
    video_captura.release()
cv2.destroyAllWindows()
