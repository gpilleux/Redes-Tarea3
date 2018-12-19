import json
from json import JSONDecodeError
from random import choice
from threading import Timer

from routing.router_port import RouterPort

'''
Un router tiene puertos que utiliza para comunicarse con otros routers (estos puertos se modelan usando la clase RouterPort).

'''


class Router(object):
    def __init__(self, name, update_time, ports, logging=True):
        self.name = name
        self.update_time = update_time
        self.ports = dict()
        self._init_ports(ports)
        self.timer = None
        self.logging = logging
        self.routing_table = {}
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

    def _init_routing_table(self):
        """
        Inicializa la tabla de ruteo con si mismo
        :return: None
        """
        '''
        Tabla: nombre_router | hops | nombre_vecino | puerto
        
        Router#1 -> Router#2
        Router#2 -> Router#3
        Router#3 -> Router#4
        
        Router#2 solicita tabla a Router#3
            Guarda: Router#2 0 None p_Router#2
                    Router#3 1 None p_Router#3
        
        Router#1 solicita tabla a Router#2
            Guarda: Router#1 0 None p_Router#1
                    Router#2 1 None p_Router#2
                    Router#3 2 Router#2 p_Router#3
                    Router#4 3 Router#2 p_Router#4
                    
        Si quiuero enviar un msj del #1 al #3
            Buscar en tabla Router#3 -> Router#3 2 Router#2 p_Router#3
                Se que debo comunicarme con Router#3 mediante puerto_Router#3 a traves del Router#2
            Buscar en tabla Router#2 -> Router#2 1 None p_Router#2
                Enviar a Router#2, indicandole el puerto destinatario = p_Router#3
                
        
        '''
        # TODO cual puerto se debería guardar en caso de ser uno a enviar por vecino
        # Posiblemente usar otro campo en el mensaje para entregar el puerto utilizado del router que envia su tabla
        self.routing_table[self.name] = json.dumps(
            {'nombre': self.name, 'hops': 0, 'neighbour_name': "None", 'port': list(self.ports.keys())})


        '''
        enviar mensajes
            queremos rutear a Router#n
                escogemos puerto alzar del Router#n de nuestro diccionario
        '''

    # cuando se recibe un nuevo paquete de un puerto, se revisa el destino del paquete: si es para el router, se llama a _success, sino, se elige a quien forwardear el paquete.
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
                '''
                # Randomly choose a port to forward
                port = choice(list(self.ports.keys()))
                self._log("Forwarding to port {}".format(port))
                self.ports[port].send_packet(packet)
                '''

                final_router = json.loads(self.routing_table[message['destination']])
                # Revisar que sea un router vecino o no
                if final_router['neighbour_name'] != 'None':
                    # Encontrar al router vecino para continuar el ruteo
                    final_router = json.loads(self.routing_table[message['destination']])['neighbour_name']
                # Enviar mensaje al puerto del router vecino
                # TODO ver de usar lista o solo uno en especifico
                port = choice(list(final_router['port']))
                self._log("Forwarding to port {}".format(port))
                self.ports[port].send_packet(packet)
        elif 'routing_table' in message:
            # TODO ver que parametro le pasamos en la tabla: una lista o un puerto especifico?
            '''
            diccionario -> 
                muchos nombres
                    hops
                    listado de puertos

                    existe este nombre en nuestro diccionario?
                        existe: hops < hops nuestro?
                            intercambiar...
                        no existe:
                            agregarlo
                            
            Tabla: nombre_router | hops | nombre_vecino | puerto
            
            Router#1 -> Router#2
            Router#2 -> Router#3
            Router#3 -> Router#4
            
            Router#2 solicita tabla a Router#3
                Guarda: Router#2 0 None p_Router#2
                        Router#3 1 None p_Router#3
            
            Router#1 solicita tabla a Router#2
                Guarda: Router#1 0 None p_Router#1
                        Router#2 1 None p_Router#2
                        Router#3 2 Router#2 p_Router#3
                        Router#4 3 Router#2 p_Router#4
            '''
            neighbour_RT = message['routing_table']
            # diccionario = message['routing_table']
            for key in neighbour_RT:
                #print(neighbour_RT[key])
                RT = json.loads(neighbour_RT[key])
                print(RT)
                # usar el nombre de este router y no del que viene en la tabla del vecino SAGFAGAFDSGAG #
                self_RT = json.loads(self.routing_table[self.name])
                if RT['nombre'] in self.routing_table:
                    print("Existe")
                    print(RT['hops'])
                    print(self_RT['hops'])
                    if int(RT['hops']) + 1 < int(self_RT['hops']):
                        print("Menos hops")
                        # Actualizar fila de nuestra tabla
                        self.routing_table[RT['nombre']] = json.dumps(
                            {'nombre': RT['nombre'], 'hops': int(RT['hops']) + 1,
                             'neighbour_name': RT['nombre'], 'port': list(RT['port'])})
                else:
                    print("No existe, agregandolo...")
                    # Agregarlo
                    self.routing_table[RT['nombre']] = json.dumps(
                        {'nombre': RT['nombre'], 'hops': RT['hops'] + 1,
                         'neighbour_name': "None", 'port': list(RT['port'])})

            print("Imprimir RT")
            print(self.routing_table)
        else:
            self._log("Malformed packet")


    def _broadcast(self):
        """
        Internal method to broadcast
        :return: None
        """
        self._log("Broadcasting")
        # TODO
        '''
        para cada out_port:
            enviar self.routing_table
        '''
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
