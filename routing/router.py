import json
from json import JSONDecodeError
from random import choice
from threading import Timer

from routing.router_port import RouterPort

'''
Un router tiene puertos que utiliza para comunicarse con otros routers (estos puertos se modelan usando la clase RouterPort).

'''


'''
Cambiar topologia

'''

class Router(object):
    def __init__(self, name, update_time, ports, logging=True):
        self.name = name
        self.logging = logging
        self.update_time = update_time
        self.ports = dict()
        self.input_to_output = dict()
        self._init_ports(ports)
        self.timer = None
        self.routing_table = dict()
        self._init_routing_table()

    # el paquete es para el router que lo recibe, se imprime la data que lleva en consola.
    def _success(self, message):
        """
        Internal method called when a packet is successfully received.
        :param message:
        :return:
        """
        print("[{}] {}: {}".format(self.name, 'Success! Data', message))

    def _log(self, message):
        """
        Internal method to log messages.
        :param message:
        :return: None
        """
        if self.logging:
            print("[{}] {}".format(self.name, message))

    def _init_ports(self, ports):
        """
        Internal method to initialize the ports.
        :param ports:
        :return: None
        """
        for port in ports:
            input_port = port['input']
            output_port = port['output']

            router_port = RouterPort(
                input_port, output_port, lambda p: self._new_packet_received(p)
            )

            self.ports[output_port] = router_port
            self.input_to_output[input_port] = output_port

        self._log("Puertos: {}".format(self.ports))

    def _init_routing_table(self):
        """
        Inicializa la tabla de ruteo con si mismo
        :return: None
        """
        '''
        Tabla: nombre_router | hops | nombre_vecino | puerto
        '''

        self.routing_table[self.name] = json.dumps(
            {'nombre': self.name, 'hops': 0, 'neighbour_name': "None", 'port': list(self.input_to_output.keys())})


    def _new_packet_received(self, packet):
        """
        Internal method called as callback when a packet is received.
        :param packet:
        :return: None
        """
        self._log("Packet received")
        message = packet.decode()

        try:
            message = json.loads(message)
        except JSONDecodeError:
            self._log("Malformed packet")
            return

        if 'destination' in message and 'data' in message:
            if message['destination'] == self.name:
                self._success(message['data'])
            else:
                try:
                    final_router = json.loads(self.routing_table[message['destination']])
                    # Revisar que sea un router vecino o no
                    if final_router['neighbour_name'] != 'None':
                        # Encontrar al router vecino para continuar el ruteo
                        next_router = json.loads(self.routing_table[message['destination']])['neighbour_name']
                        final_router = json.loads(self.routing_table[next_router])
                    # Enviar mensaje al puerto del router vecino
                    port = list(final_router['port'])[0]  # choice(list(final_router['port']))
                    self._log("Forwarding to port {}".format(port))
                    self.ports[port].send_packet(packet)
                except KeyError:
                    self._log("Destination router not in table")

        elif 'routing_table' in message:
            neighbour_RT = message['routing_table']

            is_first = True
            first_router_name = ""

            for key in neighbour_RT:
                RT = json.loads(neighbour_RT[key])
                if is_first:
                    neighbour = "None"
                    first_router_name = RT['nombre']
                    is_first = False
                else:
                    neighbour = first_router_name

                self_RT = json.loads(self.routing_table[self.name])

                # Si es vecino, vemos a que port nos corresponde
                if RT['neighbour_name'] == "None":
                    port_matched = self._match_my_port(list(RT['port']))
                else:
                    port_matched = list(RT['port'])

                if RT['nombre'] in self.routing_table:
                    if int(RT['hops']) + 1 < int(self_RT['hops']):
                        self._log("Modificando la tabla para {}, menos hops".format(RT['nombre']))
                        # Actualizar fila de nuestra tabla
                        self.routing_table[RT['nombre']] = json.dumps(
                            {'nombre': RT['nombre'], 'hops': int(RT['hops']) + 1,
                             'neighbour_name': neighbour, 'port': port_matched})
                else:
                    self._log("No existe {}, agregandolo...".format(RT['nombre']))
                    # Agregarlo
                    self.routing_table[RT['nombre']] = json.dumps(
                        {'nombre': RT['nombre'], 'hops': RT['hops'] + 1,
                         'neighbour_name': neighbour, 'port': port_matched})

        else:
            self._log("Malformed packet")


    def _broadcast(self):
        """
        Internal method to broadcast
        :return: None
        """
        self._log("Broadcasting")
        for o_port in list(self.ports.keys()):
            self._log("Forwarding to port {}".format(o_port))
            self.ports[o_port].send_packet(str.encode(json.dumps({'routing_table': self.routing_table})))

        self.timer = Timer(self.update_time, lambda: self._broadcast())
        self.timer.start()

    def start(self):
        """
        Method to start the routing.
        :return: None
        """
        self._log("Starting")
        self._broadcast()
        for port in self.ports.values():
            port.start()

    def stop(self):
        """
        Method to stop the routing.
        Is in charge of stop the router ports threads.
        :return: None
        """
        self._log("Stopping")
        if self.timer:
            self.timer.cancel()

        for port in self.ports.values():
            port.stop_running()

        for port in self.ports.values():
            port.join()

        self._log(self.routing_table)
        self._log("Stopped")



    def _match_my_port(self, list_port):
        '''
        Entrega el port de comunicacion
        :param list_port:
        :return:
        '''
        result_port = []
        # Iterar sobre nuestros output_ports
        for my_port in list(self.ports.keys()):
            if my_port in list_port:
                result_port.append(my_port)

        return result_port

