
import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from Funciones import (agregar_ingreso, agregar_gasto, obtener_ingresos, obtener_gastos,
                      obtener_total_gastos, obtener_total_por_categoria_periodo, exportar_reportes,
                      calculate_period_dates)

# Ruta de la base de datos SQLite
DB_PATH = os.path.join("MGF", "gastos.db")

class GastoApp:
    def __init__(self, root):
        # Inicializa la ventana principal
        self.root = root
        self.root.title("Monitoreo de Gastos Familiares 💰")
        self.root.geometry("1200x900")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#E5E7EB", borderwidth=1, relief=tk.FLAT)
        
        # Intenta cargar el ícono de la aplicación
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # Define la paleta de colores para la interfaz
        self.primary_color = "#3B82F6"   # Azul moderno
        self.secondary_color = "#6366F1" # Índigo para hover
        self.text_color = "#1F2A44"      # Gris oscuro para texto
        self.success_color = "#22C55E"   # Verde vibrante
        self.danger_color = "#EF4444"    # Rojo para errores
        self.warning_color = "#F59E0B"   # Ámbar para alertas
        self.neutral_color = "#6B7280"   # Gris neutro
        self.bg_color = "#F8FAFC"        # Fondo claro
        self.light_bg = "#F1F5F9"        # Fondo alterno
        self.card_bg = "#FFFFFF"         # Blanco puro para tarjetas
        
        # Verifica si la base de datos existe
        if not os.path.exists(DB_PATH):
            messagebox.showerror("Error", "La base de datos no existe. Ejecute BD.py primero.")
            self.root.quit()
            return

        # Configura los estilos visuales
        self.setup_styles()
        
        # Crea el notebook para las pestañas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=15, pady=15)

        # Define los frames para cada pestaña
        self.ingresos_frame = ttk.Frame(self.notebook)
        self.gastos_frame = ttk.Frame(self.notebook)
        self.reportes_frame = ttk.Frame(self.notebook)
        self.resumen_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.ingresos_frame, text="Ingresos 📊")
        self.notebook.add(self.gastos_frame, text="Gastos 💸")
        self.notebook.add(self.reportes_frame, text="Reportes 📈")
        self.notebook.add(self.resumen_frame, text="Resumen 🏆")

        # Configura las interfaces de cada pestaña
        self.setup_ingresos()
        self.setup_gastos()
        self.setup_reportes()
        self.setup_resumen()
        
        # Barra de estado en la parte inferior
        self.status_bar = ttk.Label(root, text="Listo", relief=tk.FLAT, anchor=tk.W,
                                   background=self.light_bg, foreground=self.neutral_color,
                                   font=("Inter", 10), padding=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Actualiza los datos iniciales
        self.mostrar_ingresos()
        self.mostrar_gastos()
        self.actualizar_reportes()
        self.actualizar_resumen()

    def setup_styles(self):
        """Configura los estilos visuales de la aplicación"""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configura estilos generales
        self.style.configure(".", font=("Inter", 11))
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TButton", padding=10, font=("Inter", 11, "bold"))
        self.style.configure("TEntry", fieldbackground=self.light_bg, padding=8)
        self.style.configure("TCombobox", fieldbackground=self.light_bg, padding=8)
        
        # Estilos para botones
        self.style.configure("Primary.TButton", background=self.primary_color, foreground="white")
        self.style.map("Primary.TButton",
                      background=[("active", self.secondary_color), ("disabled", self.neutral_color)],
                      foreground=[("active", "white"), ("disabled", "white")])
        
        self.style.configure("Success.TButton", background=self.success_color, foreground="white")
        self.style.map("Success.TButton",
                      background=[("active", "#16A34A"), ("disabled", self.neutral_color)])
        
        self.style.configure("Danger.TButton", background=self.danger_color, foreground="white")
        self.style.map("Danger.TButton",
                      background=[("active", "#DC2626"), ("disabled", self.neutral_color)])
        
        # Estilo para pestañas
        self.style.configure("TNotebook", background=self.bg_color)
        self.style.configure("TNotebook.Tab", padding=[12, 8], font=("Inter", 11, "bold"))
        self.style.map("TNotebook.Tab",
                      background=[("selected", self.card_bg), ("active", self.light_bg)],
                      foreground=[("selected", self.primary_color), ("active", self.text_color)])
        
        # Estilo para tablas
        self.style.configure("Treeview", background=self.card_bg, fieldbackground=self.card_bg, 
                           foreground=self.text_color, rowheight=28)
        self.style.configure("Treeview.Heading", background=self.primary_color, foreground="white", 
                           font=("Inter", 11, "bold"))
        self.style.map("Treeview", background=[("selected", self.secondary_color)])
        
        # Estilo para tarjetas
        self.style.configure("Card.TFrame", background=self.card_bg, relief=tk.RAISED, borderwidth=1, 
                           bordercolor="#E5E7EB")
        self.style.configure("Card.TLabel", background=self.card_bg)

    def validate_date(self, date_str):
        """Valida que la fecha tenga formato YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_amount(self, amount_str):
        """Valida que el monto sea un número positivo"""
        try:
            amount = float(amount_str)
            return amount >= 0
        except ValueError:
            return False

    def setup_ingresos(self):
        """Configura la pestaña de ingresos con formulario y tabla"""
        main_frame = ttk.Frame(self.ingresos_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(title_frame, text="Gestión de Ingresos", font=("Inter", 22, "bold"), 
                 foreground=self.primary_color).pack(side=tk.LEFT)
        
        # Panel de formulario
        form_card = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        form_card.pack(fill=tk.X, pady=10)
        
        ttk.Label(form_card, text="Agregar Nuevo Ingreso", font=("Inter", 14, "bold"), 
                 foreground=self.primary_color).pack(anchor=tk.W, pady=(0, 15))
        
        # Campos del formulario
        fields = [
            ("Fecha (YYYY-MM-DD)", self.validate_date),
            ("Monto", self.validate_amount),
            ("Descripción", None),
            ("Usuario", None),
            ("Notas", None)
        ]
        
        self.ing_entries = {}
        for idx, (label, validator) in enumerate(fields):
            row = ttk.Frame(form_card)
            row.pack(fill=tk.X, pady=8)
            
            ttk.Label(row, text=label, width=15, font=("Inter", 11), anchor=tk.E).pack(side=tk.LEFT, padx=10)
            
            if label == "Fecha (YYYY-MM-DD)":
                entry = ttk.Entry(row, font=("Inter", 11))
                entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            elif label == "Usuario":
                entry = ttk.Entry(row, font=("Inter", 11))
                entry.insert(0, "Familia")
            else:
                entry = ttk.Entry(row, font=("Inter", 11))
                
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
            self.ing_entries[label] = (entry, validator)
            
            if label in ["Fecha (YYYY-MM-DD)", "Monto"]:
                help_btn = ttk.Button(row, text="?", width=2, style="Danger.TButton",
                                    command=lambda l=label: self.show_help(l))
                help_btn.pack(side=tk.LEFT, padx=5)
        
        # Botones de acción
        btn_frame = ttk.Frame(form_card)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(btn_frame, text="Limpiar", style="Danger.TButton",
                  command=self.limpiar_formulario_ingresos).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Agregar Ingreso", style="Success.TButton",
                  command=self.guardar_ingreso).pack(side=tk.RIGHT, padx=10)
        
        # Panel de visualización de datos
        data_card = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        data_card.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Controles de filtrado
        filter_frame = ttk.Frame(data_card)
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(filter_frame, text="Filtrar por:", font=("Inter", 11)).pack(side=tk.LEFT, padx=10)
        
        self.periodo_ing = ttk.Combobox(filter_frame, values=["Todos", "Hoy", "Semana", "Mes", "Año"], 
                                      state="readonly", width=12, font=("Inter", 11))
        self.periodo_ing.set("Todos")
        self.periodo_ing.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(filter_frame, text="Aplicar", style="Primary.TButton",
                  command=self.mostrar_ingresos).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(filter_frame, text="Exportar CSV", style="Primary.TButton",
                  command=lambda: self.exportar_datos("ingresos")).pack(side=tk.RIGHT, padx=10)
        
        # Tabla de ingresos
        table_frame = ttk.Frame(data_card)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Fecha", "Monto", "Descripción", "Usuario")
        self.tabla_ingresos = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        col_widths = [120, 100, 250, 150]
        for col, width in zip(columns, col_widths):
            self.tabla_ingresos.heading(col, text=col, anchor=tk.CENTER)
            self.tabla_ingresos.column(col, width=width, anchor=tk.CENTER)
        
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tabla_ingresos.yview)
        self.tabla_ingresos.configure(yscrollcommand=scroll_y.set)
        
        self.tabla_ingresos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tabla_ingresos.tag_configure("oddrow", background="#F9FAFB")
        self.tabla_ingresos.tag_configure("evenrow", background="#FFFFFF")

    def setup_gastos(self):
        """Configura la pestaña de gastos con formulario y tabla"""
        main_frame = ttk.Frame(self.gastos_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(title_frame, text="Gestión de Gastos", font=("Inter", 22, "bold"), 
                 foreground=self.primary_color).pack(side=tk.LEFT)
        
        # Panel de formulario
        form_card = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        form_card.pack(fill=tk.X, pady=10)
        
        ttk.Label(form_card, text="Agregar Nuevo Gasto", font=("Inter", 14, "bold"), 
                 foreground=self.primary_color).pack(anchor=tk.W, pady=(0, 15))
        
        # Campos del formulario
        fields = [
            ("Fecha (YYYY-MM-DD)", self.validate_date),
            ("Categoría", None),
            ("Monto", self.validate_amount),
            ("Descripción", None),
            ("Usuario", None),
            ("Notas", None)
        ]
        
        self.gas_entries = {}
        for idx, (label, validator) in enumerate(fields):
            row = ttk.Frame(form_card)
            row.pack(fill=tk.X, pady=8)
            
            ttk.Label(row, text=label, width=15, font=("Inter", 11), anchor=tk.E).pack(side=tk.LEFT, padx=10)
            
            if label == "Fecha (YYYY-MM-DD)":
                entry = ttk.Entry(row, font=("Inter", 11))
                entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            elif label == "Categoría":
                entry = ttk.Combobox(row, values=["Alimentación", "Transporte", "Vivienda", 
                                                "Salud", "Educación", "Entretenimiento", 
                                                "Ropa", "Otros"], state="readonly", font=("Inter", 11))
                entry.set("Alimentación")
            elif label == "Usuario":
                entry = ttk.Entry(row, font=("Inter", 11))
                entry.insert(0, "Familia")
            else:
                entry = ttk.Entry(row, font=("Inter", 11))
                
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
            self.gas_entries[label] = (entry, validator)
            
            if label in ["Fecha (YYYY-MM-DD)", "Monto", "Categoría"]:
                help_btn = ttk.Button(row, text="?", width=2, style="Danger.TButton",
                                    command=lambda l=label: self.show_help(l))
                help_btn.pack(side=tk.LEFT, padx=5)
        
        # Botones de acción
        btn_frame = ttk.Frame(form_card)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(btn_frame, text="Limpiar", style="Danger.TButton",
                  command=self.limpiar_formulario_gastos).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Agregar Gasto", style="Success.TButton",
                  command=self.guardar_gasto).pack(side=tk.RIGHT, padx=10)
        
        # Panel de visualización de datos
        data_card = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        data_card.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Controles de filtrado
        filter_frame = ttk.Frame(data_card)
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(filter_frame, text="Filtrar por:", font=("Inter", 11)).pack(side=tk.LEFT, padx=10)
        
        self.periodo_gas = ttk.Combobox(filter_frame, values=["Todos", "Hoy", "Semana", "Mes", "Año"], 
                                      state="readonly", width=12, font=("Inter", 11))
        self.periodo_gas.set("Todos")
        self.periodo_gas.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(filter_frame, text="Aplicar", style="Primary.TButton",
                  command=self.mostrar_gastos).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(filter_frame, text="Exportar CSV", style="Primary.TButton",
                  command=lambda: self.exportar_datos("gastos")).pack(side=tk.RIGHT, padx=10)
        
        # Tabla de gastos
        table_frame = ttk.Frame(data_card)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Fecha", "Categoría", "Monto", "Descripción", "Usuario")
        self.tabla_gastos = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        col_widths = [120, 120, 100, 200, 150]
        for col, width in zip(columns, col_widths):
            self.tabla_gastos.heading(col, text=col, anchor=tk.CENTER)
            self.tabla_gastos.column(col, width=width, anchor=tk.CENTER)
        
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tabla_gastos.yview)
        self.tabla_gastos.configure(yscrollcommand=scroll_y.set)
        
        self.tabla_gastos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tabla_gastos.tag_configure("oddrow", background="#F9FAFB")
        self.tabla_gastos.tag_configure("evenrow", background="#FFFFFF")

    def setup_reportes(self):
        """Configura la pestaña de reportes con métricas y gráficos"""
        main_frame = ttk.Frame(self.reportes_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(title_frame, text="Reportes y Análisis", font=("Inter", 22, "bold"), 
                 foreground=self.primary_color).pack(side=tk.LEFT)
        
        # Panel de resumen
        summary_card = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        summary_card.pack(fill=tk.X, pady=10)
        
        # Fila de métricas
        metrics_frame = ttk.Frame(summary_card)
        metrics_frame.pack(fill=tk.X, pady=10)
        
        self.metric_ingresos = self.create_metric(metrics_frame, "Ingresos", "$0.00", self.success_color)
        self.metric_gastos = self.create_metric(metrics_frame, "Gastos", "$0.00", self.danger_color)
        self.metric_balance = self.create_metric(metrics_frame, "Balance", "$0.00", self.primary_color)
        
        # Controles de filtrado
        filter_frame = ttk.Frame(summary_card)
        filter_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(filter_frame, text="Período:", font=("Inter", 11)).pack(side=tk.LEFT, padx=10)
        
        self.periodo_reportes = ttk.Combobox(filter_frame, values=["Hoy", "Semana", "Mes", "Año", "Todos"], 
                                           state="readonly", width=12, font=("Inter", 11))
        self.periodo_reportes.set("Mes")
        self.periodo_reportes.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(filter_frame, text="Actualizar", style="Primary.TButton",
                  command=self.actualizar_reportes).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(filter_frame, text="Exportar Reporte", style="Success.TButton",
                  command=self.exportar_csv).pack(side=tk.RIGHT, padx=10)
        
        # Panel de gráficos
        graph_card = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        graph_card.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Notebook para gráficos
        graph_notebook = ttk.Notebook(graph_card)
        graph_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de gráfico de barras
        bar_frame = ttk.Frame(graph_notebook)
        graph_notebook.add(bar_frame, text="Gastos por Categoría")
        
        self.fig_bar = Figure(figsize=(10, 5), dpi=100, facecolor=self.bg_color)
        self.canvas_bar = FigureCanvasTkAgg(self.fig_bar, master=bar_frame)
        self.canvas_bar.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(self.canvas_bar, bar_frame)
        toolbar.update()
        self.canvas_bar._tkcanvas.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de gráfico circular
        pie_frame = ttk.Frame(graph_notebook)
        graph_notebook.add(pie_frame, text="Distribución de Gastos")
        
        self.fig_pie = Figure(figsize=(10, 5), dpi=100, facecolor=self.bg_color)
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, master=pie_frame)
        self.canvas_pie.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar_pie = NavigationToolbar2Tk(self.canvas_pie, pie_frame)
        toolbar_pie.update()
        self.canvas_pie._tkcanvas.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de tendencias
        trend_frame = ttk.Frame(graph_notebook)
        graph_notebook.add(trend_frame, text="Tendencias Mensuales")
        
        self.fig_trend = Figure(figsize=(10, 5), dpi=100, facecolor=self.bg_color)
        self.canvas_trend = FigureCanvasTkAgg(self.fig_trend, master=trend_frame)
        self.canvas_trend.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar_trend = NavigationToolbar2Tk(self.canvas_trend, trend_frame)
        toolbar_trend.update()
        self.canvas_trend._tkcanvas.pack(fill=tk.BOTH, expand=True)

    def setup_resumen(self):
        """Configura la pestaña de resumen con estadísticas y consejos"""
        main_frame = ttk.Frame(self.resumen_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(title_frame, text="Resumen Financiero", font=("Inter", 22, "bold"), 
                 foreground=self.primary_color).pack(side=tk.LEFT)
        
        # Panel de estadísticas rápidas
        quick_stats_card = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        quick_stats_card.pack(fill=tk.X, pady=10)
        
        stats_frame = ttk.Frame(quick_stats_card)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.quick_ingresos = self.create_quick_stat(stats_frame, "Ingresos Mensuales", "$0.00", 
                                                    self.success_color, "📈")
        self.quick_gastos = self.create_quick_stat(stats_frame, "Gastos Mensuales", "$0.00", 
                                                  self.danger_color, "💸")
        self.quick_balance = self.create_quick_stat(stats_frame, "Balance", "$0.00", 
                                                   self.primary_color, "💰")
        self.quick_ahorro = self.create_quick_stat(stats_frame, "Tasa de Ahorro", "0%", 
                                                 self.warning_color, "🏦")
        
        # Panel de categorías
        categories_card = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        categories_card.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        ttk.Label(categories_card, text="Gastos por Categoría", font=("Inter", 14, "bold"), 
                 foreground=self.primary_color).pack(anchor=tk.W, pady=(0, 15))
        
        self.fig_summary = Figure(figsize=(8, 4), dpi=100, facecolor=self.bg_color)
        self.canvas_summary = FigureCanvasTkAgg(self.fig_summary, master=categories_card)
        self.canvas_summary.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar_summary = NavigationToolbar2Tk(self.canvas_summary, categories_card)
        toolbar_summary.update()
        self.canvas_summary._tkcanvas.pack(fill=tk.BOTH, expand=True)
        
        # Panel de consejos
        tips_card = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        tips_card.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(tips_card, text="Consejos Financieros", font=("Inter", 14, "bold"), 
                 foreground=self.primary_color).pack(anchor=tk.W, pady=(0, 15))
        
        self.tips_text = tk.Text(tips_card, height=4, wrap=tk.WORD, bg=self.card_bg, 
                               font=("Inter", 11), padx=10, pady=10)
        self.tips_text.pack(fill=tk.X)
        self.tips_text.insert(tk.END, "Cargando consejos...")
        self.tips_text.config(state=tk.DISABLED)

    def create_metric(self, parent, title, value, color):
        """Crea un widget para mostrar métricas"""
        metric_frame = ttk.Frame(parent, style="Card.TFrame", padding=15)
        metric_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
        
        ttk.Label(metric_frame, text=title, font=("Inter", 11), 
                 foreground=self.neutral_color).pack(anchor=tk.W)
        value_label = ttk.Label(metric_frame, text=value, font=("Inter", 16, "bold"), 
                              foreground=color)
        value_label.pack(anchor=tk.W, pady=(5, 0))
        
        return value_label

    def create_quick_stat(self, parent, title, value, color, icon):
        """Crea un widget para estadísticas rápidas"""
        stat_frame = ttk.Frame(parent, style="Card.TFrame", padding=15)
        stat_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
        
        header_frame = ttk.Frame(stat_frame)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text=icon, font=("Inter", 14)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(header_frame, text=title, font=("Inter", 11, "bold"), 
                 foreground=self.neutral_color).pack(side=tk.LEFT)
        
        value_label = ttk.Label(stat_frame, text=value, font=("Inter", 18, "bold"), 
                              foreground=color)
        value_label.pack(anchor=tk.CENTER, pady=(10, 0))
        
        return value_label

    def show_help(self, field):
        """Muestra ayuda para campos del formulario"""
        help_messages = {
            "Fecha (YYYY-MM-DD)": "Ingrese la fecha en formato año-mes-día (ej. 2023-12-31)",
            "Monto": "Ingrese un valor numérico positivo (ej. 1250.50)",
            "Categoría": "Seleccione la categoría que mejor describa el gasto"
        }
        
        messagebox.showinfo("Ayuda", help_messages.get(field, "No hay información de ayuda disponible."))

    def limpiar_formulario_ingresos(self):
        """Limpia los campos del formulario de ingresos"""
        for label, (entry, _) in self.ing_entries.items():
            if label == "Fecha (YYYY-MM-DD)":
                entry.delete(0, tk.END)
                entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            elif label == "Usuario":
                entry.delete(0, tk.END)
                entry.insert(0, "Familia")
            else:
                entry.delete(0, tk.END)
        
        self.status_bar.config(text="Formulario de ingresos limpiado")

    def limpiar_formulario_gastos(self):
        """Limpia los campos del formulario de gastos"""
        for label, (entry, _) in self.gas_entries.items():
            if label == "Fecha (YYYY-MM-DD)":
                entry.delete(0, tk.END)
                entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            elif label == "Categoría":
                entry.set("Alimentación")
            elif label == "Usuario":
                entry.delete(0, tk.END)
                entry.insert(0, "Familia")
            else:
                entry.delete(0, tk.END)
        
        self.status_bar.config(text="Formulario de gastos limpiado")

    def guardar_ingreso(self):
        """Guarda un ingreso en la base de datos"""
        fecha = self.ing_entries["Fecha (YYYY-MM-DD)"][0].get()
        monto = self.ing_entries["Monto"][0].get()
        desc = self.ing_entries["Descripción"][0].get()
        user = self.ing_entries["Usuario"][0].get()
        notes = self.ing_entries["Notas"][0].get()

        if not self.validate_date(fecha):
            messagebox.showerror("Error", "Formato de fecha inválido (YYYY-MM-DD).")
            return
        if not self.validate_amount(monto):
            messagebox.showerror("Error", "Monto inválido. Debe ser un número positivo.")
            return

        try:
            agregar_ingreso(fecha, float(monto), desc, user, notes)
            messagebox.showinfo("Éxito", "Ingreso agregado correctamente.")
            self.limpiar_formulario_ingresos()
            self.mostrar_ingresos()
            self.actualizar_reportes()
            self.actualizar_resumen()
            self.status_bar.config(text="Ingreso registrado exitosamente")
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudo guardar el ingreso: {ex}")
            self.status_bar.config(text=f"Error al guardar ingreso: {ex}")

    def mostrar_ingresos(self):
        """Muestra los ingresos en la tabla según el filtro"""
        for item in self.tabla_ingresos.get_children():
            self.tabla_ingresos.delete(item)
            
        try:
            periodo = self.periodo_ing.get()
            ingresos = obtener_ingresos(periodo)
            
            if not ingresos:
                self.status_bar.config(text=f"No hay ingresos para mostrar ({periodo})")
                return
                
            for i, ingreso in enumerate(ingresos):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.tabla_ingresos.insert("", tk.END, values=(
                    ingreso[0], 
                    f"{ingreso[1]:.2f}", 
                    ingreso[2] or "-", 
                    ingreso[3] or "-"
                ), tags=(tag,))
                
            self.status_bar.config(text=f"Mostrando {len(ingresos)} ingresos ({periodo})")
        except Exception as ex:
            messagebox.showerror("Error", f"Error al cargar ingresos: {ex}")
            self.status_bar.config(text=f"Error al cargar ingresos: {ex}")

    def guardar_gasto(self):
        """Guarda un gasto en la base de datos"""
        fecha = self.gas_entries["Fecha (YYYY-MM-DD)"][0].get()
        categoria = self.gas_entries["Categoría"][0].get()
        monto = self.gas_entries["Monto"][0].get()
        desc = self.gas_entries["Descripción"][0].get()
        user = self.gas_entries["Usuario"][0].get()
        notes = self.gas_entries["Notas"][0].get()

        if not self.validate_date(fecha):
            messagebox.showerror("Error", "Formato de fecha inválido (YYYY-MM-DD).")
            return
        if not categoria:
            messagebox.showerror("Error", "Seleccione una categoría.")
            return
        if not self.validate_amount(monto):
            messagebox.showerror("Error", "Monto inválido. Debe ser un número positivo.")
            return

        try:
            agregar_gasto(fecha, categoria, float(monto), desc, user, notes)
            messagebox.showinfo("Éxito", "Gasto agregado correctamente.")
            self.limpiar_formulario_gastos()
            self.mostrar_gastos()
            self.actualizar_reportes()
            self.actualizar_resumen()
            self.status_bar.config(text="Gasto registrado exitosamente")
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudo guardar el gasto: {ex}")
            self.status_bar.config(text=f"Error al guardar gasto: {ex}")

    def mostrar_gastos(self):
        """Muestra los gastos en la tabla según el filtro"""
        for item in self.tabla_gastos.get_children():
            self.tabla_gastos.delete(item)
            
        try:
            periodo = self.periodo_gas.get()
            gastos = obtener_gastos(periodo)
            
            if not gastos:
                self.status_bar.config(text=f"No hay gastos para mostrar ({periodo})")
                return
                
            for i, gasto in enumerate(gastos):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.tabla_gastos.insert("", tk.END, values=(
                    gasto[0], 
                    gasto[1], 
                    f"{gasto[2]:.2f}", 
                    gasto[3] or "-", 
                    gasto[4] or "-"
                ), tags=(tag,))
                
            self.status_bar.config(text=f"Mostrando {len(gastos)} gastos ({periodo})")
        except Exception as ex:
            messagebox.showerror("Error", f"Error al cargar gastos: {ex}")
            self.status_bar.config(text=f"Error al cargar gastos: {ex}")

    def actualizar_reportes(self):
        """Actualiza métricas y gráficos en la pestaña de reportes"""
        try:
            periodo = self.periodo_reportes.get()
            start, end = calculate_period_dates(periodo)
            
            total_ingresos = sum(float(i[1]) for i in obtener_ingresos(periodo))
            total_gastos = obtener_total_gastos(periodo)
            balance = total_ingresos - total_gastos
            
            self.metric_ingresos.config(text=f"${total_ingresos:.2f}")
            self.metric_gastos.config(text=f"${total_gastos:.2f}")
            self.metric_balance.config(text=f"${balance:.2f}", 
                                     foreground=self.success_color if balance >= 0 else self.danger_color)
            
            self.generate_bar_chart(start, end)
            self.generate_pie_chart(start, end)
            self.generate_trend_chart()
            
            self.status_bar.config(text=f"Reportes actualizados ({periodo})")
        except Exception as ex:
            messagebox.showerror("Error", f"Error al actualizar reportes: {ex}")
            self.status_bar.config(text=f"Error al actualizar reportes: {ex}")

    def actualizar_resumen(self):
        """Actualiza estadísticas y gráficos en la pestaña de resumen"""
        try:
            total_ingresos = sum(float(i[1]) for i in obtener_ingresos("Mes"))
            total_gastos = obtener_total_gastos("Mes")
            balance = total_ingresos - total_gastos
            tasa_ahorro = (balance / total_ingresos * 100) if total_ingresos > 0 else 0
            
            self.quick_ingresos.config(text=f"${total_ingresos:.2f}")
            self.quick_gastos.config(text=f"${total_gastos:.2f}")
            self.quick_balance.config(text=f"${balance:.2f}", 
                                    foreground=self.success_color if balance >= 0 else self.danger_color)
            self.quick_ahorro.config(text=f"{tasa_ahorro:.1f}%", 
                                   foreground=self.success_color if tasa_ahorro >= 0 else self.danger_color)
            
            self.generate_summary_chart()
            self.update_financial_tips(balance, tasa_ahorro)
            
            self.status_bar.config(text="Resumen actualizado")
        except Exception as ex:
            messagebox.showerror("Error", f"Error al actualizar resumen: {ex}")
            self.status_bar.config(text=f"Error al actualizar resumen: {ex}")

    def generate_bar_chart(self, start, end):
        """Genera un gráfico de barras de gastos por categoría"""
        try:
            self.fig_bar.clear()
            ax = self.fig_bar.add_subplot(111)
            
            totals = obtener_total_por_categoria_periodo(start, end)
            if not totals:
                ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=12, color=self.text_color)
                self.canvas_bar.draw()
                return
            
            totals_sorted = sorted(totals, key=lambda x: x[1], reverse=True)
            categories, amounts = zip(*totals_sorted) if totals_sorted else ([], [])
            
            colors = plt.cm.Blues([0.3 + x * 0.5 / len(amounts) for x in range(len(amounts))])
            
            bars = ax.bar(categories, amounts, color=colors, edgecolor="#E5E7EB", linewidth=1)
            ax.set_title(f"Gastos por Categoría ({start} a {end})", 
                        fontsize=16, pad=20, color=self.text_color)
            ax.set_xlabel("Categoría", fontsize=12, color=self.text_color)
            ax.set_ylabel("Monto ($)", fontsize=12, color=self.text_color)
            
            ax.tick_params(axis='x', rotation=45, colors=self.text_color)
            ax.tick_params(axis='y', colors=self.text_color)
            ax.set_facecolor(self.card_bg)
            ax.grid(True, axis="y", linestyle="--", alpha=0.4)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:.2f}', ha='center', va='bottom', 
                        color=self.text_color, fontsize=10)
            
            self.fig_bar.tight_layout()
            self.canvas_bar.draw()
        except Exception as ex:
            print(f"Error al generar gráfico de barras: {ex}")

    def generate_pie_chart(self, start, end):
        """Genera un gráfico circular de distribución de gastos"""
        try:
            self.fig_pie.clear()
            ax = self.fig_pie.add_subplot(111)
            
            totals = obtener_total_por_categoria_periodo(start, end)
            if not totals:
                ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=12, color=self.text_color)
                self.canvas_pie.draw()
                return
            
            totals_sorted = sorted(totals, key=lambda x: x[1], reverse=True)
            categories, amounts = zip(*totals_sorted) if totals_sorted else ([], [])
            
            threshold = sum(amounts) * 0.03
            main_categories = []
            main_amounts = []
            other_amount = 0
            
            for cat, amt in zip(categories, amounts):
                if amt >= threshold:
                    main_categories.append(cat)
                    main_amounts.append(amt)
                else:
                    other_amount += amt
            
            if other_amount > 0:
                main_categories.append("Otros")
                main_amounts.append(other_amount)
            
            colors = plt.cm.tab20c(range(len(main_categories)))
            
            wedges, texts, autotexts = ax.pie(main_amounts, labels=main_categories, 
                                            colors=colors, autopct='%1.1f%%',
                                            startangle=90, counterclock=False,
                                            textprops={'color': self.text_color, 'fontsize': 10})
            
            ax.set_title(f"Distribución de Gastos ({start} a {end})", 
                        fontsize=16, pad=20, color=self.text_color)
            
            ax.axis('equal')
            self.fig_pie.tight_layout()
            self.canvas_pie.draw()
        except Exception as ex:
            print(f"Error al generar gráfico circular: {ex}")

    def generate_trend_chart(self):
        """Genera un gráfico de tendencias mensuales"""
        try:
            self.fig_trend.clear()
            ax = self.fig_trend.add_subplot(111)
            
            meses = []
            ingresos = []
            gastos = []
            
            for i in range(12):
                date = datetime.now().replace(day=1)
                month = date.month - i
                year = date.year
                if month <= 0:
                    month += 12
                    year -= 1
                
                periodo = f"{year}-{month:02d}"
                meses.insert(0, periodo)
                
                total_ing = sum(float(i[1]) for i in obtener_ingresos(periodo))
                total_gas = obtener_total_gastos(periodo)
                
                ingresos.insert(0, total_ing)
                gastos.insert(0, total_gas)
            
            ax.plot(meses, ingresos, label='Ingresos', color=self.success_color, marker='o')
            ax.plot(meses, gastos, label='Gastos', color=self.danger_color, marker='o')
            
            ax.fill_between(meses, ingresos, gastos, where=[i >= g for i, g in zip(ingresos, gastos)], 
                          interpolate=True, color=self.success_color, alpha=0.2, 
                          label='Superávit')
            ax.fill_between(meses, ingresos, gastos, where=[i < g for i, g in zip(ingresos, gastos)], 
                          interpolate=True, color=self.danger_color, alpha=0.2, 
                          label='Déficit')
            
            ax.set_title("Tendencias Mensuales (Últimos 12 meses)", 
                        fontsize=16, pad=20, color=self.text_color)
            ax.set_xlabel("Mes", fontsize=12, color=self.text_color)
            ax.set_ylabel("Monto ($)", fontsize=12, color=self.text_color)
            
            ax.tick_params(axis='x', rotation=45, colors=self.text_color)
            ax.tick_params(axis='y', colors=self.text_color)
            ax.set_facecolor(self.card_bg)
            ax.grid(True, axis="y", linestyle="--", alpha=0.4)
            
            ax.legend(loc='upper left', facecolor=self.card_bg)
            
            self.fig_trend.tight_layout()
            self.canvas_trend.draw()
        except Exception as ex:
            print(f"Error al generar gráfico de tendencias: {ex}")

    def generate_summary_chart(self):
        """Genera un gráfico de barras horizontal para el resumen"""
        try:
            self.fig_summary.clear()
            ax = self.fig_summary.add_subplot(111)
            
            totals = obtener_total_por_categoria_periodo(*calculate_period_dates("Mes"))
            if not totals:
                ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=12, color=self.text_color)
                self.canvas_summary.draw()
                return
            
            totals_sorted = sorted(totals, key=lambda x: x[1], reverse=True)
            categories, amounts = zip(*totals_sorted) if totals_sorted else ([], [])
            
            colors = plt.cm.Pastel1(range(len(categories)))
            
            bars = ax.barh(categories, amounts, color=colors, edgecolor="#E5E7EB", linewidth=1)
            ax.set_title("Gastos del Mes por Categoría", 
                        fontsize=16, pad=20, color=self.text_color)
            ax.set_xlabel("Monto ($)", fontsize=12, color=self.text_color)
            
            ax.tick_params(axis='x', colors=self.text_color)
            ax.tick_params(axis='y', colors=self.text_color)
            ax.set_facecolor(self.card_bg)
            ax.grid(True, axis="x", linestyle="--", alpha=0.4)
            
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                        f'${width:.2f}', ha='left', va='center', 
                        color=self.text_color, fontsize=10)
            
            self.fig_summary.tight_layout()
            self.canvas_summary.draw()
        except Exception as ex:
            print(f"Error al generar gráfico de resumen: {ex}")

    def update_financial_tips(self, balance, savings_rate):
        """Actualiza los consejos financieros según balance y ahorros"""
        self.tips_text.config(state=tk.NORMAL)
        self.tips_text.delete(1.0, tk.END)
        
        tips = []
        
        if balance < 0:
            tips.append("⚠️ Estás gastando más de lo que ganas. Considera reducir gastos no esenciales.")
        elif savings_rate < 10:
            tips.append("💡 Tu tasa de ahorro es baja. Intenta ahorrar al menos el 10% de tus ingresos.")
        else:
            tips.append("✅ Buen trabajo! Mantén tus buenos hábitos financieros.")
        
        if savings_rate >= 20:
            tips.append("🌟 Excelente tasa de ahorro! Considera invertir parte de tus ahorros.")
        
        tips.append("📅 Revisa tus gastos regularmente para identificar patrones.")
        tips.append("🎯 Establece metas financieras claras y alcanzables.")
        tips.append("💳 Evita deudas de alto interés, especialmente en tarjetas de crédito.")
        
        self.tips_text.insert(tk.END, "\n\n".join(tips))
        self.tips_text.config(state=tk.DISABLED)

    def exportar_csv(self):
        """Exporta reportes a un archivo CSV"""
        try:
            periodo = self.periodo_reportes.get()
            file_path = exportar_reportes(periodo)
            messagebox.showinfo("Éxito", f"Reporte exportado exitosamente:\n{file_path}")
            self.status_bar.config(text=f"Reporte exportado: {os.path.basename(file_path)}")
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudo exportar el reporte: {ex}")
            self.status_bar.config(text=f"Error al exportar reporte: {ex}")

    def exportar_datos(self, tipo):
        """Exporta datos de ingresos o gastos a CSV"""
        try:
            periodo = self.periodo_ing.get() if tipo == "ingresos" else self.periodo_gas.get()
            file_path = exportar_reportes(periodo, tipo)
            messagebox.showinfo("Éxito", f"Datos de {tipo} exportados exitosamente:\n{file_path}")
            self.status_bar.config(text=f"{tipo.capitalize()} exportados: {os.path.basename(file_path)}")
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudieron exportar los datos: {ex}")
            self.status_bar.config(text=f"Error al exportar {tipo}: {ex}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GastoApp(root)
    root.mainloop()
