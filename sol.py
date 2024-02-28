from math import inf, sqrt
from random import choices, choice, randint
from numpy.random import exponential, uniform, normal, gumbel, laplace, logistic, rayleigh
import matplotlib.pyplot as plt

client_wait = [i for i in range(11)]
client_wait.append(inf)

# Tipos de generadores de variables aleatoria
var = [exponential, normal, gumbel, laplace, logistic, rayleigh]

def simulation(k, t, n, clients_wait, regression, time_wait):
    """Inicializa las variables y controla el flujo de toda la simulación

    Args:
        k (int): Cantidad de simulaciones a realizar
        t (float): Tiempo que están abiertos los servidores
        n (int): Cantidad de servidores
        clients_wait (bool): Dice si los clientes tendrán la característica de esperar una cantidad aleatoria de elementos en la cola
        regression (bool): Dice si los clientes tendrán la característica de salir del sistema cuando los envíen a un servidor menor una cantidad aleatoria de veces
        time_wait (bool): Dice si los clientes tendrán la característica de salir del sistema si un servidor demora más de un número aleatorio

    Returns:
        tuple: retorna una tupla con listas de todos los datos recopilados (tiempo extra, estadisticas de clientes, de servidor; para más información leer el informe)
    """
    TIME = t

    # Estadisticas
    
    # Posiciones:
    # 0 - Cantidad de personas que entran al sistema
    # 1 - Cantidad de personas que completan el recorrido en el sistema
    # 2 - Cantidad de personas que se van del sistema por esperar mucho tiempo
    # 3 - Cantidad de personas que se van del sistema por regresar muchas veces
    # 4 - Cantidad de personas que se van del sistema por cola larga
    stats_finish_mode = [[] for i in range(5)]

    # Para cada variable aleatoria cuanto se demoran las personas en un servidor con dicha variable como generador de tiempo
    stats_server_time = [[] for i in range(len(var))]

    # Para cada variable aleatoria cuantos clientes pierde
    stats_server_lose = [[] for i in range(len(var))]

    # Para cada simulacion cuanto tiempo sigue el sistema despues de la hora de cierre
    time_less = []

    # Probabilidad de pasar del Servidor i al Servidor j (determinado de manera random)
    p = [uniform(.5, 1) for i in range(n)]

    class Client:
        def __init__(self, id):
            self.id = id
            self.clients_wait = choice(client_wait)
            self.patience = randint(0, 3)
            self.time_wait = uniform(10, 50)

    def arrive(arrive_time, arrive_count, servers_count, servers_history, servers_time, server_generate):
        """Operacion a realizar cuando llega un cliente nuevo al primer servidor
        Args:
            arrive_time (float): Tiempo del arribo
            arrive_count (int): Número del Cliente que arriba
            servers_count (list): Lista donde van los Clients que estan en la cola de cada Servidor 
            servers_history (list): Lista de diccionarios de entrada a cada Servidor
            servers_time (list): Lista de proxima salida de cada Servidor
            server_generate (list): Lista de variables aleatorias

        Returns:
            tuple: Devuelve actualizados los valores de arrive_time y arrive_count
        """
        
        # Solo para uso auxiliar
        time = arrive_time

        # Actualizar valores de arribo
        arrive_count += 1
        new_arrive_time = exponential()
        arrive_time += new_arrive_time

        client = Client(arrive_count)

        # Caso en que el cliente debe esperar en una cola mayor a la que esta dispuesto y abandona la cola
        if clients_wait and len(servers_count[0]) > client.clients_wait:
            servers_history[0][arrive_count] = time
            server_client_lose[0].append('client_wait')
            return arrive_time, arrive_count
        
        # Añadir en Servidor 1
        servers_count[0].append(client)
        
        # Inicializar timer de Servidor 1 si la cola estaba vacia
        if len(servers_count[0]) == 1:
            server_time = abs(server_generate[0]())
            servers_time[0] = time + server_time

        # Añadir al historial del Servidor 1
        servers_history[0][arrive_count] = time

        # Retornar solo para actualizar valores
        return arrive_time, arrive_count

    def exit_server(servers_count, servers_history, servers_time, server_generate, server_jump, i):
        """Operacion a realizar cuando un cliente termina en el Servidor i

        Args:
            servers_count (list): Lista donde van los Clients que estan en la cola de cada Servidor 
            servers_history (list): Lista de diccionarios de entrada a cada Servidor
            servers_time (list): Lista de proxima salida de cada Servidor
            server_generate (list): Lista de variables aleatorias
            server_jump (float): Variable uniforme de 0.5 a 1
            i (int): Servidor actual
        """
        # Solo para uso auxiliar
        time = servers_time[i]

        # Cliente que termino en el Servidor i
        client = servers_count[i].pop(0)
        
        # Si el Servidor i queda vacio su tiempo se maximiza para que no participe en las operaciones posibles
        if len(servers_count[i]) == 0:
            servers_time[i] = inf 
        # En caso contrario se calcula el nuevo tiempo
        else:
            new_server_time = abs(server_generate[i]())
            servers_time[i] = time + new_server_time

        # Probabilidad de saltar a un Servidor j, j != i
        if uniform(0, 1) > server_jump[i]:
            j = i
            while j == i:
                j = randint(0, len(servers_count)-1)
            # Cuando hacen regresar a un Servidor anterior el cliente pierde paciencia
            if j < i:
                client.patience -= 1
            # Caso en que al cliente se le acaba la paciencia y abandona la cola
            if regression and client.patience < 0:
                server_client_lose[i].append('regression')
                last = servers_history[i][client.id]
                server_time_wait[i].append(time-last)
                return
        else: j = i + 1

        # Si el servidor j es el final porque ya fue atendido por el ultimo Servidor
        if j == len(servers_count): 
            exit_history[client.id] = time
            last = servers_history[i][client.id]
            server_time_wait[i].append(time-last)
        else:
            # Caso en que el cliente debe esperar en una cola mayor a la que esta dispuesto y abandona la cola
            if clients_wait and len(servers_count[j]) > client.clients_wait:
                server_client_lose[i].append('client_wait')
                last = servers_history[i][client.id]
                server_time_wait[i].append(time-last)
                return
            
            last = servers_history[i][client.id]
            server_time_wait[i].append(time-last)
            # Añadir al cliente al Servidor j, pero puede ser que el cliente ya haya pasado por dicho servidor
            servers_count[j].append(client)
            # Inicializar timer de Servidor J si la cola estaba vacia
            if len(servers_count[j]) == 1:
                new_server_time = abs(server_generate[j]())
                servers_time[j] = time + new_server_time
            servers_history[j][client.id] = time

    def time_wait_review(servers_clients, servers_history, servers_time, min_time):
        """Revisar los clientes para eliminar los que se cansaron de esperar y abandonaron sus colas
        Args:
            servers_clients (list): Lista donde van los Clients que estan en la cola de cada Servidor
            servers_history (list): Lista de diccionarios de entrada a cada Servidor
            servers_time (list): Lista de proxima salida de cada Servidor
            min_time (float): Número que representa la siguiente operación (salida o arribo)
        """
        for i in range(len(servers_clients)):
            leave = []
            for client in servers_clients[i]:
                init = servers_history[0][client.id]
                if min_time - init > client.time_wait:
                    leave.append(client)
                    server_client_lose[i].append('time_wait')
                    last = servers_history[i][client.id]
                    server_time_wait[i].append(init + client.time_wait - last)
            for client in leave:
                servers_clients[i].remove(client)
            # Si la cola se quedo vacia su tiempo se maximiza
            if len(servers_clients[i]) == 0: 
                servers_time[i] = inf

    def simulate(n, server_generate, server_jump):
        """Controla el flujo de la simulación

        Args:
            n (int): Cantidad de servidores
            server_generate (list): Lista de variables aleatorias de los servidores
            server_jump (int): Servidor actual

        Returns:
            float: Número que representa el tiempo de la siguiente operación
        """
        # Inicializar variables
        # Cantidad de arribos
        arrive_count = 0

        # Lista donde van los Clients que estan en la cola de cada Servidor 
        servers_clients = [[] for i in range(n)]

        # Lista de diccionarios de entrada a cada Servidor
        servers_history = [{} for i in range(n)]

        # Lista de proxima salida de cada Servidor
        servers_time = [inf for i in range(n)]

        # Generar tiempo de arribo inicial
        arrive_time = exponential()

        # La primera operacion siempre es un arribo
        min_time = arrive_time
        
        # Posibles operaciones: Arribo y Salida de Servidor
        while min_time < TIME:
            # Caso Operacion Arribo
            if min_time == arrive_time: 
                arrive_time, arrive_count = arrive(arrive_time, arrive_count, servers_clients, servers_history, servers_time, 
                                                server_generate)
            # Caso Operacion Salida de Servidor
            else:
                # Se determina cual es el Servidor
                index = servers_time.index(min_time)
                exit_server(servers_clients, servers_history, servers_time, server_generate, server_jump, index)
            # Calculo de la siguiente operacion
            min_time = min(arrive_time, min(servers_time))
            if time_wait and min_time > TIME/10:
                time_wait_review(servers_clients, servers_history, servers_time, min_time)
                min_time = min(arrive_time, min(servers_time))

        shape = [len(i) for i in servers_clients]
        # Posibles operaciones: Salida de Servidor
        while max(shape) > 0:
            min_time = min(servers_time)
            index = servers_time.index(min_time)
            exit_server(servers_clients, servers_history, servers_time, server_generate, server_jump, index)
            if time_wait:
                time_wait_review(servers_clients, servers_history, servers_time, min_time)
            shape = [len(i) for i in servers_clients]
        
        stats_finish_mode[0].append(len(servers_history[0]))
        return min_time

    for sim in range(k):
        # Seleccion de generadores para la simulacion
        generate = choices(var, k=n)

        # Datos a obtener de la simulacion i
        server_time_wait = [[] for i in range(n)]
        server_client_lose = [[] for i in range(n)]
        exit_history = {}

        end = simulate(n, generate, p)

        # Añadir datos de la simulacion i a las estadisticas generales
        time_less.append(end - TIME)
        stats_finish_mode[1].append(len(exit_history))
        cw = tw = r = 0
        for i in range(n):
            index = var.index(generate[i])
            mean = sum(server_time_wait[i]) / len(server_time_wait[i])
            stats_server_time[index].append(mean)
            stats_server_lose[index].append(len(server_client_lose[i]))
            for val in server_client_lose[i]:
                if val == 'client_wait': cw += 1
                if val == 'time_wait': tw += 1
                if val == 'regression': r += 1
        stats_finish_mode[2].append(tw)
        stats_finish_mode[3].append(r)
        stats_finish_mode[4].append(cw)

    return time_less, stats_finish_mode, stats_server_time, stats_server_lose

def confidence(vector):
    """ Devuelve la media y la desviacion estandar muestral de un vector de muestras
    Args:
        vector (list): Representa los valores a los que se le quiere calcular media y desviación

    Returns:
        float: Media y desviación estándar muestral de un vector de muestras
    """
    mean = sum(vector) / len(vector)
    variance = sum([(x - mean)**2 for x in vector]) / (len(vector) - 1)
    deviation = sqrt(variance)
    return round(mean, 1), round(deviation, 1)

time_opened = 500
servers = 5
time_less, stats_finish_mode, stats_server_time, stats_server_lose = simulation(1000, time_opened, servers, True, True, False)

print(f'Tiempo Final: {time_opened}')
print(f'Servidores: {servers}')
data = confidence(time_less)
print(f'Tiempo extra: {data[0]} // {data[1]}')

finish = ['Entrada de clientes', 'Salida de clientes', 'Perdida por espera', 'Perdida por retroceso', 'Perdida por cola']
for i in range(5):
    data = confidence(stats_finish_mode[i])
    print(f'{finish[i]}: {data[0]} // {data[1]}')

types = ['exponencial', 'normal', 'gumbel', 'laplace', 'logistic', 'rayleigh']
for i in range(6):
    data = confidence(stats_server_lose[i])
    print(f'Perdida de clientes con distribucion {types[i]}: {data[0]} // {data[1]}')

    data = confidence(stats_server_time[i])
    print(f'Tiempo en servidor con distribucion {types[i]}: {data[0]} // {data[1]}')
