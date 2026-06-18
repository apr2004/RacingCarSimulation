# --- main.py ---
import tkinter as tk
from tkinter import ttk

# Importamos la función principal de nuestro motor de físicas
from simulacion_chicane import ejecutar_simulacion

def lanzar_menu():
    root = tk.Tk()
    root.title("Configuración de Simulación")
    root.geometry("400x350")
    root.configure(padx=20, pady=20)
    
    tk.Label(root, text="Simulador Dinámico de Chicane", font=("Arial", 14, "bold")).pack(pady=10)
    
    # Selección de Coche
    tk.Label(root, text="Selecciona el Vehículo:").pack(anchor="w")
    var_coche = tk.StringVar(value="F1_Alonso_R25")
    ttk.Radiobutton(root, text="Fórmula 1 (Renault R25 - Alta carga aero)", variable=var_coche, value="F1_Alonso_R25").pack(anchor="w")
    ttk.Radiobutton(root, text="GT3 (Mercedes AMG - Mayor peso/menor aero)", variable=var_coche, value="GT3_Verstappen").pack(anchor="w")
    
    # Selección de Fenómeno
    tk.Label(root, text="\nSelecciona el Fenómeno a simular:").pack(anchor="w")
    var_fenomeno = tk.StringVar(value="Ideal")
    ttk.Radiobutton(root, text="Trazada Ideal (Control perfecto)", variable=var_fenomeno, value="Ideal").pack(anchor="w")
    ttk.Radiobutton(root, text="Subviraje (Frenada tardía -> Recto)", variable=var_fenomeno, value="Subviraje").pack(anchor="w")
    ttk.Radiobutton(root, text="Sobreviraje (Acelerar en apoyo -> Trompo)", variable=var_fenomeno, value="Sobreviraje").pack(anchor="w")
    
    def on_start():
        coche_elegido = var_coche.get()
        fenomeno_elegido = var_fenomeno.get()
        root.destroy() # Cerramos la ventana de Tkinter
        
        # Arrancamos Pygame
        ejecutar_simulacion(coche_elegido, fenomeno_elegido)
        
    tk.Button(root, text="INICIAR SIMULACIÓN", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=on_start).pack(pady=30, fill="x")
    
    root.mainloop()

if __name__ == "__main__":
    lanzar_menu()