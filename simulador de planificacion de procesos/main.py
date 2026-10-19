import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from modelos import Proceso
from simulador import SimuladorPlanificacion
from graficos import dibujar_gantt
from modulo_concurrencia import VentanaConcurrencia 

class InterfazSimulador:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Planificación de SO")
        self.root.geometry("880x750")
        self.root.configure(bg="#1e1e2f")
        self.lista_procesos = []
        self.ultimo_simulador = None
        
        self._configurar_estilos()
        self._crear_widgets()
        
    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Treeview", 
                        background="#2b2b36", 
                        foreground="white", 
                        fieldbackground="#2b2b36", 
                        rowheight=30, 
                        borderwidth=0,
                        font=('Helvetica', 10))
        style.configure("Treeview.Heading", 
                        background="#1a1a24", 
                        foreground="#20c997", 
                        font=('Helvetica', 11, 'bold'),
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#347083')])
        style.configure("TLabelframe", background="#1e1e2f", borderwidth=0)
        style.configure("TLabelframe.Label", background="#1e1e2f", foreground="#a9b7c6", font=('Helvetica', 11, 'bold'))

    def _crear_widgets(self):
        frame_indicadores = tk.Frame(self.root, bg="#1a1a24", pady=20)
        frame_indicadores.pack(fill="x")
        
        self.lbl_num_procesos = tk.Label(frame_indicadores, text="Procesos en Cola: 0", font=("Helvetica", 16, "bold"), fg="#20c997", bg="#1a1a24")
        self.lbl_num_procesos.pack(side="left", expand=True)
        
        self.lbl_cpu = tk.Label(frame_indicadores, text="Carga solicitada: 0 u/t", font=("Helvetica", 16, "bold"), fg="#3498db", bg="#1a1a24")
        self.lbl_cpu.pack(side="left", expand=True)

        frame_input = tk.Frame(self.root, bg="#2b2b36", padx=15, pady=15)
        frame_input.pack(fill="x", padx=20, pady=20)
        
        tk.Label(frame_input, text="Llegada:", font=("Helvetica", 11), fg="white", bg="#2b2b36").grid(row=0, column=0, padx=5)
        self.entry_llegada = tk.Entry(frame_input, width=8, font=("Helvetica", 11), bg="#1e1e2f", fg="white", insertbackground="white", relief="flat")
        self.entry_llegada.grid(row=0, column=1, padx=5, ipady=4)
        
        tk.Label(frame_input, text="Ráfaga:", font=("Helvetica", 11), fg="white", bg="#2b2b36").grid(row=0, column=2, padx=5)
        self.entry_rafaga = tk.Entry(frame_input, width=8, font=("Helvetica", 11), bg="#1e1e2f", fg="white", insertbackground="white", relief="flat")
        self.entry_rafaga.grid(row=0, column=3, padx=5, ipady=4)
        
        btn_agregar = tk.Button(frame_input, text="Agregar", font=("Helvetica", 10, "bold"), bg="#20c997", fg="#1e1e2f", relief="flat", padx=10, pady=2, command=self.agregar_proceso)
        btn_agregar.grid(row=0, column=4, padx=15)
        
        btn_cargar = tk.Button(frame_input, text="Cargar CSV", font=("Helvetica", 10, "bold"), bg="#f39c12", fg="#1e1e2f", relief="flat", padx=10, pady=2, command=self.cargar_archivo)
        btn_cargar.grid(row=0, column=5, padx=5)

        frame_tabla = tk.Frame(self.root, bg="#1e1e2f")
        frame_tabla.pack(fill="both", expand=True, padx=20)
        
        columnas = ("pid", "llegada", "rafaga", "finalizacion", "retorno", "espera")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=8)
        
        self.tabla.heading("pid", text="Proceso")
        self.tabla.heading("llegada", text="Llegada")
        self.tabla.heading("rafaga", text="Ráfaga")
        self.tabla.heading("finalizacion", text="Finalización")
        self.tabla.heading("retorno", text="T. Retorno")
        self.tabla.heading("espera", text="T. Espera")
        
        for col in columnas:
            self.tabla.column(col, anchor="center", width=120)
            
        self.tabla.pack(fill="both", expand=True)
        
        btn_detalle_proc = tk.Button(frame_tabla, text="Inspeccionar Proceso Seleccionado", font=("Helvetica", 10), bg="#34495e", fg="white", relief="flat", padx=10, pady=4, command=self.ver_detalle_proceso)
        btn_detalle_proc.pack(pady=10)

        frame_control = tk.Frame(self.root, bg="#2b2b36", padx=15, pady=15)
        frame_control.pack(fill="x", padx=20, pady=20)
        
        tk.Label(frame_control, text="Política:", font=("Helvetica", 11), fg="white", bg="#2b2b36").grid(row=0, column=0, padx=5)
        self.combo_algo = ttk.Combobox(frame_control, values=["FCFS", "SJF", "SRTF", "Round Robin"], state="readonly", width=12, font=("Helvetica", 10))
        self.combo_algo.current(0)
        self.combo_algo.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_control, text="Quantum:", font=("Helvetica", 11), fg="white", bg="#2b2b36").grid(row=0, column=2, padx=5)
        self.entry_quantum = tk.Entry(frame_control, width=5, font=("Helvetica", 11), bg="#1e1e2f", fg="white", insertbackground="white", relief="flat")
        self.entry_quantum.insert(0, "2")
        self.entry_quantum.grid(row=0, column=3, padx=5, ipady=4)
        
        btn_simular = tk.Button(frame_control, text="EJECUTAR", font=("Helvetica", 10, "bold"), bg="#3498db", fg="white", relief="flat", padx=15, pady=4, command=self.ejecutar)
        btn_simular.grid(row=0, column=4, padx=15)
        
        self.btn_detalles = tk.Button(frame_control, text="Ver Detalles y Trazas", font=("Helvetica", 10), bg="#9b59b6", fg="white", relief="flat", padx=10, pady=4, state="disabled", command=self.abrir_ventana_detalles)
        self.btn_detalles.grid(row=0, column=5, padx=10)
        
        self.btn_concurrencia = tk.Button(frame_control, text="Problemas Concurrencia", font=("Helvetica", 10), bg="#e67e22", fg="white", relief="flat", padx=10, pady=4, command=self.abrir_modulo_concurrencia)
        self.btn_concurrencia.grid(row=0, column=6, padx=10)

        self.lbl_linea_tiempo = tk.Label(self.root, text="Flujo: [Esperando simulación...]", font=("Courier", 10), bg="#1a1a24", fg="#2ecc71", pady=8)
        self.lbl_linea_tiempo.pack(fill="x", side="bottom")

    def actualizar_indicadores(self, uso_cpu=None):
        num = len(self.lista_procesos)
        carga_total = sum(p.rafaga_cpu for p in self.lista_procesos)
        self.lbl_num_procesos.config(text=f"Procesos en Cola: {num}")
        if uso_cpu is None:
            self.lbl_cpu.config(text=f"Carga solicitada: {carga_total} u/t")
        else:
            self.lbl_cpu.config(text=f"Carga CPU: {carga_total} u/t  |  Uso Total: {uso_cpu}%")

    def agregar_proceso(self):
        pid_automatico = f"P{len(self.lista_procesos) + 1}"
        try:
            llegada = int(self.entry_llegada.get())
            rafaga = int(self.entry_rafaga.get())
            nuevo_proceso = Proceso(pid_automatico, llegada, rafaga)
            self.lista_procesos.append(nuevo_proceso)
            self.tabla.insert("", "end", values=(pid_automatico, llegada, rafaga, "-", "-", "-"))
            self.actualizar_indicadores()
            self.entry_llegada.delete(0, 'end')
            self.entry_rafaga.delete(0, 'end')
        except ValueError:
            messagebox.showerror("Error", "Los tiempos deben ser números enteros.")

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
        if not ruta: return
        try:
            with open(ruta, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    nuevo_proceso = Proceso(row['PID'], int(row['Llegada']), int(row['Rafaga']))
                    self.lista_procesos.append(nuevo_proceso)
                    self.tabla.insert("", "end", values=(row['PID'], row['Llegada'], row['Rafaga'], "-", "-", "-"))
            self.actualizar_indicadores()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar archivo. Verifique cabeceras PID,Llegada,Rafaga.\n{e}")

    def refrescar_tabla_resultados(self, procesos_simulados):
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        for p in sorted(procesos_simulados, key=lambda x: int(x.pid[1:])):
            self.tabla.insert("", "end", values=(p.pid, p.tiempo_llegada, p.rafaga_cpu, p.tiempo_finalizacion, p.tiempo_retorno, p.tiempo_espera))

    def abrir_ventana_eleccion_grafico(self, gantt, titulo):
        ventana = tk.Toplevel(self.root)
        ventana.title("Elegir Estilo")
        
        ancho, alto = 400, 180
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (ancho // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (alto // 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
        ventana.configure(bg="#2b2b36")
        ventana.transient(self.root) 
        ventana.grab_set() 
        
        tk.Label(ventana, text="¿Cómo deseas visualizar el Diagrama?", font=("Helvetica", 12, "bold"), bg="#2b2b36", fg="white").pack(pady=25)
        
        def elegir(estilo_escalera):
            ventana.destroy()
            dibujar_gantt(gantt, titulo, es_expulsivo=estilo_escalera)
            
        frame_btns = tk.Frame(ventana, bg="#2b2b36")
        frame_btns.pack(pady=10)
        
        btn_linea = tk.Button(frame_btns, text="Línea Continua", font=("Helvetica", 10), bg="#347083", fg="white", width=15, relief="flat", pady=5, command=lambda: elegir(False))
        btn_linea.pack(side="left", padx=10)
        
        btn_escalera = tk.Button(frame_btns, text="Múltiples Filas", font=("Helvetica", 10), bg="#17a2b8", fg="white", width=15, relief="flat", pady=5, command=lambda: elegir(True))
        btn_escalera.pack(side="left", padx=10)

    def ejecutar(self):
        if not self.lista_procesos:
            messagebox.showwarning("Advertencia", "Agregue al menos un proceso.")
            return
            
        self.ultimo_simulador = SimuladorPlanificacion(self.lista_procesos)
        algoritmo = self.combo_algo.get()
        
        try:
            if algoritmo == "FCFS": procesos, gantt = self.ultimo_simulador.ejecutar_fcfs()
            elif algoritmo == "SJF": procesos, gantt = self.ultimo_simulador.ejecutar_sjf()
            elif algoritmo == "SRTF": procesos, gantt = self.ultimo_simulador.ejecutar_srtf()
            elif algoritmo == "Round Robin": procesos, gantt = self.ultimo_simulador.ejecutar_rr(int(self.entry_quantum.get()))
            
            self.refrescar_tabla_resultados(procesos)
            
            linea = " ➔ ".join([f"{b.pid} ({b.inicio}-{b.fin})" for b in gantt])
            self.lbl_linea_tiempo.config(text=f"Flujo: [ {linea} ]")
            
            tiempo_total_simulacion = max(p.tiempo_finalizacion for p in procesos)
            carga_cpu = sum(p.rafaga_cpu for p in procesos)
            uso_porcentaje = round((carga_cpu / tiempo_total_simulacion) * 100, 2) if tiempo_total_simulacion > 0 else 0
            self.actualizar_indicadores(uso_cpu=uso_porcentaje)
            
            self.btn_detalles.config(state="normal")
            self.abrir_ventana_eleccion_grafico(gantt, f"Diagrama de Gantt - {algoritmo}")
            
        except ValueError:
            messagebox.showerror("Error", "Parámetros inválidos (Revisar Quantum).")

    def ver_detalle_proceso(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un proceso de la tabla primero.")
            return

        valores = self.tabla.item(seleccion[0])['values']
        pid_seleccionado = str(valores[0])

        proceso = None
        if self.ultimo_simulador and self.ultimo_simulador.procesos_simulados:
            for p in self.ultimo_simulador.procesos_simulados:
                if p.pid == pid_seleccionado:
                    proceso = p
                    break
        else:
            for p in self.lista_procesos:
                if p.pid == pid_seleccionado:
                    proceso = p
                    break

        if not proceso: return

        ven = tk.Toplevel(self.root)
        ven.title(f"Detalles de {proceso.pid}")
        ven.geometry("380x420")
        ven.configure(bg="#1e1e2f")

        marco = tk.Frame(ven, bg="#2b2b36", padx=20, pady=20)
        marco.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(marco, text=f"Ficha Técnica: {proceso.pid}", font=("Helvetica", 14, "bold"), fg="white", bg="#2b2b36").pack(anchor="center", pady=(0, 15))

        tk.Label(marco, text=f"Tiempo Llegada: {proceso.tiempo_llegada} u/t", font=("Helvetica", 11), fg="#a9b7c6", bg="#2b2b36").pack(anchor="w", pady=2)
        tk.Label(marco, text=f"Ráfaga Inicial:   {proceso.rafaga_cpu} u/t", font=("Helvetica", 11), fg="#a9b7c6", bg="#2b2b36").pack(anchor="w", pady=2)

        tk.Frame(marco, bg="#3b3b54", height=2).pack(fill="x", pady=15)
        
        estado = "Esperando" if proceso.tiempo_comienzo == -1 else "Simulado / Terminado"
        color_estado = "#f1c40f" if proceso.tiempo_comienzo == -1 else "#2ecc71"
        tk.Label(marco, text=f"Estado actual: {estado}", font=("Helvetica", 10, "bold"), fg=color_estado, bg="#2b2b36").pack(anchor="w", pady=2)

        if proceso.tiempo_comienzo != -1:
            tk.Label(marco, text=f"Primer contacto: {proceso.tiempo_comienzo}", font=("Helvetica", 11), fg="white", bg="#2b2b36").pack(anchor="w", pady=2)
            tk.Label(marco, text=f"Finalización:    {proceso.tiempo_finalizacion}", font=("Helvetica", 11), fg="white", bg="#2b2b36").pack(anchor="w", pady=2)
            tk.Label(marco, text=f"Retorno (TR):    {proceso.tiempo_retorno}", font=("Helvetica", 11), fg="#3498db", bg="#2b2b36").pack(anchor="w", pady=2)
            tk.Label(marco, text=f"Espera (TE):     {proceso.tiempo_espera}", font=("Helvetica", 11), fg="#e74c3c", bg="#2b2b36").pack(anchor="w", pady=2)

            bloques = [b for b in self.ultimo_simulador.diagrama_gantt if b.pid == proceso.pid]
            if bloques:
                tk.Label(marco, text="\nEjecuciones Reales:", font=("Helvetica", 11, "bold"), fg="white", bg="#2b2b36").pack(anchor="w")
                for b in bloques:
                    tk.Label(marco, text=f"  ➔ De {b.inicio} a {b.fin}", font=("Courier", 11), fg="#1abc9c", bg="#2b2b36").pack(anchor="w")

        btn_cerrar = tk.Button(ven, text="Cerrar", bg="#e74c3c", fg="white", relief="flat", width=10, command=ven.destroy)
        btn_cerrar.pack(pady=10)


    def abrir_ventana_detalles(self):
        if not self.ultimo_simulador: return
        ven_detalles = tk.Toplevel(self.root)
        ven_detalles.title("Traza de Estados y Promedios")
        ven_detalles.geometry("900x500")
        ven_detalles.configure(bg="#1e1e2f")
        
        prom_espera, prom_retorno = self.ultimo_simulador.calcular_promedios()
        frame_promedios = tk.Frame(ven_detalles, bg="#20c997", pady=15)
        frame_promedios.pack(fill="x")
        tk.Label(frame_promedios, text=f"Promedio Espera: {prom_espera:.2f} u/t    |    Promedio Retorno: {prom_retorno:.2f} u/t", font=("Helvetica", 13, "bold"), fg="#1e1e2f", bg="#20c997").pack()
        
        frame_matriz = tk.Frame(ven_detalles, bg="#1e1e2f", padx=15, pady=15)
        frame_matriz.pack(fill="both", expand=True)
        tk.Label(frame_matriz, text="N=Nuevo  |  L=Listo  |  E=Ejecución  |  T=Terminado", font=("Helvetica", 10, "bold"), fg="#a9b7c6", bg="#1e1e2f").pack(anchor="w", pady=(0, 10))
    
        txt_estados = tk.Text(frame_matriz, font=("Courier", 11), wrap="none", bg="#11111a", fg="#4ade80", relief="flat", padx=15, pady=15)
        scroll_y = ttk.Scrollbar(frame_matriz, orient="vertical", command=txt_estados.yview)
        scroll_x = ttk.Scrollbar(frame_matriz, orient="horizontal", command=txt_estados.xview)
        txt_estados.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        txt_estados.pack(side="left", fill="both", expand=True)
        
        matriz, max_t = self.ultimo_simulador.generar_matriz_estados()
      
        max_pid_len = max([len(str(p)) for p in matriz.keys()] + [4])
    
        ancho_tick = 3
        if max_t > 99: ancho_tick = 4
        if max_t > 999: ancho_tick = 5
     
        header_ticks = "".join([f"{t:^{ancho_tick}}" for t in range(max_t)])
        cabecera = f"{'PID':<{max_pid_len}} |" + header_ticks + "\n"
        
        separador = "-" * max_pid_len + "-|" + "-" * (max_t * ancho_tick) + "\n"
        
        txt_estados.insert("end", cabecera)
        txt_estados.insert("end", separador)
    
        for pid in sorted(matriz.keys(), key=lambda x: int(x.replace("P", "")) if "P" in x else 0):
            estados_str = "".join([f"{e:^{ancho_tick}}" for e in matriz[pid]])
            fila = f"{pid:<{max_pid_len}} |{estados_str}\n"
            txt_estados.insert("end", fila)
            
        txt_estados.config(state="disabled")

    def abrir_modulo_concurrencia(self):
        VentanaConcurrencia(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazSimulador(root)
    for p in [("0", "8"), ("1", "4"), ("2", "9")]:
        app.entry_llegada.insert(0, p[0]); app.entry_rafaga.insert(0, p[1])
        app.agregar_proceso()
    root.mainloop()