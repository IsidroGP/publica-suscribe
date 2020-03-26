#!/usr/bin/env python
# -- coding: utf-8 --
#-------------------------------------------------------------------------
# Archivo: procesador_de_tiempo_de_medicamento.py
# Capitulo: 3 Estilo Publica-Subscribe
# Autor(es): Juan Isidro Gonzalez Parra, Oscar Nájera Santana, Marisol Delgado Villegas,
# Eduardo Aguilar Yáñez, Francisco Vargas de la Llata
# Version: 2.0.1 Marzo 2020
# Descripción:
#
#   Esta clase define el rol de un suscriptor, es decir, es un componente que recibe mensajes.
#
#   Las características de ésta clase son las siguientes:
#
#                                   procesador_de_posicion.py
#           +-----------------------+-------------------------+------------------------+
#           |  Nombre del elemento  |     Responsabilidad     |      Propiedades       |
#           +-----------------------+-------------------------+------------------------+
#           |                       |                         |  - Se suscribe a los   |
#           |                       |                         |    eventos generados   |
#           |                       |  - Procesar valores     |    por el wearable     |
#           |     Procesador de     |    de hora actual,      |    de los ejes para    |
#           |                       |    nombre de            |    detectar caidas.    |
#           |                       |    medicamento y la     |  - Notifica al monitor |
#           |                       |    dosis de este.       |    cuando se ha        |
#           |                       |                         |    detectado una caida.|
#           +-----------------------+-------------------------+------------------------+
#
#   A continuación se describen los métodos que se implementaron en ésta clase:
#
#                                               Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Recibe los datos   |
#           |       consume()        |          Ninguno         |    del medicamento    |
#           |                        |                          |    desde el distribui-|
#           |                        |                          |    dor de mensajes.   |
#           +------------------------+--------------------------+-----------------------+
#           |                        |  - ch: propio de Rabbit. |  - Procesa y detecta  |
#           |                        |  - method: propio de     |    valores de la hora |
#           |       callback()       |  - properties: propio de |    actual.            |
#           |                        |     Rabbit.              |                       |
#           |                        |  - body: mensaje recibi- |                       |
#           |                        |     do.                  |                       |
#           +------------------------+--------------------------+-----------------------+
#           |    string_to_json()    |  - string: texto a con-  |  - Convierte un string|
#           |                        |     vertir en JSON.      |    en un objeto JSON. |
#           +------------------------+--------------------------+-----------------------+
#
#
#           Nota: "propio de Rabbit" implica que se utilizan de manera interna para realizar
#            de manera correcta la recepcion de datos, para éste ejemplo no hubo necesidad
#            de utilizarlos y para evitar la sobrecarga de información se han omitido sus
#            detalles. Para más información acerca del funcionamiento interno de RabbitMQ
#            puedes visitar: https://www.rabbitmq.com/
#
#-------------------------------------------------------------------------
import pika
import sys
sys.path.append('../')
from monitor import Monitor
import time


class ProcesadorTiempoMedicamento:

    def consume(self):
        try:
            # Se establece la conexión con el Distribuidor de Mensajes
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            # Se solicita un canal por el cuál se enviarán los signos vitales
            channel = connection.channel()
            # Se declara una cola para leer los mensajes enviados por el
            # Publicador
            channel.queue_declare(queue='time', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(on_message_callback=self.callback, queue='time')
            channel.start_consuming()  # Se realiza la suscripción en el Distribuidor de Mensajes
        except (KeyboardInterrupt, SystemExit):
            channel.close()  # Se cierra la conexión
            sys.exit("Conexión finalizada...")
            time.sleep(1)
            sys.exit("Programa terminado...")

    def callback(self, ch, method, properties, body):
        json_message = self.string_to_json(body)
        
        hourNow = int(json_message['datetime'][11] + json_message['datetime'][12])
        minuteNow = int(json_message['datetime'][14] + json_message['datetime'][15])
        secondNow = int(json_message['datetime'][17] + json_message['datetime'][18])

        print(hourNow)
        if(hourNow==9) or (hourNow==7) or (hourNow==15): #Se evalua si es la hora de tomar pastillas (tres veces al dia)
            if(minuteNow == 0):
                if(secondNow<10):
                    monitor = Monitor()
                    monitor.print_notification_tim(json_message['datetime'], json_message['id'], json_message[
                                       'quantity'], json_message['medicine'], json_message['model'])
        time.sleep(1)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def string_to_json(self, string):
        message = {}
        string = string.decode('utf-8')
        string = string.replace('{', '')
        string = string.replace('}', '')
        values = string.split(', ')
        for x in values:
            v = x.split(': ')
            message[v[0].replace('\'', '')] = v[1].replace('\'', '')
        return message

if __name__ == '__main__':
    p_tiempo = ProcesadorTiempoMedicamento()
    p_tiempo.consume()
