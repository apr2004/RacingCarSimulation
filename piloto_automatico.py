# --- piloto_automatico.py ---
import math

# =================================================================
# PERFILES DE CONDUCCIÓN 
# =================================================================
PERFILES_PILOTO = {
    "F1_Alonso_R25": {
        "punto_frenada": 390,        # Píxel X donde empieza a frenar 
        "vel_paso_curva": 35,        # m/s (Aprox 126 km/h en el vértice)
        
        # 1er Vértice (Derecha)
        "inicio_curva_derecha": 490, # Empieza a girar a la derecha
        "angulo_derecha": 70,        # Grados de volante
        "fin_curva_derecha": 551,    # Deja de girar a la derecha
        
        # Transición (La zona central de la "S")
        "transicion_recta": 300,     # Hasta aquí el volante va recto, píxel y
        
        # 2º Vértice (Izquierda)
        "inicio_curva_izquierda": 578, 
        "angulo_izquierda": -80,     
        "salida_curva": 628           # Vuelve a poner recto el volante
    },
    
    "GT3_Verstappen": {
        "punto_frenada": 350,       
        "vel_paso_curva": 25,       
        
        "inicio_curva_derecha": 410,
        "angulo_derecha": 1, # En GT3, la curva es más abierta, casi una chicane rápida sin necesidad de mucho volante       
        "fin_curva_derecha": 555,
        
        "transicion_recta": 300, 
        
        "inicio_curva_izquierda": 575,
        "angulo_izquierda": -1,
        "salida_curva": 700
    }
}

def calcular_acciones_piloto(pos_x, pos_y, v_mod, fenomeno, nombre_coche):
    perfil = PERFILES_PILOTO[nombre_coche]
    acelerador = 0.0
    angulo_volante = 0.0
    forzar_trompo = False

    # 1. RECTA PRINCIPAL
    if pos_x < perfil["punto_frenada"]:
        acelerador = 1.0
        
    # 2. ZONA DE FRENADA
    elif pos_x < perfil["inicio_curva_derecha"]:
        if fenomeno == "Subviraje":
            acelerador = -1.0 if pos_x > (perfil["punto_frenada"] + 80) else 1.0
        else:
            acelerador = -1.0 if v_mod > perfil["vel_paso_curva"] else 0.0
            
    # 3. PRIMER VÉRTICE (Derecha)
    elif pos_x < perfil["fin_curva_derecha"]:
        angulo_volante = math.radians(perfil["angulo_derecha"])
        acelerador = 0.1 # Mantenimiento
        
    # 4. ZONA DE TRANSICIÓN (Recto entre las dos curvas)
    elif pos_y < perfil["transicion_recta"]:
        angulo_volante = 0.0 # Volante centrado
        acelerador = 0.2     # Ligero toque de gas
        
    # 5. SEGUNDO VÉRTICE (Izquierda - Hacia el muro)
    elif pos_x < perfil["salida_curva"]:
        angulo_volante = math.radians(perfil["angulo_izquierda"])
        
        # En sobreviraje, aceleramos para provocar derrape INMEDIATAMENTE al entrar
        if fenomeno == "Sobreviraje":
            acelerador = 5.0  # Aceleración máxima durante toda la curva
            forzar_trompo = True  # Forzar trompo durante toda la curva izquierda
            perfil["angulo_izquierda"] = -90 # Volante a tope para asegurar derrape
            perfil["salida_curva"] = 600 # No enderezar el volante hasta el final de la curva
        else:
            acelerador = 0.4 # Aceleración progresiva normal
            
    # 6. SALIDA DE CURVA
    else:
        acelerador = 1.0
        angulo_volante = 0.0
        
    return acelerador, angulo_volante, forzar_trompo

def gestionar_caja_cambios(rpm, rpm_max, marcha_actual):
    # Sube de marcha rozando el límite
    if rpm > rpm_max - 500 and marcha_actual < 6:
        return marcha_actual + 1
    # Baja de marcha si caemos por debajo del 60% del régimen máximo del motor
    elif rpm < (rpm_max * 0.60) and marcha_actual > 1:
        return marcha_actual - 1
    return marcha_actual