import matplotlib.pyplot as plt
import numpy as np

# Set dark theme for all plots
plt.style.use('dark_background')

def plot_workpiece(initial_dia, final_dia, initial_len, final_len, ops_type="Turning"):
    """
    Generates a premium digital twin preview of the workpiece.
    """
    fig, ax = plt.subplots(figsize=(8, 3))
    
    # Initial workpiece outline (Industrial Steel color)
    ax.add_patch(plt.Rectangle((0, -initial_dia/2), initial_len, initial_dia, 
                                 edgecolor='#555555', facecolor='#A9A9A9', alpha=0.6, label='Initial Stock'))
    
    # Centerline
    ax.axhline(0, color='white', linestyle='--', linewidth=0.5, alpha=0.3)
    
    # Finished part outline logic
    if ops_type == "Turning":
        # Turning reduces diameter (Primary Cyan Accent)
        ax.add_patch(plt.Rectangle((0, -final_dia/2), final_len, final_dia, 
                                     edgecolor='#38bdf8', facecolor='#0ea5e9', alpha=0.5, label='Finished Part'))
    elif ops_type == "Facing":
        # Facing reduces length (Forest Green Accent)
        ax.add_patch(plt.Rectangle((initial_len - final_len, -initial_dia/2), final_len, initial_dia, 
                                     edgecolor='#22c55e', facecolor='#16a34a', alpha=0.5, label='Finished Part'))
    
    # Labels and Grid
    ax.set_xlabel('Length (Z) [mm]', fontsize=10, fontweight='bold', color='#38bdf8')
    ax.set_ylabel('Diameter (X) [mm]', fontsize=10, fontweight='bold', color='#38bdf8')
    ax.set_title('Digital Workpiece Twin', fontsize=14, fontweight='bold', color='#f8fafc', pad=15)
    
    legend = ax.legend(frameon=True, facecolor='#020617', edgecolor='#1e293b')
    plt.setp(legend.get_texts(), color='#f8fafc')
    
    ax.grid(True, linestyle=':', alpha=0.2, color='#475569')
    
    # Theme Backgrounds
    ax.set_facecolor('#020617')
    fig.patch.set_facecolor('#020617')
    
    # Spine Colors
    for spine in ax.spines.values():
        spine.set_color('#1e293b')
    
    # Padding
    ax.set_xlim(-10, initial_len + 10)
    ax.set_ylim(-initial_dia/2 - 10, initial_dia/2 + 10)
    
    return fig

def plot_step_turning(initial_dia, initial_len, steps):
    """
    Visualizes multiple machining steps on a single workpiece.
    """
    fig, ax = plt.subplots(figsize=(8, 3))
    
    # Initial stock
    ax.add_patch(plt.Rectangle((0, -initial_dia/2), initial_len, initial_dia, 
                                 edgecolor='#555555', facecolor='#A9A9A9', alpha=0.4, label='Initial Stock'))
    
    # Centerline
    ax.axhline(0, color='white', linestyle='--', linewidth=0.5, alpha=0.3)

    # Render Steps (Neon Orange Accent)
    z_pos = 0
    for i, (dia, length) in enumerate(steps):
        ax.add_patch(plt.Rectangle((z_pos, -dia/2), length, dia, 
                                     edgecolor='#fb923c', facecolor='#f97316', alpha=0.7, 
                                     label=f'Machine Steps' if i==0 else ""))
        z_pos += length
        
    ax.set_xlabel('Length (Z) [mm]', fontsize=10, fontweight='bold', color='#38bdf8')
    ax.set_ylabel('Diameter (X) [mm]', fontsize=10, fontweight='bold', color='#38bdf8')
    ax.set_title('Step Machining Preview', fontsize=14, fontweight='bold', color='#f8fafc', pad=15)
    
    legend = ax.legend(frameon=True, facecolor='#020617', edgecolor='#1e293b')
    plt.setp(legend.get_texts(), color='#f8fafc')
    
    ax.grid(True, linestyle=':', alpha=0.2, color='#475569')
    ax.set_facecolor('#020617')
    fig.patch.set_facecolor('#020617')
    
    for spine in ax.spines.values():
        spine.set_color('#1e293b')
    
    ax.set_xlim(-10, initial_len + 10)
    ax.set_ylim(-initial_dia/2 - 10, initial_dia/2 + 10)
    
    return fig
