from tkinter import *
from tkinter import Tk, messagebox as mes, simpledialog
from tkinter import ttk
import webbrowser
#Libreria para la calculadora
import os
import sqlite3
#Libreria para reportar las actividades del empleado
from datetime import datetime
import sys

def recurso(nombre):
    try:
        base = sys._MEIPASS
    except:
        base = os.path.abspath(".")
    return os.path.join(base, nombre)



class registro:
    def __init__(self):
        self.ven = Tk()
        self.ven.title("FerreLab")
        self.ven.geometry("550x660")
        self.ven.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))
        self.ven.config(bg="#FFECE8")
        self.ven.resizable(0, 0)

        # Variables para ventanas secundarias
        self.ven_acerca_de = None
        self.ven_info_equipo = None
        self.ven_emp = None
        self.ven_man = None

        # Variables del empleado logueado (se llenan en registrar())
        self.id_empleado_actual  = None
        self.nom_empleado_actual = "Empleado"

        # --- TÍTULO ---
        self.lbl_letras = Label(self.ven,
                                text="Ferre",
                                font=("Tahoma", 30, "bold"),
                                fg="black",
                                bg="#FFECE8")
        self.lbl_letras.place(x=170, y=15)

        self.lbl_letras2 = Label(self.ven,
                                 text="Lab",
                                 font=("Tahoma", 30, "bold"),
                                 fg="orange",
                                 bg="#FFECE8")
        self.lbl_letras2.place(x=285, y=15)

        # --- FONDO ---
        self.lbl_fondo = Label(self.ven, bg="white", width=58, height=35)
        self.lbl_fondo.place(x=65, y=80)

        # --- USUARIO ---
        self.lbl_usuario1 = Label(self.ven,
                                  text="👤 Ingrese usuario:",
                                  font=("Tahoma", 14, "bold"),
                                  bg="white")
        self.lbl_usuario1.place(x=98, y=110)
        self.Entry1 = StringVar()
        self.txt_usuario2 = Entry(self.ven, width=54, textvariable=self.Entry1, bg="#FFECE8")
        self.txt_usuario2.place(x=110, y=148)

        # --- CONTRASEÑA ---
        self.lbl_contra = Label(self.ven,
                                text="🔐 Ingrese contraseña:",
                                font=("Tahoma", 14, "bold"),
                                bg="white")
        self.lbl_contra.place(x=98, y=200)
        self.Entry2 = StringVar()
        self.txt_contra2 = Entry(self.ven, width=50, show="*", textvariable=self.Entry2, bg="#FFECE8")
        self.txt_contra2.place(x=110, y=235)

        # --- ROL ---
        self.lbl_rol = Label(self.ven,
                             text="💼 Seleccione su rol:",
                             font=("Tahoma", 14, "bold"),
                             bg="white")
        self.lbl_rol.place(x=98, y=285)
        self.cmb_rol = ttk.Combobox(self.ven, width=43, font=("Arial", 10), state="readonly")
        self.cmb_rol['values'] = ("Manager", "Empleado")
        self.cmb_rol.place(x=110, y=320)

        # --- BOTONES ---
        self.btn_registrar = Button(self.ven,
                                    text="Iniciar sesión",
                                    bg="#F87A4C",
                                    font=("Arial", 12, "bold"),
                                    width=33,
                                    command=self.registrar,
                                    fg="white")
        self.btn_registrar.place(x=98, y=390)

        self.btn_limpiar = Button(self.ven,
                                  text="Limpiar",
                                  bg="#BD5732",
                                  font=("Arial", 12, "bold"),
                                  width=10,
                                  command=self.limpiar,
                                  fg="white")
        self.btn_limpiar.place(x=145, y=450)

        self.btn_salir = Button(self.ven,
                                text="Salir",
                                font=("Arial", 12, "bold"),
                                bg="black",
                                fg="white",
                                width=10,
                                command=self.ven.destroy)
        self.btn_salir.place(x=280, y=450)

        # --- OJO ---
        self.cerrado = PhotoImage(file=recurso("descarga (15) (1).png")).subsample(20, 20)
        self.btn_mostrar = Button(self.ven,
                                  image=self.cerrado,
                                  command=self.mostrar,
                                  bg="white",
                                  width=30,
                                  height=15)
        self.btn_mostrar.place(x=422, y=233)
        self.abierto = PhotoImage(file=recurso("ojo abierto.png")).subsample(20, 20)

        # --- SOPORTE ---
        self.lbl_soporte = Label(self.ven, text="❓", font=("Arial", 11, "bold"),
                                 fg="red", bg="#FFECE8", cursor="hand2")
        self.lbl_soporte.place(x=510, y=10)
        self.lbl_soporte.bind("<ButtonRelease-1>", self.abrir_enlace)

        self.lbl_informacion_empresa = Button(self.ven, text="ⓘ",
                                              font=("Tahoma", 11, "bold"), fg="black",
                                              bg="#FFECE8", cursor="hand2",
                                              command=self.info_empresa, relief="flat", bd=0)
        self.lbl_informacion_empresa.place(x=485, y=8)

        self.btn_equipo = Button(self.ven, text="👥",
                                 font=("Tahoma", 11, "bold"), fg="black",
                                 bg="#FFECE8", cursor="hand2",
                                 command=self.info_equipo, relief="flat", bd=0)
        self.btn_equipo.place(x=450, y=8)

        self.ven.mainloop()

    def abrir_menu_empleado(self):
        if self.ven_emp is not None and self.ven_emp.winfo_exists():
            self.ven_emp.focus()
            return
        from Menu_empleado import menu_empleado
        self.ven.withdraw()
        self.ven_emp = Toplevel(self.ven)
        self.ven_emp.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_menu(self.ven_emp, "empleado"))
        self.app_emp = menu_empleado(self.ven_emp, self)

    def abrir_menu_manager(self):
        if self.ven_man is not None and self.ven_man.winfo_exists():
            self.ven_man.focus()
            return
        from Menu_manager import menu_manager
        self.ven.withdraw()
        self.ven_man = Toplevel(self.ven)
        #controla qué pasa cuando el usuario presiona la X para cerrar la ventana del Manager.
        self.ven_man.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_menu(self.ven_man, "manager"))
        self.app_man = menu_manager(self.ven_man, self)

    def cerrar_menu(self, ventana, tipo):
        if mes.askyesno("Salir", "¿Estás segura de que deseas salir?"):
            ventana.destroy()
            if tipo == "empleado": self.ven_emp = None
            if tipo == "manager": self.ven_man = None
            self.ven.deiconify()

    def registrar(self):
        u = self.Entry1.get().strip()
        c = self.Entry2.get().strip()
        r = self.cmb_rol.get()

     
        if u == "" or c == "" or r == "":
            mes.showerror("Error", "Todos los campos son obligatorios")
            return

    
        if r == "Manager":
            pass_maestra = simpledialog.askstring(
                "Seguridad", "Ingrese la contraseña de Manager:", show="*")
            if pass_maestra != "Ferre2026":
                mes.showerror("Error", "Contraseña de Manager incorrecta o acceso cancelado.")
                return

      
        try:
            ruta_bd = recurso("FerreLAB.db")

            print("BD LOGIN:", ruta_bd)

            con = sqlite3.connect(ruta_bd, timeout=10)
            con.execute("PRAGMA foreign_keys = ON;")
            cur = con.cursor()



            cur.execute("""
                SELECT id_empleado, nombre, estado
                FROM empleados
                WHERE nombre = ? AND contrasena = ?
            """, (u, c))
            empleado = cur.fetchone()

            if empleado is None:
                con.close()
                mes.showerror("Error", "Usuario o contraseña incorrectos.")
                return

            id_empleado, nombre, estado = empleado

            if estado == "inactivo":
                con.close()
                mes.showerror("Acceso denegado",
                              "Tu cuenta está desactivada. Contacta al Manager.")
                return

       
            self.id_empleado_actual  = id_empleado
            self.nom_empleado_actual = nombre

            # ── Registrar actividad ──
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO actividades (id_empleado, fecha_hora, usuario, actividad)
                VALUES (?, ?, ?, ?)
            """, (id_empleado, fecha_hora, nombre, "Inicio de sesión"))
            con.commit()
            con.close()
        except sqlite3.OperationalError as e:
            mes.showerror("Error de base de datos", f"No se pudo acceder a la BD:{e}")
            return

        # ── Abrir menú según rol  (UNA SOLA VEZ) ──
        if r == "Empleado":
            self.abrir_menu_empleado()
        elif r == "Manager":
            self.abrir_menu_manager()

 
    def mostrar(self):
        if self.txt_contra2.winfo_exists():
            if self.txt_contra2.cget('show') == '*':
                self.txt_contra2.config(show="")
                self.btn_mostrar.config(image=self.abierto)
            else:
                self.txt_contra2.config(show="*")
                self.btn_mostrar.config(image=self.cerrado)

    def limpiar(self):
        self.Entry1.set("")
        self.Entry2.set("")
        self.cmb_rol.set("")

    def abrir_enlace(self, event):
        webbrowser.open("https://13492942.github.io/Base-de-datos-Python/")

 
    def info_equipo(self):
        if self.ven_info_equipo is not None and self.ven_info_equipo.winfo_exists():
            self.ven_info_equipo.focus()
            mes.showwarning("Aviso", "La ventana ya está abierta.")
            return

        self.ven_info_equipo = Toplevel(self.ven)
        self.ven_info_equipo.title("Información del Equipo - FerreLab")
        self.ven_info_equipo.geometry("950x750")
        self.ven_info_equipo.config(bg="#FFECE8")
        self.ven_info_equipo.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))
        self.ven_info_equipo.resizable(0, 0)

        Label(self.ven_info_equipo, text="", bg="#73372B", height=3).place(x=0, y=0, width=950)
        Label(self.ven_info_equipo, text="👥 EQUIPO DE PROGRAMACION",
              font=("Tahoma", 24, "bold"), bg="#73372B", fg="white").place(x=238, y=4)
        Label(self.ven_info_equipo, text="12 BTP - Bachillerato Técnico Profesional",
              font=("Tahoma", 11, "bold"), bg="#FFECE8", fg="black").place(x=320, y=52)

        LabelFrame(self.ven_info_equipo, text="Descripción del Proyecto",
                   font=("Tahoma", 10, "bold"), bg="#FFD9D4", fg="#BF360C",
                   width=900, height=70).place(x=25, y=85)
        td = Text(self.ven_info_equipo, font=("Tahoma", 9), bg="#FFD9D4", fg="black",
                  wrap="word", relief="flat", height=4)
        td.place(x=40, y=105, width=870, height=45)
        # agregar una fila (registro) dentro del Treeview
        td.insert("1.0", "Sistema integral de gestión para FerreLab - una ferretería dedicada a la venta de materiales de construcción. El proyecto incluye módulos de gestión de empleados, productos, proveedores, categorías, inventario y reportes de ventas con base de datos SQLite.")
        td.config(state="disabled")

        LabelFrame(self.ven_info_equipo, text="Miembros del Equipo",
                   font=("Tahoma", 11, "bold"), bg="#FFD9D4", fg="#BF360C",
                   width=900, height=530).place(x=25, y=165)

        #Para poner el encabezado en negrita y con fondo diferente
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Tahoma', 10, 'bold'))
        tree = ttk.Treeview(self.ven_info_equipo,
                            columns=("id", "nombre_completo", "grado", "rol"),
                            show="headings", height=4)
        tree.heading("id", text="ID")
        tree.heading("nombre_completo", text="Nombre Completo")
        tree.heading("grado", text="Grado")
        tree.heading("rol", text="Rol en el Proyecto")
        tree.column("id", width=40)
        tree.column("nombre_completo", width=200)
        tree.column("grado", width=150)
        tree.column("rol", width=400)
        tree.place(x=40, y=185, width=870, height=105)
        for fila in [
            ("12", "Gabriela Padilla", "12 BTP", "Desarrolladora de Interfaces"),
            ("15", "Helen Licona",     "12 BTP", "Desarrolladora de Base de Datos"),
            ("33", "Anibal Benites",   "12 BTP", "Desarrollador de Base de Datos"),
            ("46", "Isaac Schneider",  "12 BTP", "Desarrollador de Base de Datos"),
            ("51", "Juan Jose",        "12 BTP", "Desarrollador de Base de Datos"),
        ]:
            tree.insert("", "end", values=fila)

        Label(self.ven_info_equipo, text="Aportaciones Específicas:",
              font=("Tahoma", 11, "bold"), bg="#FFD9D4", fg="#BF360C").place(x=40, y=300)

        miembros = [
            ("Gabriela Padilla (ID: 12)", 325, 350,
             "🎨 Interfaces Gráficas: Diseñó y desarrolló todas las ventanas del sistema."),
            ("Helen Licona (ID: 15)", 395, 420,
             "💾 Base de Datos: Participó en el diseño de la estructura de tablas y consultas SQL."),
            ("Anibal Benites (ID: 33)", 460, 485,
             "💾 Base de Datos: Colaboró en el diseño e implementación de la base de datos SQLite."),
            ("Isaac Schneider (ID: 46)", 525, 550,
             "💾 Base de Datos: Participó en el desarrollo de consultas SQL y validaciones."),
            ("Juan Jose (ID: 51)", 590, 615,
             "💾 Base de Datos: Contribuyó en el diseño y prueba de la base de datos."),
        ]
        for nombre, y_lbl, y_txt, texto in miembros:
            Label(self.ven_info_equipo, text=f"👤 {nombre}",
                  font=("Tahoma", 10, "bold"), bg="#FFD9D4", fg="#BF360C").place(x=40, y=y_lbl)
            t = Text(self.ven_info_equipo, font=("Tahoma", 8), bg="#FFD9D4", fg="black",
                     wrap="word", relief="flat")
            t.place(x=50, y=y_txt, width=850, height=30)
            t.insert("1.0", texto)
            t.config(state="disabled")

        Button(self.ven_info_equipo, text="Cerrar", bg="black", width=20,
               font=("Tahoma", 10, "bold"), fg="white",
               command=self.ven_info_equipo.destroy).place(x=375, y=705)


    def info_empresa(self):
        if self.ven_acerca_de is not None and self.ven_acerca_de.winfo_exists():
            self.ven_acerca_de.focus()
            mes.showwarning("Aviso", "La ventana ya está abierta.")
            return

        self.ven_acerca_de = Toplevel(self.ven)
        self.ven_acerca_de.title("Acerca de FerreLab")
        self.ven_acerca_de.geometry("850x700")
        self.ven_acerca_de.config(bg="#FFECE8")
        self.ven_acerca_de.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))
        self.ven_acerca_de.resizable(0, 0)

        Label(self.ven_acerca_de, text="", bg="#73372B", height=3).place(x=0, y=0, width=850)
        Label(self.ven_acerca_de, text="🏢 FERRELAB",
              font=("Tahoma", 24, "bold"), bg="#73372B", fg="white").place(x=300, y=15)

        LabelFrame(self.ven_acerca_de, text="Nombre de la Empresa",
                   font=("Tahoma", 10, "bold"), bg="#FFD9D4", fg="#BF360C",
                   width=800, height=50).place(x=25, y=70)
        Label(self.ven_acerca_de, text="FerreLab - Ferretería y Laboratorio de Construcción S.A.",
              font=("Tahoma", 11), bg="#FFD9D4").place(x=40, y=85)

        LabelFrame(self.ven_acerca_de, text="Información General",
                   font=("Tahoma", 10, "bold"), bg="#FFD9D4", fg="#BF360C",
                   width=800, height=55).place(x=25, y=135)
        Label(self.ven_acerca_de, text="Año de Fundación: 2018",
              font=("Tahoma", 10), bg="#FFD9D4").place(x=40, y=150)
        Label(self.ven_acerca_de, text="Sector: Venta de Materiales de Construcción",
              font=("Tahoma", 10), bg="#FFD9D4").place(x=40, y=170)

        secciones = [
            ("📍 Misión", 205, 225,
             "Proporcionar materiales de construcción de alta calidad con excelente servicio al cliente, garantizando confiabilidad y eficiencia en cada transacción."),
            ("🎯 Visión", 290, 310,
             "Ser la ferretería líder en el mercado, reconocida por la calidad de sus productos, servicio al cliente excepcional y contribución al desarrollo de proyectos constructivos."),
            ("💎 Valores", 375, 395,
             "• Honestidad: Transparencia en todas nuestras operaciones.\n• Calidad: Productos y servicios de primera categoría.\n• Compromiso: Dedicación a satisfacer las necesidades de nuestros clientes.\n• Responsabilidad: Social y ambiental."),
            ("🛠️ Servicios que Ofrece", 475, 495,
             "• Venta de materiales de construcción en general.\n• Asesoramiento técnico personalizado.\n• Entregas a domicilio.\n• Garantía en productos seleccionados.\n• Promociones y descuentos por volumen."),
        ]
        for titulo, y_frame, y_txt, contenido in secciones:
            LabelFrame(self.ven_acerca_de, text=titulo,
                       font=("Tahoma", 10, "bold"), bg="#FFD9D4", fg="#BF360C",
                       width=800, height=80).place(x=25, y=y_frame)
            t = Text(self.ven_acerca_de, font=("Tahoma", 9), bg="#FFD9D4", fg="black",
                     wrap="word", relief="flat")
            t.place(x=40, y=y_txt, width=770, height=50)
            t.insert("1.0", contenido)
            t.config(state="disabled")

        Button(self.ven_acerca_de, text="Cerrar", bg="black", width=20,
               font=("Tahoma", 10, "bold"), fg="white",
               command=self.ven_acerca_de.destroy).place(x=325, y=650)


app = registro()