from topology import start, stop
from send_packet import send_packet
import json
import time

routers = start('topology.json')

# Esperar un tiempo para que los routers comuniquen sus tablas de ruteo para evitar perdida de paquetes
time.sleep(10)

# Seccion: Paquetes a enviar
send_packet(12345, json.dumps({'destination': "Router#2", 'data': "Saludines"}))

time.sleep(3)


# Fin Seccion: Paquetes a enviar
stop(routers)
