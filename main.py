import sys
import os
import pygame
import random
import time
from collections import deque  # Para manejar la cola finita

#Funcion para usar rutas relativas, sirve para usar recursos dentro del enterno de desarrollo como desde fuera como un ejecutable (pyinstaller)
def resource_path(relative_path):
    """Devuelve la ruta absoluta al recurso, compatible con PyInstaller."""
    try:
        # Cuando se ejecuta como .exe
        base_path = sys._MEIPASS
    except AttributeError:
        # Cuando se ejecuta desde código fuente
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Inicializar Pygame
pygame.init()

# Configuración de pantalla
WIDTH, HEIGHT = 1025, 576
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de cola de clientes en supermercado")

# carga de recursos
imagen_cajero_base = pygame.image.load(resource_path("assets/images/cajero.png")).convert_alpha()
imagen_cajero_base = pygame.transform.scale(imagen_cajero_base, (60, 60))  # Ajusta al tamaño
imagen_cliente_base = pygame.image.load(resource_path("assets/images/cliente.png")).convert_alpha()
imagen_cliente_base = pygame.transform.scale(imagen_cliente_base, (50, 50))  # Ajusta al tamaño

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
# ---------- Paleta Flat
PETER_RIVER = (52, 152, 219)
SUN_FLOWER = (241, 196, 15)
ALIZARIN = (231, 76, 60)
EMERALD = (46, 204, 113)
CARROT = (230, 126, 34)
MIDNIGHT_BLUE = (44, 62, 80)
CLOUDS = (236, 240, 241)
#----colores para colorear cajeros
CAJERO_COLORES = [
    (52, 152, 219),   # Azul
    (46, 204, 113),   # Verde
    (243, 156, 18),   # Naranja
    (231, 76, 60),    # Rojo
    (155, 89, 182),   # Púrpura
    (26, 188, 156),   # Turquesa
    (44, 62, 80),     # Azul oscuro
    (189, 195, 199),  # Plateado
]

# fuentes
font = pygame.font.SysFont(None, 24)
small_font = pygame.font.SysFont(None, 18)

# Panel de controles
PANEL_WIDTH = 200
panel_rect = pygame.Rect(WIDTH - PANEL_WIDTH, 0, PANEL_WIDTH, HEIGHT)

# Slider para número de cajeros
slider_rect = pygame.Rect(WIDTH - PANEL_WIDTH + 40, 100, 120, 10)
slider_handle = pygame.Rect(slider_rect.x + 60, slider_rect.y - 5, 10, 20)
slider_dragging = False
slider_value = 4  # Valor inicial

# Slider para número de productos
producto_slider_rect = pygame.Rect(WIDTH - PANEL_WIDTH + 40, 180, 120, 10)
producto_slider_handle = pygame.Rect(producto_slider_rect.x + 60, producto_slider_rect.y - 5, 10, 20)
producto_slider_dragging = False
producto_slider_value = 50  # Valor inicial

# Slider para tiempo por producto
tiempo_slider_rect = pygame.Rect(WIDTH - PANEL_WIDTH + 40, 260, 120, 10)
tiempo_slider_handle = pygame.Rect(tiempo_slider_rect.x + 50, tiempo_slider_rect.y - 5, 10, 20)
tiempo_slider_dragging = False
tiempo_por_producto = 5  # Valor inicial

# Slider para número de clientes
cola_slider_rect = pygame.Rect(WIDTH - PANEL_WIDTH + 40, 340, 120, 10)
cola_slider_handle = pygame.Rect(cola_slider_rect.x + 60, cola_slider_rect.y - 5, 10, 20)
cola_slider_dragging = False
cola_slider_value = 4  # Valor inicial para la capacidad máxima de cada cola

#funcion para colorear imagen de cajero
def tintar_imagen(imagen, color):
    copia = imagen.copy()
    tint = pygame.Surface(imagen.get_size(), flags=pygame.SRCALPHA)
    tint.fill(color)
    copia.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return copia

#funcion para colorear clientes
def tint_image(image, color):
    tinted = image.copy()
    tinted.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    tinted.fill(color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    return tinted

def dibujar_panel():
    pygame.draw.rect(screen, CLOUDS, panel_rect)
    title = font.render("Controles", True, BLACK)
    screen.blit(title, (panel_rect.x + 50, 30))

    slider_color = ALIZARIN if not simulacion_activa else GRAY

    # -------------------------------Slider de cajeros-----------------------------------
    # Etiqueta para slider
    cajeros_label = font.render("N° Cajeros", True, BLACK)
    screen.blit(cajeros_label, (panel_rect.x + 50, 70))

    # Dibuja la barra
    pygame.draw.rect(screen, BLACK, slider_rect)
    pygame.draw.rect(screen, slider_color, slider_handle)

    # Mostrar el valor actual
    valor_cajeros = font.render(str(slider_value), True, BLACK)
    screen.blit(valor_cajeros, (slider_rect.x + 45, slider_rect.y + 20))

    # -------------------------------Slider de productos-----------------------------------
    # Etiqueta para slider de productos
    productos_label = font.render("Máx. Productos", True, BLACK)
    screen.blit(productos_label, (panel_rect.x + 30, 150))

    # Dibuja la barra
    pygame.draw.rect(screen, BLACK, producto_slider_rect)
    pygame.draw.rect(screen, slider_color, producto_slider_handle)

    # Mostrar el valor actual
    valor_productos = font.render(str(producto_slider_value), True, BLACK)
    screen.blit(valor_productos, (producto_slider_rect.x + 40, producto_slider_rect.y + 20))

    # -------------------------------Slider tiempo de servicio-----------------------------------
    # Etiqueta para tiempo por producto
    tiempo_label = font.render("Tiempo x Producto (s)", True, BLACK)
    screen.blit(tiempo_label, (panel_rect.x + 20, 230))

    # Dibuja la barra
    pygame.draw.rect(screen, BLACK, tiempo_slider_rect)
    pygame.draw.rect(screen, slider_color, tiempo_slider_handle)

    # Mostrar el valor actual
    valor_tiempo = font.render(str(tiempo_por_producto), True, BLACK)
    screen.blit(valor_tiempo, (tiempo_slider_rect.x + 40, tiempo_slider_rect.y + 20))

    # ------------------ Slider para capacidad de cola -----------------------------------------
    # Etiqueta para slider clientes
    cola_label = font.render("Capacidad Cola", True, BLACK)
    screen.blit(cola_label, (panel_rect.x + 35, 310))

    # Dibuja la barra
    pygame.draw.rect(screen, BLACK, cola_slider_rect)
    pygame.draw.rect(screen, slider_color, cola_slider_handle)

    # Mostrar el valor actual
    valor_cola = font.render(str(cola_slider_value), True, BLACK)
    screen.blit(valor_cola, (cola_slider_rect.x + 45, cola_slider_rect.y + 20))



# Configuración de la simulación
PRODUCT_RANGE = lambda: (1, producto_slider_value)
CUSTOMER_SIZE = 30  # Tamaño de dibujado

# Botones
dynamic_button = pygame.Rect(50, 20, 90, 30)
stop_button = pygame.Rect(160, 20, 80, 30)
simulacion_activa = False
simulacion_pausada = False

# variables globales
clientes_atendidos = 0  # Contador de clientes atendidos
tiempos_espera = []  # Lista para registrar tiempos de espera
clientes_saliendo = []  # Lista para los clientes que salen
intervalo_clientes = 1.5  # tiempo entre clientes (en segundos)
tiempo_ultimo_cliente = time.time()
clientes_rechazados = 0 # Contador de clientes rechazados

# variables para el cronometro
start_time = None
paused_time = 0
pause_start = None

# Clases
class Cliente:
    def __init__(self, id):
        self.id = id
        self.color = (
            random.randint(50, 255),  # Rojo
            random.randint(50, 255),  # Verde
            random.randint(50, 255)  # Azul
        )
        self.productos = random.randint(*PRODUCT_RANGE())
        self.tiempo_atencion = self.productos * tiempo_por_producto  # Depende de productos
        self.x, self.y = 50, HEIGHT - (id + 1) * (CUSTOMER_SIZE + 10)  # Posición inicial en la cola
        self.tiempo_llegada = time.time()  # Marca el momento en que el cliente fue creado
        # para animar en la cola
        self.destino_x = self.x
        self.destino_y = self.y
        self.velocidad = 5  # pixeles por frame
        self.image = tint_image(imagen_cliente_base, self.color)

    # funcion para animacion
    def mover(self):
        dx = self.destino_x - self.x
        dy = self.destino_y - self.y
        distancia = (dx ** 2 + dy ** 2) ** 0.5
        if distancia > self.velocidad:
            self.x += self.velocidad * dx / distancia
            self.y += self.velocidad * dy / distancia
        else:
            self.x = self.destino_x
            self.y = self.destino_y

class Cajero:
    def __init__(self, id):
        self.id = id
        self.ocupado = False
        self.tiempo_restante = 0
        self.cliente_actual = None
        self.ultimo_tiempo = time.time()
        self.x = 40 + (id * (CUSTOMER_SIZE + 50))  # Separación horizontal
        self.y = 130  # Todos en la misma línea
        self.cola = deque(maxlen=cola_slider_value)  # Cola individual por cajero
        self.color = CAJERO_COLORES[id]
        self.sprite = tintar_imagen(imagen_cajero_base, self.color)

    def atender_cliente(self):
        if self.cola and not self.ocupado:
            cliente = self.cola.popleft()
            self.ocupado = True
            self.tiempo_restante = cliente.tiempo_atencion
            self.cliente_actual = cliente
            self.ultimo_tiempo = time.time()
            # Mover al cliente al centro del cajero (animado)
            cliente.destino_x = self.x + (60 - CUSTOMER_SIZE) // 2
            cliente.destino_y = self.y + (60 - CUSTOMER_SIZE) // 2

    def actualizar(self):
        global clientes_atendidos, tiempos_espera
        if self.ocupado:
            now = time.time()
            if now - self.ultimo_tiempo >= tiempo_por_producto:
                self.tiempo_restante -= tiempo_por_producto
                if self.cliente_actual and self.cliente_actual.productos > 0:
                    self.cliente_actual.productos -= 1
                self.ultimo_tiempo = now
            if self.tiempo_restante <= 0:
                self.ocupado = False
                if self.cliente_actual:
                    tiempo_espera = time.time() - self.cliente_actual.tiempo_llegada
                    tiempos_espera.append(tiempo_espera)
                clientes_atendidos += 1

                # Preparar al cliente para salir animado
                if self.cliente_actual:
                    self.cliente_actual.destino_x = self.cliente_actual.x  # mantener misma X
                    self.cliente_actual.destino_y = -CUSTOMER_SIZE - 10  # salir por arriba
                    clientes_saliendo.append(self.cliente_actual)
                self.cliente_actual = None
        else:
            self.atender_cliente()

# Crear cajeros
def crear_cajeros(n, clientes_existentes=None):
    nuevos_cajeros = [Cajero(i) for i in range(n)]
    for c in nuevos_cajeros:
        c.cola = deque(maxlen=cola_slider_value)
    if clientes_existentes:
        for cliente in clientes_existentes:
            cajero_con_menor_cola = min(nuevos_cajeros, key=lambda c: len(c.cola))
            if len(cajero_con_menor_cola.cola) < cola_slider_value:
                cajero_con_menor_cola.cola.append(cliente)
    return nuevos_cajeros

# Crear clientes
def generar_cliente():
    global clientes_rechazados
    cliente = Cliente(random.randint(1, 1000))

    # 1. Cajeros libres y sin cola
    for cajero in cajeros:
        if not cajero.ocupado and len(cajero.cola) == 0:
            cliente.x = cajero.x
            cliente.y = cajero.y + 70
            cliente.destino_x = cliente.x
            cliente.destino_y = cliente.y
            cajero.cola.append(cliente)
            return

    # 2. Cajeros con espacio
    cajeros_con_espacio = [c for c in cajeros if len(c.cola) < cola_slider_value]
    if cajeros_con_espacio:
        cajero_destino = min(cajeros_con_espacio, key=lambda c: len(c.cola))
        index = len(cajero_destino.cola)
        cliente.x = cajero_destino.x
        cliente.y = cajero_destino.y + 70 + index * (CUSTOMER_SIZE + 5)
        cliente.destino_x = cliente.x
        cliente.destino_y = cliente.y
        cajero_destino.cola.append(cliente)
    else:
        clientes_rechazados += 1  # 3. Rechazar si todas las colas están llenas

# Dibujar botones y contador
def dibujar_botones():
    # Para dinamizar texto iniciar-continuar-pausar y color del boton
    if not simulacion_activa:
        boton_texto = "Iniciar"
        boton_color = PETER_RIVER
    elif simulacion_pausada:
        boton_texto = "Continuar"
        boton_color = SUN_FLOWER
    else:
        boton_texto = "Pausar"
        boton_color = CARROT

    pygame.draw.rect(screen, boton_color, dynamic_button)
    pygame.draw.rect(screen, ALIZARIN if simulacion_activa else GRAY, stop_button)

    #Muestra los clientes rechazados
    rechazados_text = font.render(f"Clientes rechazados: {clientes_rechazados}", True, BLACK)
    screen.blit(rechazados_text, (WIDTH - 450, 80))

    dynamic_text = font.render(boton_texto, True, BLACK)
    stop_text = font.render("Detener", True, BLACK)
    contador_text = font.render(f"Total clientes atendidos: {clientes_atendidos}", True, BLACK)

    # promediar tiempos de espara para dibujar texto
    if tiempos_espera:
        promedio_espera = sum(tiempos_espera) / len(tiempos_espera)
        minutos = int(promedio_espera) // 60
        segundos = int(promedio_espera) % 60
        tiempo_formateado = f"{minutos:02}:{segundos:02}"
    else:
        tiempo_formateado = "00:00"

    promedio_text = font.render(f"Promedio de espera: {tiempo_formateado}", True, BLACK)

    screen.blit(dynamic_text, (dynamic_button.x + 5, dynamic_button.y + 5))
    screen.blit(stop_text, (stop_button.x + 10, stop_button.y + 5))
    screen.blit(contador_text, (WIDTH - 450, 20))
    screen.blit(promedio_text, (WIDTH - 450, 50))

    # Mostrar cronómetro
    if start_time:
        if simulacion_pausada and pause_start:
            tiempo_transcurrido = pause_start - start_time - paused_time
        else:
            tiempo_transcurrido = time.time() - start_time - paused_time
        minutos = int(tiempo_transcurrido) // 60
        segundos = int(tiempo_transcurrido) % 60
        cronometro_text = font.render(f"Tiempo: {minutos:02}:{segundos:02}", True, BLACK)
        screen.blit(cronometro_text, (WIDTH - 750, 30))


# Bucle principal
running = True
clock = pygame.time.Clock()

cajeros = []

while running:
    screen.fill(WHITE)

    # Dibujar botones y contador
    dibujar_botones()

    # Dibujar el panel
    dibujar_panel()

    # Ejecutar simulación
    if simulacion_activa:
        if not simulacion_pausada:
            # Solo si no está pausada: generar clientes y actualizar cajeros
            # if random.random() < 0.05:
            #    generar_cliente()
            if time.time() - tiempo_ultimo_cliente >= intervalo_clientes:
                generar_cliente()
                tiempo_ultimo_cliente = time.time()
            for cajero in cajeros:
                cajero.actualizar()

        # Dibujar clientes en la cola
        for cajero in cajeros:
            for i, cliente in enumerate(cajero.cola):
                destino_x = cajero.x
                destino_y = cajero.y + 70 + i * 45 #45 para separacion entre clientes
                # Solo actualiza si ha cambiado su destino
                if cliente.destino_x != destino_x or cliente.destino_y != destino_y:
                    cliente.destino_x = destino_x
                    cliente.destino_y = destino_y
                cliente.mover()
                #pygame.draw.rect(screen, cliente.color, (cliente.x, cliente.y, CUSTOMER_SIZE, CUSTOMER_SIZE))
                # muestra la cantidad de productos en cada cliente
                texto_productos = small_font.render(str(cliente.productos), True, BLACK)
                texto_rect = texto_productos.get_rect(topright=(cliente.x + 45, cliente.y + 10))
                screen.blit(cliente.image, (cliente.x, cliente.y))
                screen.blit(texto_productos, texto_rect)


        # Dibujar cajeros
        for cajero in cajeros:
            cajero_text = font.render(f"Cajero {cajero.id + 1}", True, BLACK)
            screen.blit(cajero_text, (cajero.x - 10, cajero.y - 25))
            screen.blit(cajero.sprite, (cajero.x, cajero.y)) #dibujar sprite cajero

            # Dibujar cliente sobre el cajero si está siendo atendido
            if cajero.cliente_actual:
                cliente = cajero.cliente_actual
                cliente.mover()  # anima mientras va llegando
                cliente_rect = pygame.Rect(cliente.x, cliente.y, CUSTOMER_SIZE, CUSTOMER_SIZE)
                screen.blit(cliente.image, (cliente.x, cliente.y)) #dibujar sprite cliente

                # Mostrar productos restantes en esquina superior derecha del cliente
                texto_productos = small_font.render(str(cliente.productos), True, BLACK)
                texto_rect = texto_productos.get_rect(topright=(cliente.x + 55, cliente.y + 20))
                screen.blit(texto_productos, texto_rect)

        # Dibujar a los clientes saliendo
        for cliente in list(clientes_saliendo):  # Copia segura para eliminar durante el loop
            cliente.mover()
            productos_texto = font.render(str(cliente.productos), True, BLACK)
            screen.blit(cliente.image, (cliente.x, cliente.y))
            screen.blit(productos_texto, (cliente.x + CUSTOMER_SIZE - 10, cliente.y))

            # Si ya salió de pantalla, lo removemos
            if cliente.y < -CUSTOMER_SIZE:
                clientes_saliendo.remove(cliente)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not simulacion_activa:
                if slider_handle.collidepoint(event.pos):
                    slider_dragging = True
                if producto_slider_handle.collidepoint(event.pos):
                    producto_slider_dragging = True
                if tiempo_slider_handle.collidepoint(event.pos):
                    tiempo_slider_dragging = True
                if cola_slider_handle.collidepoint(event.pos):
                    cola_slider_dragging = True


            # Boton dinamico
            if dynamic_button.collidepoint(event.pos):
                if not simulacion_activa:
                    simulacion_activa = True  # Comienza la simulación
                    simulacion_pausada = False  # No está pausada
                    start_time = time.time()
                    paused_time = 0
                    pause_start = None
                    # Recoger clientes en espera antes de recrear cajeros
                    clientes_en_espera = []
                    for cajero in cajeros:
                        clientes_en_espera.extend(list(cajero.cola))
                    cajeros = crear_cajeros(slider_value, clientes_en_espera)
                elif simulacion_activa and not simulacion_pausada:
                    simulacion_pausada = True
                    pause_start = time.time()
                elif simulacion_activa and simulacion_pausada:
                    simulacion_pausada = False
                    paused_time += time.time() - pause_start
                    pause_start = None

            # Boton de detener
            elif stop_button.collidepoint(event.pos):
                simulacion_activa = False
                simulacion_pausada = False
                clientes_rechazados = 0 # Reinicia los clientes rechazados
                clientes_atendidos = 0  # Reinicia los clientes atendidos
                tiempos_espera = []  # Reinicia los tiempos de espera también
                cajeros = []
                start_time = None
                paused_time = 0
                pause_start = None

        elif event.type == pygame.MOUSEBUTTONUP:
            slider_dragging = False
            producto_slider_dragging = False
            tiempo_slider_dragging = False
            cola_slider_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if slider_dragging:
                new_x = min(max(event.pos[0], slider_rect.x), slider_rect.x + slider_rect.width)
                slider_handle.x = new_x
                # Mapea la posición del slider a un valor entre 1 y 8
                porcentaje = (slider_handle.x - slider_rect.x) / slider_rect.width
                slider_value = max(1, min(8, round(1 + porcentaje * 7)))
            if producto_slider_dragging:
                new_x = min(max(event.pos[0], producto_slider_rect.x),
                            producto_slider_rect.x + producto_slider_rect.width)
                producto_slider_handle.x = new_x
                porcentaje = (producto_slider_handle.x - producto_slider_rect.x) / producto_slider_rect.width
                producto_slider_value = max(1, min(100, round(1 + porcentaje * 99)))
            if tiempo_slider_dragging:
                new_x = min(max(event.pos[0], tiempo_slider_rect.x), tiempo_slider_rect.x + tiempo_slider_rect.width)
                tiempo_slider_handle.x = new_x
                porcentaje = (tiempo_slider_handle.x - tiempo_slider_rect.x) / tiempo_slider_rect.width
                tiempo_por_producto = max(1, min(10, round(1 + porcentaje * 9)))
            if cola_slider_dragging:
                new_x = min(max(event.pos[0], cola_slider_rect.x), cola_slider_rect.x + cola_slider_rect.width)
                cola_slider_handle.x = new_x
                porcentaje = (cola_slider_handle.x - cola_slider_rect.x) / cola_slider_rect.width
                cola_slider_value = max(1, min(8, round(1 + porcentaje * 7)))


    pygame.display.flip()
    clock.tick(60)

pygame.quit()