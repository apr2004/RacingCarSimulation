# 🏎️ Simulación Dinámica de una Curva: F1 vs GT3

Este proyecto consiste en un simulador dinámico en 2D desarrollado en Python para estudiar y comparar cómo dos filosofías de ingeniería totalmente opuestas afrontan una sección de curvas críticas (*chicane*). La simulación recrea el comportamiento del coche al límite de su adherencia, modelando fenómenos avanzados de la física automovilística.

---

### 🎨 Recursos Visuales Utilizados
Para aportar un gran realismo visual al entorno, los elementos gráficos se obtuvieron utilizando el modo fotografía del videojuego *Automobilista 2*:
*   `fondo.jpg`: Imagen de fondo que representa la pista en vista cenital de la *chicane* y sus muros.
*   `coche_alonso.png`: Renderizado desde una perspectiva cenital del monoplaza histórico **Renault R25 V10 (2005)** de Fernando Alonso.
*   `coche_verstappen.png`: Renderizado cenital del turismo de competición **Mercedes-AMG GT3 (2026)** utilizado por Max Verstappen.

---

### ⚙️ Características de los Vehículos a Estudio
El simulador implementa las especificaciones técnicas reales de ambos coches para contrastar el efecto de la inercia frente a la carga aerodinámica:

*   **Renault R25 V10 (F1):** Vehículo extremadamente ligero con una masa de 605 kg (piloto incluido). Destaca por su inmensa capacidad para generar carga aerodinámica ($C_L = 3.2$), permitiéndole duplicar su propio peso estático a altas velocidades y pasar por la curva a ritmos increíbles.
*   **Mercedes-AMG GT3:** Turismo mucho más pesado y voluminoso (1300 kg), derivado de un coche de calle. Su apoyo aerodinámico es sustancialmente menor ($C_L = 1.2$), por lo que depende en gran medida del agarre mecánico de sus neumáticos y debe lidiar con más del doble de inercia lineal.

---

### 📐 Fundamentos Físicos Implementados
El motor matemático del script computa frame a frame el sumatorio de fuerzas reales que actúan sobre el vehículo:

1.  **Dinámica Longitudinal y Motor:** El par motor no es constante; varía según las revoluciones (RPM). Se han utilizado **Splines Cúbicos** mediante `scipy.interpolate.interp1d` para interpolar las curvas de par reales de los motores. La tracción se multiplica por las relaciones de marchas de sus respectivas cajas de cambios de 6 velocidades.
2.  **Aerodinámica de Competición:** Se calcula la resistencia al avance (Drag) mediante $F_{D} = \frac{1}{2}C_{D}\rho Av^{2}$ y la carga aerodinámica (Downforce), que modifica de forma dinámica la Fuerza Normal total sobre el asfalto: $F_{N} = mg + \frac{1}{2}\rho AC_{L}v^{2}$.
3.  **Elipse de Fricción:** El agarre disponible del neumático se distribuye entre la fuerza tangencial (acelerar/frenar) y la fuerza centrípeta necesaria para girar. El simulador evalúa constantemente la condición estática máxima ($F_{max} = \sqrt{F_{c}^{2} + F_{t}^{2}} \le \mu_{s}F_{N}$). Si se supera este límite, las ruedas patinan y se pasa al régimen de fricción dinámica ($\mu_{d} < \mu_{s}$).

---

### 🕹️ Modos de Simulación
A través de un menú de inicio diseñado con Tkinter (`main.py`), es posible evaluar tres escenarios dinámicos bien diferenciados:

*   **Modo 1: Trazada Ideal:** Un piloto automático inteligente basado en máquinas de estados y guiado por coordenadas espaciales controla el acelerador, freno y volante con una calibración milimétrica para pasar de forma óptima la *chicane*.
*   **Modo 2: Subviraje:** Ocurre al forzar una frenada tardía al entrar a la curva. El eje delantero agota su elipse de fricción, las ruedas directrices patinan perdiendo capacidad angular y el coche se va recto ignorando las órdenes del volante.
*   **Modo 3: Sobreviraje:** Simula el error de dar gas a fondo en pleno apoyo a la salida de la curva. El eje trasero rompe su límite de adherencia por exceso de par de tracción, desatando un momento angular parásito que provoca que la parte posterior derrape y el coche termine en un trompo contra el "Muro de los Campeones".

---

### 🛠️ Arquitectura y Sistema de Colisiones
El proyecto cuenta con un diseño modular que independiza la lógica física de la representación en pantalla. 

En lugar de utilizar las físicas genéricas de rebote del motor PyMunk, la gestión de impactos contra el muro se realiza mediante **máscaras de colisión perfectas a nivel de píxel** de Pygame (`pygame.mask.overlap`). Al producirse el impacto, la simulación se congela de manera instantánea, manteniendo visible en pantalla la telemetría exacta del coche en el milisegundo del choque (Velocidad, Marcha, RPM, Fuerza Normal y Estado Dinámico) para su posterior análisis científico.

![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-4B275F?style=for-the-badge&logo=python&logoColor=white)
![PyMunk](https://img.shields.io/badge/PyMunk-FF6F00?style=for-the-badge&logo=box2d&logoColor=white)
