# Graficador Volumen vs Variacion Diaria en %

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![PyQt5](https://img.shields.io/badge/Qt-PyQt5-green.svg)
![Matplotlib](https://img.shields.io/badge/Plotting-Matplotlib-orange.svg)

## Descripción

Esta es una aplicación de escritorio desarrollada con PyQt5 y Matplotlib, diseñada para monitorear y analizar datos de mercado en tiempo real obtenidos a través de la API de SHDA. Ofrece una interfaz de usuario interactiva para visualizar los datos de diferentes instrumentos (Bluechips, Bonos, CEDEARs, Letras y Panel General) en tablas y gráficos de burbujas dinámicos con funcionalidades de zoom y scroll.

## Características

* **Obtención de Datos en Tiempo Real:** Conecta con la API de SHDA para obtener los últimos datos de mercado.
* **Visualización en Tablas:** Muestra los datos de instrumentos en tablas claras y organizadas, con codificación de color para las variaciones positivas y negativas.
* **Gráficos de Burbujas Interactivos:**
    * Visualiza la relación entre `Volumen Operado` y `Variación Diaria (%)`.
    * **Zoom con Rueda del Mouse:** Acerca o aleja el gráfico usando la rueda del mouse, centrándose en la posición del cursor.
    * **Pan con Arrastre del Mouse:** Desplaza el gráfico arrastrando con el clic izquierdo del mouse.
    * **Scrollbars Dinámicos:** Barras de desplazamiento horizontales y verticales que aparecen y se ajustan automáticamente según el nivel de zoom, permitiendo una navegación precisa en gráficos detallados.
    * **Botón "Reset Zoom":** Restaura la vista original del gráfico.
* **Auto-actualización de Datos:** Configuración de un intervalo para actualizar automáticamente los datos de mercado.
* **Interfaz de Usuario Intuitiva:** Diseño limpio y fácil de usar, con una barra de estado para notificaciones y progreso.
* **Manejo de Errores:** Notificaciones de errores para una mejor depuración y experiencia del usuario.

## Requisitos

Asegúrate de tener Python 3.x instalado.
Las dependencias necesarias se pueden instalar usando `pip`:




pip install PyQt5 matplotlib pandas numpy


Además, esta aplicación utiliza la librería SHDA para interactuar con la API de SHDA. Deberás asegurarte de tener esta librería disponible y configurada correctamente con tus credenciales.

Configuración y Uso

## Configurar Credenciales SHDA:
Abre el archivo Analisis_data.py y actualiza tus credenciales en las clases SHDAHomeBrokerApp y SHDADataWorker:

Python


```bash

class SHDADataWorker(QThread):
    def __init__(self, host, dni, user, password, comitente):
        super().__init__()
        self.host = 203 # O tu host SHDA
        self.dni = "TU_DNI" # ¡Importante: Reemplaza con tu DNI real!
        self.user = "TU_USUARIO" # ¡Importante: Reemplaza con tu usuario real!
        self.password = "TU_PASSWORD" # ¡Importante: Reemplaza con tu contraseña real!
        self.comitente = 78495 # O tu número de comitente
        # ...

class SHDAHomeBrokerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Configuración de conexión
        self.host = 203 # O tu host SHDA
        self.dni = "TU_DNI"
        self.user = "TU_USUARIO"
        self.password = "TU_PASSWORD"
        self.comitente = 76542 # O tu número de comitente
        # ...
     
