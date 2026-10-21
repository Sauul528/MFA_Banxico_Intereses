#Sistema de consulta en Banxico en tiempo real, calula interes simple con la tasa de cetes a 28 dias y envia el reporte por correo
"""
Autor: Saul Reyes Nava
Fecha: 21/10/2026 
Objetivo:
Obtener el interes simple con tasa de cetes a 28 dias
haciendo requests en tiempo real a las series oportunas banxico enviando por email el reporte de resultados
Version extendida SMS o Whatsapp solo si no se conecta al email
"""
import os
import requests
import time as t
import smtplib
from email.mime.text import MIMEText
from smtplib import SMTP
from dotenv import load_dotenv
load_dotenv()
""" 
Funcion 1 conexion a banxico cambio dólar FIX
funcion 2 conexion a banxico series oportuno cetes
funcion 3 calculo de interes simple
funcion 4 conexion y envio de email
funcion 5 menú de opciones solo si lo necesitas
"""
#url es puerta , token es llave de preferencia dato oportuno 
TOKEN = os.getenv("TOKEN_BANXICO")
def BanxicoDollar()->float:
     """
     @BanxicoDollar:La función consulta una serie de banxico, en este caso el tipo de cambio dólar FIX regresando el valor como entero o decimal.
     """
     try:
        headers = {'Bmx-Token': TOKEN}
        serie = "SF43718"
        tipo_Cambio = 0
        enlace = f'https://www.banxico.org.mx/SieAPIRest/service/v1/series/{serie}/datos/oportuno'
        response = requests.get(url=enlace, headers=headers , timeout=10)
        if response.status_code == 200:
                json_response = response.json()
                tipo_Cambio = float(json_response['bmx']['series'][0]['datos'][0]['dato'])
                print(f"el tipo de cambio FIX es de: {tipo_Cambio}")
        elif response.status_code == 404:
                print("Conexión fallida, revise su conexion a internet")
        else:
         print(f"[Error] Banxico respondió con código {response.status_code}, revise su token.")
     except requests.exceptions.RequestException as error:
          print(f"[Error] No se pudo conectar con Banxico: {error}")
     except (KeyError, IndexError, ValueError, TypeError) as error:
          print(f"[Error] La respuesta de Banxico no tiene el formato esperado o el dato no es numérico: {error}")
     return tipo_Cambio
     
def Consulta_Cetes()->float:
    """
    @Cetes: la función consulta el valor de los cetes y devuelve la tasa porcentual en valor entero o decimal.

    """
    headers = {'Bmx-Token': TOKEN}
    serie = "SF43936"
    tasa_porcentual = 0
    enlace = f'https://www.banxico.org.mx/SieAPIRest/service/v1/series/{serie}/datos/oportuno'
    try:
        response = requests.get(url=enlace, headers=headers, timeout=10)
        if response.status_code == 200:
                json_response = response.json()
                tasa_porcentual = float(json_response['bmx']['series'][0]['datos'][0]['dato'])
                print(f"El valor de cetes hoy es de : {tasa_porcentual}")
        elif response.status_code == 404:
                print("Conexión fallida, revise su conexion a internet")
        else:
         print(f"[Error] Banxico respondió con código {response.status_code}, revise su token.")
    except requests.exceptions.RequestException as error:
        print(f"[Error] No se pudo conectar con Banxico: {error}")
    except (KeyError, IndexError, ValueError, TypeError) as error:
        print(f"[Error] La respuesta de Banxico no tiene el formato esperado o el dato no es numérico: {error}")
    return tasa_porcentual
CONTRASEÑA = os.getenv('PASSWORDGMAIL')
remitente = os.getenv('USERMAIL')
def Calcular_Interés(capital:float, dias:int, cetes:float)->tuple:
     """
     @Calcular_interés: Calcula el interés con los cetes, capital y dias. Regresa (interes, valor_acumulado)
     @capital: Valor entero o decimal
     @dias: Valor entero
     @cetes: Tasa de cetes obtenida con Cetes()
     """
     try:
        if capital <= 0 or dias <= 0 or cetes <= 0:
             print("[Error] Capital, días y tasa de cetes deben ser mayores que 0.")
             return 0.0, 0.0
        tasa_interés = (cetes/100)/(1-(cetes/100)*(28/360))
        valor_acumulado = capital*(1+(tasa_interés*(dias/360)))
        print(f"El interés es de: {valor_acumulado}")
     except (TypeError, ValueError, ZeroDivisionError) as error:
          print(f"[Error] No se pudo calcular el interés: {error}")
     return tasa_interés, valor_acumulado


def Enviar_Reporte(destinatario:str, asunto:str, reporte)->None:
     """
     @enviar_reporte: Envía el reporte al correo electrónico proporcionado.
     @destinatario: Dirección de correo capturada como str
     @asunto: Asunto del correo
     @reporte: Texto del reporte con los resultados
     """
     try:
        msg = MIMEText(reporte, 'plain', 'utf-8')
        msg['From']= remitente
        msg['To'] = destinatario
        msg['Subject'] = asunto
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(remitente, CONTRASEÑA)
            smtp_server.sendmail(remitente, destinatario, msg.as_string())
            print("Enviando mensaje")
     except smtplib.SMTPAuthenticationError:
          print("[Error] Gmail rechazó el usuario o la contraseña de aplicación.")
     except (smtplib.SMTPException, OSError) as error:
          print(f"[Error] No se pudo enviar el correo: {error}")

def menu():
    """
    Muestra las opciones del programa y llama a la función 
    seleccionada por el usuario, hasta que cierra el programa.
    return: No regresa nada, solo controla el menú
    """
    Continuar_Programa = True

    while Continuar_Programa:
        print("\nBIENVENIDO AL SISTEMA DE CONSULTA BANXICO E INTERES SIMPLE")
        print("SELECCIONE LA OPERACION A REALIZAR:")
        print("Consultar tipo de cambio USD/MXN (FIX)  : 1")
        print("Calcular interés  : 2")
        print("Salir: 3")
        try:
            Opción_Usuario = int(input("Selecciona tu opción: "))
        except ValueError:
            print("\n[Error] Ingresa un número de opción válido entre 1 y 3.")
            continue

        try:
            if Opción_Usuario == 1:
                 BanxicoDollar()
            elif Opción_Usuario == 2:
                capital= float(input("Ingrese el monto a invertir: "))
                dias = int(input("Ingrese el plazo(dias): "))
                if capital <= 0 or dias <= 0 :
                    print("\n [Error] El capital y dias NO pueden ser menores a 0 intente de nuevo.")
                    continue
                destinatario=str(input("Correo destinatario(ej. usuario@gmail.com): ")).strip().lower()
                if "@" not in destinatario:
                    print("\n[Error] ingrese correo válido con @")
                    continue
                asunto= str(input("Ingrese el asunto: "))
                cetes = Consulta_Cetes()
                if cetes == 0:
                    print("No se obtubo ningun valor para cetes")
                    continue
                interes, valor_acumulado = Calcular_Interés(capital, dias, cetes)
                if valor_acumulado == 0:
                    print("No se generó el reporte porque el cálculo falló.")
                    continue
                reporte  = (
                    f"Los cetes a 28 dias: {cetes} \n"
                    f"Monto inicial: ${capital:,.2f}\n"
                    f"Plazo(días): {dias}\n"
                    f"Interés: {interes*100:,.2f}%\n"
                    f"Valor acumulado: ${valor_acumulado:,.2f}"
                )
                print("\n"+ reporte)
                t.sleep(3.0)
                Enviar_Reporte(destinatario, asunto, reporte)
                
            elif Opción_Usuario == 3:
                 print("Saliendo del programa, por favor espera...")
                 t.sleep(5.0)
                 break
            else:
                print("\n[Error] Opción no válida, elige entre 1 y 3.")
                continue
        except ValueError:
            print("\n[Error] Los valores del capital deben ser números , los dias un entero o debe de ser un correo válido. Intenta otra vez.")
            continue

        respuesta = input("\nPara continuar presiona S o Para cerrar presiona N: ").strip().lower()
        if respuesta == 'n':
            print('Gracias por tu tiempo, hasta luego.')
            print("Saliendo del programa, por favor espera...")
            t.sleep(5.0)
            Continuar_Programa = False

    print("Ya saliste del ciclo")

if __name__ == "__main__":
    menu()

    

    
