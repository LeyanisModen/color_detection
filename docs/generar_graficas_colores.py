import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import colorsys

# Funciones auxiliares para conversión de color
def rgb_to_ycrcb(r, g, b):
    # SDTV formula (BT.601)
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
    cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b
    return y, cr, cb

def f_lab(t):
    if t > (6/29)**3:
        return t**(1/3)
    else:
        return (1/3) * (29/6)**2 * t + 4/29

def rgb_to_lab(r, g, b):
    # sRGB to XYZ
    def pivot_rgb(c):
        return (c/12.92) if c <= 0.04045 else ((c+0.055)/1.055)**2.4
    
    # Asegurar que r, g, b estén en rango 0-1
    r, g, b = pivot_rgb(r), pivot_rgb(g), pivot_rgb(b)
    
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    
    # XYZ to LAB (D65 illuminant)
    xn, yn, zn = 0.95047, 1.00000, 1.08883
    
    x, y, z = x/xn, y/yn, z/zn
    
    L = 116 * f_lab(y) - 16
    a = 500 * (f_lab(x) - f_lab(y))
    L_b = 200 * (f_lab(y) - f_lab(z)) # variable renamed to not conflict with b
    
    return L, a, L_b

def plot_rgb_cube(filename):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Crear una cuadrícula de puntos
    r, g, b = np.mgrid[0:1:12j, 0:1:12j, 0:1:12j]
    r = r.flatten()
    g = g.flatten()
    b = b.flatten()
    
    # Dibujar solo las caras externas para que se vea mejor (no un bloque sólido)
    mask = (r == 0) | (r == 1) | (g == 0) | (g == 1) | (b == 0) | (b == 1)
    
    colors = np.vstack((r[mask], g[mask], b[mask])).T
    
    ax.scatter(r[mask], g[mask], b[mask], c=colors, marker='o', alpha=0.8, s=40)
    
    ax.set_xlabel('Rojo (R)')
    ax.set_ylabel('Verde (G)')
    ax.set_zlabel('Azul (B)')
    plt.title('Espacio de Color RGB (Cubo)')
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

def plot_hsv_cylinder(filename):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Crear coordenadas polares para HSV
    h = np.linspace(0, 1, 36) # Ángulos de color
    s = np.linspace(0, 1, 8)  # Radio (Saturación)
    v = np.linspace(0.1, 1, 10) # Altura (Valor) - evitar muchos negros
    
    h_grid, s_grid, v_grid = np.meshgrid(h, s, v)
    
    x = s_grid * np.cos(h_grid * 2 * np.pi)
    y = s_grid * np.sin(h_grid * 2 * np.pi)
    z = v_grid
    
    x_flat = x.flatten()
    y_flat = y.flatten()
    z_flat = z.flatten()
    
    # Convertir HSV a RGB solo para pintar los puntos en la gráfica
    colors = [colorsys.hsv_to_rgb(h_val, s_val, v_val) 
              for h_val, s_val, v_val in zip(h_grid.flatten(), s_grid.flatten(), v_grid.flatten())]
    
    # Quitar un poco los puntos interiores para mejor visualización (opcional)
    mask = (s_grid.flatten() == 1) | (v_grid.flatten() == 1) | (v_grid.flatten() == 0.1)
    
    x_mask = x_flat[mask]
    y_mask = y_flat[mask]
    z_mask = z_flat[mask]
    c_mask = np.array(colors)[mask]

    ax.scatter(x_mask, y_mask, z_mask, c=c_mask, marker='o', alpha=0.9, s=40)
    
    ax.set_xlabel('Saturación * cos(Matiz)')
    ax.set_ylabel('Saturación * sin(Matiz)')
    ax.set_zlabel('Valor (Brillo)')
    plt.title('Espacio de Color HSV (Cilindro)')
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

def plot_ycrcb_space(filename):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Crear cubo RGB y transformarlo
    r, g, b = np.mgrid[0:1:10j, 0:1:10j, 0:1:10j]
    r, g, b = r.flatten(), g.flatten(), b.flatten()
    
    # Dibujar solo las caras para mejor visualización
    mask = (r == 0) | (r == 1) | (g == 0) | (g == 1) | (b == 0) | (b == 1)
    r_mask, g_mask, b_mask = r[mask], g[mask], b[mask]
    
    colors = np.vstack((r_mask, g_mask, b_mask)).T
    
    y = np.zeros_like(r_mask)
    cr = np.zeros_like(r_mask)
    cb = np.zeros_like(r_mask)
    
    for i in range(len(r_mask)):
        y[i], cr[i], cb[i] = rgb_to_ycrcb(r_mask[i]*255, g_mask[i]*255, b_mask[i]*255)
    
    ax.scatter(cb, cr, y, c=colors, marker='o', alpha=0.8, s=40)
    
    ax.set_xlabel('Cb (Diferencia Azul)')
    ax.set_ylabel('Cr (Diferencia Rojo)')
    ax.set_zlabel('Y (Luma)')
    plt.title('Espacio de Color YCrCb')
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

def plot_lab_space(filename):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Crear cubo RGB y transformarlo
    r, g, b = np.mgrid[0:1:10j, 0:1:10j, 0:1:10j]
    r, g, b = r.flatten(), g.flatten(), b.flatten()
    
    # Dibujar solo las caras
    mask = (r == 0) | (r == 1) | (g == 0) | (g == 1) | (b == 0) | (b == 1)
    r_mask, g_mask, b_mask = r[mask], g[mask], b[mask]
    
    colors = np.vstack((r_mask, g_mask, b_mask)).T
    
    L = np.zeros_like(r_mask)
    a = np.zeros_like(r_mask)
    L_b = np.zeros_like(r_mask)
    
    for i in range(len(r_mask)):
        L[i], a[i], L_b[i] = rgb_to_lab(r_mask[i], g_mask[i], b_mask[i])
    
    ax.scatter(a, L_b, L, c=colors, marker='o', alpha=0.8, s=40)
    
    ax.set_xlabel('a (Verde-Rojo)')
    ax.set_ylabel('b (Azul-Amarillo)')
    ax.set_zlabel('L (Luminancia)')
    plt.title('Espacio de Color CIE-LAB')
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

def plot_hsl_cylinder(filename):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    h = np.linspace(0, 1, 36)
    s = np.linspace(0, 1, 8)
    l = np.linspace(0.1, 0.9, 10) # Evitar negros o blancos puros (doble cono)
    
    h_grid, s_grid, l_grid = np.meshgrid(h, s, l)
    
    # Convertir HSL a RGB para obtener colores
    colors = [colorsys.hls_to_rgb(h_val, l_val, s_val) 
              for h_val, l_val, s_val in zip(h_grid.flatten(), l_grid.flatten(), s_grid.flatten())]
    
    # La geometría de HSL es un doble cono, el radio S depende de L
    # Radio es maximo cuando L=0.5, y 0 cuando L=0 o L=1
    r_hsl = s_grid * (1 - np.abs(2 * l_grid - 1))
    
    x = r_hsl * np.cos(h_grid * 2 * np.pi)
    y = r_hsl * np.sin(h_grid * 2 * np.pi)
    z = l_grid
    
    x_flat, y_flat, z_flat = x.flatten(), y.flatten(), z.flatten()
    
    # Visualizar superficie externa
    mask = (s_grid.flatten() == 1) | (l_grid.flatten() == 0.9) | (l_grid.flatten() == 0.1)
    
    ax.scatter(x_flat[mask], y_flat[mask], z_flat[mask], c=np.array(colors)[mask], marker='o', alpha=0.9, s=40)
    
    ax.set_xlabel('Saturación * cos(Matiz)')
    ax.set_ylabel('Saturación * sin(Matiz)')
    ax.set_zlabel('Luminosidad (Lightness)')
    plt.title('Espacio de Color HSL (Doble Cono)')
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

if __name__ == "__main__":
    plot_rgb_cube('rgb_cube.png')
    plot_hsv_cylinder('hsv_cylinder.png')
    plot_ycrcb_space('ycrcb_space.png')
    plot_lab_space('lab_space.png')
    plot_hsl_cylinder('hsl_cylinder.png')
    print("Gráficas generadas exitosamente: rgb_cube.png, hsv_cylinder.png, ycrcb_space.png, lab_space.png, hsl_cylinder.png")
