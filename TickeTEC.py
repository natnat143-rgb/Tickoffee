import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
import datetime
import os

USUARIOS_TXT = "usuarios.txt"
TICKETS_TXT = "tickets.txt"


# -------------------------
# Utilidades
# -------------------------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def cargar_usuarios():
    """Regresa un dict con usuarios: {username: password_hash}."""
    if not os.path.exists(USUARIOS_TXT):
        return {}

    usuarios = {}
    with open(USUARIOS_TXT, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            try:
                username, pwd_hash, created = linea.split("|")
                usuarios[username] = pwd_hash
            except:
                pass
    return usuarios


def guardar_usuario(username, pwd_hash):
    created = datetime.datetime.utcnow().isoformat()
    with open(USUARIOS_TXT, "a", encoding="utf-8") as f:
        f.write(f"{username}|{pwd_hash}|{created}\n")


def append_ticket_to_file(text: str):
    with open(TICKETS_TXT, "a", encoding="utf-8") as f:
        f.write(text + "\n\n")


# -----------------------------
# Datos del menú
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
        self.root.title("🍽️ Sistema de Pedidos - Solo archivos TXT")
        self.root.geometry("760x640")

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        # Usuario logueado
        self.current_user = None  # ("username")

        self.platillos_vars = {}
        self.bebidas_vars = {}
        self.metodo_pago_var = tk.StringVar()

        self.container = ttk.Frame(self.root, padding=12)
        self.container.pack(fill="both", expand=True)

        self.pantalla_login()

    # -------------------------
    # Pantalla login / registro
    # -------------------------
    def pantalla_login(self):
        self.limpiar_container()

        ttk.Label(self.container, text="Inicia sesión o regístrate",
                  font=("Arial", 16, "bold")).pack(pady=12)

        form = ttk.Frame(self.container)
        form.pack(pady=8)

        ttk.Label(form, text="Usuario:").grid(row=0, column=0, pady=4, sticky="w")
        self.login_username = ttk.Entry(form)
        self.login_username.grid(row=0, column=1, pady=4)

        ttk.Label(form, text="Contraseña:").grid(row=1, column=0, pady=4, sticky="w")
        self.login_password = ttk.Entry(form, show="*")
        self.login_password.grid(row=1, column=1, pady=4)

        ttk.Button(self.container, text="🔐 Iniciar sesión",
                   command=self.handle_login).pack(pady=5)
        ttk.Button(self.container, text="🧾 Registrarse",
                   command=self.pantalla_registro).pack(pady=5)

    def pantalla_registro(self):
        self.limpiar_container()

        ttk.Label(self.container, text="Registro Nuevo Usuario",
                  font=("Arial", 16, "bold")).pack(pady=12)

        form = ttk.Frame(self.container)
        form.pack(pady=8)

        ttk.Label(form, text="Usuario:").grid(row=0, column=0, pady=4)
        self.reg_username = ttk.Entry(form)
        self.reg_username.grid(row=0, column=1, pady=4)

        ttk.Label(form, text="Contraseña:").grid(row=1, column=0, pady=4)
        self.reg_password = ttk.Entry(form, show="*")
        self.reg_password.grid(row=1, column=1, pady=4)

        ttk.Label(form, text="Confirmar:").grid(row=2, column=0, pady=4)
        self.reg_password_confirm = ttk.Entry(form, show="*")
        self.reg_password_confirm.grid(row=2, column=1, pady=4)

        ttk.Button(self.container, text="Crear cuenta",
                   command=self.handle_register).pack(pady=6)
        ttk.Button(self.container, text="Volver",
                   command=self.pantalla_login).pack()

    def handle_register(self):
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_password_confirm.get()

        usuarios = cargar_usuarios()

        if not username or not password:
            messagebox.showwarning("Error", "Datos incompletos.")
            return
        if password != confirm:
            messagebox.showwarning("Error", "Las contraseñas no coinciden.")
            return
        if username in usuarios:
            messagebox.showwarning("Error", "Usuario ya existe.")
            return

        pwd_hash = hash_password(password)
        guardar_usuario(username, pwd_hash)

        messagebox.showinfo("OK", "Usuario registrado correctamente.")
        self.pantalla_login()

    def handle_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()

        usuarios = cargar_usuarios()

        if username not in usuarios:
            messagebox.showerror("Error", "Usuario no existe.")
            return

        if usuarios[username] != hash_password(password):
            messagebox.showerror("Error", "Contraseña incorrecta.")
            return

        self.current_user = username
        self.pantalla_inicio()

    # -------------------------
    # Pantalla inicio
    # -------------------------
    def pantalla_inicio(self):
        self.limpiar_container()

        ttk.Label(self.container, text=f"Bienvenido, {self.current_user}",
                  font=("Arial", 18, "bold")).pack(pady=12)

        ttk.Button(self.container, text="🛒 Hacer pedido",
                   command=self.pantalla_menu).pack(pady=10)

        ttk.Button(self.container, text="🧾 Ver tickets guardados",
                   command=self.mostrar_tickets_guardados).pack(pady=10)

        ttk.Button(self.container, text="Salir",
                   command=self.logout).pack(pady=10)

    def logout(self):
        self.current_user = None
        self.pantalla_login()

    # -------------------------
    # Pantalla menú
    # -------------------------
    def pantalla_menu(self):
        self.limpiar_container()

        ttk.Label(self.container, text="Selecciona tus productos",
                  font=("Arial", 16, "bold")).pack(pady=12)

        frame = ttk.Frame(self.container)
        frame.pack()

        # Platillos
        col1 = ttk.Frame(frame)
        col1.grid(row=0, column=0, padx=20)

        ttk.Label(col1, text="Platillos", font=("Arial", 14, "underline")).pack()

        self.platillos_vars = {}
        for nombre, precio in PRECIOS_PLATILLOS.items():
            f = ttk.Frame(col1)
            f.pack(pady=4)

            ttk.Label(f, text=f"{nombre} ${precio}").pack(side="left")
            var = tk.IntVar()
            tk.Spinbox(f, from_=0, to=99, width=5, textvariable=var).pack(side="right")
            self.platillos_vars[nombre] = var

        # Bebidas
        col2 = ttk.Frame(frame)
        col2.grid(row=0, column=1, padx=20)

        ttk.Label(col2, text="Bebidas", font=("Arial", 14, "underline")).pack()

        self.bebidas_vars = {}
        for nombre, precio in PRECIOS_BEBIDAS.items():
            f = ttk.Frame(col2)
            f.pack(pady=4)

            ttk.Label(f, text=f"{nombre} ${precio}").pack(side="left")
            var = tk.IntVar()
            tk.Spinbox(f, from_=0, to=99, width=5, textvariable=var).pack(side="right")
            self.bebidas_vars[nombre] = var

        # Métodos de pago
        ttk.Label(self.container, text="Método de pago:", font=("Arial", 12)).pack(pady=6)
        self.metodo_pago_var.set("")

        for metodo in METODOS_PAGO:
            ttk.Radiobutton(self.container, text=metodo,
                            variable=self.metodo_pago_var, value=metodo).pack()

        ttk.Button(self.container, text="Continuar",
                   command=self.procesar_seleccion).pack(pady=20)

    # -------------------------
    # Procesar selección
    # -------------------------
    def procesar_seleccion(self):
        metodo = self.metodo_pago_var.get()

        plat = {p: v.get() for p, v in self.platillos_vars.items() if v.get() > 0}
        beb = {b: v.get() for b, v in self.bebidas_vars.items() if v.get() > 0}

        if not plat and not beb:
            messagebox.showwarning("Error", "Selecciona algún producto.")
            return

        if metodo == "":
            messagebox.showwarning("Error", "Selecciona método de pago.")
            return

        self.ultima_seleccion = {"plat": plat, "beb": beb, "metodo": metodo}
        self.pantalla_confirmacion()

    # -------------------------
    # Confirmación
    # -------------------------
    def pantalla_confirmacion(self):
        self.limpiar_container()

        sel = self.ultima_seleccion

        texto = ""
        total = 0

        texto += "Platillos:\n"
        for p, c in sel["plat"].items():
            subtotal = PRECIOS_PLATILLOS[p] * c
            total += subtotal
            texto += f" - {p} x{c} = ${subtotal}\n"

        texto += "\nBebidas:\n"
        for b, c in sel["beb"].items():
            subtotal = PRECIOS_BEBIDAS[b] * c
            total += subtotal
            texto += f" - {b} x{c} = ${subtotal}\n"

        texto += f"\nMétodo de pago: {sel['metodo']}\n"
        texto += f"TOTAL: ${total}\n"

        tk.Label(self.container, text=texto, justify="left",
                 font=("Consolas", 11)).pack(pady=10)

        ttk.Button(self.container, text="Generar ticket",
                   command=self.generar_ticket).pack(pady=10)
        ttk.Button(self.container, text="Volver",
                   command=self.pantalla_menu).pack()

    # -------------------------
    # Generar ticket (solo .txt)
    # -------------------------
    def generar_ticket(self):
        sel = self.ultima_seleccion

        # Generar ID de ticket simple incremental:
        ticket_id = sum(1 for _ in open(TICKETS_TXT, "r", encoding="utf-8")) // 2 if os.path.exists(TICKETS_TXT) else 1

        created = datetime.datetime.utcnow().isoformat()

        texto = f"--- Ticket #{ticket_id} ---\n"
        texto += f"Usuario: {self.current_user}\n"
        texto += f"Fecha (UTC): {created}\n\n"

        total = 0

        texto += "Items:\n"
        for p, c in sel["plat"].items():
            sub = PRECIOS_PLATILLOS[p] * c
            total += sub
            texto += f" - {p} x{c} : ${sub}\n"

        for b, c in sel["beb"].items():
            sub = PRECIOS_BEBIDAS[b] * c
            total += sub
            texto += f" - {b} x{c} : ${sub}\n"

        texto += f"\nMétodo de pago: {sel['metodo']}\n"
        texto += f"TOTAL: ${total}\n"
        texto += "-----------------------------"

        append_ticket_to_file(texto)

        messagebox.showinfo("OK", "Ticket guardado")
        self.pantalla_inicio()

    # -------------------------
    # Ver tickets guardados
    # -------------------------
    def mostrar_tickets_guardados(self):
        if not os.path.exists(TICKETS_TXT):
            messagebox.showinfo("Tickets", "No hay tickets aún.")
            return

        win = tk.Toplevel(self.root)
        win.title("Tickets")
        win.geometry("600x500")

        txt = tk.Text(win, wrap="word")
        txt.pack(fill="both", expand=True)

        with open(TICKETS_TXT, "r", encoding="utf-8") as f:
            txt.insert("1.0", f.read())

        txt.config(state="disabled")

    # -------------------------
    # Utilidad
    # -------------------------
    def limpiar_container(self):
        for w in self.container.winfo_children():
            w.destroy()



# -------------------------
# Ejecutar app
# -------------------------
def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
