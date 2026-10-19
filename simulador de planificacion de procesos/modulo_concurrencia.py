import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import queue

class VentanaConcurrencia:
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        self.root.title("Simulación Visual de Concurrencia")
        self.root.geometry("950x650")
        self.root.configure(bg="#1e1e2f")
        
        self.simulacion_activa = False
        self.hilos = []
        self.cola_eventos = queue.Queue() 
        
        self._configurar_estilos()
        self._crear_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        self.procesar_cola_eventos()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("TCombobox", fieldbackground="#2b2b36", background="#1e1e2f", foreground="white")

    def _crear_widgets(self):
        # 1. Panel de Control (Flat Design)
        frame_control = tk.Frame(self.root, bg="#2b2b36", padx=15, pady=15)
        frame_control.pack(fill="x", padx=20, pady=15)
        
        tk.Label(frame_control, text="Problema Clásico:", font=("Helvetica", 11, "bold"), fg="#a9b7c6", bg="#2b2b36").pack(side="left", padx=10)
        
        self.combo_problemas = ttk.Combobox(frame_control, values=[
            "1. Productor - Consumidor",
            "2. Filósofos Comensales",
            "3. Barbero Dormilón",
            "4. Lectores - Escritores (Sin Inanición)",
            "5. Problema de los Fumadores"
        ], state="readonly", width=35, font=("Helvetica", 10))
        self.combo_problemas.current(0)
        self.combo_problemas.pack(side="left", padx=10)
        
        self.btn_iniciar = tk.Button(frame_control, text="▶ INICIAR SIMULACIÓN", font=("Helvetica", 10, "bold"), bg="#20c997", fg="#1e1e2f", relief="flat", padx=15, pady=4, command=self.iniciar_simulacion)
        self.btn_iniciar.pack(side="left", padx=10)
        
        self.btn_detener = tk.Button(frame_control, text="⏹ DETENER", font=("Helvetica", 10, "bold"), bg="#e74c3c", fg="white", relief="flat", padx=15, pady=4, state="disabled", command=self.detener_simulacion)
        self.btn_detener.pack(side="left", padx=5)

        # 2. Panel de Simulación Visual en Vivo
        frame_visual = tk.Frame(self.root, bg="#1a1a24", pady=20, bd=0)
        frame_visual.pack(fill="x", padx=20, pady=(0, 15))
        
        tk.Label(frame_visual, text="SIMULACIÓN EN VIVO", font=("Helvetica", 10, "bold"), fg="#f39c12", bg="#1a1a24").pack()
        
        self.lbl_visual = tk.Label(frame_visual, text="[ Seleccione un problema y presione Iniciar ]", font=("Segoe UI Emoji", 20), fg="white", bg="#1a1a24", pady=15)
        self.lbl_visual.pack(expand=True)

        # 3. Consola de Logs (Identificación de Zonas Críticas)
        frame_consola = tk.Frame(self.root, bg="#1e1e2f")
        frame_consola.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        tk.Label(frame_consola, text="Monitor de Ejecución (Sincronización y Secciones Críticas)", font=("Helvetica", 10, "bold"), fg="#a9b7c6", bg="#1e1e2f").pack(anchor="w", pady=(0, 5))
        
        self.consola = tk.Text(frame_consola, bg="#11111a", fg="#4ade80", font=("Courier", 11), state="disabled", relief="flat", padx=10, pady=10)
        scroll_y = ttk.Scrollbar(frame_consola, orient="vertical", command=self.consola.yview)
        self.consola.configure(yscrollcommand=scroll_y.set)
        
        scroll_y.pack(side="right", fill="y")
        self.consola.pack(side="left", fill="both", expand=True)

    def log(self, mensaje):
        self.cola_eventos.put({'tipo': 'log', 'datos': mensaje})

    def actualizar_visual(self, estado):
        self.cola_eventos.put({'tipo': 'visual', 'datos': estado})

    def procesar_cola_eventos(self):
        while not self.cola_eventos.empty():
            evento = self.cola_eventos.get()
            if evento['tipo'] == 'log':
                self.consola.config(state="normal")
                self.consola.insert("end", evento['datos'] + "\n")
                self.consola.see("end")
                self.consola.config(state="disabled")
            elif evento['tipo'] == 'visual':
                self.lbl_visual.config(text=evento['datos'])
        self.root.after(50, self.procesar_cola_eventos)

    def iniciar_simulacion(self):
        self.consola.config(state="normal")
        self.consola.delete(1.0, "end")
        self.consola.config(state="disabled")
        
        self.simulacion_activa = True
        self.btn_iniciar.config(state="disabled", bg="#7f8c8d")
        self.btn_detener.config(state="normal", bg="#e74c3c")
        self.combo_problemas.config(state="disabled")
        
        seleccion = self.combo_problemas.get()
        self.hilos = []
        
        if "Productor" in seleccion: self.ejecutar_productor_consumidor()
        elif "Filósofos" in seleccion: self.ejecutar_filosofos()
        elif "Barbero" in seleccion: self.ejecutar_barbero()
        elif "Lectores" in seleccion: self.ejecutar_lectores_escritores()
        elif "Fumadores" in seleccion: self.ejecutar_fumadores()

    def detener_simulacion(self):
        self.log("\n[SISTEMA] Sincronizando parada. Liberando Secciones Críticas...")
        self.simulacion_activa = False
        self.btn_iniciar.config(state="normal", bg="#20c997")
        self.btn_detener.config(state="disabled", bg="#7f8c8d")
        self.combo_problemas.config(state="normal")
        self.actualizar_visual("[ Simulación Detenida ]")

    def cerrar_ventana(self):
        self.simulacion_activa = False
        self.root.destroy()

    # =========================================================================
    # 1. PRODUCTOR - CONSUMIDOR (Simulación Visual de Buffer)
    # =========================================================================
    def ejecutar_productor_consumidor(self):
        buffer = []
        capacidad = 5
        mutex = threading.Lock()  # Protege la Sección Crítica (el buffer)
        sem_llenos = threading.Semaphore(0)
        sem_vacios = threading.Semaphore(capacidad)

        def renderizar_buffer():
            slots = "".join(["📦" if i < len(buffer) else "🔲" for i in range(capacidad)])
            self.actualizar_visual(f"Cinta Transportadora:\n{slots}")

        def productor():
            item = 1
            while self.simulacion_activa:
                if sem_vacios.acquire(timeout=1):
                    with mutex: # [ZONA CRÍTICA]
                        buffer.append(item)
                        self.log(f"[SINCRONIZACIÓN] Productor ingresa a Zona Crítica. Produjo 📦 {item}")
                        renderizar_buffer()
                        item += 1
                    sem_llenos.release()
                time.sleep(random.uniform(0.5, 1.5))

        def consumidor():
            while self.simulacion_activa:
                if sem_llenos.acquire(timeout=1):
                    with mutex: # [ZONA CRÍTICA]
                        item = buffer.pop(0)
                        self.log(f"[SINCRONIZACIÓN] Consumidor en Zona Crítica. Retiró 📦 {item}")
                        renderizar_buffer()
                    sem_vacios.release()
                time.sleep(random.uniform(1.0, 2.0))

        renderizar_buffer()
        h_prod = threading.Thread(target=productor); self.hilos.append(h_prod); h_prod.start()
        h_cons = threading.Thread(target=consumidor); self.hilos.append(h_cons); h_cons.start()

    # =========================================================================
    # 2. FILÓSOFOS COMENSALES (Simulación Visual Circular)
    # =========================================================================
    def ejecutar_filosofos(self):
        num_filosofos = 5
        tenedores = [threading.Lock() for _ in range(num_filosofos)]
        estados = ["🤔"] * num_filosofos

        def renderizar_mesa():
            visual = "Mesa Redonda:\n" + "  ".join([f"F{i+1}:{estados[i]}" for i in range(num_filosofos)])
            self.actualizar_visual(visual)

        def filosofo(id_fil):
            izq, der = id_fil, (id_fil + 1) % num_filosofos
            while self.simulacion_activa:
                estados[id_fil] = "🤔"
                renderizar_mesa()
                time.sleep(random.uniform(1, 2))
                
                estados[id_fil] = "⏳" # Esperando
                renderizar_mesa()
                
                # Sincronización asimétrica para evitar Deadlock y mitigar Inanición
                if id_fil == num_filosofos - 1:
                    tenedores[der].acquire(); tenedores[izq].acquire()
                else:
                    tenedores[izq].acquire(); tenedores[der].acquire()
                
                # [ZONA CRÍTICA]
                estados[id_fil] = "🍝"
                self.log(f"[ZONA CRÍTICA] Filósofo {id_fil+1} comiendo con tenedores {izq} y {der}")
                renderizar_mesa()
                time.sleep(random.uniform(1, 2))
                
                tenedores[izq].release(); tenedores[der].release()

        renderizar_mesa()
        for i in range(num_filosofos):
            t = threading.Thread(target=filosofo, args=(i,)); self.hilos.append(t); t.start()

    # =========================================================================
    # 3. BARBERO DORMILÓN (Simulación Visual de Sillas)
    # =========================================================================
    def ejecutar_barbero(self):
        sillas_espera = 3
        clientes_esperando = [0]
        estado_barbero = ["💤"]
        mutex = threading.Lock()
        sem_barbero, sem_clientes = threading.Semaphore(0), threading.Semaphore(0)

        def renderizar_barberia():
            sillas = "".join(["🧍" for _ in range(clientes_esperando[0])]) + "".join(["🪑" for _ in range(sillas_espera - clientes_esperando[0])])
            self.actualizar_visual(f"Barbero: {estado_barbero[0]}    Sala de Espera: {sillas}")

        def barbero():
            while self.simulacion_activa:
                estado_barbero[0] = "💤"
                renderizar_barberia()
                if sem_clientes.acquire(timeout=2):
                    if not self.simulacion_activa: break
                    with mutex: clientes_esperando[0] -= 1
                    sem_barbero.release()
                    
                    estado_barbero[0] = "✂️"
                    self.log("[ZONA CRÍTICA] Barbero cortando el cabello.")
                    renderizar_barberia()
                    time.sleep(random.uniform(1, 2))

        def generador_clientes():
            id_cliente = 1
            while self.simulacion_activa:
                time.sleep(random.uniform(0.5, 2))
                with mutex:
                    if clientes_esperando[0] < sillas_espera:
                        clientes_esperando[0] += 1
                        self.log(f"[SINCRONIZACIÓN] Cliente {id_cliente} toma asiento.")
                        sem_clientes.release()
                        renderizar_barberia()
                        sem_barbero.acquire()
                    else:
                        self.log(f"[RECHAZO] Cliente {id_cliente} encuentra tienda llena 😡.")
                id_cliente += 1

        renderizar_barberia()
        t_barbero = threading.Thread(target=barbero); self.hilos.append(t_barbero); t_barbero.start()
        t_clientes = threading.Thread(target=generador_clientes); self.hilos.append(t_clientes); t_clientes.start()

    # =========================================================================
    # 4. LECTORES - ESCRITORES (Con Torniquete para evitar Inanición)
    # =========================================================================
    def ejecutar_lectores_escritores(self):
        lectores_activos = [0]
        estado_db = ["💾 LIBRE"]
        
        mutex_lectores = threading.Lock()
        recurso_db = threading.Lock() # Bloquea la base de datos
        torniquete = threading.Lock() # SOLUCIÓN A INANICIÓN: Fila justa

        def renderizar_db():
            self.actualizar_visual(f"Base de Datos: {estado_db[0]}\nLectores Activos: {'👁️' * lectores_activos[0]}")

        def lector(id_lec):
            while self.simulacion_activa:
                time.sleep(random.uniform(1, 3))
                
                # El Torniquete asegura que si un escritor está esperando, los nuevos lectores formen fila atrás
                torniquete.acquire()
                with mutex_lectores:
                    lectores_activos[0] += 1
                    if lectores_activos[0] == 1: 
                        recurso_db.acquire() # Primer lector bloquea DB para escritores
                torniquete.release()
                
                estado_db[0] = "📖 LEYENDO"
                self.log(f"[SINCRONIZACIÓN] Lector {id_lec} accediendo a BD.")
                renderizar_db()
                time.sleep(random.uniform(1, 2))
                
                with mutex_lectores:
                    lectores_activos[0] -= 1
                    if lectores_activos[0] == 0: 
                        estado_db[0] = "💾 LIBRE"
                        recurso_db.release()
                renderizar_db()

        def escritor(id_esc):
            while self.simulacion_activa:
                time.sleep(random.uniform(2, 4))
                self.log(f"[TICK] Escritor {id_esc} solicita turno en el Torniquete.")
                
                torniquete.acquire() # Solicita turno prioritario
                recurso_db.acquire() # [ZONA CRÍTICA EXCLUSIVA]
                
                estado_db[0] = "✏️ ESCRIBIENDO"
                self.log(f"[ZONA CRÍTICA] Escritor {id_esc} alterando datos de BD de forma exclusiva.")
                renderizar_db()
                time.sleep(random.uniform(1.5, 2.5))
                
                estado_db[0] = "💾 LIBRE"
                recurso_db.release()
                torniquete.release()
                renderizar_db()

        renderizar_db()
        for i in range(3):
            t = threading.Thread(target=lector, args=(i+1,)); self.hilos.append(t); t.start()
        for i in range(2):
            t = threading.Thread(target=escritor, args=(i+1,)); self.hilos.append(t); t.start()

    # =========================================================================
    # 5. FUMADORES (Agente y Recursos Estrictos)
    # =========================================================================
    def ejecutar_fumadores(self):
        sem_tabaco, sem_papel, sem_fosforo = threading.Semaphore(0), threading.Semaphore(0), threading.Semaphore(0)
        sem_agente = threading.Semaphore(1)
        mesa = ["🔲", "🔲"]

        def renderizar_mesa():
            self.actualizar_visual(f"Mesa del Agente:\n[ {mesa[0]} ]  [ {mesa[1]} ]")

        def agente():
            while self.simulacion_activa:
                if sem_agente.acquire(timeout=1):
                    if not self.simulacion_activa: break
                    ingredientes = random.choice([1, 2, 3])
                    if ingredientes == 1:
                        mesa[0], mesa[1] = "🌿 Tabaco", "📜 Papel"
                        self.log("[SINCRONIZACIÓN] Agente libera recursos. Despierta fumador de Fósforos.")
                        sem_fosforo.release()
                    elif ingredientes == 2:
                        mesa[0], mesa[1] = "📜 Papel", "🔥 Fósforos"
                        self.log("[SINCRONIZACIÓN] Agente libera recursos. Despierta fumador de Tabaco.")
                        sem_tabaco.release()
                    else:
                        mesa[0], mesa[1] = "🌿 Tabaco", "🔥 Fósforos"
                        self.log("[SINCRONIZACIÓN] Agente libera recursos. Despierta fumador de Papel.")
                        sem_papel.release()
                    renderizar_mesa()

        def fumador(nombre, sem_ingrediente, emoji):
            while self.simulacion_activa:
                if sem_ingrediente.acquire(timeout=2):
                    self.log(f"[ZONA CRÍTICA] Fumador con {nombre} toma recursos y comienza a fumar 🚬.")
                    mesa[0], mesa[1] = "💨 Humo", "💨 Humo"
                    renderizar_mesa()
                    time.sleep(random.uniform(1.5, 2.5))
                    
                    mesa[0], mesa[1] = "🔲", "🔲"
                    sem_agente.release()

        renderizar_mesa()
        self.hilos.append(threading.Thread(target=agente))
        self.hilos.append(threading.Thread(target=fumador, args=("Fósforos", sem_fosforo, "🔥")))
        self.hilos.append(threading.Thread(target=fumador, args=("Tabaco", sem_tabaco, "🌿")))
        self.hilos.append(threading.Thread(target=fumador, args=("Papel", sem_papel, "📜")))
        for t in self.hilos: t.start()