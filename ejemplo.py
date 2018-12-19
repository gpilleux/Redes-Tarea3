from topology import start, stop
from send_packet import send_packet
import json
import time

routers = start('topology.json')
#send_packet(4321, json.dumps({'destination': "Router#1", 'data': "Saludines"}))

d = dict()
d['algo'] = json.dumps({'nombre': "Router#2", 'hops': 0, 'neighbour_name': "None", 'port': [10]})

'''
for key in d:
    if("nombre" in d[key]):
        print(d[key])
    else:
        print("naite")
        '''

send_packet(4321, json.dumps({'routing_table': d}))

time.sleep(10)

stop(routers)
