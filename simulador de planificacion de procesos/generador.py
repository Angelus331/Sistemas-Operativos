import random
import csv

def generar_datos(cantidad=300, archivo="procesos_300.csv"):
    # Generamos los datos aleatorios
    procesos = []
    for i in range(1, cantidad + 1):
        pid = f"P{i}"
        llegada = random.randint(0, 300) # Tiempos de llegada entre 0 y 300
        rafaga = random.randint(1, 25)   # Ráfagas entre 1 y 25 unidades de tiempo
        procesos.append([pid, llegada, rafaga])
    
    # Es vital ordenar los datos por llegada para simular un flujo realista en el CSV
    procesos.sort(key=lambda x: x[1])
    
    # Escribimos el archivo CSV
    with open(archivo, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["PID", "Llegada", "Rafaga"])
        writer.writerows(procesos)
        
    print(f"Se han generado {cantidad} procesos en '{archivo}'")

if __name__ == "__main__":
    generar_datos()