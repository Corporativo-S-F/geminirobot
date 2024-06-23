# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# NOTE: this example requires PyAudio because it uses the Microphone class

import json
import requests
import re
import base64
import speech_recognition as sr
import subprocess
import pipes
import json
import apiai
import time
import yaml
import os
import wave
from multiprocessing import Process, Queue
import time
import cv2
import serial
import binascii
import QboCmd
import sys
import time

class QBOtalk:
    def __init__(self):
        config = yaml.safe_load(open("/home/pi/Documents/config.yml"))
        CLIENT_ACCESS_TOKEN = config["tokenAPIai"]
        print("TOKEN: " + CLIENT_ACCESS_TOKEN)
#       You can enter your token in the next line
#        CLIENT_ACCESS_TOKEN = 'YOUR_TOKEN'
        # obtain audio from the microphone
        self.r = sr.Recognizer()
        self.ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
        self.Response = "hello"
        self.GetResponse = False
        self.GetAudio = False
        self.strAudio = ""
        self.config = config

        for i, mic_name in enumerate (sr.Microphone.list_microphone_names()):
            if(mic_name == "dmicQBO_sv"):
                self.m = sr.Microphone(i)
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)

    def Decode(self, audio):
        try:
            if self.config.get("language") == "spanish":
                str_audio = self.r.recognize_google(audio, language="es-ES")
            else:
                str_audio = self.r.recognize_google(audio)

            print("Audio detectado:" + str_audio)
            GEMINIAPI = self.config.get("geminiAPI")
            response = geminiai(str_audio,GEMINIAPI)
            print(response)

        except sr.UnknowValueError:
                print("Unknow error")
        except sr.RequestError as e:
                print ("Error on Speech Recognition service")

        return response

    def downsampleWav(self, src):
        print("src: " + src)
        s_read = wave.open(src, 'r')
        print("frameRate: " + s_read.getframerate())
        s_read.setframerate(16000)
        print("frameRate_2: " + s_read.getframerate())
        return


    def downsampleWave_2(self, src, dst, inrate, outrate, inchannels, outchannels):
        if not os.path.exists(src):
            print('Source not found!')
            return False

        if not os.path.exists(os.path.dirname(dst)):
            print("dst: " + dst)
            print("path: " + os.path.dirname(dst))
            os.makedirs(os.path.dirname(dst))

        try:
            s_read = wave.open(src, 'r')
            s_write = wave.open(dst, 'w')
        except:
            print('Failed to open files!')
            return False

        n_frames = s_read.getnframes()
        data = s_read.readframes(n_frames)

        try:
            converted = audioop.ratecv(data, 2, inchannels, inrate, outrate, None)
            if outchannels == 1:
                converted = audioop.tomono(converted[0], 2, 1, 0)
        except:
            print('Failed to downsample wav')
            return False

        try:
            s_write.setparams((outchannels, 2, outrate, 0, 'NONE', 'Uncompressed'))
            s_write.writeframes(converted)
        except:
            print('Failed to write wav')
            return False

        try:
            s_read.close()
            s_write.close()
        except:
            print('Failed to close wav files')
            return False

        return True

    def SpeechText(self, text_to_speech):
        self.config = yaml.safe_load(open("/home/pi/Documents/config.yml"))
        print("config:" + str(self.config))

        if (self.config["language"] == "spanish"):
                speak = "pico2wave -l \"es-ES\" -w /home/pi/Documents/pico2wave.wav \"<volume level='" + str(self.config["volume"]) + "'>" + text_to_speech + "\" && aplay -D convertQBO /home/pi/Documents/pico2wave.wav"
#               speak = "pico2wave -l \"es-ES\" -w /var/local/pico2wave.wav \"" + text_to_speech + "\" | aplay -D convertQBO"
        else:
                speak = "pico2wave -l \"en-US\" -w /home/pi/Documents/pico2wave.wav \"<volume level='" + str(self.config["volume"]) + "'>" + text_to_speech + "\" && aplay -D convertQBO /home/pi/Documents/pico2wave.wav"
#               speak = "pico2wave -l \"en-US\" -w /var/local/pico2wave.wav \"" + text_to_speech + "\" | aplay -D convertQBO"

#        speak = "espeak -ven+f3 \"" + text_to_speech + "\" --stdout  | aplay -D convertQBO"

#       tts = gTTS(text = text_to_speech, lang = 'en')
#       tts.save("/home/pi/Documents/say.wav")
#       self.downsampleWav("/home/pi/Documents/say.wav")
#       self.downsampleWav("./say.wav", "./say16.wav", 8000, 16000, 1, 1)
#       downsampleWav("say.wav", "say16.wav")
#       os.system("aplay -D convertQBO say16.wav")
# hasta aqui

        print("QBOtalk: " + speak)
        result = subprocess.call(speak, shell = True)


    def SpeechText_2(self, text_to_speech, text_spain):
        self.config = yaml.safe_load(open("/home/pi/Documents/config.yml"))
        print("config:" + str(self.config))
        if (self.config["language"] == "spanish"):
                speak = "pico2wave -l \"es-ES\" -w /home/pi/Documents/pico2wave.wav \"<volume level='" + str(self.config["volume"]) + "'>" + text_spain + "\" && aplay -D convertQBO /home/pi/Documents/pico2wave.wav"
        else:
                speak = "pico2wave -l \"en-US\" -w /home/pi/Documents/pico2wave.wav \"<volume level='" + str(self.config["volume"]) + "'>" + text_to_speech + "\" && aplay -D convertQBO /home/pi/Documents/pico2wave.wav"

        print("QBOtalk_2: " + speak)
        result = subprocess.call(speak, shell = True)

    def callback(self, recognizer, audio):
        try:
            self.Response = self.Decode(audio)
            self.GetResponse = True
            print("Google say ")
            #self.SpeechText(self.Response)
        except:
            return

    def callback_listen(self, recognizer, audio):
        print("callback listen")
        try:
            #strSpanish = self.r.recognize_google(audio,language="es-ES")
#           with open("microphone-results.wav", "wb") as f:
#               f.write(audio.get_wav_data())
            if (self.config["language"] == "spanish"):
                    self.strAudio = self.r.recognize_google(audio, language="es-ES")
            else:
                    self.strAudio = self.r.recognize_google(audio)

            self.strAudio = self.r.recognize_google(audio)
            self.GetAudio = True
            print("listen: " + self.strAudio)
            #print("listenSpanish: ", strSpanish)
            #self.SpeechText(self.Response)
        except:
            print("callback listen exception")
            self.strAudio = ""
            return

    def Start(self):
        print("Say something!")
        self.r.operation_timeout = 10
        with self.m as source:
            audio = self.r.listen(source = source, timeout = 2)

        # recognize speech using Google Speech Recognition

        Response = self.Decode(audio)
        self.SpeechText(Response)

    def StartBack(self):
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)

        print("start background listening")

        return self.r.listen_in_background(self.m, self.callback)

    def StartBackListen(self):
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)

        print("start background only listening")

        return self.r.listen_in_background(self.m, self.callback_listen)

############################################################################
########## gemini script
############################################################################
#================================================================================
# Historial de chat
chat_history = []

def cargar_historial(archivo):
    global chat_history
    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            for line in file:
                if ': ' in line:
                    role, text = line.strip().split(': ', 1)
                    chat_history.append({"role": role, "parts": [{"text": text}]})
    except FileNotFoundError:
        pass  # El archivo no existe, así que no hay nada que cargar

def guardar_historial(archivo):
    with open(archivo, 'w', encoding='utf-8') as file:
        for entry in chat_history:
            role = entry["role"]
            text = entry["parts"][0]["text"]
            file.write(role + ":" + text + "\n")

def leer_historial(archivo):
    with open(archivo, 'r', encoding='utf-8') as file:
        return file.read()

def eliminar_historial(archivo):
    with open(archivo, 'w', encoding='utf-8') as file:
        file.write('')  # Escribir una cadena vacía al archivo para eliminar su contenido

def eliminar_acentos(texto):
    acentos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
    }
    for acento, reemplazo in acentos.items():
        texto = texto.replace(acento, reemplazo)
    return texto

# Función para limpiar el texto
def limpiar_texto(texto):
    # Reemplazar letras con acentos por sus equivalentes sin acento
    texto = eliminar_acentos(texto)
    # Eliminar saltos de línea
    texto = texto.replace('\n', ' ')
    # Definir la expresión regular para mantener solo letras, espacios y los caracteres permitidos
    caracteres_permitidos = r'[^a-zA-Z\s.,!?¡¿]'
    # Usar la expresión regular para reemplazar los caracteres no deseados con una cadena vacía
    texto_limpio = re.sub(caracteres_permitidos, '', texto)
    # Eliminar emojis
    texto_limpio = re.sub(r'[^\w\s,.!?¡¿]', '', texto_limpio)
    return texto_limpio


def procesar_solicitud(text, key, archivo_historial, image=False):
    if image:
        with open("image.jpg", "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        img = {
                "inline_data": {
                    "mime_type":"image/jpeg",
                    "data": encoded_image
                }
            }
    else :
        img = None

    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=' + key
    headers = {'Content-Type': 'application/json'}

    # Cargar historial de chat
    cargar_historial(archivo_historial)

    # Agregar nueva entrada al historial de chat
    new_entry = {
        "role": "user",
        "parts": [
            {
                "text": text
            },
            *([img] if img else [])
        ]
    }
    chat_history.append(new_entry)

    data = {
        "contents": [
            {"role": "user",
                "parts": [
                    {
                        "text": "Eres un asistente robot llamado BroxStar, formas parte de Broxel una empresa en México, cuando pregunten tu nombre eres BroxStar de Broxel, no digas nada acerca de google, en lugar genera una respuesta orientada a ser perteneciente a Broxel. Si te preguntan por Broxel respondes lo siguiente: Broxel es una empresa líder en la industria FinTech en México. Se especializa en la innovación de soluciones a medida en medios de pago basadas en tecnología financiera. Nuestro objetivo es crear ecosistemas financieros eficientes, ágiles y disruptivos, disponibles en todo momento y en cualquier parte del mundo. En Broxel, estamos comprometidos con la innovación y la creación de soluciones que mejoren la vida de nuestros clientes. Trabajamos con un equipo de expertos en tecnología financiera para desarrollar productos y servicios que sean fáciles de usar, seguros y confiables. ¿Te gustaría saber más sobre algún producto o servicio en específico de Broxel?, uno de tus objetivos es conocer todo acerca del usuario, nombre, apellido, edad etc, el cual estaras obteniendo conforme la conversación se este generando, si alguien te pregunta algo sobre ti, al finalizar la respuesta pregunta acerca de esa persona para obtener información, el chat completo se esta guardando directamente en tu memoria local, estas funcionando en un robot que usa un entorno linux, posees dos camaras de video las cuales te permiten tomar video y fotografia y analizar los que observas, eres un robot que esta al servicio de las personas del corproativo y por lo tanto debes ser muy amigable y platicador, con respuestas creativas e informativas, cuando te pregunten acerca de acciones que tengan que ver con ver, analizar imagenes y no tengas información, responde unicamente sin agregar mas a la respuesta: 'capturando imagen', es importante que no incluyas texto despues de este comando"
                    }
                ]
            },
            {"role": "model",
                "parts": [
                    {
                        "text": "entendido"
                    }
                ]
            },
            *chat_history
        ],
        "generationConfig": {
            "stopSequences": ["Title"],
            "temperature": 1.0,
            "maxOutputTokens": 200,
            "topP": 0.8,
            "topK": 10
        },
    }

    json_data = json.dumps(data)
    response = requests.post(url, headers=headers, data=json_data)

    if response.status_code == 200:
        response_json = response.json()
        return response_json
    else:
        print("Error en el request. Status code: ", response.status_code)
        return None

def manejar_respuesta(response_json, archivo_historial):
    global chat_history
    
    if "candidates" in response_json and len(response_json["candidates"]) > 0:
        content_parts = response_json["candidates"][0]["content"]["parts"]
        if len(content_parts) > 0:
            generated_text = content_parts[0]["text"]
            clean_text = limpiar_texto(generated_text)
            # Agregar respuesta del modelo al historial de chat
            model_response = {
                "role": "model",
                "parts": [
                    {
                        "text": clean_text
                    }
                ]
            }
            chat_history.append(model_response)

            # Guardar el historial de chat en un archivo de texto
            guardar_historial(archivo_historial)

            return clean_text
    else:
        print("Failed to get response. Status code: ", response.status_code)
        print(response.text)
        return "No puedo responder ahora, intenta nuevamente"


def geminiai(text, key, archivo_historial):
    response_json = procesar_solicitud(text, key, archivo_historial)
    if "capturando imagen" in response_json['candidates'][0]['content']['parts'][0]['text']:
        response_json = procesar_solicitud(text, key, archivo_historial, True)

    if response_json:
        return manejar_respuesta(response_json, archivo_historial)
    else:
        return "Error"

archivo_historial = 'historial_chat.txt'



###########################################################################
############## main controlers
###########################################################################
Qbo = QBOtalk.QBOtalk()
Kpx = 1
Kpy = 1
Ksp = 40

## Head X and Y angle limits

Xmax = 725
Xmin = 290
Ymax = 550
Ymin = 420

## Initial Head position

Xcoor = 511
Ycoor = 450
Facedet = 0

## Time head wait turned
touch_wait = 2

no_face_tm = time.time()
face_det_tm = time.time()
touch_tm = 0
touch_samp = time.time()
qbo_touch = 0
touch_det = False
Listenig = False
listen_thd = 0

Step_x = ([2, 5, 10])
Step_y = ([1, 3, 7])

if len(sys.argv) > 1:
        port = sys.argv[1]
else:
        port = '/dev/serial0'

try:
        # Open serial port
        ser = serial.Serial(port, baudrate=115200, bytesize = serial.EIGHTBITS, stopbits = serial.STOPBITS_ONE, parity = serial.PARITY_NONE, rtscts = False, dsrdtr =False, timeout = 0)
        print("Open serial port sucessfully.")
        print(ser.name)
except:
        print("Error opening serial port.")
        sys.exit()


QBO = QboCmd.Controller(ser)

QBO.SetServo(1, Xcoor, 100)
QBO.SetServo(2, Ycoor, 100)
QBO.SetNoseColor(0)       #Off QBO nose brigth

webcam = cv2.VideoCapture(0)                            # Get ready to start getting images from the webcam
webcam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)         # I have found this to be about the highest-
webcam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)        #       resolution you'll want to attempt on the pi

frontalface = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")         # frontal face pattern detection
profileface = cv2.CascadeClassifier("haarcascade_profileface.xml")              # side face pattern detection

face = [0,0,0,0]        # This will hold the array that OpenCV returns when it finds a face: (makes a rectangle)
Cface = [0,0]           # Center of the face: a point calculated from the above variable
lastface = 0            # int 1-3 used to speed up detection. The script is looking for a right profile face,-
                        # a left profile face, or a frontal face; rather than searching for all three every time,-
                        # it uses this variable to remember which is last saw: and looks for that again. If it-
                        # doesn't find it, it's set back to zero and on the next loop it will search for all three.-
                        # This basically tripples the detect time so long as the face hasn't moved much.

time.sleep(1)           # Wait for them to start

#====================================================================================================
def ServoHome():
        global Xcoor, Ycoor, touch_tm
        Xcoor = 511
        Ycoor = 450
        QBO.SetServo(1, Xcoor, 100)
        QBO.SetServo(2, Ycoor, 100)
        touch_tm = time.time()
        return

def CamLeft( distance, speed ):                # To move left, we are provided a distance to move and a speed to move.
        global Xcoor, Xmin, touch_tm
        Xcoor = Xcoor - Kpx * distance
        if Xcoor < Xmin:
                Xcoor = Xmin
        #print "LEFT:",distance, Xcoor, Ycoor
        QBO.SetServo(1, Xcoor, Ksp * speed)
        touch_tm = time.time()
        return
def CamRight(distance, speed):                   # Same logic as above
        global Xcoor, Xmax, touch_tm
        Xcoor = Xcoor + Kpx * distance
        if Xcoor > Xmax:
                Xcoor = Xmax
        #print "RIGHT:",distance, Xcoor, Ycoor
        QBO.SetServo(1, Xcoor, Ksp * speed)
        touch_tm = time.time()
        return
def CamDown(distance, speed):                   # Same logic as above
        global Ycoor, Ymax, touch_tm
        Ycoor = Ycoor + Kpy * distance
        if Ycoor > Ymax:
                Ycoor = Ymax
        #print "DOWN:",distance, Xcoor, Ycoor
        QBO.SetServo(2, Ycoor, Ksp * speed)
        touch_tm = time.time()
        return
def CamUp(distance, speed):                     # Same logic as above
        global Ycoor, Ymin, touch_tm
        Ycoor = Ycoor - Kpy * distance
        if Ycoor < Ymin:
                Ycoor = Ymin
        #print "UP:",distance, Xcoor,Ycoor
        QBO.SetServo(2, Ycoor, Ksp * speed)
        touch_tm = time.time()
        return


def WaitForSpeech():
        global Listenig, listen_thd
        if Listenig == False:
                return
        elif Qbo.GetResponse == True:
                listen_thd(wait_for_stop = True)
                Qbo.SpeechText(Qbo.Response)
                QBO.SetNoseColor(0)
                Qbo.GetResponse = False
                Listenig = False
        return
def WaitTouchMove():
        global Xcoor, Ycoor, touch_tm
        time.sleep(2)
        QBO.SetServo(1, Xcoor, 100)
        time.sleep(0.1)
        QBO.SetServo(2, Ycoor, 100)
        #time.sleep(1)
        touch_tm = time.time()
        return
#============================================================================================================

print(" Face tracking running.")
print(" QBO nose bright green when see your face")

Qbo.SpeechText("Sistema cargado")

touch_tm = time.time()

while True:
    faceFound = False       # This variable is set to true if, on THIS loop a face has already been found
                                # We search for a face three diffrent ways, and if we have found one already-
                                # there is no reason to keep looking.
    WaitForSpeech()

    if not faceFound:
        if lastface == 0 or lastface == 1:
            aframe = webcam.read()[1]       #       there seems to be an issue in OpenCV or V4L or my webcam-
            aframe = webcam.read()[1]       #       driver, I'm not sure which, but if you wait too long,
            aframe = webcam.read()[1]       #       the webcam consistantly gets exactly five frames behind-
            fface = frontalface.detectMultiScale(aframe,1.3,4,(cv2.cv.CV_HAAR_DO_CANNY_PRUNING + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH),(60,60))
            if fface != ():                 # if we found a frontal face...
                lastface = 1            # set lastface 1 (so next loop we will only look for a frontface)
                for f in fface:         # f in fface is an array with a rectangle representing a face
                    faceFound = True
                    face = f

    if not faceFound:                               # if we didnt find a face yet...
        if lastface == 0 or lastface == 2:      # only attempt it if we didn't find a face last loop or if-
            aframe = webcam.read()[1]       #       THIS method was the one who found it last loop
            aframe = webcam.read()[1]
            aframe = webcam.read()[1]       # again we grab some frames, things may have gotten stale-
            pfacer = profileface.detectMultiScale(aframe,1.3,4,(cv2.cv.CV_HAAR_DO_CANNY_PRUNING + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH),(80,80))

            if pfacer != ():                # if we found a profile face...
                lastface = 2
                for f in pfacer:
                    faceFound = True
                    face = f

    if not faceFound:               # if no face was found...-
        lastface = 0            #       the next loop needs to know
        face = [0,0,0,0]        # so that it doesn't think the face is still where it was last loop
        QBO.SetNoseColor(0)       #Off QBO nose brigth
        if Facedet != 0:
            Facedet = 0
            no_face_tm = time.time()
            #print "No face.!"
        elif(time.time() - no_face_tm > 10):
            ServoHome()
            Cface[0] = [0,0]
            no_face_tm = time.time()
    else:
        x,y,w,h = face
        Cface = [(w/2+x),(h/2+y)]       # we are given an x,y corner point and a width and height, we need the center
        #print str(Cface[0]) + "," + str(Cface[1])
        if Facedet == 0:
            if Listenig == False:
                    QBO.SetNoseColor(4)
            Facedet = 1
            face_det_tm = time.time()
            #print "Face detected.!"
        elif Listenig == False & (time.time() - face_det_tm > 2):
            face_det_tm = time.time()
            if Listenig == False:
                QBO.SetNoseColor(1)
                listen_thd = Qbo.StartBack()
                Listenig = True
        else :
            if Listenig:
                QBO.SetNoseColor(1)       # Set QBO nose blue
            else:
                QBO.SetNoseColor(4)

        if touch_det == False:
            if Cface[0] > 190:
                CamLeft(Step_x[0],1)
            if Cface[0] > 200:
                CamLeft(Step_x[1],2)
            if Cface[0] > 210:
                CamLeft(Step_x[2],3)
            if Cface[0] < 150:
                CamRight(Step_x[0],1)
            if Cface[0] < 140:
                CamRight(Step_x[1],2)
            if Cface[0] < 130:
                CamRight(Step_x[2],3)
            if Cface[1] > 150:
                CamDown(Step_y[0],1)
            if Cface[1] > 160:
                CamDown(Step_y[1],2)
            if Cface[1] > 170:
                CamDown(Step_y[2],3)

            if Cface[1] < 130:
                CamUp(Step_y[0],1)
            if Cface[1] < 100:
                CamUp(Step_y[1],2)
            if Cface[1] < 90:
                CamUp(Step_y[2],3)
    if time.time() -touch_samp > 0.5:
            qbo_touch = QBO.GetHeadCmd("GET_TOUCH", 0)
            if touch_tm == 0 and qbo_touch:
                if qbo_touch == [1]:
                    QBO.SetServo(1, Xmax - 25, 100)
                    time.sleep(0.1)
                    QBO.SetServo(2, Ymin - 5, 100)
                    WaitTouchMove()
                elif qbo_touch == [2]:
                    QBO.SetServo(2, Ymin - 5, 100)
                    WaitTouchMove()
                elif qbo_touch == [3]:
                    QBO.SetServo(1, Xmin + 25, 100)
                    time.sleep(0.1)
                    QBO.SetServo(2, Ymin - 5, 100)
                    WaitTouchMove()
    if touch_tm != 0 and time.time() - touch_tm > touch_wait:
        print("touch ready")
        touch_tm = 0

#api_key = "AIzaSyAScHaoycBlr80cdA4yU09mR41bCJYba2I"
#response = geminiai("no me gustan",api_key, archivo_historial)

#eliminar_historial(archivo_historial)
#print("Historial eliminado.")
#curl https://generativelanguage.googleapis.com/v1beta/models?key=AIzaSyAScHaoycBlr80cdA4yU09mR41bCJYba2I