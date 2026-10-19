import copy
from typing import List
from collections import deque
from modelos import Proceso, BloqueGantt

class SimuladorPlanificacion:
    def __init__(self, procesos_iniciales: List[Proceso]):
        self.procesos_base = procesos_iniciales
        self.procesos_simulados = []
        self.diagrama_gantt: List[BloqueGantt] = []
        
    def limpiar_estado(self):
        self.procesos_simulados = copy.deepcopy(self.procesos_base)
        self.diagrama_gantt = []

    def ejecutar_fcfs(self):
        self.limpiar_estado()
        self.procesos_simulados.sort(key=lambda p: p.tiempo_llegada)
        tiempo_actual = 0
        
        for p in self.procesos_simulados:
            if tiempo_actual < p.tiempo_llegada:
                tiempo_actual = p.tiempo_llegada
                
            p.tiempo_comienzo = tiempo_actual
            p.tiempo_finalizacion = tiempo_actual + p.rafaga_cpu
            p.tiempo_retorno = p.tiempo_finalizacion - p.tiempo_llegada
            p.tiempo_espera = p.tiempo_retorno - p.rafaga_cpu
            p.tiempo_restante = 0
            
            self.diagrama_gantt.append(BloqueGantt(p.pid, p.tiempo_comienzo, p.tiempo_finalizacion))
            tiempo_actual = p.tiempo_finalizacion
            
        return self.procesos_simulados, self.diagrama_gantt

    def ejecutar_sjf(self):
        self.limpiar_estado()
        procesos_pendientes = sorted(self.procesos_simulados, key=lambda p: p.tiempo_llegada)
        cola_listos = []
        tiempo_actual = 0
        
        while procesos_pendientes or cola_listos:
            while procesos_pendientes and procesos_pendientes[0].tiempo_llegada <= tiempo_actual:
                cola_listos.append(procesos_pendientes.pop(0))
                
            if not cola_listos:
                tiempo_actual = procesos_pendientes[0].tiempo_llegada
                continue
                
            cola_listos.sort(key=lambda p: (p.rafaga_cpu, p.tiempo_llegada))
            p_actual = cola_listos.pop(0)
            
            p_actual.tiempo_comienzo = tiempo_actual
            p_actual.tiempo_finalizacion = tiempo_actual + p_actual.rafaga_cpu
            p_actual.tiempo_retorno = p_actual.tiempo_finalizacion - p_actual.tiempo_llegada
            p_actual.tiempo_espera = p_actual.tiempo_retorno - p_actual.rafaga_cpu
            p_actual.tiempo_restante = 0
            
            self.diagrama_gantt.append(BloqueGantt(p_actual.pid, tiempo_actual, p_actual.tiempo_finalizacion))
            tiempo_actual = p_actual.tiempo_finalizacion
            
        return self.procesos_simulados, self.diagrama_gantt

    def ejecutar_srtf(self):
        self.limpiar_estado()
        procesos_pendientes = sorted(self.procesos_simulados, key=lambda p: p.tiempo_llegada)
        cola_listos = []
        tiempo_actual = 0
        
        while procesos_pendientes or cola_listos:
            while procesos_pendientes and procesos_pendientes[0].tiempo_llegada <= tiempo_actual:
                cola_listos.append(procesos_pendientes.pop(0))
                
            if not cola_listos:
                tiempo_actual = procesos_pendientes[0].tiempo_llegada
                continue
                
            cola_listos.sort(key=lambda p: (p.tiempo_restante, p.tiempo_llegada))
            p_actual = cola_listos.pop(0)
            
            if p_actual.tiempo_comienzo == -1:
                p_actual.tiempo_comienzo = tiempo_actual
                
            if procesos_pendientes:
                siguiente_llegada = procesos_pendientes[0].tiempo_llegada
                tiempo_ejecucion = min(p_actual.tiempo_restante, siguiente_llegada - tiempo_actual)
            else:
                tiempo_ejecucion = p_actual.tiempo_restante
                
            inicio_bloque = tiempo_actual
            tiempo_actual += tiempo_ejecucion
            p_actual.tiempo_restante -= tiempo_ejecucion
            
            if self.diagrama_gantt and self.diagrama_gantt[-1].pid == p_actual.pid and self.diagrama_gantt[-1].fin == inicio_bloque:
                self.diagrama_gantt[-1].fin = tiempo_actual
            else:
                self.diagrama_gantt.append(BloqueGantt(p_actual.pid, inicio_bloque, tiempo_actual))
            
            if p_actual.tiempo_restante > 0:
                cola_listos.append(p_actual)
            else:
                p_actual.tiempo_finalizacion = tiempo_actual
                p_actual.tiempo_retorno = p_actual.tiempo_finalizacion - p_actual.tiempo_llegada
                p_actual.tiempo_espera = p_actual.tiempo_retorno - p_actual.rafaga_cpu
                
        return self.procesos_simulados, self.diagrama_gantt

    def ejecutar_rr(self, quantum: int):
        self.limpiar_estado()
        procesos_pendientes = sorted(self.procesos_simulados, key=lambda p: p.tiempo_llegada)
        cola_listos = deque()
        tiempo_actual = 0
        
        while procesos_pendientes or cola_listos:
            while procesos_pendientes and procesos_pendientes[0].tiempo_llegada <= tiempo_actual:
                cola_listos.append(procesos_pendientes.pop(0))
                
            if not cola_listos:
                tiempo_actual = procesos_pendientes[0].tiempo_llegada
                continue
                
            p_actual = cola_listos.popleft()
            
            if p_actual.tiempo_comienzo == -1:
                p_actual.tiempo_comienzo = tiempo_actual
                
            tiempo_ejecucion = min(p_actual.tiempo_restante, quantum)
            inicio_bloque = tiempo_actual
            
            tiempo_actual += tiempo_ejecucion
            p_actual.tiempo_restante -= tiempo_ejecucion
            
            self.diagrama_gantt.append(BloqueGantt(p_actual.pid, inicio_bloque, tiempo_actual))
            
            while procesos_pendientes and procesos_pendientes[0].tiempo_llegada <= tiempo_actual:
                cola_listos.append(procesos_pendientes.pop(0))
                
            if p_actual.tiempo_restante > 0:
                cola_listos.append(p_actual)
            else:
                p_actual.tiempo_finalizacion = tiempo_actual
                p_actual.tiempo_retorno = p_actual.tiempo_finalizacion - p_actual.tiempo_llegada
                p_actual.tiempo_espera = p_actual.tiempo_retorno - p_actual.rafaga_cpu
                
        return self.procesos_simulados, self.diagrama_gantt

    def calcular_promedios(self):
        if not self.procesos_simulados: return 0.0, 0.0
        n = len(self.procesos_simulados)
        prom_espera = sum(p.tiempo_espera for p in self.procesos_simulados) / n
        prom_retorno = sum(p.tiempo_retorno for p in self.procesos_simulados) / n
        return prom_espera, prom_retorno

    def generar_matriz_estados(self):
        if not self.procesos_simulados:
            return {}, 0
            
        tiempo_maximo = max(p.tiempo_finalizacion for p in self.procesos_simulados)
        matriz = {}
        
        for p in self.procesos_simulados:
            estados = ['N'] * tiempo_maximo
            for t in range(p.tiempo_llegada, p.tiempo_finalizacion):
                estados[t] = 'L'
            for t in range(p.tiempo_finalizacion, tiempo_maximo):
                estados[t] = 'T'
            matriz[p.pid] = estados
            
        for b in self.diagrama_gantt:
            for t in range(b.inicio, b.fin):
                matriz[b.pid][t] = 'E'
                
        return matriz, tiempo_maximo