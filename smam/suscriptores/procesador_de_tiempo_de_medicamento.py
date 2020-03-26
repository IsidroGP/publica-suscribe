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

        if(hourNow==20) or (hourNow==4) or (hourNow==12):
            if(minuteNow == 0):
                if(secondNow<10):
                    monitor = Monitor()
                    monitor.print_notification3(json_message['datetime'], json_message['id'], json_message[
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
