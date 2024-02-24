import math
from random import choices
from numpy.random import exponential, uniform, normal, gumbel, laplace, logistic, rayleigh

class Client:
    def __init__(self, id):
        self.id = id       

def arrive(arrive_time, arrive_count, servers_count, servers_history, servers_time, server_generate):
    """
    Operacion a realizar cuando llega un cliente nuevo al primer servidor
    """
    # Solo para uso auxiliar
    time = arrive_time

    # Actualizar valores de arribo
    arrive_count += 1
    new_arrive_time = exponential()
    arrive_time += new_arrive_time

    # Añadir en Servidor 1
    servers_count[0].append(Client(arrive_count))
    
    # Inicializar timer de Servidor 1 si la cola estaba vacia
    if len(servers_count[0]) == 1:
        server_time = abs(server_generate[0]())
        servers_time[0] = time + server_time

    # Añadir al historial del Servidor 1
    servers_history[0][arrive_count] = time

    # Retornar solo para actualizar valores
    return arrive_time, arrive_count

def exit_server(servers_count, servers_history, servers_time, server_generate, server_jump, exit_count, exit_history, i):
    """
    Operacion a realizar cuando un cliente termina en el Servidor i
    """
    # Solo para uso auxiliar
    time = servers_time[i]

    # Cliente que termino en el Servidor i
    client = servers_count[i].pop(0)
    
    # Si el Servidor i queda vacio su tiempo se maximiza para que no participe en las operaciones posibles
    if len(servers_count[i]) == 0:
        servers_time[i] = math.inf 
    # En caso contrario se calcula el nuevo tiempo
    else:
        new_server_time = abs(server_generate[i]())
        servers_time[i] = time + new_server_time
    
    # Probabilidad de saltar a un Servidor j, j != i
    if uniform(0, 1) > server_jump[i]:
        j = i
        while j == i:
            j = int(uniform(0, len(servers_count)))
    else: j = i + 1

    # Si el servidor j es el final porque ya fue atendido por el ultimo Servidor
    if j == len(servers_count): 
        exit_count += 1
        exit_history[exit_count] = time
    else:
        # Añadir al cliente al Servidor j, pero puede ser que el cliente ya haya pasado por dicho servidor
        servers_count[j].append(client)
        # Inicializar timer de Servidor J si la cola estaba vacia
        if len(servers_count[j]) == 1:
            new_server_time = abs(server_generate[j]())
            servers_time[j] = time + new_server_time
        try:
            val = servers_history[j][client.id]
            # Caso en que el cliente paso 1 vez por el Servidor j
            if type(val) == float:
                new_val = [val]
            # Caso en que el cliente paso varias veces por el Servidor j
            else:
                new_val = [timed for timed in val]
            new_val.append(time)
            servers_history[j][client.id] = new_val
        except:
            # Caso en que el cliente no ha pasado por el Servidor J
            servers_history[j][client.id] = time

    # Retornar solo para actualizar valores
    return exit_count

def simulate(n, final_time, server_generate, server_jump):
    # Inicializar variables
    # Cantidad de arribos, Cantidad de salidas, tiempo de la proxima operacion
    arrive_count = exit_count = min_time = 0

    # Diccionario de salidas
    exit_history = {}

    # Lista donde van los Clients que estan en la cola de cada Servidor 
    servers_clients = [[] for i in range(n)]

    # Lista de diccionarios de entrada a cada Servidor
    servers_history = [{} for i in range(n)]

    # Lista de proxima salida de cada Servidor
    servers_time = [math.inf for i in range(n)]

    # Generar tiempo de arribo inicial
    arrive_time = exponential()

    # La primera operacion siempre es un arribo
    min_time = arrive_time
    
    # Posibles operaciones: Arribo y Salida de Servidor
    while min_time < final_time:
        # Caso Operacion Arribo
        if min_time == arrive_time: 
            arrive_time, arrive_count = arrive(arrive_time, arrive_count, servers_clients, servers_history, servers_time, server_generate)
        # Caso Operacion Salida de Servidor
        else:
            # Se determina cual es el Servidor
            index = servers_time.index(min_time)
            exit_count = exit_server(servers_clients, servers_history, servers_time, server_generate, server_jump, exit_count, exit_history, index)
        # Calculo de la siguiente operacion
        min_time = min(arrive_time, min(servers_time))

    shape = [len(i) for i in servers_clients]
    # Posibles operaciones: Salida de Servidor
    while max(shape) > 0:
        min_time = min(servers_time)
        index = servers_time.index(min_time)
        exit_count = exit_server(servers_clients, servers_history, servers_time, server_generate, server_jump, exit_count, exit_history, index)
        shape = [len(i) for i in servers_clients]
    
    # Se muestran los clientes atendidos por cada Servidor y sus respectivos tiempos de atencion en cada uno
    print(f'{arrive_count} clientes recibidos')
    for i in servers_history:
        print(f'{len(i)} clientes recibos:')
        for j in i:
            print(f'{j}: {i[j]}')
        print()
    print(f'{exit_count} clientes atendidos:\n{exit_history}')




# Tipos de generadores de variables aleatoria
var = [exponential, normal, gumbel, laplace, logistic, rayleigh]

# Cantidad de Servidores
n = 5

# Probabilidad de pasar del Servidor i al Servidor j (determinado de manera random)
p = [.9 for i in range(n)]

# Seleccion de generadores para la simulacion
generate = choices(var, k=n)

simulate(n, 30, generate, p)