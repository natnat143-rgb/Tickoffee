import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import hashlib
import datetime
import os

# -----------------------------
# Configuración de la base de datos (SQLite)
# -----------------------------
DB_FILENAME = "app_pedidos.db"
TICKETS_TXT = "tickets.txt"


def get_db_connection():
    conn = sqlite3.connect(DB_FILENAME)
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Usuarios
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """
    )
    # Tickets
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total REAL,
        payment_method TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """
    )
    # Items por ticket
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS ticket_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER,
        item_name TEXT,
        item_type TEXT,
        price REAL,
        FOREIGN KEY(ticket_id) REFERENCES tickets(id)
    )
    """
    )
    conn.commit()
    conn.close()


# -----------------------------
# Utilidades
# -----------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def append_ticket_to_file(text: str):
    with open(TICKETS_TXT, "a", encoding="utf-8") as f:
        f.write(text + "\n\n")


# -----------------------------
# Datos del menú (puedes editarlos)
# -----------------------------
PRECIOS_PLATILLOS = {
    "Tacos": 15.0,
    "Quesadillas": 22.0,
    "Torta": 35.0,
    "Enchiladas": 45.0,
    "Hamburguesa": 55.0,
}

PRECIOS_BEBIDAS = {
    "Agua": 10.0,
    "Refresco": 18.0,
    "Cerveza": 28.0,
    "Jugo": 20.0,
    "Café": 12.0,
}

METODOS_PAGO = ["Tarjeta", "Efectivo", "Transferencia"]


# -----------------------------
# Aplicación Tkinter
# -----------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("🍽️ Sistema de Pedidos - Restaurante")
        self.root.geometry("760x640")
        # Para apariencia: ttk themes
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Usuario logueado (tuple id, username) o None
        self.current_user = None

        # Variables para cantidades (IntVar por producto)
        self.platillos_vars = {}  # nombre -> IntVar
        self.bebidas_vars = {}    # nombre -> IntVar
        self.metodo_pago_var = tk.StringVar(master=self.root, value="")

        # Frame contenedor principal
        self.container = ttk.Frame(self.root, padding=12)
        self.container.pack(fill="both", expand=True)

        # Iniciar DB
        init_db()

        # Mostrar pantalla de login
        self.pantalla_login()

    # -------------------------
    # Pantalla: Login / Registro
    # -------------------------
    def pantalla_login(self):
        self.limpiar_container()

        top = ttk.Frame(self.container, padding=10)
        top.pack(fill="x")

        lbl_title = ttk.Label(top, text="Bienvenido — Inicia sesión o regístrate", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=(4, 12))

        form = ttk.Frame(self.container, padding=10, relief="ridge")
        form.pack(fill="x", pady=8)

        ttk.Label(form, text="Usuario:").grid(row=0, column=0, sticky="w", pady=6, padx=6)
        self.login_username = ttk.Entry(form)
        self.login_username.grid(row=0, column=1, sticky="ew", padx=6)

        ttk.Label(form, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=6, padx=6)
        self.login_password = ttk.Entry(form, show="*")
        self.login_password.grid(row=1, column=1, sticky="ew", padx=6)

        form.columnconfigure(1, weight=1)

        btns = ttk.Frame(self.container, padding=6)
        btns.pack(fill="x")

        # Uso de emojis como "iconos"
        ttk.Button(btns, text="🔐 Iniciar sesión", command=self.handle_login).pack(side="left", padx=6)
        ttk.Button(btns, text="🧾 Registrarse", command=self.pantalla_registro).pack(side="left", padx=6)
        ttk.Button(btns, text="❓ Ayuda", command=self.mostrar_ayuda).pack(side="right", padx=6)

    def pantalla_registro(self):
        self.limpiar_container()

        lbl = ttk.Label(self.container, text="Registro de nuevo usuario", font=("Arial", 16, "bold"))
        lbl.pack(pady=8)

        form = ttk.Frame(self.container, padding=8, relief="ridge")
        form.pack(fill="x", pady=6)

        ttk.Label(form, text="Usuario:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.reg_username = ttk.Entry(form)
        self.reg_username.grid(row=0, column=1, sticky="ew", padx=6)

        ttk.Label(form, text="Contraseña:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.reg_password = ttk.Entry(form, show="*")
        self.reg_password.grid(row=1, column=1, sticky="ew", padx=6)

        ttk.Label(form, text="Confirmar:").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        self.reg_password_confirm = ttk.Entry(form, show="*")
        self.reg_password_confirm.grid(row=2, column=1, sticky="ew", padx=6)

        form.columnconfigure(1, weight=1)

        btns = ttk.Frame(self.container, padding=6)
        btns.pack(fill="x")

        ttk.Button(btns, text="✅ Crear cuenta", command=self.handle_register).pack(side="left", padx=6)
        ttk.Button(btns, text="↩️ Volver", command=self.pantalla_login).pack(side="left", padx=6)

    def handle_register(self):
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_password_confirm.get()

        if not username or not password:
            messagebox.showwarning("Datos incompletos", "Escribe usuario y contraseña.")
            return

        if len(password) < 4:
            messagebox.showwarning("Contraseña", "La contraseña debe tener al menos 4 caracteres.")
            return

        if password != confirm:
            messagebox.showwarning("Contraseña", "Las contraseñas no coinciden.")
            return

        pwd_hash = hash_password(password)
        created_at = datetime.datetime.utcnow().isoformat()

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)", (username, pwd_hash, created_at))
            conn.commit()
            messagebox.showinfo("Registro", "Usuario creado correctamente. Inicia sesión.")
            self.pantalla_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El nombre de usuario ya existe. Elige otro.")
        finally:
            conn.close()

    def handle_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()

        if not username or not password:
            messagebox.showwarning("Datos incompletos", "Escribe usuario y contraseña.")
            return

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Acceso denegado", "Usuario no encontrado. Regístrate.")
            return

        user_id, pwd_hash = row
        if hash_password(password) != pwd_hash:
            messagebox.showerror("Acceso denegado", "Contraseña incorrecta.")
            return

        # Login exitoso
        self.current_user = (user_id, username)
        self.pantalla_inicio_postlogin()

    def mostrar_ayuda(self):
        messagebox.showinfo("Ayuda", "Crea una cuenta o inicia sesión. Luego selecciona platillos y bebidas, elige método de pago y confirma tu pedido.\nLos tickets se guardan en la base de datos y en tickets.txt")

    # -------------------------
    # Pantalla: Menú (selección)
    # -------------------------
    def pantalla_menu(self):
        if not self.current_user:
            # Si no hay usuario, pedir login
            self.pantalla_login()
            return

        self.limpiar_container()

        header = ttk.Frame(self.container)
        header.pack(fill="x")
        ttk.Label(header, text=f"Usuario: {self.current_user[1]}", font=("Arial", 12, "italic")).pack(side="left")
        ttk.Button(header, text="🔒 Cerrar sesión", command=self.logout).pack(side="right")

        title = ttk.Label(self.container, text="🍽️ Selecciona platillos y bebidas", font=("Arial", 16, "bold"))
        title.pack(pady=8)

        content = ttk.Frame(self.container, padding=8)
        content.pack(fill="both", expand=True)

        # Columnas para platillos y bebidas
        col_left = ttk.Frame(content)
        col_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        col_right = ttk.Frame(content)
        col_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        # Encabezados
        ttk.Label(col_left, text="🍔 Platillos", font=("Arial", 14, "underline")).pack(anchor="w")
        ttk.Label(col_right, text="🥤 Bebidas", font=("Arial", 14, "underline")).pack(anchor="w")

        # Platillos con Spinbox (cantidad)
        self.platillos_vars.clear()
        for nombre, precio in PRECIOS_PLATILLOS.items():
            frame = ttk.Frame(col_left)
            frame.pack(anchor="w", pady=4, fill="x")

            lbl = ttk.Label(frame, text=f"{nombre} — ${precio:.2f}")
            lbl.pack(side="left")

            var = tk.IntVar(master=self.root, value=0)
            # Spinbox integrado y con validación simple
            spin = tk.Spinbox(frame, from_=0, to=99, width=5, textvariable=var, justify="center")
            spin.pack(side="right")
            self.platillos_vars[nombre] = var

        # Bebidas con Spinbox (cantidad)
        self.bebidas_vars.clear()
        for nombre, precio in PRECIOS_BEBIDAS.items():
            frame = ttk.Frame(col_right)
            frame.pack(anchor="w", pady=4, fill="x")

            lbl = ttk.Label(frame, text=f"{nombre} — ${precio:.2f}")
            lbl.pack(side="left")

            var = tk.IntVar(master=self.root, value=0)
            spin = tk.Spinbox(frame, from_=0, to=99, width=5, textvariable=var, justify="center")
            spin.pack(side="right")
            self.bebidas_vars[nombre] = var

        # Pago
        pay_frame = ttk.Frame(self.container, padding=8, relief="groove")
        pay_frame.pack(fill="x", pady=10)
        ttk.Label(pay_frame, text="💳 Método de pago (obligatorio):", font=("Arial", 12)).pack(anchor="w")
        self.metodo_pago_var.set("")  # reset
        for metodo in METODOS_PAGO:
            r = ttk.Radiobutton(pay_frame, text=metodo, variable=self.metodo_pago_var, value=metodo)
            r.pack(side="left", padx=6, pady=6)

        # Botones
        footer = ttk.Frame(self.container, padding=6)
        footer.pack(fill="x")
        ttk.Button(footer, text="➡️ Continuar", command=self.procesar_seleccion).pack(side="left", padx=6)
        ttk.Button(footer, text="🗒️ Ver tickets guardados", command=self.mostrar_tickets_guardados).pack(side="left", padx=6)
        ttk.Button(footer, text="🏠 Volver", command=self.pantalla_inicio_postlogin).pack(side="right", padx=6)

    def logout(self):
        self.current_user = None
        self.pantalla_login()

    def procesar_seleccion(self):
        # Obtener selección con cantidades > 0
        plat_sel = {p: v.get() for p, v in self.platillos_vars.items() if v.get() > 0}
        beb_sel = {b: v.get() for b, v in self.bebidas_vars.items() if v.get() > 0}
        metodo = self.metodo_pago_var.get()

        if not plat_sel and not beb_sel:
            messagebox.showwarning("Nada seleccionado", "Selecciona al menos un platillo o bebida (cantidad > 0).")
            return

        if metodo == "":
            messagebox.showwarning("Método de pago", "Debes elegir un método de pago.")
            return

        # Guardamos en atributos temporales para la pantalla de confirmación
        self.ultima_seleccion = {
            "platillos": plat_sel,  # dict nombre->cantidad
            "bebidas": beb_sel,     # dict nombre->cantidad
            "metodo": metodo,
        }

        self.pantalla_confirmacion()
