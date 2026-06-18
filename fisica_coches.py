import math
import numpy as np
from scipy.interpolate import interp1d

def crear_curva_motor(rpm_datos, par_datos):
    """Crea la función spline cúbica exacta (Diapositiva 9)."""
    return interp1d(rpm_datos, par_datos, kind='cubic', fill_value="extrapolate")

# Curvas de potencia
curva_f1 = crear_curva_motor(
    np.array([1000, 4000, 8000, 12000, 16000, 19000, 20000]),
    np.array([200,  250,  300,  330,   350,   320,   0])
)

curva_gt3 = crear_curva_motor(
    np.array([1000, 3000, 5000, 7000, 8500, 9000]),
    np.array([400,  550,  600,  550,  450,   0])
)

# Diferenciamos mu_s (estático) y mu_d (dinámico)
DATOS_COCHES = {
    "F1_Alonso_R25": {
        "masa": 605, "area_frontal": 1.45, "cd": 1.1, "cl": 3.2, 
        "crr": 0.015, "mu_s": 1.7, "mu_d": 1.2, # Neumáticos Slicks
        "radio_rueda": 0.33, "final_drive": 4.0,
        "marchas": {1: 7.39, 2: 4.54, 3: 3.28, 4: 2.57, 5: 2.07, 6: 1.74},
        "rpm_max": 19000, "eficiencia": 0.9, "curva_motor": curva_f1,
        "distancia_ejes": 3.1
    },
    "GT3_Verstappen": {
        "masa": 1300, "area_frontal": 2.2, "cd": 0.65, "cl": 1.2, 
        "crr": 0.015, "mu_s": 1.35, "mu_d": 0.95, # GT3
        "radio_rueda": 0.35, "final_drive": 3.2,
        "marchas": {1: 2.8, 2: 2.2, 3: 1.7, 4: 1.3, 5: 1.0, 6: 0.8},
        "rpm_max": 8500, "eficiencia": 0.88, "curva_motor": curva_gt3,
        "distancia_ejes": 2.7
    }
}

def rpm_velocidad(v_ms, marcha, coche):
    """Calcula las RPM del motor."""
    if marcha < 1 or v_ms <= 0: return 1000.0
    rpm = ((v_ms / coche["radio_rueda"]) * coche["marchas"][marcha] * coche["final_drive"] * 60) / (2 * math.pi)
    return max(rpm, 1000.0)

def resolver_dinamica(v_mod, acelerador, angulo_volante, marcha, coche):
    """
    Resuelve el sumatorio de fuerzas y comprueba la elipse de fricción.
    Retorna la aceleración longitudinal, la velocidad angular (omega) y el estado.
    """
    # 1. RPM y Fuerza del Motor
    rpm = rpm_velocidad(v_mod, marcha, coche)
    torque = max(0, float(coche["curva_motor"](rpm)))
    f_empuje = (torque * coche["marchas"][marcha] * coche["final_drive"] * coche["eficiencia"]) / coche["radio_rueda"]

    # 2. Aerodinámica y Carga Normal
    rho = 1.225
    fd = 0.5 * rho * (v_mod**2) * coche["cd"] * coche["area_frontal"]
    downforce = 0.5 * rho * (v_mod**2) * coche["cl"] * coche["area_frontal"]
    f_normal = (coche["masa"] * 9.81) + downforce
    
    # FR = Crr * R * FN 
    fr = coche["crr"] * coche["radio_rueda"] * f_normal

    # 3. Límites Estáticos
    f_max_estatica = coche["mu_s"] * f_normal

    # Determinar fuerza tangencial solicitada (Aceleración o Frenado)
    if acelerador >= 0:
        ft_solicitada = acelerador * f_empuje
    else:
        # Frenado limitado por adherencia máxima
        ft_solicitada = acelerador * f_max_estatica 

    # 4. Dinámica en Curva
    radio_giro = float('inf')
    fc_solicitada = 0
    if abs(angulo_volante) > 0.001 and v_mod > 0.5:
        radio_giro = coche["distancia_ejes"] / math.tan(abs(angulo_volante))
        fc_solicitada = (coche["masa"] * v_mod**2) / radio_giro

    # 5. Elipse de fricción
    f_total_solicitada = math.sqrt(ft_solicitada**2 + fc_solicitada**2)
    
    estado = "Agarre Ideal"
    
    if f_total_solicitada > f_max_estatica:
        # PÉRDIDA DE ADHERENCIA: Pasamos a fricción dinámica
        f_max_dinamica = coche["mu_d"] * f_normal
        
        proporcion = f_max_dinamica / f_total_solicitada if f_total_solicitada > 0 else 0
        ft_real = ft_solicitada * proporcion
        fc_real = fc_solicitada * proporcion
        
        # Diferenciamos la recta de la curva
        if abs(angulo_volante) < 0.05: # Si vamos rectos o casi rectos
            if acelerador > 0:
                estado = "Patinaje (Ruedas derrapando)"
            else:
                estado = "Bloqueo de frenos"
        elif acelerador < 0 or (abs(angulo_volante) > 0.05 and acelerador == 0):
            estado = "Subviraje" # Pierde agarre al girar frenando
        else:
            estado = "Sobreviraje" # Pierde agarre al girar acelerando
    else:
        ft_real = ft_solicitada
        fc_real = fc_solicitada

    # 6. Sumatorio final 
    f_neta = ft_real - fd - fr
    
    # Si frenamos a muy baja velocidad, detener
    if f_neta < 0 and v_mod < 0.5 and acelerador <= 0: 
        f_neta = 0
        v_mod = 0
        
    aceleracion = f_neta / coche["masa"]
    
    # Velocidad angular (efecto pivote)
    omega = 0
    if radio_giro != float('inf') and v_mod > 0:
        omega = math.copysign(fc_real / (coche["masa"] * v_mod), angulo_volante)
        
    return aceleracion, omega, estado, rpm, f_normal