# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# NOTE: this example requires PyAudio because it uses the Microphone class

import json
import requests
import re
import base64

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
            file.write(role +": " + text + "\n")

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

#api_key = "AIzaSyAScHaoycBlr80cdA4yU09mR41bCJYba2I"
#archivo_historial = 'historial_chat.txt'
#response = geminiai("no me gustan",api_key, archivo_historial)
#print(response)

#eliminar_historial(archivo_historial)
#print("Historial eliminado.")
#curl https://generativelanguage.googleapis.com/v1beta/models?key=AIzaSyAScHaoycBlr80cdA4yU09mR41bCJYba2I
