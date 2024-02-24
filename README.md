# Sim-Project1


# Proyecto: Simulación de Eventos Discretos

Este proyecto tiene como objetivo desarrollar una simulación de eventos discretos para analizar y entender mejor ciertos fenómenos. A través de este trabajo, buscamos aplicar los principios de la simulación de eventos discretos para modelar y experimentar con estos fenómenos, y obtener resultados que nos ayuden a tomar decisiones informadas.

El proyecto debe ser entregado en un repositorio público de GitHub. Este repositorio debe contener tanto el código fuente de tu simulación como el informe del proyecto en LaTeX. Asegúrese de que el repositorio esté bien organizado y que tanto el código como el informe sean fácilmente accesibles.

# Estructura del informe

## S1 Introducción

- Breve descripción del proyecto
- Objetivos y metas
- El sistema específico a simular y las variables de interés que cada equipo debe analizar se les hará saber por esta misma vía.
- Variables que describen el problema

## S2 Detalles de Implementación

- Pasos seguidos para la implementación

## S3 Resultados y Experimentos

- Hallazgos de la simulación
- Interpretación de los resultados
- Necesidad de realizar el análisis estadístico de la simulación (Variables de interés)
- Análisis de parada de la simulación

## S4 Modelo Matemático

- Descripción del modelo de simulación
- Supuestos y restricciones


## Tema 5 n servidores en serie

Los clientes llegan a un sistema que tiene n servidores, y las llegadas distribuye M. Cada cliente que llega debe ser atendido primero por el servidor 1 y, al completar el servicio en el servidor 1, el cliente pasa al servidor 2.

Cuando un cliente llega, entra en servicio con el servidor 1 si ese servidor está libre, o se une a la cola del servidor 1 en caso contrario. De manera similar, cuando el cliente completa el servicio en el servidor 1, entra en servicio con el servidor 2 si ese servidor está libre, o se une a su cola y asi sucesivamente. Después de ser atendido en el servidor n, el cliente abandona el sistema.

Los tiempos de servicio en el servidor i tienen la distribución Gi.

En servidor i con una probabilidad p se puede saltar a la cola del servidor j.
