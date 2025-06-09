import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QTabWidget, QTableWidget, QTableWidgetItem,
                             QPushButton, QLabel, QStatusBar, QMessageBox, QProgressBar,
                             QSpinBox, QCheckBox, QFrame, QSplitter, QScrollBar, QGridLayout,
                             QGroupBox, QSlider, QButtonGroup, QRadioButton)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
import matplotlib.patches as patches
import numpy as np
import SHDA
from datetime import datetime
import traceback

class SHDADataWorker(QThread):
    """Worker thread para obtener datos de SHDA"""

    # Señales para cada tipo de instrumento
    bluechips_updated = pyqtSignal(object)
    bonds_updated = pyqtSignal(object)
    cedears_updated = pyqtSignal(object)
    short_term_bonds_updated = pyqtSignal(object)
    galpones_updated = pyqtSignal(object)

    status_updated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)

    def __init__(self, host, dni, user, password, comitente):
        super().__init__()
        self.host = 123
        self.dni = "12345678"
        self.user = "nnnnnnnnn"
        self.password = "xxxxxxxxx"
        self.comitente = 12345
        self.hb = None
        self.is_running = True

    def run(self):
        """Ejecutar obtención de datos"""
        try:
            self.connect_and_fetch_data()
        except Exception as e:
            self.error_occurred.emit(f"Error en worker: {str(e)}")
            print(f"Error detallado: {traceback.format_exc()}")

    def connect_and_fetch_data(self):
        """Conectar a SHDA y obtener todos los datos"""
        try:
            self.status_updated.emit("Conectando a SHDA...")
            self.progress_updated.emit(10)

            # Crear conexión SHDA
            self.hb = SHDA.SHDA(self.host, self.dni, self.user, self.password)

            self.status_updated.emit("Conectado. Obteniendo datos...")
            self.progress_updated.emit(20)

            # Obtener bluechips
            try:
                self.status_updated.emit("Obteniendo bluechips...")
                lideres = self.hb.get_bluechips("24hs")
                if lideres is not None and not lideres.empty:
                    self.bluechips_updated.emit(lideres)
                    print(f"Bluechips obtenidos: {len(lideres)} registros")
                self.progress_updated.emit(35)
            except Exception as e:
                print(f"Error obteniendo bluechips: {e}")

            # Obtener bonos
            try:
                self.status_updated.emit("Obteniendo bonos...")
                bonos = self.hb.get_bonds("24hs")
                if bonos is not None and not bonos.empty:
                    self.bonds_updated.emit(bonos)
                    print(f"Bonos obtenidos: {len(bonos)} registros")
                self.progress_updated.emit(50)
            except Exception as e:
                print(f"Error obteniendo bonos: {e}")

            # Obtener CEDEARs
            try:
                self.status_updated.emit("Obteniendo CEDEARs...")
                cedears = self.hb.get_cedear("24hs")
                if cedears is not None and not cedears.empty:
                    self.cedears_updated.emit(cedears)
                    print(f"CEDEARs obtenidos: {len(cedears)} registros")
                self.progress_updated.emit(65)
            except Exception as e:
                print(f"Error obteniendo CEDEARs: {e}")

            # Obtener letras
            try:
                self.status_updated.emit("Obteniendo letras...")
                letras = self.hb.get_short_term_bonds("24hs")
                if letras is not None and not letras.empty:
                    self.short_term_bonds_updated.emit(letras)
                    print(f"Letras obtenidas: {len(letras)} registros")
                self.progress_updated.emit(80)
            except Exception as e:
                print(f"Error obteniendo letras: {e}")

            # Obtener Galpones
            try:
                self.status_updated.emit("Obteniendo Panel General...")
                galpones = self.hb.get_galpones("24hs")
                if galpones is not None and not galpones.empty:
                    self.galpones_updated.emit(galpones)
                    print(f"Activos Panel general obtenidos: {len(galpones)} registros")
                self.progress_updated.emit(90)
            except Exception as e:
                print(f"Error obteniendo Panel General: {e}")

            self.progress_updated.emit(100)
            self.status_updated.emit(f"Datos actualizados - {datetime.now().strftime('%H:%M:%S')}")

        except Exception as e:
            self.error_occurred.emit(f"Error conectando: {str(e)}")
            print(f"Error detallado en conexión: {traceback.format_exc()}")

    def stop(self):
        """Detener worker"""
        self.is_running = False
        self.quit()

class PlotWidget(QWidget):
    """Widget personalizado para mostrar gráficos matplotlib con funcionalidad de zoom y scroll"""

    def __init__(self):
        super().__init__()
        self.original_xlim = None
        self.original_ylim = None
        self.zoom_factor = 1.5
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Crear figura matplotlib
        self.figure = Figure(figsize=(12, 8), facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)

        # Layout para canvas y scrollbars
        plot_layout = QHBoxLayout()
        plot_layout.addWidget(self.canvas)

        self.v_scrollbar = QScrollBar(Qt.Vertical)
        self.v_scrollbar.setMinimum(0)
        self.v_scrollbar.setMaximum(1000)
        self.v_scrollbar.setValue(500) # Centered initially
        self.v_scrollbar.setSingleStep(10)
        self.v_scrollbar.setPageStep(100)
        self.v_scrollbar.valueChanged.connect(self.v_scroll_plot)
        plot_layout.addWidget(self.v_scrollbar)

        main_plot_area = QWidget()
        main_plot_area_layout = QVBoxLayout(main_plot_area)
        main_plot_area_layout.addLayout(plot_layout)

        self.h_scrollbar = QScrollBar(Qt.Horizontal)
        self.h_scrollbar.setMinimum(0)
        self.h_scrollbar.setMaximum(1000)
        self.h_scrollbar.setValue(500) # Centered initially
        self.h_scrollbar.setSingleStep(10)
        self.h_scrollbar.setPageStep(100)
        self.h_scrollbar.valueChanged.connect(self.h_scroll_plot)
        main_plot_area_layout.addWidget(self.h_scrollbar)

        layout.addWidget(main_plot_area)


        # Configurar estilo
        plt.style.use('dark_background')

        # Conectar eventos del mouse
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)

        self.is_panning = False
        self.pan_start_point = None


        # Agregar botón de reset zoom
        self.reset_button = QPushButton("🔍 Reset Zoom")
        self.reset_button.clicked.connect(self.reset_zoom)
        self.reset_button.setMaximumWidth(120)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.reset_button)
        layout.addLayout(button_layout)

    def on_scroll(self, event):
        """Manejar evento de scroll del mouse para zoom"""
        try:
            ax = self.figure.gca()
            if ax is None:
                return

            # Obtener posición del mouse en coordenadas de datos
            xdata, ydata = event.xdata, event.ydata
            if xdata is None or ydata is None:
                return

            # Obtener límites actuales
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

            # Calcular factor de zoom
            if event.button == 'up':
                # Zoom in
                scale_factor = 1.0 / self.zoom_factor
            elif event.button == 'down':
                # Zoom out
                scale_factor = self.zoom_factor
            else:
                return

            # Calcular nuevos límites centrados en la posición del mouse
            new_width = (xlim[1] - xlim[0]) * scale_factor
            new_height = (ylim[1] - ylim[0]) * scale_factor

            relx = (xlim[1] - xdata) / (xlim[1] - xlim[0])
            rely = (ylim[1] - ydata) / (ylim[1] - ylim[0])

            new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * relx]
            new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * rely]

            # Aplicar límites (evitar zoom excesivo)
            if self.original_xlim and self.original_ylim:
                # No permitir zoom out más allá de los límites originales
                if scale_factor > 1:  # Zoom out
                    orig_width = self.original_xlim[1] - self.original_xlim[0]
                    orig_height = self.original_ylim[1] - self.original_ylim[0]

                    if new_width > orig_width * 1.1:
                        new_xlim = self.original_xlim
                    if new_height > orig_height * 1.1:
                        new_ylim = self.original_ylim

                # No permitir zoom in excesivo
                elif scale_factor < 1:  # Zoom in
                    min_width = (self.original_xlim[1] - self.original_xlim[0]) * 0.01
                    min_height = (self.original_ylim[1] - self.original_ylim[0]) * 0.01

                    if new_width < min_width:
                        center_x = (new_xlim[0] + new_xlim[1]) / 2
                        new_xlim = [center_x - min_width/2, center_x + min_width/2]
                    if new_height < min_height:
                        center_y = (new_ylim[0] + new_ylim[1]) / 2
                        new_ylim = [center_y - min_height/2, center_y + min_height/2]

            # Aplicar nuevos límites
            ax.set_xlim(new_xlim)
            ax.set_ylim(new_ylim)

            self.update_scrollbars()
            self.canvas.draw_idle()

        except Exception as e:
            print(f"Error en zoom: {e}")

    def on_click(self, event):
        """Manejar click del mouse para pan (arrastrar) o reset"""
        if event.button == 1:  # Left click for pan
            self.is_panning = True
            self.pan_start_point = (event.xdata, event.ydata)
            self.canvas.setCursor(Qt.ClosedHandCursor)
        elif event.button == 2:  # Middle click for reset
            self.reset_zoom()

    def on_release(self, event):
        """Manejar liberación del click del mouse"""
        if event.button == 1:
            self.is_panning = False
            self.canvas.unsetCursor()

    def on_motion(self, event):
        """Manejar movimiento del mouse para pan"""
        if self.is_panning and self.pan_start_point and event.xdata is not None and event.ydata is not None:
            ax = self.figure.gca()
            if ax is None:
                return

            dx = event.xdata - self.pan_start_point[0]
            dy = event.ydata - self.pan_start_point[1]

            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

            new_xlim = [xlim[0] - dx, xlim[1] - dx]
            new_ylim = [ylim[0] - dy, ylim[1] - dy]

            ax.set_xlim(new_xlim)
            ax.set_ylim(new_ylim)
            self.update_scrollbars()
            self.canvas.draw_idle()

    def reset_zoom(self):
        """Resetear zoom a vista original"""
        try:
            if self.original_xlim and self.original_ylim:
                ax = self.figure.gca()
                ax.set_xlim(self.original_xlim)
                ax.set_ylim(self.original_ylim)
                self.update_scrollbars()
                self.canvas.draw_idle()
        except Exception as e:
            print(f"Error reseteando zoom: {e}")

    def plot_bubble_chart(self, data, title, instrument_type):
        """Crear gráfico de burbujas con funcionalidad de zoom y scroll"""
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_facecolor('#2d2d2d')

            if data is None or data.empty:
                ax.text(0.5, 0.5, 'No hay datos disponibles',
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=16, color='white')
                self.canvas.draw_idle()
                return

            # Preparar datos
            df = self.prepare_data(data)
            if df is None or df.empty:
                ax.text(0.5, 0.5, 'Error procesando datos',
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=16, color='white')
                self.canvas.draw_idle()
                return

            # Normalizar tamaños de burbujas
            if len(df) > 1:
                turnover_sizes = df['turnover'].values
                min_size, max_size = 100, 2000
                size_range = turnover_sizes.max() - turnover_sizes.min()
                if size_range > 0:
                    normalized_sizes = min_size + (turnover_sizes - turnover_sizes.min()) * (max_size - min_size) / size_range
                else:
                    normalized_sizes = [min_size] * len(df)
            else:
                normalized_sizes = [500]

            # Colores basados en variación
            colors = []
            for change in df['change']:
                if change > 0:
                    colors.append('#44ff44')  # Verde
                elif change < 0:
                    colors.append('#ff4444')  # Rojo
                else:
                    colors.append('#ffffff')  # Blanco

            # Crear scatter plot
            scatter = ax.scatter(
                df['change'],
                df['turnover'],
                s=normalized_sizes,
                c=colors,
                alpha=0.7,
                edgecolors='white',
                linewidth=1.5
            )

            # Agregar etiquetas para puntos importantes
            for idx, row in df.iterrows():
                if len(df) <= 15 or row['turnover'] > df['turnover'].quantile(0.75):
                    ax.annotate(
                        row['symbol'],
                        (row['change'], row['turnover']),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=8,
                        color='white',
                        weight='regular'
                    )

            # Configurar ejes
            ax.set_xlabel('Variación Diaria (%)', fontsize=12, color='white')
            ax.set_ylabel('Volumen Operado', fontsize=12, color='white')
            ax.set_title(f'{title}\n(Usar rueda del mouse para zoom, click izquierdo para pan, click medio para reset)',
                        fontsize=14, color='white', pad=20)

            # Formatear eje Y
            ax.yaxis.set_major_formatter(plt.FuncFormatter(
                lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K' if x >= 1000 else f'{x:.0f}'
            ))

            # Líneas de referencia
            ax.axvline(x=0, color='white', linestyle='--', alpha=0.3)
            if len(df) > 0:
                ax.axhline(y=df['turnover'].median(), color='yellow', linestyle='--', alpha=0.3)

            # Grilla
            ax.grid(True, alpha=0.3, color='white')

            # Guardar límites originales para zoom
            self.original_xlim = ax.get_xlim()
            self.original_ylim = ax.get_ylim()

            # Ajustar layout
            self.figure.tight_layout()
            self.update_scrollbars()
            self.canvas.draw_idle()

        except Exception as e:
            print(f"Error creando gráfico: {e}")
            ax.text(0.5, 0.5, f'Error: {str(e)}',
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='red')
            self.canvas.draw_idle()

    def prepare_data(self, df):
        """Preparar datos para graficar"""
        try:
            data = df.copy()

            # Mapear columnas comunes
            column_mapping = {
                'ticker': 'symbol',
                'simbolo': 'symbol',
                'precio': 'price',
                'turnover': 'turnover',
                'variacion': 'change',
                'var': 'change',
                'cambio': 'change',
                'pct_change': 'change'
            }

            for old_col, new_col in column_mapping.items():
                if old_col in data.columns and new_col not in data.columns:
                    data[new_col] = data[old_col]

            # Verificar que tenemos las columnas necesarias
            if 'symbol' not in data.columns:
                if data.index.name:
                    data['symbol'] = data.index
                else:
                    data['symbol'] = [f'INST_{i}' for i in range(len(data))]

            if 'turnover' not in data.columns:
                # Intentar encontrar una columna de turnover
                vol_cols = [col for col in data.columns if 'vol' in col.lower()]
                if vol_cols:
                    data['turnover'] = pd.to_numeric(data[vol_cols[0]], errors='coerce')
                else:
                    data['turnover'] = np.random.randint(1000, 100000, len(data))

            if 'change' not in data.columns:
                # Intentar encontrar una columna de variación
                change_cols = [col for col in data.columns if any(word in col.lower() for word in ['var', 'change', 'pct', 'cambio'])]
                if change_cols:
                    data['change'] = pd.to_numeric(data[change_cols[0]], errors='coerce')
                else:
                    data['change'] = np.random.uniform(-5, 5, len(data))

            # Limpiar datos
            data = data.dropna(subset=['symbol'])
            data['turnover'] = pd.to_numeric(data['turnover'], errors='coerce')
            data['change'] = pd.to_numeric(data['change'], errors='coerce')
            data = data.dropna(subset=['turnover', 'change'])

            return data[['symbol', 'turnover', 'change']]

        except Exception as e:
            print(f"Error preparando datos: {e}")
            return None

    def update_scrollbars(self):
        """Actualiza el rango y posición de las barras de desplazamiento."""
        ax = self.figure.gca()
        if ax is None or self.original_xlim is None or self.original_ylim is None:
            return

        current_xlim = ax.get_xlim()
        current_ylim = ax.get_ylim()

        # Horizontal Scrollbar
        original_width = self.original_xlim[1] - self.original_xlim[0]
        current_width = current_xlim[1] - current_xlim[0]

        if original_width > 0 and current_width > 0:
            h_range = original_width - current_width
            if h_range > 0:
                h_value = (current_xlim[0] - self.original_xlim[0]) / h_range * 1000
                self.h_scrollbar.blockSignals(True)
                self.h_scrollbar.setRange(0, 1000)
                self.h_scrollbar.setValue(int(h_value))
                self.h_scrollbar.setPageStep(int(current_width / original_width * 1000))
                self.h_scrollbar.blockSignals(False)
                self.h_scrollbar.setEnabled(True)
            else:
                self.h_scrollbar.setEnabled(False)
        else:
            self.h_scrollbar.setEnabled(False)

        # Vertical Scrollbar
        original_height = self.original_ylim[1] - self.original_ylim[0]
        current_height = current_ylim[1] - current_ylim[0]

        if original_height > 0 and current_height > 0:
            v_range = original_height - current_height
            if v_range > 0:
                # Invertir para que el valor de la barra de desplazamiento coincida con la visualización
                v_value = (self.original_ylim[1] - current_ylim[1]) / v_range * 1000
                self.v_scrollbar.blockSignals(True)
                self.v_scrollbar.setRange(0, 1000)
                self.v_scrollbar.setValue(int(v_value))
                self.v_scrollbar.setPageStep(int(current_height / original_height * 1000))
                self.v_scrollbar.blockSignals(False)
                self.v_scrollbar.setEnabled(True)
            else:
                self.v_scrollbar.setEnabled(False)
        else:
            self.v_scrollbar.setEnabled(False)

    def h_scroll_plot(self, value):
        """Maneja el desplazamiento horizontal del gráfico."""
        ax = self.figure.gca()
        if ax is None or self.original_xlim is None:
            return

        original_width = self.original_xlim[1] - self.original_xlim[0]
        current_xlim = ax.get_xlim()
        current_width = current_xlim[1] - current_xlim[0]

        if original_width > 0 and original_width > current_width:
            h_range = original_width - current_width
            new_x_start = self.original_xlim[0] + (value / 1000.0) * h_range
            ax.set_xlim(new_x_start, new_x_start + current_width)
            self.canvas.draw_idle()

    def v_scroll_plot(self, value):
        """Maneja el desplazamiento vertical del gráfico."""
        ax = self.figure.gca()
        if ax is None or self.original_ylim is None:
            return

        original_height = self.original_ylim[1] - self.original_ylim[0]
        current_ylim = ax.get_ylim()
        current_height = current_ylim[1] - current_ylim[0]

        if original_height > 0 and original_height > current_height:
            v_range = original_height - current_height
            # Invertir para que el valor de la barra de desplazamiento coincida con la visualización
            new_y_start = self.original_ylim[1] - (value / 1000.0) * v_range - current_height
            ax.set_ylim(new_y_start, new_y_start + current_height)
            self.canvas.draw_idle()

class SHDAHomeBrokerApp(QMainWindow):
    """Aplicación principal"""

    def __init__(self):
        super().__init__()

        # Configuración de conexión
        self.host = 123
        self.dni = "12345678"
        self.user = "nnnnnnnnn"
        self.password = "xxxxxxxxx"
        self.comitente = 12345
        self.hb = None
        self.is_running = True

        # Datos
        self.data_storage = {
            'bluechips': None,
            'galpones': None,
            'bonds': None,
            'cedears': None,
            'short_term_bonds': None,
        }

        # Worker y timer
        self.worker = None
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.fetch_data)

        self.setup_ui()
        self.setup_styles()

        # Fetch inicial
        self.fetch_data()

    def setup_ui(self):
        """Configurar interfaz de usuario"""
        self.setWindowTitle("Análisis de Mercado")
        self.setGeometry(100, 200, 1800, 900)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Panel de control
        control_frame = QFrame()
        control_frame.setMaximumHeight(80)
        control_layout = QHBoxLayout(control_frame)

        # Botones
        self.fetch_btn = QPushButton("📊 Actualizar Datos")
        self.auto_update_checkbox = QCheckBox("Auto-actualizar")
        self.auto_update_checkbox.setStyleSheet("color: #cccccc; font-style: regular;")
        self.auto_update_checkbox.setChecked(True)

        # Intervalo de actualización
        interval_label = QLabel("Intervalo (min):")
        interval_label.setStyleSheet("color: #cccccc; font-style: regular;")
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 60)
        self.interval_spinbox.setValue(3)

        # Info de zoom
        zoom_info = QLabel("💡 Usa la rueda del mouse para zoom, click izquierdo para pan, scrollbars para mover el gráfico.")
        zoom_info.setStyleSheet("color: #cccccc; font-style: regular;")

        # Agregar controles
        control_layout.addWidget(self.fetch_btn)
        control_layout.addWidget(self.auto_update_checkbox)
        control_layout.addWidget(interval_label)
        control_layout.addWidget(self.interval_spinbox)
        control_layout.addWidget(zoom_info)
        control_layout.addStretch()

        # Conectar eventos
        self.fetch_btn.clicked.connect(self.fetch_data)
        self.auto_update_checkbox.toggled.connect(self.toggle_auto_update)
        self.interval_spinbox.valueChanged.connect(self.update_timer_interval)

        layout.addWidget(control_frame)

        # Splitter para dividir tabla y gráfico
        splitter = QSplitter(Qt.Horizontal)

        # Tab widget para tablas
        self.tab_widget = QTabWidget()
        self.tab_widget.setMaximumWidth(1000)

        # Crear tabs
        self.tables = {}
        self.plot_widgets = {}


        

        tab_configs = [
            ('bluechips', '🔵 Bluechips'),
            ('galpones', '🔵 Panel General'),
            ('bonds', '🔵 Bonos'),
            ('short_term_bonds', '🔴 Letras'),
            ('cedears', '🔴CEDEARs'),

        ]

        for key, title in tab_configs:
            # Tabla
            table = QTableWidget()
            table.setSortingEnabled(True)
            self.tables[key] = table
            self.tab_widget.addTab(table, title)

        splitter.addWidget(self.tab_widget)

        # Tab widget para gráficos
        self.plot_tab_widget = QTabWidget()

        for key, title in tab_configs:
            plot_widget = PlotWidget()
            self.plot_widgets[key] = plot_widget
            self.plot_tab_widget.addTab(plot_widget, title)

        splitter.addWidget(self.plot_tab_widget)
        splitter.setSizes([400, 800])

        layout.addWidget(splitter)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.connection_label = QLabel("Desconectado")
        self.status_bar.addPermanentWidget(self.connection_label)

        # Iniciar auto-actualización
        self.toggle_auto_update(True)

    def setup_styles(self):
        """Configurar estilos"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: white;
                padding: 8px 12px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #5d5d5d;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: white;
                gridline-color: #3d3d3d;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QStatusBar {
                background-color: #3d3d3d;
                color: white;
            }
            QScrollBar:horizontal {
                border: 1px solid #2d2d2d;
                background: #1e1e1e;
                height: 15px;
                margin: 0px 15px 0px 15px;
            }
            QScrollBar::handle:horizontal {
                background: #5d5d5d;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal {
                border: 1px solid #2d2d2d;
                background: #3d3d3d;
                width: 15px;
                subcontrol-position: right;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:horizontal {
                border: 1px solid #2d2d2d;
                background: #3d3d3d;
                width: 15px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }
            QScrollBar:vertical {
                border: 1px solid #2d2d2d;
                background: #1e1e1e;
                width: 15px;
                margin: 15px 0px 15px 0px;
            }
            QScrollBar::handle:vertical {
                background: #5d5d5d;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical {
                border: 1px solid #2d2d2d;
                background: #3d3d3d;
                height: 15px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                border: 1px solid #2d2d2d;
                background: #3d3d3d;
                height: 15px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
        """)

    def fetch_data(self):
        """Obtener datos de SHDA"""
        if self.worker and self.worker.isRunning():
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.fetch_btn.setEnabled(False)

        self.worker = SHDADataWorker(self.host, self.dni, self.user, self.password, self.comitente)

        # Conectar señales
        self.worker.bluechips_updated.connect(lambda data: self.update_data('bluechips', data))
        self.worker.galpones_updated.connect(lambda data: self.update_data('galpones', data))
        self.worker.bonds_updated.connect(lambda data: self.update_data('bonds', data))
        self.worker.cedears_updated.connect(lambda data: self.update_data('cedears', data))
        self.worker.short_term_bonds_updated.connect(lambda data: self.update_data('short_term_bonds', data))

        self.worker.status_updated.connect(self.update_status)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.progress_updated.connect(self.progress_bar.setValue)

        self.worker.finished.connect(self.on_worker_finished)

        self.worker.start()

    def update_data(self, data_type, data):
        """Actualizar datos y visualizaciones"""
        try:
            # Almacenar datos
            self.data_storage[data_type] = data.copy()

            # Actualizar tabla
            self.update_table(data_type, data)

            # Actualizar gráfico
            self.update_plot(data_type, data)

        except Exception as e:
            print(f"Error actualizando {data_type}: {e}")
            self.show_error(f"Error actualizando {data_type}: {str(e)}")

    def update_table(self, data_type, data):
        """Actualizar tabla"""
        try:
            table = self.tables[data_type]

            if data is None or data.empty:
                table.setRowCount(0)
                table.setColumnCount(0)
                return

            # Configurar tabla
            table.setRowCount(len(data))
            table.setColumnCount(len(data.columns))
            table.setHorizontalHeaderLabels(data.columns.tolist())

            # Llenar tabla
            for row_idx, (_, row) in enumerate(data.iterrows()):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))

                    # Colorear celdas de variación
                    if 'var' in data.columns[col_idx].lower() or 'change' in data.columns[col_idx].lower():
                        try:
                            val = float(value)
                            if val > 0:
                                item.setBackground(QColor(68, 255, 68, 50))
                            elif val < 0:
                                item.setBackground(QColor(255, 68, 68, 50))
                        except:
                            pass

                    table.setItem(row_idx, col_idx, item)

            table.resizeColumnsToContents()

        except Exception as e:
            print(f"Error actualizando tabla {data_type}: {e}")

    def update_plot(self, data_type, data):
        """Actualizar gráfico"""
        try:
            plot_widget = self.plot_widgets[data_type]

            titles = {
                'bluechips': 'Bluechips - Volumen vs Variación',
                'galpones': 'Panel General - Volumen vs Variación',
                'bonds': 'Bonos - Volumen vs Variación',
                'cedears': 'CEDEARs - Volumen vs Variación',
                'short_term_bonds': 'Letras - Volumen vs Variación',
            }

            plot_widget.plot_bubble_chart(data, titles.get(data_type, data_type), data_type)

        except Exception as e:
            print(f"Error actualizando gráfico {data_type}: {e}")

    def toggle_auto_update(self, enabled):
        """Activar/desactivar auto-actualización"""
        if enabled:
            interval_ms = self.interval_spinbox.value() * 60 * 1000  # Convertir a ms
            self.update_timer.start(interval_ms)
            self.connection_label.setText("Auto-actualización activa")
            self.connection_label.setStyleSheet("color: green")
        else:
            self.update_timer.stop()
            self.connection_label.setText("Auto-actualización desactivada")
            self.connection_label.setStyleSheet("color: orange")

    def update_timer_interval(self, minutes):
        """Actualizar intervalo del timer"""
        if self.update_timer.isActive():
            self.update_timer.stop()
            self.update_timer.start(minutes * 60 * 1000)

    def on_worker_finished(self):
        """Cuando termina el worker"""
        self.progress_bar.setVisible(False)
        self.fetch_btn.setEnabled(True)

    def update_status(self, message):
        """Actualizar mensaje de estado"""
        self.status_bar.showMessage(message, 5000)

    def show_error(self, error_message):
        """Mostrar error"""
        QMessageBox.critical(self, "Error", error_message)
        self.status_bar.showMessage(f"Error: {error_message}", 10000)

    def closeEvent(self, event):
        """Al cerrar la aplicación"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        self.update_timer.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SHDA HomeBroker")

    # Configurar fuente
    font = QFont("Arial", 9)
    app.setFont(font)

    window = SHDAHomeBrokerApp()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
