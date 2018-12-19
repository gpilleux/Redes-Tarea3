# Redes-Tarea3

Integrantes: Maximiliano Edwards, Guillermo Pilleux

La tarea 3 fue implementada en Python 3.6

-------o-------

Para ejecutar la tarea, es necesario tener un archivo json con la topología, la cual se utiliza en el archivo ejemplo.py
al usar la función start de topology.py.
En caso de querer usar una topología distinta hay que cambiar el parámetro en esta función.

En el archivo ejemplo.py se deben enviar los mensajes a los routers deseados con el formato estándar.
En este mismo archivo, se pueden ingresar los paquetes a enviar.

Se adjunta el json de una topología más compleja con una imágen de la representación.

-------o-------
Nuestra implementación

Variables agregadas:
dict() input_to_output: asocia los puertos de entradas y de salida del mismo router
dict() routing_table: tabla de ruteo de cada router

Funciones agregadas
_init_routing_table(self): Pobla la tabla de rutas con el mismo router y su lista de puertos de entrada asociados
_match_my_port(self, list_port): Entrega los puertos de comunicación correspondientes con otro router.

Funciones modificadas
_new_packet_recieved(self, packet): Agregamos un posible campo ('routing_table') al paquete para poder distinguir cuando se envía la tabla de rutas versus un mensaje.
    En este caso se revisa la tabla de rutas recibida y se compara con la del router para ver si se tiene que modiciar o agregar nuevas filas a su tabla

_broadcast(self): Para cada puerto de salida del router se envía la tabla de ruta del router

Nota: Se agregaron logs de los pasos importante de la ejecución en los routers para visualizar el funcionamiento de la implementación.