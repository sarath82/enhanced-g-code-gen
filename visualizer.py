import matplotlib.pyplot as plt
import numpy as np

# Set dark theme for all plots
plt.style.use('dark_background')

def plot_workpiece(initial_dia, final_dia, initial_len, final_len, ops_type="Turning"):
    fig, ax = plt.subplots(figsize=(8, 3)) # Reduced from (10, 5)
    
    # Workpiece (Initial) - Rectangle from (0, -D/2) to (L, D/2)
    # Note: In CNC turning, Z is horizontal axis (longitudinal) and X is vertical (diameter)
    # For visualization, we plot Z on x-axis and X on y-axis
    
    # Initial workpiece outline (Using a more visible 'Steel' color)
    ax.add_patch(plt.Rectangle((0, -initial_dia/2), initial_len, initial_dia, 
                                 edgecolor='#555555', facecolor='#A9A9A9', alpha=0.6, label='Initial Stock'))
    
    # Axis lines
    ax.axhline(0, color='black', linestyle='--', linewidth=0.5)
    
    # Finished part outline (simplified)
    # We assume the right side is Z=0
    # The part is usually defined from Z=0 to Z=-final_len
    # But in the app's coordinate system, it seems to use relative offsets.
    # Let's assume Z positive is away from the chuck, Z negative is into the part.
    
    # Final profile depends on operation
    if ops_type == "Turning":
        # Turning reduces diameter
        ax.add_patch(plt.Rectangle((0, -final_dia/2), final_len, final_dia, 
                                     edgecolor='#1E90FF', facecolor='#00BFFF', alpha=0.4, label='Finished Part'))
    elif ops_type == "Facing":
        # Facing reduces length
        ax.add_patch(plt.Rectangle((initial_len - final_len, -initial_dia/2), final_len, initial_dia, 
                                     edgecolor='#228B22', facecolor='#32CD32', alpha=0.4, label='Finished Part'))
    
    ax.set_xlabel('Length (Z) [mm]', fontsize=12, fontweight='bold', color='#38bdf8')
    ax.set_ylabel('Diameter (X) [mm]', fontsize=12, fontweight='bold', color='#38bdf8')
    ax.set_title('Workpiece Preview', fontsize=16, fontweight='bold', color='#f8fafc', pad=20)
    
    legend = ax.legend(frameon=True, facecolor='#020617', edgecolor='#1e293b')
    plt.setp(legend.get_texts(), color='#f8fafc')
    
    ax.grid(True, linestyle=':', alpha=0.3, color='#475569')
    
    # Set background color of the plot area
    ax.set_facecolor('#020617')
    fig.patch.set_facecolor('#020617')
    
    # Set axis spine colors
    for spine in ax.spines.values():
        spine.set_color('#1e293b')
    
    # Set limits with some padding
    ax.set_xlim(-10, initial_len + 10)
    ax.set_ylim(-initial_dia/2 - 10, initial_dia/2 + 10)
    
    return fig

def plot_step_turning(initial_dia, initial_len, steps):
    fig, ax = plt.subplots(figsize=(8, 3)) # Reduced from (10, 5)
    
    # Initial stock
    ax.add_patch(plt.Rectangle((0, -initial_dia/2), initial_len, initial_dia, 
                                 edgecolor='#555555', facecolor='#A9A9A9', alpha=0.6, label='Initial Stock'))
    
    # Steps
    z_pos = 0
    for i, (dia, length) in enumerate(steps):
        ax.add_patch(plt.Rectangle((z_pos, -dia/2), length, dia, 
                                     edgecolor='#DC143C', facecolor='#FF4500', alpha=0.7, label=f'Step {i+1}' if i==0 else ""))
        z_pos += length
        
    ax.axhline(0, color='black', linestyle='--', linewidth=0.5)
    ax.set_xlabel('Length (Z) [mm]', fontsize=12, fontweight='bold', color='#38bdf8')
    ax.set_ylabel('Diameter (X) [mm]', fontsize=12, fontweight='bold', color='#38bdf8')
    ax.set_title('Step Turning Preview', fontsize=16, fontweight='bold', color='#f8fafc', pad=20)
    
    legend = ax.legend(frameon=True, facecolor='#020617', edgecolor='#1e293b')
    plt.setp(legend.get_texts(), color='#f8fafc')
    
    ax.grid(True, linestyle=':', alpha=0.3, color='#475569')
    
    # Set background color
    ax.set_facecolor('#020617')
    fig.patch.set_facecolor('#020617')
    
    # Set axis spine colors
    for spine in ax.spines.values():
        spine.set_color('#1e293b')
    
    ax.set_xlim(-10, initial_len + 10)
    ax.set_ylim(-initial_dia/2 - 10, initial_dia/2 + 10)
    
    return fig
