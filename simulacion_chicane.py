import pygame
import math
from pymunk import Vec2d
from simulaciones_genericas import Tsim

from fisica_coches import *
from piloto_automatico import *

WIDTH, HEIGHT = 1200, 600

def ejecutar_simulacion(nombre_coche, fenomeno):
    print(f"Iniciando Pygame: {nombre_coche} | Modo: {fenomeno}")
    
    sim = Tsim(width=WIDTH, height=HEIGHT, fondo=r"/fondo.jpg")
    FPS = 60
    dt = (1.0 / FPS)*2  # Multiplicamos por 2 para acelerar la simulación
    
    # Setup de imágenes
    es_f1 = (nombre_coche == "F1_Alonso_R25")
    img_ruta = r"/coche_alonso.png" if es_f1 else r"/coche_verstappen.png"
    img_original = pygame.image.load(img_ruta).convert_alpha()
    tam = (100, 100) if es_f1 else (120, 120)
    rot_inicial = -108 if es_f1 else 0
    img_coche_base = pygame.transform.rotate(pygame.transform.smoothscale(img_original, tam), rot_inicial)

    coche = DATOS_COCHES[nombre_coche]
    
    # Empezar fuera de la pantalla lanzado
    pos = Vec2d(-150, 170) 
    velocidad_entrada_kmh = 310 if es_f1 else 260
    v_mod = velocidad_entrada_kmh / 3.6 
    
    heading = 0.0
    marcha = 6 
    chocado = False

    muro = pygame.Rect(640, 430, 260, 30)
    
    # Pre-creamos la máscara del muro para optimizar
    mask_muro = pygame.mask.Mask(muro.size, fill=True)
    
    while sim.actualizar_eventos():
        # 1. IA del piloto
        acelerador, angulo_volante, forzar_trompo = calcular_acciones_piloto(pos.x, pos.y, v_mod, fenomeno, nombre_coche)
        
        # 2. RESOLUCIÓN DE FÍSICAS
        if not chocado:
            # Resolver dinámica nos devuelve la aceleración, velocidad angular, estado dinámico, rpm y fuerza normal
            aceleracion, omega, estado_dinamico, rpm, fn = resolver_dinamica(v_mod, acelerador, angulo_volante, marcha, coche)
            
            # Gestionar caja de cambios (sube o baja según rpm)
            marcha = gestionar_caja_cambios(rpm, coche["rpm_max"], marcha)
            
            if forzar_trompo or estado_dinamico == "Sobreviraje":
                estado_dinamico = "Sobreviraje"
                direccion_derrape = -1 if angulo_volante >= 0 else 1
                omega += math.radians(120) * dt * direccion_derrape
            elif estado_dinamico == "Subviraje":
                omega *= 0.3 

            v_mod = max(0, v_mod + aceleracion * dt)
            heading += omega * dt
            pos += Vec2d(v_mod * math.cos(heading) * dt, v_mod * math.sin(heading) * dt)
        
        # 3. COLISIONES CON PYGAME
        img_rotada = pygame.transform.rotate(img_coche_base, -math.degrees(heading))
        rect_rot = img_rotada.get_rect(center=(int(pos.x), int(pos.y)))
        
        # Solo comprobamos colisión si no ha chocado ya
        if not chocado:
            mask_coche = pygame.mask.from_surface(img_rotada)
            
            offset_x = int(muro.x - rect_rot.x)
            offset_y = int(muro.y - rect_rot.y)
            
            if mask_coche.overlap(mask_muro, (offset_x, offset_y)):
                chocado = True
                v_mod = 0 # Detenemos el coche en seco
                estado_dinamico = "¡ACCIDENTE CONTRA EL MURO!"
                rpm = 0
            
        # 4. RENDERIZADO
        sim.draw()
        
        s_muro = pygame.Surface(muro.size, pygame.SRCALPHA)
        s_muro.fill((255, 0, 0, 80))
        sim.screen.blit(s_muro, muro.topleft)
        sim.screen.blit(img_rotada, rect_rot)
        
        # 5. TELEMETRÍA
        font = pygame.font.SysFont("Consolas", 18, bold=True)
        color_estado = (100, 255, 100) if estado_dinamico == "Agarre Ideal" else ((255,165,0) if estado_dinamico == "Sobreviraje" else (255,100,100))
        if chocado:
            color_estado = (255, 50, 50)
        
        textos = [
            (f"Vehículo: {nombre_coche}", (255, 255, 255)),
            (f"Velocidad: {v_mod * 3.6:3.0f} km/h", (255, 255, 255)),
            (f"Marcha: {marcha}ª | Motor: {rpm:4.0f} RPM", (255, 255, 0)),
            (f"Dinámica: {estado_dinamico}", color_estado),
            (f"Posición X: {pos.x:5.1f} m, Posición Y: {pos.y:5.1f} m", (255, 255, 255)),
            (f"Fuerza Normal: {fn:5.1f} N", (255, 255, 255)),
        ]
            
        for i, (txt, col) in enumerate(textos): sim.screen.blit(font.render(txt, True, col), (20, 420 + i*25))
        
        pygame.display.flip()
        sim.clock.tick(FPS)
    pygame.quit()