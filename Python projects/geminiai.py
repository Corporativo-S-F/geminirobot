# -*- coding: utf-8 -*-
#!/usr/bin/env python2.7
# NOTE: this example requires PyAudio because it uses the Microphone class

import json
import requests
import re


def eliminar_acentos(texto):
    acentos = {
        u'á': u'a', u'é': u'e', u'í': u'i', u'ó': u'o', u'ú': u'u',
        u'Á': u'A', u'É': u'E', u'Í': u'I', u'Ó': u'O', u'Ú': u'U',
        u'ñ': u'n', u'Ñ': u'N', u'ü': u'u', u'Ü': u'U'
    }
    for acento, reemplazo in acentos.items():
        texto = texto.replace(acento, reemplazo)
    return texto

# Función para limpiar el texto
def limpiar_texto(texto):
    # Asegurarse de que el texto es una cadena Unicode
    if isinstance(texto, str):
        texto = texto.decode('utf-8')
    # Reemplazar letras con acentos por sus equivalentes sin acento
    texto = eliminar_acentos(texto)
    # Definir la expresión regular para mantener solo letras, espacios y los caracteres permitidos
    caracteres_permitidos = ur'[^a-zA-Z\s.,!?¡¿]'
    # Usar la expresión regular para reemplazar los caracteres no deseados con una cadena vacía
    texto_limpio = re.sub(caracteres_permitidos, u'', texto)
    return texto_limpio




def geminiai(text,key):
		print("Estoy en la funcion: "+ text + key)
#	try:
		url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key='+key
	        headers = {'Content-Type': 'application/json'}
       		data = {"contents": [{
				"parts": [{
                                	"text": text
                        	}]
                	}],
                	"safetySettings": [{
                        	"category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        	"threshold": "BLOCK_ONLY_HIGH"
                	}],
                	"generationConfig": {
                        	"stopSequences": ["Title"],
                        	"temperature": 1.0,
                        	"maxOutputTokens": 200,
                        	"topP": 0.8,
                        	"topK": 10
                	}
        	}

        	json_data = json.dumps(data)

		response = requests.post(url , headers=headers, data=json_data)
		if response.status_code == 200:
			response_json = response.json()
			print("Response: ")
			print(response_json)

			if "candidates" in response_json and len(response_json["candidates"]) > 0:
				content_parts = response_json["candidates"][0]["content"]["parts"]
				if len(content_parts) > 0:
					generated_text = content_parts[0]["text"]
					print("Generated text:")
					print(generated_text)
					clean_text = limpiar_texto(generated_text)
					return clean_text

			else:
				print("Failed to get response. Status code: ", response.status_code)
				print(response.text)
				return ("No puedo responder ahora, intenta nuevamente")
#	except:
#		print("hay un error en el request")
#		return ("Error")



#geminiai("texto de prueba","AIzaSyAScHaoycBlr80cdA4yU09mR41bCJYba2I")
#print("fin")
