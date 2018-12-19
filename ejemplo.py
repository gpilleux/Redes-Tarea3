from topology import start, stop
from send_packet import send_packet
import json
import time

#routers = start('topology.json')
routers = start('complex_topology.json')

# Esperar un tiempo para que los routers comuniquen sus tablas de ruteo para evitar perdida de paquetes
time.sleep(16)

# Seccion: Paquetes a enviar
send_packet(12345, json.dumps({'destination': "Router#20", 'data': "Saludines"}))

send_packet(11234, json.dumps({'destination': "Router#5", 'data': "Hola esta es una palabra"}))

time.sleep(3)


# Fin Seccion: Paquetes a enviar
stop(routers)
