from dataclasses import dataclass

@dataclass
class Proceso:
    pid: str
    tiempo_llegada: int
    rafaga_cpu: int
    
    tiempo_restante: int = 0
    tiempo_comienzo: int = -1
    tiempo_finalizacion: int = 0
    tiempo_espera: int = 0
    tiempo_retorno: int = 0

    def __post_init__(self):
        self.tiempo_restante = self.rafaga_cpu

@dataclass
class BloqueGantt:
    pid: str
    inicio: int
    fin: int