import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

def dibujar_gantt(gantt, titulo="Diagrama de Gantt", es_expulsivo=False):
    plt.style.use('dark_background')
    color_fondo = '#1e1e2f'
    
    pids = sorted(list(set(b.pid for b in gantt)), key=lambda x: int(x[1:]))
    altura_figura = max(3.5, len(pids) * 0.8) if es_expulsivo else 3.5
    fig, ax = plt.subplots(figsize=(12, altura_figura))
    fig.patch.set_facecolor(color_fondo)
    ax.set_facecolor(color_fondo)
    
    colores_base = ['#6f42c1', '#17a2b8', '#fd7e14', '#e83e8c', '#ffc107', '#0d6efd', '#20c997']
    mapa_colores = {pid: colores_base[i % len(colores_base)] for i, pid in enumerate(pids)}
    
    if es_expulsivo:
        posiciones_y = {}
        pos_actual = 10
        yticks = []
        yticklabels = []
        
        for pid in pids:
            posiciones_y[pid] = pos_actual
            yticks.append(pos_actual + 4)
            yticklabels.append(pid)
            pos_actual += 10
            
        for b in gantt:
            duracion = b.fin - b.inicio
            py = posiciones_y[b.pid]
            ax.broken_barh([(b.inicio, duracion)], (py, 8), facecolors=mapa_colores[b.pid], edgecolor='white', linewidth=0.5)
            
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels, color='white', fontweight='bold')
        ax.set_ylim(5, pos_actual)
        
    else:
        for b in gantt:
            duracion = b.fin - b.inicio
            ax.broken_barh([(b.inicio, duracion)], (10, 8), facecolors=mapa_colores[b.pid], edgecolor='#cccccc', linewidth=0.5)
            
        ax.set_ylim(5, 25)
        ax.set_yticks([])
        
    leyenda = [mpatches.Patch(color=mapa_colores[pid], label=pid) for pid in pids]
    ax.legend(handles=leyenda, bbox_to_anchor=(0.5, -0.25), loc='upper center', ncol=12, facecolor=color_fondo, edgecolor='white', labelcolor='white')
        
    ax.set_xlabel('Unidades de Tiempo', color='white')
    ax.set_title(titulo, color='white', pad=15, fontweight='bold')
    ax.grid(True, axis='x', color='#3b3b54', linestyle='-', alpha=0.5)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#4b4b64')

    plt.subplots_adjust(bottom=0.3)
    
    plt.show()