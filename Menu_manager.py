from tkinter import *
from tkinter import messagebox as mes
from tkinter import ttk, simpledialog
import webbrowser
import sqlite3
import subprocess
from datetime import datetime
import os
import sys

def recurso(nombre):
    try:
        base = sys._MEIPASS
    except:
        base = os.path.abspath(".")
    return os.path.join(base, nombre)



#  BASE DE DATOS
def get_db():
    ruta = recurso("FerreLAB.db")
    print("BD USADA:", ruta)

    con = sqlite3.connect(ruta)
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def inicializar_bd():
    con = get_db()
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_categoria TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS proveedores (
            id_proveedor INTEGER PRIMARY KEY,
            nombre_proveedor TEXT NOT NULL,
            telefono TEXT NOT NULL,
            contacto_vendedor TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS empleados (
            id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT,
            contrasena TEXT NOT NULL,
            estado TEXT DEFAULT 'activo'
        );
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_producto TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            id_categoria INTEGER REFERENCES categorias(id_categoria),
            id_proveedor INTEGER REFERENCES proveedores(id_proveedor)
        );
        CREATE TABLE IF NOT EXISTS ventas (
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            cliente TEXT,
            total REAL
        );
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER REFERENCES ventas(id_venta),
            id_producto INTEGER REFERENCES productos(id_producto),
            cantidad INTEGER,
            precio_momento REAL
        );
        CREATE TABLE IF NOT EXISTS actividades (
            id_actividad INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT,
            usuario TEXT,
            actividad TEXT
        );
    """)
    con.commit()
    con.close()


class menu_manager:
    def __init__(self, root=None, login=None):
        inicializar_bd()
        
        if root is None:
            self.ven_man = Tk()
        else:
            self.ven_man = root

        self.login = login
        self.ven_proveedores_man = None
        self.ven_productos_man = None
        self.ven_categorias_man = None
        self.ven_reportes_ventas = None
        self.ven_gestion_emp = None
        self.ven_consultas = None

        self.ven_man.title("FerreLab - Menú Manager")
        self.ven_man.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))
        self.ven_man.geometry("800x500")
        self.ven_man.config(bg="#FFECE8")
        self.ven_man.resizable(0, 0)

        self._construir_ui()

        if root is None:
            self.ven_man.mainloop()

    def regresar_al_login(self):
        if mes.askyesno("Salir", "¿Deseas cerrar el menú?"):
            self.ven_man.destroy()
            if self.login is not None:
                self.login.ven.deiconify()

    def _construir_ui(self):
        # Barra lateral
        Label(self.ven_man, bg="#1E1D1D", width=31, height=35).place(x=0, y=0)
        Label(self.ven_man, text="FerreLAB 🛠",
              font=("Tahoma", 12, "bold"), fg="white", bg="#1E1D1D").place(x=55, y=15)
        Label(self.ven_man, text="━━━━━━━━━",
              font=("Tahoma", 10, "bold"), fg="white", bg="#1E1D1D").place(x=40, y=40)

        btns = [
            ("Gestion de Empleados 👥",   self.empleados,       85),
            ("Gestion de Productos 📦",   self.productos,      145),
            ("Gestion de Proveedores 📊", self.proveedores,    205),
            ("Reportes de Ventas 📈",     self.reportes_ventas,265),
        ]
        for texto, cmd, y in btns:
            Button(self.ven_man, text=texto, font=("Tahoma", 10, "bold"),
                   bg="#CF3516", fg="white", width=20, height=2,
                   command=cmd).place(x=23, y=y)

        Button(self.ven_man, text="Salir", font=("Tahoma", 10, "bold"),
               bg="white", fg="black", width=20, bd=0, height=2,
               command=self.regresar_al_login).place(x=23, y=430)

        # Opciones
        self.marco4 = LabelFrame(self.ven_man, text="Opciones ⏣",
                                 font=("Tahoma", 10, "bold"), fg="black",
                                 bg="#E3B2A0", width=167, height=85)
        self.marco4.place(x=23, y=325)
        self.opcion3 = IntVar()
        self.cb1 = Checkbutton(self.ven_man, text="Modo Oscuro", variable=self.opcion3,
                               bg="#E3B2A0", font=("Tahoma", 10),
                               command=self.gestionar_oscuro)
        self.cb1.place(x=35, y=345)
        self.opcion4 = IntVar()
        self.cb2 = Checkbutton(self.ven_man, text="Calculadora", variable=self.opcion4,
                               bg="#E3B2A0", font=("Tahoma", 10),
                               command=self.ejecutar_calculadora)
        self.cb2.place(x=35, y=375)

        # Contenido principal
        self.titulo = Label(self.ven_man, text="BIENVENIDO A FERRELAB",
                            font=("Tahoma", 23, "bold"), fg="orange", bg="#FFECE8")
        self.titulo.place(x=253, y=20)
        self.subtitulo = Label(self.ven_man, text="Panel de Manager",
                               font=("Tahoma", 14, "bold"), fg="black", bg="#FFECE8")
        self.subtitulo.place(x=253, y=55)

        # Tarjetas
        self.marco1 = LabelFrame(self.ven_man, text="Empleados",
                                 font=("Tahoma", 10, "bold"), bg="white", width=90, height=100)
        self.marco1.place(x=253, y=100)

        self.lbl_cantidad_emp = Label(self.ven_man, text="—",
                                      font=("Tahoma", 20, "bold"), bg="white")
        self.lbl_cantidad_emp.place(x=274, y=135)
        
        
        con = get_db()
        cur = con.cursor()

        cur.execute("SELECT COUNT(*) FROM empleados")
        total_emp = cur.fetchone()[0]

        self.lbl_cantidad_emp.config(text=str(total_emp))

        con.close()





        self.marco2 = LabelFrame(self.ven_man, text="Ventas",
                                 font=("Tahoma", 10, "bold"), bg="white", width=130, height=100)
        self.marco2.place(x=400, y=100)
        self.lbl_cantidad_ventas = Label(self.ven_man, text="—",
                                         font=("Tahoma", 20, "bold"), bg="white")
        self.lbl_cantidad_ventas.place(x=416, y=135)

        hoy = datetime.now().strftime("%Y-%m-%d")
        con = get_db()
        cur = con.cursor()
        cur.execute("""
            SELECT COUNT(*)
            FROM Ventas
            WHERE fecha LIKE ?
        """, (f"{hoy}%",))
        ventas_hoy = cur.fetchone()[0]
        self.lbl_cantidad_ventas.config(text=str(ventas_hoy))
        con.close()

        self.marco3 = LabelFrame(self.ven_man, text="Consultas",
                                 font=("Tahoma", 10, "bold"), bg="white", width=90, height=100)
        self.marco3.place(x=590, y=100)

        Button(self.ven_man, text="🔎", font=("Tahoma", 20, "bold"), bg="white",
               command=self.consultas).place(x=605, y=130)
    

        # Actividades recientes
        self.lbl_info = Label(
            self.ven_man,
            text="Registros recientes de empleados:",
            font=("Tahoma", 12, "bold"),
            fg="orange",
            bg="#FFECE8"
        )
        self.lbl_info.place(x=253, y=210)



        self.lbl_info = Label(
            self.ven_man,
            text="Registros recientes de empleados:",
            font=("Tahoma", 12, "bold"),
            fg="orange",
            bg="#FFECE8"
        )
        self.lbl_info.place(x=253, y=210)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Tahoma", 10, "bold"))

        self.tree_usuario = ttk.Treeview(
            self.ven_man,
            columns=("fecha", "usuario", "detalle", "rol"),
            show="headings",
            height=10
        )

        # Encabezados
        self.tree_usuario.heading("fecha", text="Fecha/Hora")
        self.tree_usuario.heading("usuario", text="Usuario")
        self.tree_usuario.heading("detalle", text="Actividad")
        self.tree_usuario.heading("rol", text="Rol")

        # Columnas
        self.tree_usuario.column("fecha", width=80, anchor=CENTER)
        self.tree_usuario.column("usuario", width=80, anchor=CENTER)
        self.tree_usuario.column("detalle", width=80, anchor=CENTER)
        self.tree_usuario.column("rol", width=80, anchor=CENTER)

        # Posición
        self.tree_usuario.place(
            x=235,
            y=250,
            width=550,
            height=225
        )

        self._cargar_actividades_recientes()

    
    def _cargar_actividades_recientes(self):

        self.tree_usuario.delete(*self.tree_usuario.get_children())

        try:
            con = get_db()
            cur = con.cursor()

            cur.execute("""
                SELECT
                    a.fecha_hora,
                    a.usuario,
                    a.actividad,
                    e.rol
                FROM actividades a
                INNER JOIN empleados e
                    ON a.id_empleado = e.id_empleado
                ORDER BY a.fecha_hora DESC
                LIMIT 20
            """)

            registros = cur.fetchall()

            print("Cantidad de registros:", len(registros))

            for fila in registros:
                print("Insertando:", fila)

                self.tree_usuario.insert(
                    "",
                    "end",
                    values=(
                        str(fila[0]),
                        str(fila[1]),
                        str(fila[2]),
                        str(fila[3])
                    )
                )

            print("Filas cargadas:", len(self.tree_usuario.get_children()))

            con.close()

        except Exception as e:
            print("ERROR:", e)
            mes.showerror(
                "Error",
                f"No se pudieron cargar las actividades.\n{e}",
                parent=self.ven_man
            )

        

        # Ayuda
        self.lbl_ayuda1 = Label(self.ven_man, text="❔",
                                font=("Tahoma", 18, "bold"), fg="#F90101",
                                bg="#FFECE8", cursor="hand2")
        self.lbl_ayuda1.place(x=754, y=10)
        self.lbl_ayuda1.bind("<ButtonRelease-1>", self.abrir_enlace)

    def consultas(self):
        self.ven_cons = Toplevel(self.ven_emp)
        self.ven_cons.title("Consultas")
        self.ven_cons.geometry("700x450")
        self.ven_cons.resizable(False, False)
        self.ven_cons.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))

        Button(
            self.ven_cons,
            text="Productos con poco stock",
            width=30,
            command=self.consulta_stock
        ).pack(pady=10)

        Button(
            self.ven_cons,
            text="Ventas realizadas hoy",
            width=30,
            command=self.consulta_ventas_hoy
        ).pack(pady=10)

        Button(
            self.ven_cons,
            text="Top productos vendidos",
            width=30,
            command=self.consulta_top_productos
        ).pack(pady=10)

        self.txt_consulta = Text(
            self.ven_cons,
            width=80,
            height=15
        )

        self.txt_consulta.pack(pady=20)
        
    def consulta_stock(self):
        con = get_db()
        cur = con.cursor()

        cur.execute("""
        SELECT nombre_producto, stock
        FROM productos
        WHERE stock <= 5
        """)

        datos = cur.fetchall()

        self.txt_consulta.delete("1.0", END)

        for p in datos:
            self.txt_consulta.insert(
            END,
            f"{p[0]} - Stock: {p[1]}\n"
        )

        con.close()
    def consulta_ventas_hoy(self):

        hoy = datetime.now().strftime("%Y-%m-%d")

        con = get_db()
        cur = con.cursor()

        cur.execute("""
            SELECT id_venta,
                cliente,
                total
            FROM Ventas
            WHERE fecha LIKE ?
        """, (f"{hoy}%",))

        datos = cur.fetchall()

        self.txt_consulta.delete("1.0", END)

        for v in datos:
            self.txt_consulta.insert(
                END,
                f"Venta #{v[0]} | {v[1]} | L.{v[2]:.2f}\n"
            )

        con.close()
    def consulta_top_productos(self):

        con = get_db()
        cur = con.cursor()

        cur.execute("""
            SELECT p.nombre_producto,
                SUM(dv.cantidad) AS vendidos
            FROM detalle_ventas dv
            JOIN productos p
                ON p.id_producto = dv.id_producto
            GROUP BY p.id_producto
            ORDER BY vendidos DESC
            LIMIT 10
        """)

        datos = cur.fetchall()

        self.txt_consulta.delete("1.0", END)

        for p in datos:
            self.txt_consulta.insert(
                END,
                f"{p[0]} -> {p[1]} unidades\n"
            )

        con.close()

    def _actualizar_tarjetas(self):
        try:
            con = get_db()
            cur = con.cursor()

            # Empleados activos
            cur.execute("""
                SELECT COUNT(*)
                FROM empleados
                WHERE UPPER(estado) = 'ACTIVO'
            """)
            emp = cur.fetchone()[0]

            # Ventas de hoy
            hoy = datetime.now().strftime("%Y-%m-%d")

            cur.execute("""
                SELECT COUNT(*)
                FROM ventas
                WHERE fecha LIKE ?
            """, (f"{hoy}%",))

            ven = cur.fetchone()[0]

            con.close()

            self.lbl_cantidad_emp.config(text=str(emp))
            self.lbl_cantidad_ventas.config(text=str(ven))

        except Exception as e:
            print("Error tarjetas:", e)

    def regresar_al_login(self):
        if mes.askyesno("Salir", "¿Deseas cerrar el menú y volver al inicio?"):
            self.ven_man.destroy()
            if self.login is not None:
                self.login.ven.deiconify()

    def gestionar_oscuro(self):
        oscuro  = self.opcion3.get() == 1
        bg_main = "#2B2B2B" if oscuro else "#FFECE8"
        bg_opt  = "#3E3E3E" if oscuro else "#E3B2A0"
        fg_tit  = "white"   if oscuro else "orange"
        self.ven_man.config(bg=bg_main)
        self.titulo.config(bg=bg_main, fg=fg_tit)
        self.subtitulo.config(bg=bg_main, fg="white" if oscuro else "black")
        self.lbl_info.config(bg=bg_main, fg="white" if oscuro else "orange")
        self.lbl_ayuda1.config(bg=bg_main)
        self.marco4.config(bg=bg_opt)
        self.cb1.config(bg=bg_opt)
        self.cb2.config(bg=bg_opt)

    def ejecutar_calculadora(self):
        try:
            subprocess.Popen("calc")
        except Exception:
            try:
                subprocess.Popen(["gnome-calculator"])
            except Exception:
                pass
        self.opcion4.set(0)

    def abrir_enlace(self, event):
        webbrowser.open("https://13492942.github.io/Base-de-datos-Python/")

 
    def consultas(self):
        if self.ven_consultas and self.ven_consultas.winfo_exists():
            self.ven_consultas.focus(); return

        self.ven_consultas = Toplevel(self.ven_man)
        self.ven_consultas.title("Consultas - FerreLab")
        self.ven_consultas.geometry("900x600")
        self.ven_consultas.config(bg="#FFECE8")
        self.ven_consultas.resizable(0, 0)
        self.ven_consultas.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))

        Label(self.ven_consultas, text="🔍 Consultas de Productos",
              font=("Tahoma", 20, "bold"), bg="#FFECE8", fg="#E65100").place(x=250, y=15)

        nb = ttk.Notebook(self.ven_consultas)
        nb.place(x=20, y=60, width=860, height=480)

        # ── Tab 1: Stock Bajo ──
        tab1 = Frame(nb, bg="#FFECE8"); nb.add(tab1, text="Stock Bajo")
        Label(tab1, text="Límite de Stock:", bg="#FFECE8",
              font=("Tahoma", 10, "bold")).place(x=20, y=15)
        self.entry_limite_stock = StringVar()
        Entry(tab1, bg="#C5AFAB", width=10,
              textvariable=self.entry_limite_stock).place(x=140, y=15)
        Button(tab1, text="Buscar", bg="#CB6E1D", fg="white", width=12,
               font=("Tahoma", 10, "bold"),
               command=self._buscar_stock_bajo).place(x=230, y=12)

        self.tree_stock_bajo = ttk.Treeview(tab1,
            columns=("id","nombre","stock","categoria"), show="headings", height=15)
        for col, txt, w in [("id","ID",60),("nombre","Nombre",280),
                             ("stock","Stock",100),("categoria","Categoría",150)]:
            self.tree_stock_bajo.heading(col, text=txt)
            self.tree_stock_bajo.column(col, width=w)
        self.tree_stock_bajo.place(x=20, y=50, width=810, height=380)
        sb1 = ttk.Scrollbar(tab1, orient="vertical", command=self.tree_stock_bajo.yview)
        sb1.place(x=830, y=50, height=380)
        self.tree_stock_bajo.configure(yscrollcommand=sb1.set)

        # ── Tab 2: Rango Precios ──
        tab2 = Frame(nb, bg="#FFECE8"); nb.add(tab2, text="Rango de Precios")
        Label(tab2, text="Precio Mínimo:", bg="#FFECE8",
              font=("Tahoma", 10, "bold")).place(x=20, y=15)
        self.entry_precio_min = StringVar()
        Entry(tab2, bg="#C5AFAB", width=12,
              textvariable=self.entry_precio_min).place(x=130, y=15)
        Label(tab2, text="Precio Máximo:", bg="#FFECE8",
              font=("Tahoma", 10, "bold")).place(x=280, y=15)
        self.entry_precio_max = StringVar()
        Entry(tab2, bg="#C5AFAB", width=12,
              textvariable=self.entry_precio_max).place(x=400, y=15)
        Button(tab2, text="Buscar", bg="#CB6E1D", fg="white", width=12,
               font=("Tahoma", 10, "bold"),
               command=self._buscar_rango_precios).place(x=570, y=12)

        self.tree_rango_precios = ttk.Treeview(tab2,
            columns=("id","nombre","precio","stock"), show="headings", height=15)
        for col, txt, w in [("id","ID",60),("nombre","Nombre",350),
                             ("precio","Precio (Lps)",120),("stock","Stock",100)]:
            self.tree_rango_precios.heading(col, text=txt)
            self.tree_rango_precios.column(col, width=w)
        self.tree_rango_precios.place(x=20, y=50, width=810, height=380)
        sb2 = ttk.Scrollbar(tab2, orient="vertical", command=self.tree_rango_precios.yview)
        sb2.place(x=830, y=50, height=380)
        self.tree_rango_precios.configure(yscrollcommand=sb2.set)

        # ── Tab 3: Por Categoría ──
        tab3 = Frame(nb, bg="#FFECE8"); nb.add(tab3, text="Por Categoría")
        Label(tab3, text="Categoría:", bg="#FFECE8",
              font=("Tahoma", 10, "bold")).place(x=20, y=15)
        self.entry_categoria_consul = StringVar()
        self.combo_categoria_consul = ttk.Combobox(tab3,
            textvariable=self.entry_categoria_consul, width=25, state="readonly")
        self.combo_categoria_consul.place(x=110, y=15)
        Button(tab3, text="Buscar", bg="#CB6E1D", fg="white", width=12,
               font=("Tahoma", 10, "bold"),
               command=self._buscar_por_categoria).place(x=390, y=12)

        self.tree_por_categoria = ttk.Treeview(tab3,
            columns=("id","nombre","precio","stock"), show="headings", height=15)
        for col, txt, w in [("id","ID",60),("nombre","Nombre",350),
                             ("precio","Precio (Lps)",120),("stock","Stock",100)]:
            self.tree_por_categoria.heading(col, text=txt)
            self.tree_por_categoria.column(col, width=w)
        self.tree_por_categoria.place(x=20, y=50, width=810, height=380)
        sb3 = ttk.Scrollbar(tab3, orient="vertical", command=self.tree_por_categoria.yview)
        sb3.place(x=830, y=50, height=380)
        self.tree_por_categoria.configure(yscrollcommand=sb3.set)

        self._cargar_categorias_combo_consultas()

        Button(self.ven_consultas, text="Cerrar", bg="black", fg="white",
               width=20, font=("Tahoma", 10, "bold"),
               command=self.ven_consultas.destroy).place(x=350, y=555)

    def _buscar_stock_bajo(self):
        limite = self.entry_limite_stock.get().strip()
        if not limite.isdigit():
            mes.showwarning("Aviso", "Ingresa un número válido.", parent=self.ven_consultas)
            return
        for r in self.tree_stock_bajo.get_children():
            self.tree_stock_bajo.delete(r)
        try:
            con = get_db(); cur = con.cursor()
            cur.execute("""
                SELECT p.id_producto, p.nombre_producto, p.stock,
                       COALESCE(c.nombre_categoria,'Sin categoría')
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.stock <= ? ORDER BY p.stock
            """, (int(limite),))
            rows = cur.fetchall(); con.close()
            for fila in rows:
                self.tree_stock_bajo.insert("", END, values=fila)
            if not rows:
                mes.showinfo("Info", "No hay productos con ese límite de stock.",
                             parent=self.ven_consultas)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_consultas)

    def _buscar_rango_precios(self):
        mn = self.entry_precio_min.get().strip()
        mx = self.entry_precio_max.get().strip()
        try:
            mn_f, mx_f = float(mn), float(mx)
        except ValueError:
            mes.showwarning("Aviso", "Ingresa precios válidos (ej: 100 o 100.5).",
                            parent=self.ven_consultas)
            return
        for r in self.tree_rango_precios.get_children():
            self.tree_rango_precios.delete(r)
        try:
            con = get_db(); cur = con.cursor()
            cur.execute("""
                SELECT id_producto, nombre_producto,
                       printf('L. %.2f', precio), stock
                FROM productos WHERE precio BETWEEN ? AND ? ORDER BY precio
            """, (mn_f, mx_f))
            rows = cur.fetchall(); con.close()
            for fila in rows:
                self.tree_rango_precios.insert("", END, values=fila)
            if not rows:
                mes.showinfo("Info", "No hay productos en ese rango.",
                             parent=self.ven_consultas)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_consultas)

    def _cargar_categorias_combo_consultas(self):
        try:
            con = get_db(); cur = con.cursor()
            cur.execute("SELECT nombre_categoria FROM categorias ORDER BY nombre_categoria")
            cats = [r[0] for r in cur.fetchall()]; con.close()
            self.combo_categoria_consul['values'] = cats
        except Exception as e:
            print("Error combo categorias:", e)

    def _buscar_por_categoria(self):
        cat = self.entry_categoria_consul.get().strip()
        if not cat:
            mes.showwarning("Aviso", "Selecciona una categoría.", parent=self.ven_consultas)
            return
        for r in self.tree_por_categoria.get_children():
            self.tree_por_categoria.delete(r)
        try:
            con = get_db(); cur = con.cursor()
            cur.execute("""
                SELECT p.id_producto, p.nombre_producto,
                       printf('L. %.2f', p.precio), p.stock
                FROM productos p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE c.nombre_categoria = ? ORDER BY p.nombre_producto
            """, (cat,))
            rows = cur.fetchall(); con.close()
            for fila in rows:
                self.tree_por_categoria.insert("", END, values=fila)
            if not rows:
                mes.showinfo("Info", "No hay productos en esa categoría.",
                             parent=self.ven_consultas)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_consultas)

 
    def reportes_ventas(self):
        if self.ven_reportes_ventas and self.ven_reportes_ventas.winfo_exists():
            self.ven_reportes_ventas.focus(); return

        self.ven_reportes_ventas = Toplevel(self.ven_man)
        self.ven_reportes_ventas.title("Reportes de Ventas - FerreLab")
        self.ven_reportes_ventas.geometry("1000x650")
        self.ven_reportes_ventas.config(bg="#FFECE8")
        self.ven_reportes_ventas.resizable(0, 0)
        self.ven_reportes_ventas.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))

        Label(self.ven_reportes_ventas, text="📊 Reportes de Ventas",
              font=("Tahoma", 20, "bold"), bg="#FFECE8", fg="#E65100").place(x=340, y=15)

        LabelFrame(self.ven_reportes_ventas, text="Ventas Realizadas",
                   font=("Tahoma", 11, "bold"), bg="#FFD9D4", fg="#BF360C",
                   width=950, height=280).place(x=25, y=60)

        self.tree_ventas_rep = ttk.Treeview(self.ven_reportes_ventas,
            columns=("id_venta","fecha","cliente","total"), show="headings", height=10)
        for col, txt, w in [("id_venta","ID Venta",80),("fecha","Fecha",130),
                             ("cliente","Cliente",350),("total","Total (Lps)",150)]:
            self.tree_ventas_rep.heading(col, text=txt)
            self.tree_ventas_rep.column(col, width=w)
        self.tree_ventas_rep.place(x=40, y=85, width=920, height=240)
        self.tree_ventas_rep.bind("<<TreeviewSelect>>", self._cargar_detalles_venta)
        sb_v = ttk.Scrollbar(self.ven_reportes_ventas, orient="vertical",
                             command=self.tree_ventas_rep.yview)
        sb_v.place(x=960, y=85, height=240)
        self.tree_ventas_rep.configure(yscrollcommand=sb_v.set)

        LabelFrame(self.ven_reportes_ventas, text="Detalles de la Venta Seleccionada",
                   font=("Tahoma", 11, "bold"), bg="#FFD9D4", fg="#BF360C",
                   width=950, height=200).place(x=25, y=355)

        self.tree_detalles_rep = ttk.Treeview(self.ven_reportes_ventas,
            columns=("producto","cantidad","precio","subtotal"), show="headings", height=6)
        for col, txt, w in [("producto","Producto",300),("cantidad","Cantidad",100),
                             ("precio","Precio",150),("subtotal","Subtotal",150)]:
            self.tree_detalles_rep.heading(col, text=txt)
            self.tree_detalles_rep.column(col, width=w)
        self.tree_detalles_rep.place(x=40, y=380, width=920, height=150)

        Button(self.ven_reportes_ventas, text="Actualizar", bg="#CB6E1D", fg="white",
               width=15, font=("Tahoma", 10, "bold"),
               command=self._cargar_ventas_rep).place(x=40, y=590)
        Button(self.ven_reportes_ventas, text="Salir", bg="black", fg="white",
               width=15, font=("Tahoma", 10, "bold"),
               command=self.ven_reportes_ventas.destroy).place(x=840, y=590)

        self._cargar_ventas_rep()

   
    def _cargar_ventas_rep(self):
        for r in self.tree_ventas_rep.get_children():
            self.tree_ventas_rep.delete(r)
        try:
            con = get_db(); cur = con.cursor()
            cur.execute("SELECT id_venta, fecha, cliente, total FROM ventas ORDER BY id_venta DESC")
            rows = cur.fetchall(); con.close()
            for fila in rows:
                self.tree_ventas_rep.insert("", END,
                    values=(fila[0], fila[1], fila[2], f"L. {fila[3]:.2f}"))
            if not rows:
                mes.showinfo("Info", "No hay ventas registradas.",
                             parent=self.ven_reportes_ventas)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_reportes_ventas)

    def _cargar_detalles_venta(self, event=None):
        sel = self.tree_ventas_rep.selection()
        if not sel: return
        
        # Obtener valores de forma segura
        valores = self.tree_ventas_rep.item(sel[0], "values")
        if not valores:
            return
            
        id_v = valores[0]
        
        for r in self.tree_detalles_rep.get_children():
            self.tree_detalles_rep.delete(r)
        try:
            con = get_db(); cur = con.cursor()
            cur.execute("""
                SELECT p.nombre_producto, dv.cantidad, dv.precio_momento,
                       (dv.cantidad * dv.precio_momento)
                FROM detalle_ventas dv
                JOIN productos p ON dv.id_producto = p.id_producto
                WHERE dv.id_venta = ?
            """, (int(id_v),))
            for fila in cur.fetchall():
                self.tree_detalles_rep.insert("", END,
                    values=(fila[0], fila[1],
                            f"L. {fila[2]:.2f}", f"L. {fila[3]:.2f}"))
            con.close()
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_reportes_ventas)

    # ← CORRECCIÓN: Cambié nombre a _eliminar_venta_rep (con guión bajo al inicio)
    def _eliminar_venta_rep(self):
        """Elimina la venta seleccionada y restaura el stock."""
        sel = self.tree_ventas_rep.selection()
        if not sel:
            mes.showwarning("Aviso", "Selecciona una venta primero.",
                            parent=self.ven_reportes_ventas)
            return
        
        # Obtener los valores de la fila seleccionada
        valores = self.tree_ventas_rep.item(sel[0], "values")
        
        # Verificar que haya valores y que el primer valor (ID) no sea None
        if not valores or valores[0] is None:
            mes.showerror("Error", "No se pudo obtener el ID de la venta.",
                        parent=self.ven_reportes_ventas)
            return
        
        id_v = valores[0]
        
        # Convertir a entero (por si viene como string)
        try:
            id_v = int(id_v)
        except (ValueError, TypeError):
            mes.showerror("Error", f"ID de venta inválido: {id_v}",
                        parent=self.ven_reportes_ventas)
            return
        
        if not mes.askyesno("Confirmar", 
                f"¿Eliminar la venta #{id_v}?\nEsto también eliminará los detalles y restaurará el stock.",
                parent=self.ven_reportes_ventas):
            return
        
        con = None
        try:
            con = get_db()
            cur = con.cursor()
            
            # 1. Obtener detalles para restaurar stock
            cur.execute("""
                SELECT id_producto, cantidad 
                FROM detalle_ventas 
                WHERE id_venta = ?
            """, (id_v,))
            detalles = cur.fetchall()
            
            # 2. Restaurar stock de cada producto
            for id_prod, cantidad in detalles:
                cur.execute("""
                    UPDATE productos 
                    SET stock = stock + ? 
                    WHERE id_producto = ?
                """, (cantidad, id_prod))
            
            # 3. Eliminar detalles
            cur.execute("DELETE FROM detalle_ventas WHERE id_venta = ?", (id_v,))
            
            # 4. Eliminar venta
            cur.execute("DELETE FROM ventas WHERE id_venta = ?", (id_v,))
            
            con.commit()
            
            mes.showinfo("✔ Éxito", f"Venta #{id_v} eliminada y stock restaurado.",
                         parent=self.ven_reportes_ventas)
            
            self._cargar_ventas_rep()
            
        except Exception as e:
            try:
                if con:
                    con.rollback()
            except:
                pass
            mes.showerror("Error BD", f"No se pudo eliminar la venta:\n{e}",
                        parent=self.ven_reportes_ventas)
        finally:
            if con:
                con.close()
 
    def proveedores(self):
        if self.ven_proveedores_man and self.ven_proveedores_man.winfo_exists():
            self.ven_proveedores_man.focus()
            return

        v = Toplevel(self.ven_man)
        self.ven_proveedores_man = v
        v.title("Gestión de Proveedores")
        v.geometry("900x520")
        v.config(bg="#FFECE8")
        v.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))

        Label(v, bg="white", width=38, height=32).place(x=10, y=10)
        Label(v, bg="#C93B1F", width=38, height=2).place(x=10, y=10)
        Label(v, text="── Datos del Proveedor ──",
              bg="#C93B1F", fg="white", font=("Tahoma", 12, "bold")).place(x=30, y=17)

        campos = [
            ("ID (opcional):", "entry_id_prov", 70),
            ("Nombre *:", "entry_nom_prov", 140),
            ("Teléfono *:", "entry_tel_prov", 210),
            ("Contacto Vend. *:", "entry_cont_prov", 280),
        ]
        for label, attr, y in campos:
            Label(v, text=label, bg="white", font=("Tahoma", 10, "bold")).place(x=25, y=y)
            sv = StringVar()
            setattr(self, attr, sv)
            Entry(v, bg="#C5AFAB", width=33, textvariable=sv).place(x=25, y=y+25)

        self.tree_prov = ttk.Treeview(v, height=16)
        self.tree_prov.place(x=310, y=10, width=520, height=440)
        self.tree_prov["columns"] = ("id", "nombre", "telefono", "contacto_vendedor")
        self.tree_prov.heading("#0", text="")
        self.tree_prov.column("#0", width=0)
        
        for col, txt, w in [("id","ID",55),("nombre","Nombre",160),
                          ("telefono","Teléfono",120),("contacto_vendedor","Contacto",175)]:
            self.tree_prov.heading(col, text=txt)
            self.tree_prov.column(col, width=w)

        sb_p = ttk.Scrollbar(v, orient="vertical", command=self.tree_prov.yview)
        sb_p.place(x=830, y=10, height=440)
        self.tree_prov.configure(yscrollcommand=sb_p.set)
        self.tree_prov.bind("<<TreeviewSelect>>", self._seleccionar_proveedor)

        btn_cfg = [
            ("Agregar", "#27AE60", self._guardar_proveedor),
            ("Editar", "#CB6E1D", self._actualizar_proveedor),
            ("Eliminar", "#C0392B", self._eliminar_proveedor),
            ("Limpiar", "#7F8C8D", self._limpiar_prov),
        ]
        for i, (txt, color, cmd) in enumerate(btn_cfg):
            Button(v, text=txt, bg=color, fg="white", width=11,
                   font=("Tahoma", 10, "bold"), command=cmd).place(x=310 + i*132, y=460)

        Button(v, text="Salir", bg="black", fg="white", width=18,
               font=("Tahoma", 10, "bold"), command=v.destroy).place(x=60, y=440)

        self._cargar_proveedores()

    def _seleccionar_proveedor(self, event=None):
        sel = self.tree_prov.selection()
        if not sel: return
        vals = self.tree_prov.item(sel[0], "values")
        if vals:
            self.entry_id_prov.set(vals[0])
            self.entry_nom_prov.set(vals[1])
            self.entry_tel_prov.set(vals[2])
            self.entry_cont_prov.set(vals[3])

    def _cargar_proveedores(self):
        for r in self.tree_prov.get_children():
            self.tree_prov.delete(r)
        try:
            con = get_db()
            cur = con.cursor()
            cur.execute("SELECT id_proveedor, nombre_proveedor, telefono, contacto_vendedor FROM proveedores ORDER BY id_proveedor")
            for fila in cur.fetchall():
                self.tree_prov.insert("", END, values=fila)
            con.close()
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_proveedores_man)

    def _guardar_proveedor(self):
        id_p = self.entry_id_prov.get().strip()
        nom = self.entry_nom_prov.get().strip()
        tel = self.entry_tel_prov.get().strip()
        cont = self.entry_cont_prov.get().strip()
        
        if not nom or not tel or not cont:
            mes.showwarning("Aviso", "Todos los campos son obligatorios.", parent=self.ven_proveedores_man)
            return
        
        try:
            con = get_db()
            if id_p:
                con.execute("INSERT INTO proveedores (id_proveedor, nombre_proveedor, telefono, contacto_vendedor) VALUES (?,?,?,?)",
                    (int(id_p), nom, tel, cont))
            else:
                con.execute("INSERT INTO proveedores (nombre_proveedor, telefono, contacto_vendedor) VALUES (?,?,?)",
                    (nom, tel, cont))
            con.commit()
            con.close()
            self._cargar_proveedores()
            self._limpiar_prov()
            mes.showinfo("✔ Éxito", f"Proveedor '{nom}' guardado.", parent=self.ven_proveedores_man)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_proveedores_man)

    def _actualizar_proveedor(self):
        id_p = self.entry_id_prov.get().strip()
        if not id_p:
            mes.showwarning("Aviso", "Selecciona un proveedor.", parent=self.ven_proveedores_man)
            return
        
        nom = self.entry_nom_prov.get().strip()
        tel = self.entry_tel_prov.get().strip()
        cont = self.entry_cont_prov.get().strip()
        
        try:
            con = get_db()
            con.execute("UPDATE proveedores SET nombre_proveedor=?, telefono=?, contacto_vendedor=? WHERE id_proveedor=?",
                (nom, tel, cont, int(id_p)))
            con.commit()
            con.close()
            self._cargar_proveedores()
            mes.showinfo("✔ Éxito", "Proveedor actualizado.", parent=self.ven_proveedores_man)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_proveedores_man)

    def _eliminar_proveedor(self):
        id_p = self.entry_id_prov.get().strip()
        if not id_p:
            mes.showwarning("Aviso", "Selecciona un proveedor.", parent=self.ven_proveedores_man)
            return
        
        if not mes.askyesno("Confirmar", f"¿Eliminar proveedor #{id_p}?", parent=self.ven_proveedores_man):
            return
        
        try:
            con = get_db()
            con.execute("DELETE FROM proveedores WHERE id_proveedor=?", (int(id_p),))
            con.commit()
            con.close()
            self._cargar_proveedores()
            self._limpiar_prov()
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_proveedores_man)

    def _limpiar_prov(self):
        for attr in ("entry_id_prov","entry_nom_prov","entry_tel_prov","entry_cont_prov"):
            getattr(self, attr).set("")


   
    def categorias(self):
        if self.ven_categorias_man and self.ven_categorias_man.winfo_exists():
            self.ven_categorias_man.focus(); return

        v = Toplevel(self.ven_man)
        self.ven_categorias_man = v
        v.title("Gestión de Categorías")
        v.geometry("680x430")
        v.config(bg="#FFECE8")
        v.resizable(0, 0)
        v.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))

        Label(v, bg="white", width=32, height=26).place(x=10, y=10)
        Label(v, bg="#C7472D", width=32, height=2).place(x=10, y=10)
        Label(v, text="── Datos de la Categoría ──",
              bg="#C7472D", fg="white", font=("Tahoma", 11, "bold")).place(x=22, y=17)

        Label(v, text="ID (opcional al agregar):", bg="white",
              font=("Tahoma", 10, "bold")).place(x=25, y=65)
        self.entry_id_cat = StringVar()
        Entry(v, bg="#C5AFAB", width=29,
              textvariable=self.entry_id_cat).place(x=25, y=90)

        Label(v, text="Nombre categoría *:", bg="white",
              font=("Tahoma", 10, "bold")).place(x=25, y=125)
        self.entry_nom_cat = StringVar()
        Entry(v, bg="#C5AFAB", width=29,
              textvariable=self.entry_nom_cat).place(x=25, y=150)

        self.tree_cat = ttk.Treeview(v, columns=("id","nombre"), show="headings", height=14)
        self.tree_cat.heading("id",     text="ID")
        self.tree_cat.heading("nombre", text="Nombre Categoría")
        self.tree_cat.column("id",     width=70)
        self.tree_cat.column("nombre", width=290)
        self.tree_cat.place(x=260, y=10, width=400, height=360)
        sb_c = ttk.Scrollbar(v, orient="vertical", command=self.tree_cat.yview)
        sb_c.place(x=660, y=10, height=360)
        self.tree_cat.configure(yscrollcommand=sb_c.set)
        self.tree_cat.bind("<<TreeviewSelect>>", self._seleccionar_categoria)

        btns_cat = [
            ("Agregar",  "#27AE60", self._agregar_categoria),
            ("Editar",   "#CB6E1D", self._editar_categoria),
            ("Eliminar", "#C0392B", self._eliminar_categoria),
        ]
        for i, (txt, color, cmd) in enumerate(btns_cat):
            Button(v, text=txt, bg=color, fg="white", width=12,
                   font=("Tahoma", 10, "bold"),
                   command=cmd).place(x=260 + i*134, y=380)

        Button(v, text="Salir", bg="black", fg="white", width=18,
               font=("Tahoma", 9, "bold"),
               command=v.destroy).place(x=40, y=355)

        self._cargar_categorias()

    def _seleccionar_categoria(self, event=None):
        sel = self.tree_cat.selection()
        if not sel: return
        vals = self.tree_cat.item(sel[0], "values")
        self.entry_id_cat.set(vals[0])
        self.entry_nom_cat.set(vals[1])

    def _cargar_categorias(self):
        for r in self.tree_cat.get_children():
            self.tree_cat.delete(r)
        try:
            con = get_db(); cur = con.cursor()
            cur.execute("SELECT id_categoria, nombre_categoria FROM categorias ORDER BY nombre_categoria")
            for fila in cur.fetchall():
                self.tree_cat.insert("", END, values=fila)
            con.close()
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_categorias_man)

    def _agregar_categoria(self):
        id_c = self.entry_id_cat.get().strip()
        nom  = self.entry_nom_cat.get().strip()
        if not nom:
            mes.showwarning("Aviso", "El nombre de la categoría es obligatorio.",
                            parent=self.ven_categorias_man); return
        try:
            con = get_db()
            if id_c:
                con.execute("INSERT INTO categorias (id_categoria, nombre_categoria) VALUES (?,?)",
                            (int(id_c), nom))
            else:
                con.execute("INSERT INTO categorias (nombre_categoria) VALUES (?)", (nom,))
            con.commit(); con.close()
            self._cargar_categorias()
            self.entry_id_cat.set("")
            self.entry_nom_cat.set("")
            mes.showinfo("✔ Éxito", f"Categoría '{nom}' agregada.",
                         parent=self.ven_categorias_man)
        except sqlite3.IntegrityError as e:
            mes.showerror("Error", f"ID duplicado:\n{e}", parent=self.ven_categorias_man)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_categorias_man)

    def _editar_categoria(self):
        id_c = self.entry_id_cat.get().strip()
        nom  = self.entry_nom_cat.get().strip()
        if not id_c or not nom:
            mes.showwarning("Aviso", "Selecciona una categoría y escribe el nuevo nombre.",
                            parent=self.ven_categorias_man); return
        try:
            con = get_db()
            con.execute("UPDATE categorias SET nombre_categoria=? WHERE id_categoria=?",
                        (nom, int(id_c)))
            con.commit(); con.close()
            self._cargar_categorias()
            mes.showinfo("✔ Éxito", "Categoría actualizada.",
                         parent=self.ven_categorias_man)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_categorias_man)

    def _eliminar_categoria(self):
        id_c = self.entry_id_cat.get().strip()
        if not id_c:
            mes.showwarning("Aviso", "Selecciona una categoría primero.",
                            parent=self.ven_categorias_man); return
        nom = self.entry_nom_cat.get().strip() or f"#{id_c}"
        if not mes.askyesno("Confirmar", f"¿Eliminar la categoría '{nom}'?",
                            parent=self.ven_categorias_man): return
        try:
            con = get_db()
            con.execute("DELETE FROM categorias WHERE id_categoria=?", (int(id_c),))
            con.commit(); con.close()
            self._cargar_categorias()
            self.entry_id_cat.set("")
            self.entry_nom_cat.set("")
        except sqlite3.IntegrityError:
            mes.showerror("Error",
                "No se puede eliminar: hay productos asociados a esta categoría.",
                parent=self.ven_categorias_man)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_categorias_man)

   
    def productos(self):
        if self.ven_productos_man and self.ven_productos_man.winfo_exists():
            self.ven_productos_man.focus(); return

        v = Toplevel(self.ven_man)
        self.ven_productos_man = v
        v.title("Gestión de Productos")
        v.geometry("950x580")
        v.config(bg="#FFECE8")
        v.resizable(0, 0)
        v.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))

        menubar1 = Menu(v)
        v.config(menu=menubar1)
        op1 = Menu(menubar1)
        op1.add_command(label="Categorías", command=self.categorias)
        op1.add_separator()
        op1.add_command(label="Regresar", command=v.destroy)
        menubar1.add_cascade(label="Opciones", menu=op1)

        Label(v, bg="white", width=38, height=34).place(x=10, y=10)
        Label(v, bg="#CA3112", width=38, height=2).place(x=10, y=10)
        Label(v, text="── Datos del Producto ──",
              bg="#CA3112", fg="white", font=("Tahoma", 12, "bold")).place(x=40, y=17)

        Label(v, text="Nombre *:", bg="white",
              font=("Tahoma", 10, "bold")).place(x=25, y=58)
        self.entry_nom = StringVar()
        Entry(v, bg="#C5AFAB", width=36,
              textvariable=self.entry_nom).place(x=25, y=80)

        Label(v, text="Precio (Lps) *:", bg="white",
              font=("Tahoma", 10, "bold")).place(x=25, y=112)
        self.en_precio = StringVar()
        Entry(v, bg="#C5AFAB", width=36,
              textvariable=self.en_precio).place(x=25, y=134)

        Label(v, text="Stock *:", bg="white",
              font=("Tahoma", 10, "bold")).place(x=25, y=166)
        self.en_stock = StringVar()
        Entry(v, bg="#C5AFAB", width=36,
              textvariable=self.en_stock).place(x=25, y=188)

        # Combo Categoría
        Label(v, text="Categoría *:", bg="white",
              font=("Tahoma", 10, "bold")).place(x=25, y=220)
        self.en_categoria = StringVar()
        self.combo_cat_prod = ttk.Combobox(v, textvariable=self.en_categoria,
                                           width=33, state="readonly")
        self.combo_cat_prod.place(x=25, y=242)

        # Combo Proveedor
        Label(v, text="Proveedor *:", bg="white",
              font=("Tahoma", 10, "bold")).place(x=25, y=274)
        self.en_proveedor = StringVar()
        self.combo_prov_prod = ttk.Combobox(v, textvariable=self.en_proveedor,
                                            width=33, state="readonly")
        self.combo_prov_prod.place(x=25, y=296)

        self._recargar_combos_producto()

        # Treeview
        self.tree = ttk.Treeview(v,
            columns=("id","nom","pre","sto","cat","prov"), show="headings", height=17)
        for col, txt, w in [("id","ID",50),("nom","Nombre",160),("pre","Precio (Lps)",100),
                             ("sto","Stock",70),("cat","Categoría",120),("prov","Proveedor",130)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w)
        self.tree.place(x=320, y=10, width=615, height=490)
        sb_pr = ttk.Scrollbar(v, orient="vertical", command=self.tree.yview)
        sb_pr.place(x=935, y=10, height=490)
        self.tree.configure(yscrollcommand=sb_pr.set)
        self.tree.bind("<<TreeviewSelect>>", self._seleccionar_producto)

        btn_prod = [
            ("Guardar",  "#27AE60", self._guardar_producto),
            ("Editar",   "#CB6E1D", self._actualizar_producto),
            ("Eliminar", "#C0392B", self._eliminar_producto),
            ("Limpiar",  "#7F8C8D", self._limpiar_producto),
        ]
        for i, (txt, color, cmd) in enumerate(btn_prod):
            Button(v, text=txt, bg=color, fg="white", width=12,
                   font=("Tahoma", 10, "bold"),
                   command=cmd).place(x=320 + i*150, y=508)

        Button(v, text="Salir", bg="black", fg="white", width=20,
               font=("Tahoma", 10, "bold"),
               command=v.destroy).place(x=50, y=480)

        self._cargar_productos()
        self._id_producto_sel = None

    def _recargar_combos_producto(self):
        """Carga las listas de categorías y proveedores en los combos."""
        try:
            con = get_db(); cur = con.cursor()
            cur.execute("SELECT id_categoria, nombre_categoria FROM categorias ORDER BY nombre_categoria")
            cats = cur.fetchall()
            cur.execute("SELECT id_proveedor, nombre_proveedor FROM proveedores ORDER BY nombre_proveedor")
            provs = cur.fetchall()
            con.close()

            self._cat_map  = {f"{r[0]} - {r[1]}": r[0] for r in cats}
            self._prov_map = {f"{r[0]} - {r[1]}": r[0] for r in provs}

            self.combo_cat_prod['values']  = list(self._cat_map.keys())
            self.combo_prov_prod['values'] = list(self._prov_map.keys())
        except Exception as e:
            print("Error combos producto:", e)

    def _seleccionar_producto(self, event=None):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], "values")
        # vals: id, nombre, precio, stock, nombre_cat, nombre_prov
        self._id_producto_sel = vals[0]
        self.entry_nom.set(vals[1])
        self.en_precio.set(vals[2])
        self.en_stock.set(vals[3])
        # Buscar la clave del combo que coincida con la categoría/proveedor
        for key in self._cat_map:
            if key.split(" - ", 1)[1] == vals[4]:
                self.en_categoria.set(key); break
        for key in self._prov_map:
            if key.split(" - ", 1)[1] == vals[5]:
                self.en_proveedor.set(key); break

    def _cargar_productos(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        try:
            con = get_db(); cur = con.cursor()
            cur.execute("""
                SELECT p.id_producto, p.nombre_producto,
                       printf('%.2f', p.precio), p.stock,
                       COALESCE(c.nombre_categoria,'—'),
                       COALESCE(pr.nombre_proveedor,'—')
                FROM productos p
                LEFT JOIN categorias c  ON p.id_categoria  = c.id_categoria
                LEFT JOIN proveedores pr ON p.id_proveedor  = pr.id_proveedor
                ORDER BY p.nombre_producto
            """)
            for fila in cur.fetchall():
                self.tree.insert("", END, values=fila)
            con.close()
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_productos_man)

    def _guardar_producto(self):
        nom  = self.entry_nom.get().strip()
        pre  = self.en_precio.get().strip()
        sto  = self.en_stock.get().strip()
        cat_key  = self.en_categoria.get().strip()
        prov_key = self.en_proveedor.get().strip()

        if not all([nom, pre, sto, cat_key, prov_key]):
            mes.showwarning("Aviso", "Todos los campos son obligatorios.",
                            parent=self.ven_productos_man); return
        try:
            id_cat  = self._cat_map[cat_key]
            id_prov = self._prov_map[prov_key]
            con = get_db()
            con.execute("""INSERT INTO productos
                (nombre_producto, precio, stock, id_categoria, id_proveedor)
                VALUES (?,?,?,?,?)""",
                (nom, float(pre), int(sto), id_cat, id_prov))
            con.commit(); con.close()
            self._cargar_productos()
            self._limpiar_producto()
            mes.showinfo("✔ Éxito", f"Producto '{nom}' guardado.",
                         parent=self.ven_productos_man)
        except (ValueError, KeyError):
            mes.showwarning("Aviso", "Precio y stock deben ser números.",
                            parent=self.ven_productos_man)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_productos_man)

    def _actualizar_producto(self):
        if not self._id_producto_sel:
            mes.showwarning("Aviso", "Selecciona un producto primero.",
                            parent=self.ven_productos_man); return
        nom  = self.entry_nom.get().strip()
        pre  = self.en_precio.get().strip()
        sto  = self.en_stock.get().strip()
        cat_key  = self.en_categoria.get().strip()
        prov_key = self.en_proveedor.get().strip()
        try:
            id_cat  = self._cat_map[cat_key]
            id_prov = self._prov_map[prov_key]
            con = get_db()
            con.execute("""UPDATE productos SET nombre_producto=?, precio=?, stock=?,
                id_categoria=?, id_proveedor=? WHERE id_producto=?""",
                (nom, float(pre), int(sto), id_cat, id_prov,
                 int(self._id_producto_sel)))
            con.commit(); con.close()
            self._cargar_productos()
            mes.showinfo("✔ Éxito", "Producto actualizado.",
                         parent=self.ven_productos_man)
        except (ValueError, KeyError):
            mes.showwarning("Aviso", "Verifica que precio y stock sean números y que hayas seleccionado categoría y proveedor.",
                            parent=self.ven_productos_man)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_productos_man)

    def _eliminar_producto(self):
        if not self._id_producto_sel:
            mes.showwarning("Aviso", "Selecciona un producto primero.",
                            parent=self.ven_productos_man); return
        nom = self.entry_nom.get().strip() or f"#{self._id_producto_sel}"
        if not mes.askyesno("Confirmar", f"¿Eliminar el producto '{nom}'?",
                            parent=self.ven_productos_man): return
        try:
            con = get_db()
            con.execute("DELETE FROM productos WHERE id_producto=?",
                        (int(self._id_producto_sel),))
            con.commit(); con.close()
            self._cargar_productos()
            self._limpiar_producto()
        except sqlite3.IntegrityError:
            mes.showerror("Error",
                "No se puede eliminar: el producto está asociado a ventas.",
                parent=self.ven_productos_man)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_productos_man)

    def _limpiar_producto(self):
        self._id_producto_sel = None
        for sv in [self.entry_nom, self.en_precio, self.en_stock,
                   self.en_categoria, self.en_proveedor]:
            sv.set("")

   
    def empleados(self):
        if self.ven_gestion_emp and self.ven_gestion_emp.winfo_exists():
            self.ven_gestion_emp.focus(); return

        v = Toplevel(self.ven_man)
        self.ven_gestion_emp = v
        v.title("Gestión de Empleados")
        v.geometry("800x500")
        v.config(bg="#FFECE8")
        v.resizable(0, 0)
        v.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))

        Label(v, text="GESTIÓN DE EMPLEADOS 👥",
              font=("Tahoma", 16, "bold"), bg="#FFECE8", fg="#E65100").place(x=220, y=20)

        self.tree_gestion_emp = ttk.Treeview(v,
            columns=("id","nombre","contacto","estado"), show="headings", height=12)
        for col, txt, w in [("id","ID",130),("nombre","Nombre",180),
                             ("contacto","Contacto",180),("estado","Estado",130)]:
            self.tree_gestion_emp.heading(col, text=txt)
            self.tree_gestion_emp.column(col, width=w, anchor=CENTER)
        self.tree_gestion_emp.place(x=30, y=60)
        sb_e = ttk.Scrollbar(v, orient="vertical", command=self.tree_gestion_emp.yview)
        sb_e.place(x=763, y=60, height=280)
        self.tree_gestion_emp.configure(yscrollcommand=sb_e.set)
        self.tree_gestion_emp.bind("<<TreeviewSelect>>", self._seleccionar_empleado)

        # Marco contraseña
        LabelFrame(v, text="Gestión de Contraseña",
                   font=("Tahoma", 10, "bold"), bg="#E98C79", fg="white",
                   width=380, height=105).place(x=30, y=365)

        Label(v, text="Nueva Contraseña:", font=("Arial", 11, "bold"),
              bg="#E98C79", fg="white").place(x=42, y=385)

        self.txt_contra_nueva = StringVar()
        self.txt_nueva_contraseña = Entry(v, textvariable=self.txt_contra_nueva,
                                          show="*", width=17)
        self.txt_nueva_contraseña.place(x=210, y=387)

        Button(v, text="ACTUALIZAR CONTRASEÑA",
               font=("Arial", 9, "bold"), bg="#E65100", fg="white",
               width=23, height=2,
               command=self._actualizar_contrasena).place(x=42, y=415)

        try:
            self.cerrado1 = PhotoImage(file=recurso("descarga (15) (1).png")).subsample(20, 20)
            self.abierto1 = PhotoImage(file=recurso("ojo abierto.png")).subsample(20, 20)
            self.btn_mostrar_emp = Button(v, image=self.cerrado1,
                                          bg="white", width=80, height=35,
                                          command=self.mostrar1)
            self.btn_mostrar_emp.place(x=230, y=415)
        except Exception:
            pass

        Button(v, text="Agregar Empleado", bg="#CA3112", fg="white",
               font=("Arial", 11, "bold"), width=16,
               command=self._agregar_empleado).place(x=430, y=370)
        Button(v, text="Desactivar", bg="#7F8C8D", fg="white",
               font=("Arial", 11, "bold"), width=16,
               command=self._desactivar_empleado).place(x=615, y=370)
        Button(v, text="Reactivar", bg="#27AE60", fg="white",
               font=("Arial", 11, "bold"), width=16,
               command=self._reactivar_empleado).place(x=430, y=415)
        Button(v, text="Salir", bg="black", fg="white",
               font=("Arial", 11, "bold"), width=16,
               command=v.destroy).place(x=615, y=415)

        self.cargar_empleados()
        self._id_empleado_sel = None

    def _seleccionar_empleado(self, event=None):
        sel = self.tree_gestion_emp.selection()
        if not sel: return
        vals = self.tree_gestion_emp.item(sel[0], "values")
        self._id_empleado_sel = vals[0]

    def cargar_empleados(self):
        for r in self.tree_gestion_emp.get_children():
            self.tree_gestion_emp.delete(r)
        try:
            con = get_db(); cur = con.cursor()
            cur.execute("SELECT id_empleado, nombre, contacto, estado FROM empleados ORDER BY nombre")
            for fila in cur.fetchall():
                tag = "inactivo" if fila[3] == "inactivo" else ""
                self.tree_gestion_emp.insert("", END, values=fila, tags=(tag,))
            self.tree_gestion_emp.tag_configure("inactivo", foreground="gray")
            con.close()
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_gestion_emp)

    def _agregar_empleado(self):
        nom  = simpledialog.askstring("Nuevo Empleado", "Nombre:", parent=self.ven_gestion_emp)
        if not nom: return
        cont = simpledialog.askstring("Nuevo Empleado", "Contacto (opcional):", parent=self.ven_gestion_emp) or ""
        pwd  = simpledialog.askstring("Nuevo Empleado", "Contraseña:", show="*", parent=self.ven_gestion_emp)
        if not pwd:
            mes.showwarning("Aviso", "La contraseña es obligatoria.", parent=self.ven_gestion_emp); return
        try:
            con = get_db()
            con.execute("INSERT INTO empleados (nombre, contacto, contrasena, estado) VALUES (?,?,?,'activo')",
                        (nom.strip(), cont.strip(), pwd))
            con.commit(); con.close()
            self.cargar_empleados()
            self._actualizar_tarjetas()
            mes.showinfo("✔ Éxito", f"Empleado '{nom}' agregado.", parent=self.ven_gestion_emp)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_gestion_emp)

    def _desactivar_empleado(self):
        id_e = getattr(self, "_id_empleado_sel", None)
        if not id_e:
            mes.showwarning("Aviso", "Selecciona un empleado primero.",
                            parent=self.ven_gestion_emp); return
        if not mes.askyesno("Confirmar", f"¿Desactivar empleado #{id_e}?",
                            parent=self.ven_gestion_emp): return
        try:
            con = get_db()
            con.execute("UPDATE empleados SET estado='inactivo' WHERE id_empleado=?", (int(id_e),))
            con.commit(); con.close()
            self.cargar_empleados()
            self._actualizar_tarjetas()
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_gestion_emp)

    def _reactivar_empleado(self):
        id_e = getattr(self, "_id_empleado_sel", None)
        if not id_e:
            mes.showwarning("Aviso", "Selecciona un empleado primero.",
                            parent=self.ven_gestion_emp); return
        try:
            con = get_db()
            con.execute("UPDATE empleados SET estado='activo' WHERE id_empleado=?", (int(id_e),))
            con.commit(); con.close()
            self.cargar_empleados()
            self._actualizar_tarjetas()
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_gestion_emp)

    def _actualizar_contrasena(self):
        id_e  = getattr(self, "_id_empleado_sel", None)
        nueva = self.txt_contra_nueva.get().strip()
        if not id_e:
            mes.showwarning("Aviso", "Selecciona un empleado primero.",
                            parent=self.ven_gestion_emp); return
        if not nueva:
            mes.showwarning("Aviso", "Ingresa la nueva contraseña.",
                            parent=self.ven_gestion_emp); return
        try:
            con = get_db()
            con.execute("UPDATE empleados SET contrasena=? WHERE id_empleado=?",
                        (nueva, int(id_e)))
            con.commit(); con.close()
            mes.showinfo("✔ Éxito", "Contraseña actualizada.", parent=self.ven_gestion_emp)
            self.txt_contra_nueva.set("")
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_gestion_emp)

    def mostrar1(self):
        if self.txt_nueva_contraseña.cget('show') == '*':
            self.txt_nueva_contraseña.config(show="")
            self.btn_mostrar_emp.config(image=self.abierto1)
        else:
            self.txt_nueva_contraseña.config(show="*")
            self.btn_mostrar_emp.config(image=self.cerrado1)



if __name__ == "__main__":
    app = menu_manager()