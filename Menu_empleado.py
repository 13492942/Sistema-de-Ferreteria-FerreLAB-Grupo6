from tkinter import *
from tkinter import messagebox as mes
from tkinter import ttk
import webbrowser
import subprocess
import sqlite3
import os
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib import colors
from Menu_manager import recurso



def get_db():
    ruta_bd = recurso("FerreLAB.db")

    print("BD USADA:", ruta_bd)

    con = sqlite3.connect(ruta_bd)
    con.execute("PRAGMA foreign_keys = ON;")
    con.execute("PRAGMA journal_mode = WAL;")
    con.execute("PRAGMA busy_timeout = 3000;")

    return con
class menu_empleado:
    def __init__(self, root, login=None):
        self.ven_regis    = None
        self.ven_inven    = None
        self.ven_facturas = None
        self.login        = login

        #sirve para copiar el valor de id_empleado_actual desde login a self.id_empleado_actual de forma segura.
        #Igual con nom_empleado_actual
        self.id_empleado_actual  = getattr(login, "id_empleado_actual",  None)
        self.nom_empleado_actual = getattr(login, "nom_empleado_actual", "Empleado")

        self._carrito      = []
        self._productos_bd = []

        self.ven_emp = root
        self.ven_emp.title("FerreLab - Menú Empleado")
        self.ven_emp.geometry("800x500")
        self.ven_emp.config(bg="#FFECE8")
        self.ven_emp.resizable(0, 0)
        self.ven_emp.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))

        # ── BARRA LATERAL ──
        Label(self.ven_emp, bg="#CA482F", width=30, height=35).place(x=0, y=0)
        Label(self.ven_emp, text="FerreLAB 🛠",
              font=("Tahoma", 16, "bold"), fg="white", bg="#CA482F").place(x=40, y=25)
        Label(self.ven_emp, text="━━━━━━━━━━━━━━",
              fg="white", bg="#CA482F").place(x=15, y=54)

        Button(self.ven_emp, text="Registrar Venta 🛒",
               font=("Tahoma", 10, "bold"), bg="white", fg="#D88E73",
               width=20, height=2, command=self.regis_venta).place(x=22, y=90)

        Button(self.ven_emp, text="Inventario 📦",
               font=("Tahoma", 10, "bold"), bg="white", fg="#D88E73",
               width=20, bd=0, height=2, command=self.inven).place(x=22, y=145)

        Button(self.ven_emp, text="Salir",
               font=("Tahoma", 10, "bold"), bg="black", fg="white",
               width=20, bd=0, height=2, command=self.salir).place(x=22, y=430)

        # ── CONTENIDO PRINCIPAL ──
        self.lbl_menu_emp = Label(self.ven_emp, text="BIENVENIDO A FERRELAB",
                                  font=("Tahoma", 24, "bold"), fg="black", bg="#FFECE8")
        self.lbl_menu_emp.place(x=255, y=180)

        self.lbl_subt_emp = Label(self.ven_emp, text="Panel de Empleado",
                                  font=("Tahoma", 14, "bold"), fg="orange", bg="#FFECE8")
        self.lbl_subt_emp.place(x=255, y=230)

        self.lbl_info = Label(self.ven_emp,
                              text="Sistema de gestión interna para empleados. Seleccione una opción.",
                              font=("Tahoma", 10), fg="gray", bg="#FFECE8")
        self.lbl_info.place(x=255, y=270)

        lbl_ayuda = Label(self.ven_emp, text="¿Necesitas ayuda?",
                          font=("Tahoma", 9, "bold"), fg="gray", bg="#FFECE8", cursor="hand2")
        lbl_ayuda.place(x=650, y=470)
        lbl_ayuda.bind("<ButtonRelease-1>", self.abrir_enlace)

        LabelFrame(self.ven_emp, bg="#E3B2A0", width=167, height=85,
                   text="Opciones ⏣", font=("Tahoma", 10, "bold")).place(x=22, y=200)

        self.opcion1 = IntVar()
        Checkbutton(self.ven_emp, text="Modo Oscuro", variable=self.opcion1,
                    bg="#E3B2A0", font=("Tahoma", 10),
                    command=self.gestionar_oscuro).place(x=35, y=220)

        self.opcion2 = IntVar()
        Checkbutton(self.ven_emp, text="Calculadora", variable=self.opcion2,
                    bg="#E3B2A0", font=("Tahoma", 10),
                    command=self.ejecutar_calculadora).place(x=35, y=250)


    def _registrar_actividad(self, actividad: str):
        if self.id_empleado_actual is None:
            return
        con = None
        try:
            con = get_db()
            con.execute("""
                INSERT INTO actividades (id_empleado, fecha_hora, usuario, actividad)
                VALUES (?, ?, ?, ?)
            """, (self.id_empleado_actual,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  self.nom_empleado_actual,
                  actividad))
            con.commit()
        except Exception as e:
            print(f"Error registrando actividad: {e}")
        finally:
            if con:
                con.close() 

   
    def salir(self):
        if mes.askyesno("Salir", "¿Estás segura de que deseas salir?"):
            self._registrar_actividad("Cerró sesión")
            self.ven_emp.destroy()
            if self.login is not None:
                self.login.ven.deiconify()

  
    def gestionar_oscuro(self):
        if self.opcion1.get() == 1:
            self.ven_emp.config(bg="#2B2B2B")
            self.lbl_menu_emp.config(bg="#2B2B2B", fg="white")
            self.lbl_subt_emp.config(bg="#2B2B2B")
            self.lbl_info.config(bg="#2B2B2B", fg="white")
        else:
            self.ven_emp.config(bg="#FFECE8")
            self.lbl_menu_emp.config(bg="#FFECE8", fg="black")
            self.lbl_subt_emp.config(bg="#FFECE8")
            self.lbl_info.config(bg="#FFECE8", fg="gray")

    def ejecutar_calculadora(self):
        subprocess.Popen("calc")
        self.opcion2.set(0)

    def abrir_enlace(self, event):
        webbrowser.open("https://13492942.github.io/Base-de-datos-Python/")

   
    def inven(self):
        if self.ven_inven and self.ven_inven.winfo_exists():
            self.ven_inven.focus()
            return

        self._registrar_actividad("Consultó el inventario")

        self.ven_inven = Toplevel(self.ven_emp)
        self.ven_inven.title("Ver inventario")
        self.ven_inven.geometry("700x420")
        self.ven_inven.config(bg="#FFECE8")
        self.ven_inven.resizable(0, 0)
        self.ven_inven.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))

        Label(self.ven_inven, text="", bg="#D94B2F", width=120, height=4).place(x=0, y=0)
        Label(self.ven_inven, text="INVENTARIO 🛍️",
              font=("Tahoma", 18, "bold"), bg="#D94B2F", fg="white").place(x=255, y=15)

        estilo = ttk.Style()
        estilo.configure("Treeview.Heading", font=("Tahoma", 11, "bold"))

        columnas = ("id", "nombre", "stock", "precio", "categoria", "proveedor")
        tree = ttk.Treeview(self.ven_inven, columns=columnas, show="headings", height=14)
        tree.heading("id",        text="ID")
        tree.heading("nombre",    text="Nombre Producto")
        tree.heading("stock",     text="Stock")
        tree.heading("precio",    text="Precio (Lps)")
        tree.heading("categoria", text="Categoría")
        tree.heading("proveedor", text="Proveedor")
        tree.column("id",        width=45,  anchor=CENTER)
        tree.column("nombre",    width=160)
        tree.column("stock",     width=70,  anchor=CENTER)
        tree.column("precio",    width=100, anchor=CENTER)
        tree.column("categoria", width=110)
        tree.column("proveedor", width=120)

        sb = ttk.Scrollbar(self.ven_inven, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.place(x=10, y=75, width=660, height=290)
        sb.place(x=670, y=75, height=290)

        con = None
        try:
            con = get_db()
            cur = con.cursor()
            cur.execute("""
                SELECT p.id_producto, p.nombre_producto, p.stock,
                       p.precio, c.nombre_categoria, pr.nombre_proveedor
                FROM productos p
                LEFT JOIN categorias c   ON p.id_categoria  = c.id_categoria
                LEFT JOIN proveedores pr ON p.id_proveedor  = pr.id_proveedor
                ORDER BY p.nombre_producto
            """)
            for fila in cur.fetchall():
                tree.insert("", "end", values=(fila[0], fila[1], fila[2],
                                               f"L. {fila[3]:.2f}", fila[4], fila[5]))
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_inven)
        finally:
            if con:
                con.close()

        Button(self.ven_inven, text="CERRAR", bg="maroon", fg="white",
               font=("Tahoma", 10, "bold"), width=30,
               command=self.ven_inven.destroy).place(x=220, y=375)

  

    def regis_venta(self):
        
        ventana_existe = getattr(self, 'ven_regis', None)
        if ventana_existe is not None:
            try:
                if ventana_existe.winfo_exists():
                    self.ven_regis.focus()
                    return
            except:
                pass

        self._carrito = []
        self._productos_bd = []

        self.ven_regis = Toplevel(self.ven_emp)
        self.ven_regis.title("Registrar Venta")
        self.ven_regis.geometry("920x640")
        self.ven_regis.config(bg="#FFECE8")
        self.ven_regis.resizable(0, 0)
        self.ven_regis.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))

        

       


  
        self.ven_marco1=LabelFrame(self.ven_regis, text="Registrar Venta", font=("Tahoma", 12, "bold"), bg="white", fg="#E65100")
        self.ven_marco1.place(x=27, y=70, width=858, height=110)


        # Título
        Label(self.ven_regis, text="Registrar Venta 🛒",
              font=("Tahoma", 24, "bold"), bg="#FFECE8", fg="#E65100").place(x=320, y=10)

        # --- FILA 1: CLIENTE Y EMPLEADO ---
        Label(self.ven_regis, text="Cliente:", bg="white", font=("Tahoma", 10, "bold")).place(x=40, y=100)
        self._sv_cliente = StringVar()
        Entry(self.ven_regis, width=25, textvariable=self._sv_cliente,bg="#DEA593").place(x=110, y=100)

        Label(self.ven_regis, text="Empleado:", bg="white", font=("Tahoma", 10, "bold")).place(x=390, y=145)
        self.combo_empleado = ttk.Combobox(self.ven_regis, width=20, state="readonly")
        self.combo_empleado.place(x=465, y=145)

        # Cargar empleados reales en el combo
        con = get_db()
        cur = con.cursor()

        cur.execute("""
            SELECT id_empleado, nombre
            FROM empleados
            WHERE UPPER(estado) = 'ACTIVO'
        """)

        empleados = cur.fetchall()

        con.close()

        self.combo_empleado['values'] = [
            f"{e[0]} - {e[1]}" for e in empleados
        ]




        # --- FILA 2: PRODUCTO (ID y COMBO) ---
        Label(self.ven_regis, text="ID Producto:", bg="white", font=("Tahoma", 10, "bold")).place(x=320, y=100)
        self._sv_id_prod = StringVar()
        self.entry_id = Entry(self.ven_regis, width=10, textvariable=self._sv_id_prod,bg="#DEA593")
        self.entry_id.place(x=425, y=100)
        self.entry_id.bind('<Return>', self._buscar_por_id)

        Label(self.ven_regis, text="O", bg="white", font=("Tahoma", 10, "bold")).place(x=520, y=100)

        Label(self.ven_regis, text="Producto:", bg="white", font=("Tahoma", 10, "bold")).place(x=550, y=100)
        self.combo_prod = ttk.Combobox(self.ven_regis, width=30, state="readonly")
        self.combo_prod.place(x=640, y=110)
        self.combo_prod.bind("<<ComboboxSelected>>", self._mostrar_info_producto)

        # --- FILA 3: CANTIDAD, PRECIO, STOCK ---
        Label(self.ven_regis, text="Cantidad:", bg="white", font=("Tahoma", 10, "bold")).place(x=40, y=146)
        self._sv_cantidad = StringVar()
        Entry(self.ven_regis, width=8, textvariable=self._sv_cantidad,bg="#DEA593").place(x=110, y=146)

        Label(self.ven_regis, text="Precio:", bg="white", font=("Tahoma", 10, "bold")).place(x=187, y=146)
        self.lbl_precio = Label(self.ven_regis, text="L. 0.00", bg="white", fg="#BF360C", font=("Tahoma", 10, "bold"))
        self.lbl_precio.place(x=237, y=146)

        Label(self.ven_regis, text="Stock:", bg="white", font=("Tahoma", 10, "bold")).place(x=300, y=146)
        self.lbl_stock = Label(self.ven_regis, text="0", bg="white", fg="#BF360C", font=("Tahoma", 10, "bold"))
        self.lbl_stock.place(x=350, y=146)

        Button(self.ven_regis, text="➕ Agregar", bg="#27AE60", fg="white",
               font=("Tahoma", 10, "bold"), command=self._agregar_item).place(x=752, y=143)

        # --- TREEVIEW ---
        self.tree_venta = ttk.Treeview(self.ven_regis,
                                        columns=("id", "producto", "precio", "cantidad", "subtotal"),
                                        show="headings", height=14)
        self.tree_venta.heading("id", text="ID")
        self.tree_venta.heading("producto", text="Producto")
        self.tree_venta.heading("precio", text="Precio")
        self.tree_venta.heading("cantidad", text="Cant.")
        self.tree_venta.heading("subtotal", text="Subtotal")
        self.tree_venta.column("id", width=50)
        self.tree_venta.column("producto", width=280)
        self.tree_venta.column("precio", width=100)
        self.tree_venta.column("cantidad", width=80)
        self.tree_venta.column("subtotal", width=120)
        self.tree_venta.place(x=30, y=200, width=860, height=300)

        # --- TOTALES ---
        Label(self.ven_regis, text="Subtotal:", bg="#FFECE8", font=("Tahoma", 12, "bold")).place(x=30, y=520)
        self.lbl_subtotal = Label(self.ven_regis, text="L. 0.00", bg="#FFECE8", fg="#BF360C", font=("Tahoma", 12, "bold"))
        self.lbl_subtotal.place(x=110, y=520)

        Label(self.ven_regis, text="ISV (15%):", bg="#FFECE8", font=("Tahoma", 12, "bold")).place(x=250, y=520)
        self.lbl_isv = Label(self.ven_regis, text="L. 0.00", bg="#FFECE8", fg="#BF360C", font=("Tahoma", 12, "bold"))
        self.lbl_isv.place(x=350, y=520)

        Label(self.ven_regis, text="TOTAL:", bg="#FFECE8", font=("Tahoma", 14, "bold")).place(x=520, y=520)
        self.lbl_total = Label(self.ven_regis, text="L. 0.00", bg="#FFECE8", fg="#E65100", font=("Tahoma", 14, "bold"))
        self.lbl_total.place(x=600, y=520)

        # --- BOTONES ---
        Button(self.ven_regis, text="Eliminar", bg="#C0392B", fg="white",
               font=("Tahoma", 10, "bold"), width=15, command=self._eliminar_item).place(x=30, y=570)
        Button(self.ven_regis, text="Confirmar Venta", bg="#27AE60", fg="white",
               font=("Tahoma", 10, "bold"), width=20, command=self._guardar_venta).place(x=220, y=570)
    

        Button(self.ven_regis,
            text="📄 Generar PDF",
            bg="#F39C12",
            fg="black",
            font=("Tahoma", 10, "bold"),
            width=18,
            command=self._pdf_ultima_venta).place(x=590, y=570)
        Button(self.ven_regis, text="Salir", bg="#7F8C8D", fg="white",
               font=("Tahoma", 10, "bold"), width=15, command=self.ven_regis.destroy).place(x=750, y=570)

        # Cargar productos al abrir
        self._cargar_productos()
        self.ven_regis.mainloop()
  

    def _buscar_por_id(self, event=None):
        if not self._productos_bd:
            mes.showwarning("Aviso", "No hay productos cargados.", parent=self.ven_regis)
            return

        id_buscado = self._sv_id_prod.get().strip()
        
        for i, prod in enumerate(self._productos_bd):
            if str(prod[0]) == id_buscado:
                self.combo_prod.current(i)
                self._mostrar_info_producto()
                return
        
        mes.showwarning("Aviso", "ID de producto no encontrado.", parent=self.ven_regis)
        self.lbl_precio.config(text="L. 0.00")
        self.lbl_stock.config(text="0")


    def _cargar_productos(self):
        self._productos_bd = []
        try:
            con = get_db()
            cur = con.cursor()
            cur.execute("""
                SELECT id_producto, nombre_producto, precio, stock
                FROM productos
                WHERE stock > 0
                ORDER BY nombre_producto
            """)
            self._productos_bd = cur.fetchall()
            con.close()

            # Formato: "ID | Nombre (Stock: X)"
            self.combo_prod['values'] = [
                f"{r[0]} | {r[1]} (Stock: {r[3]})" for r in self._productos_bd
            ]
        except Exception as e:
            print(f"Error cargando productos: {e}")


    def _mostrar_info_producto(self, event=None):
        try:
            idx = self.combo_prod.current()
            if idx >= 0 and idx < len(self._productos_bd):
                prod = self._productos_bd[idx]
                self.lbl_precio.config(text=f"L. {prod[2]:.2f}")
                self.lbl_stock.config(text=str(prod[3]))
        except:
            pass


    def _agregar_item(self):
        if not self._productos_bd:
            mes.showwarning("Aviso", "No hay productos.", parent=self.ven_regis)
            return

        idx = self.combo_prod.current()
        if idx < 0:
            mes.showwarning("Aviso", "Selecciona un producto.", parent=self.ven_regis)
            return

        cant = self._sv_cantidad.get().strip()
        if not cant.isdigit() or int(cant) <= 0:
            mes.showwarning("Aviso", "Cantidad inválida.", parent=self.ven_regis)
            return

        cant = int(cant)
        prod = self._productos_bd[idx]

        if cant > prod[3]:
            mes.showwarning("Aviso", f"Solo hay {prod[3]} en stock.", parent=self.ven_regis)
            return

        # Verificar si ya está en el carrito
        for item in self._carrito:
            if item["id_producto"] == prod[0]:
                nueva_cant = item["cantidad"] + cant
                if nueva_cant > prod[3]:
                    mes.showwarning("Aviso", "Stock insuficiente.", parent=self.ven_regis)
                    return
                item["cantidad"] = nueva_cant
                item["subtotal"] = round(nueva_cant * prod[2], 2)
                self._actualizar_tree()
                self._actualizar_totales()
                self._sv_cantidad.set("")
                return

        # Agregar nuevo item
        self._carrito.append({
            "id_producto": prod[0],
            "nombre": prod[1],
            "precio": prod[2],
            "cantidad": cant,
            "subtotal": round(cant * prod[2], 2)
        })

        self._actualizar_tree()
        self._actualizar_totales()
        self._sv_cantidad.set("")


    def _actualizar_tree(self):
        for row in self.tree_venta.get_children():
            self.tree_venta.delete(row)

        for item in self._carrito:
            self.tree_venta.insert("", "end", values=(
                item["id_producto"],
                item["nombre"],
                f"L. {item['precio']:.2f}",
                item["cantidad"],
                f"L. {item['subtotal']:.2f}"
            ))


    def _actualizar_totales(self):
        subtotal = sum(i["subtotal"] for i in self._carrito)
        isv = round(subtotal * 0.15, 2)
        total = subtotal + isv

        self.lbl_subtotal.config(text=f"L. {subtotal:.2f}")
        self.lbl_isv.config(text=f"L. {isv:.2f}")
        self.lbl_total.config(text=f"L. {total:.2f}")


    def _eliminar_item(self):
        sel = self.tree_venta.selection()
        if not sel:
            mes.showwarning("Aviso", "Selecciona una línea.", parent=self.ven_regis)
            return
        idx = self.tree_venta.index(sel[0])
        self._carrito.pop(idx)
        self._actualizar_tree()
        self._actualizar_totales()


    def _guardar_venta(self):
        if not self._carrito:
            mes.showwarning("Aviso", "El carrito está vacío.", parent=self.ven_regis)
            return

        cliente = self._sv_cliente.get().strip()
        if not cliente:
            mes.showwarning("Aviso", "Ingresa el nombre del cliente.", parent=self.ven_regis)
            return
        
        emp_seleccionado = self.combo_empleado.get()
        if not emp_seleccionado:
            mes.showwarning("Aviso", "Selecciona un empleado.", parent=self.ven_regis)
            return
        
        # Convertimos el ID a entero (int) aquí mismo
        try:
            id_empleado = int(emp_seleccionado.split(" - ")[0])
        except ValueError:
            mes.showerror("Error", "ID de empleado inválido.")
            return

        from datetime import datetime
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subtotal = sum(i["subtotal"] for i in self._carrito)
        isv = round(subtotal * 0.15, 2)
        total = subtotal + isv

        con = None
        try:
            con = get_db()
            con.execute("PRAGMA foreign_keys = ON;")
            cur = con.cursor()
            cur.execute("BEGIN TRANSACTION")

            # Ahora id_empleado es un número entero
            cur.execute("""
                INSERT INTO ventas (fecha, cliente, id_empleado, total) 
                VALUES (?, ?, ?, ?)
            """, (fecha, cliente, id_empleado, total))
            
            id_venta = cur.lastrowid
            self.ultima_venta = id_venta

            for item in self._carrito:
                cur.execute("""
                    INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_momento)
                    VALUES (?, ?, ?, ?)
                """, (id_venta, item["id_producto"], item["cantidad"], item["precio"]))
                
                cur.execute("UPDATE productos SET stock = stock - ? WHERE id_producto = ?",
                            (item["cantidad"], item["id_producto"]))

            con.commit()
            mes.showinfo("Éxito", f"Venta #{id_venta} registrada.", parent=self.ven_regis)
            
            # Limpieza corregida: eliminamos self._sv_empleado que ya no usas
            self._carrito = []
            self._actualizar_tree()
            self._actualizar_totales()
            self._sv_cliente.set("")
            self._sv_cantidad.set("")
            self.combo_empleado.set("") # Limpiamos el combo
            self._cargar_productos()

        except Exception as e:
            if con:
                con.rollback()
                print("Empleado seleccionado:", id_empleado)

                for item in self._carrito:
                    print("Producto:", item["id_producto"])
            mes.showerror("Error", f"No se pudo guardar la venta.\n{str(e)}", parent=self.ven_regis)
        finally:
            if con:
                con.close()
    def _pdf_ultima_venta(self):
        if not hasattr(self, "ultima_venta"):
            mes.showwarning("Aviso", "Primero registra una venta.")
            return

        id_venta = self.ultima_venta

        con = get_db()
        cur = con.cursor()

        cur.execute("""
            SELECT fecha, cliente, total
            FROM ventas
            WHERE id_venta = ?
        """, (id_venta,))

        venta = cur.fetchone()

        cur.execute("""
            SELECT p.nombre_producto,
                dv.cantidad,
                dv.precio_momento
            FROM detalle_ventas dv
            JOIN productos p
                ON p.id_producto = dv.id_producto
            WHERE dv.id_venta = ?
        """, (id_venta,))

        detalle = cur.fetchall()
        con.close()

        archivo = f"Factura_Venta_{id_venta}.pdf"

        c = pdf_canvas.Canvas(archivo, pagesize=letter)

        c.setFont("Helvetica-Bold", 18)
        c.drawString(200, 760, "FERRELAB")

        c.setFont("Helvetica", 11)
        c.drawString(50, 720, f"Venta #: {id_venta}")
        c.drawString(50, 700, f"Fecha: {venta[0]}")
        c.drawString(50, 680, f"Cliente: {venta[1]}")

        y = 620

        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Producto")
        c.drawString(280, y, "Cantidad")
        c.drawString(380, y, "Precio")

        y -= 20

        c.setFont("Helvetica", 10)

        for prod, cant, precio in detalle:
            c.drawString(50, y, str(prod))
            c.drawString(300, y, str(cant))
            c.drawString(400, y, f"L. {precio:.2f}")
            y -= 20

        c.setFont("Helvetica-Bold", 12)
        c.drawString(350, y-20, f"TOTAL: L. {venta[2]:.2f}")

        c.save()

        mes.showinfo(
            "PDF",
            f"Factura PDF generada:\n{archivo}"
        )

        os.startfile(archivo)

    
    
    

    def facturas(self):
        if self.ven_facturas is not None and self.ven_facturas.winfo_exists():
            self.ven_facturas.focus()
            return

        self.ven_facturas = Toplevel(self.ven_emp)
        self.ven_facturas.title("Gestión de Facturas - FerreLab")
        self.ven_facturas.geometry("950x680")
        self.ven_facturas.config(bg="#FFECE8")
        self.ven_facturas.resizable(0, 0)
        self.ven_facturas.iconbitmap(recurso("FerreLab__1_-removebg-preview.ico"))

        

        Label(self.ven_facturas, text="", bg="#73372B", height=2).place(x=0, y=0, width=950)
        Label(self.ven_facturas, text="🧾 GESTIÓN DE FACTURAS",
              font=("Tahoma", 15, "bold"), bg="#73372B", fg="white").place(x=340, y=6)

        LabelFrame(self.ven_facturas, text="Información de la Factura",
                   font=("Tahoma", 11, "bold"), bg="#FFD9D4", fg="#BF360C",
                   width=900, height=110).place(x=25, y=50)

        Label(self.ven_facturas, text="ID Factura:", font=("Tahoma", 9, "bold"),
              bg="#FFD9D4").place(x=40, y=72)
        self.entry_id_factura = StringVar()
        Entry(self.ven_facturas, bg="#C5AFAB", width=15,
              textvariable=self.entry_id_factura, state="readonly").place(x=130, y=72)

        Label(self.ven_facturas, text="ID Venta:", font=("Tahoma", 9, "bold"),
              bg="#FFD9D4").place(x=280, y=72)
        self.entry_id_venta_f = StringVar()
        Entry(self.ven_facturas, bg="#C5AFAB", width=15,
              textvariable=self.entry_id_venta_f).place(x=365, y=72)
        Button(self.ven_facturas, text="Buscar", bg="#FF9800", fg="black",
               font=("Tahoma", 8, "bold"),
               command=self._buscar_venta_para_factura).place(x=500, y=69)

        Label(self.ven_facturas, text="Fecha:", font=("Tahoma", 9, "bold"),
              bg="#FFD9D4").place(x=590, y=72)
        self.entry_fecha_factura = StringVar()
        Entry(self.ven_facturas, bg="#C5AFAB", width=18,
              textvariable=self.entry_fecha_factura, state="readonly").place(x=650, y=72)

        Label(self.ven_facturas, text="Cliente:", font=("Tahoma", 9, "bold"),
              bg="#FFD9D4").place(x=40, y=105)
        self.entry_cliente_factura = StringVar()
        Entry(self.ven_facturas, bg="#C5AFAB", width=40,
              textvariable=self.entry_cliente_factura, state="readonly").place(x=110, y=105)

        Label(self.ven_facturas, text="Estado:", font=("Tahoma", 9, "bold"),
              bg="#FFD9D4").place(x=630, y=105)
        self.entry_estado_factura = StringVar()
        ttk.Combobox(self.ven_facturas, textvariable=self.entry_estado_factura,
                     values=["Pendiente", "Pagada", "Anulada"],
                     width=15, state="readonly").place(x=700, y=105)

        LabelFrame(self.ven_facturas, text="Totales",
                   font=("Tahoma", 11, "bold"), bg="#FFD9D4", fg="#BF360C",
                   width=900, height=90).place(x=25, y=200)

        Label(self.ven_facturas, text="Subtotal (Lps):", font=("Tahoma", 9, "bold"),
              bg="#FFD9D4").place(x=40, y=222)
        self.entry_subtotal_factura = StringVar()
        Entry(self.ven_facturas, bg="#C5AFAB", width=15,
              textvariable=self.entry_subtotal_factura, state="readonly").place(x=170, y=222)

        Label(self.ven_facturas, text="ISV 15% (Lps):", font=("Tahoma", 9, "bold"),
              bg="#FFD9D4").place(x=335, y=222)
        self.entry_isv_factura = StringVar()
        Entry(self.ven_facturas, bg="#C5AFAB", width=15,
              textvariable=self.entry_isv_factura, state="readonly").place(x=470, y=222)

        Label(self.ven_facturas, text="TOTAL (Lps):", font=("Tahoma", 11, "bold"),
              bg="#FFD9D4", fg="#BF360C").place(x=660, y=222)
        self.entry_total_factura = StringVar()
        Entry(self.ven_facturas, bg="#C5AFAB", width=15,
              textvariable=self.entry_total_factura, state="readonly",
              font=("Tahoma", 10, "bold")).place(x=780, y=222)

        Label(self.ven_facturas, text="Descripción:", font=("Tahoma", 9, "bold"),
              bg="#FFD9D4").place(x=40, y=255)
        self.entry_descripcion_factura = StringVar()
        Entry(self.ven_facturas, bg="#C5AFAB", width=108,
              textvariable=self.entry_descripcion_factura).place(x=140, y=255)

        LabelFrame(self.ven_facturas, text="Listado de Facturas",
                   font=("Tahoma", 11, "bold"), bg="#FFD9D4", fg="#BF360C",
                   width=900, height=250).place(x=25, y=305)

        cols_f = ("id_factura", "id_venta", "fecha", "cliente",
                  "subtotal", "isv", "total", "estado")
        self.tree_facturas = ttk.Treeview(self.ven_facturas, columns=cols_f,
                                          show="headings", height=9)
        for col, txt, w in [
            ("id_factura", "ID Fact.", 65), ("id_venta", "ID Venta", 65),
            ("fecha", "Fecha", 130),        ("cliente", "Cliente", 180),
            ("subtotal", "Subtotal", 80),   ("isv", "ISV", 65),
            ("total", "Total (Lps)", 90),   ("estado", "Estado", 85),
        ]:
            self.tree_facturas.heading(col, text=txt)
            self.tree_facturas.column(col, width=w)
        self.tree_facturas.place(x=40, y=325, width=870, height=210)
        self.tree_facturas.bind("<<TreeviewSelect>>", self._seleccionar_factura)

        self._cargar_facturas()

        for txt, bg, fg, x, cmd in [
            ("💾 Guardar",   "#CB6E1D", "white", 40,  self._guardar_factura),
            ("🖨️ Imprimir", "#CB6E1D", "white", 185, self._imprimir_factura),
            ("📄 PDF",       "#FF9800", "black", 330, self._exportar_pdf),
            ("❌ Anular",    "#CA3112", "white", 475, self._anular_factura),
            ("🗑️ Limpiar",  "#FF9800", "black", 620, self._limpiar_factura),
            ("Salir",        "black",   "white", 765, self.ven_facturas.destroy),
        ]:
            Button(self.ven_facturas, text=txt, bg=bg, fg=fg, width=12,
                   font=("Tahoma", 10, "bold"), command=cmd).place(x=x, y=632)


    def _buscar_venta_para_factura(self):
        id_v = self.entry_id_venta_f.get().strip()
        if not id_v.isdigit():
            mes.showwarning("Aviso", "Ingresa un ID de venta válido.", parent=self.ven_facturas)
            return
        con = None
        try:
            con = get_db()
            cur = con.cursor()
            cur.execute("SELECT id_venta, fecha, cliente, total FROM ventas WHERE id_venta=?", (int(id_v),))
            row = cur.fetchone()
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_facturas)
            return
        finally:
            if con:
                con.close()

        if row is None:
            mes.showwarning("No encontrada", f"No existe la venta #{id_v}.", parent=self.ven_facturas)
            return

        _, fecha, cliente, total = row
        subtotal = round(total / 1.15, 2)
        isv      = round(total - subtotal, 2)
        self.entry_fecha_factura.set(fecha)
        self.entry_cliente_factura.set(cliente)
        self.entry_subtotal_factura.set(f"{subtotal:.2f}")
        self.entry_isv_factura.set(f"{isv:.2f}")
        self.entry_total_factura.set(f"{total:.2f}")
        self.entry_estado_factura.set("Pendiente")

    def _guardar_factura(self):
        id_v     = self.entry_id_venta_f.get().strip()
        fecha    = self.entry_fecha_factura.get().strip()
        cliente  = self.entry_cliente_factura.get().strip()
        subtotal = self.entry_subtotal_factura.get().strip()
        isv      = self.entry_isv_factura.get().strip()
        total    = self.entry_total_factura.get().strip()
        estado   = self.entry_estado_factura.get().strip()
        desc     = self.entry_descripcion_factura.get().strip()

        if not all([id_v, fecha, cliente, subtotal, isv, total, estado]):
            mes.showwarning("Aviso", "Busca primero una venta y completa todos los campos.",
                            parent=self.ven_facturas)
            return
        con = None
        try:
            con = get_db()
            cur = con.cursor()
            cur.execute("""
                INSERT INTO facturas (id_venta, fecha, cliente, subtotal, isv, total, estado, descripcion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (int(id_v), fecha, cliente, float(subtotal), float(isv), float(total), estado, desc))
            con.commit()
            id_f = cur.lastrowid
            self.entry_id_factura.set(str(id_f))
            self._registrar_actividad(f"Creó factura #{id_f} para venta #{id_v}")
            mes.showinfo("Guardado", f"Factura #{id_f} guardada correctamente.", parent=self.ven_facturas)
            self._cargar_facturas()
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_facturas)
        finally:
            if con:
                con.close()

    def _cargar_facturas(self):
        for row in self.tree_facturas.get_children():
            self.tree_facturas.delete(row)
        con = None
        try:
            con = get_db()
            cur = con.cursor()
            cur.execute("""
                SELECT id_factura, id_venta, fecha, cliente, subtotal, isv, total, estado
                FROM facturas ORDER BY id_factura DESC
            """)
            for fila in cur.fetchall():
                self.tree_facturas.insert("", "end", values=(
                    fila[0], fila[1], fila[2], fila[3],
                    f"L. {fila[4]:.2f}", f"L. {fila[5]:.2f}",
                    f"L. {fila[6]:.2f}", fila[7]
                ))
        except Exception as e:
            mes.showerror("Error BD", str(e))
        finally:
            if con:
                con.close()

    def _seleccionar_factura(self, event=None):
        sel = self.tree_facturas.selection()
        if not sel:
            return
        vals = self.tree_facturas.item(sel[0], "values")
        self.entry_id_factura.set(vals[0])
        self.entry_id_venta_f.set(vals[1])
        self.entry_fecha_factura.set(vals[2])
        self.entry_cliente_factura.set(vals[3])
        self.entry_subtotal_factura.set(vals[4].replace("L. ", ""))
        self.entry_isv_factura.set(vals[5].replace("L. ", ""))
        self.entry_total_factura.set(vals[6].replace("L. ", ""))
        self.entry_estado_factura.set(vals[7])

    def _anular_factura(self):
        id_f = self.entry_id_factura.get().strip()
        if not id_f:
            mes.showwarning("Aviso", "Selecciona una factura primero.", parent=self.ven_facturas)
            return
        if not mes.askyesno("Confirmar", f"¿Anular factura #{id_f}?", parent=self.ven_facturas):
            return
        con = None
        try:
            con = get_db()
            con.execute("UPDATE facturas SET estado='Anulada' WHERE id_factura=?", (int(id_f),))
            con.commit()
            self._registrar_actividad(f"Anuló factura #{id_f}")
            self._cargar_facturas()
            mes.showinfo("Anulada", f"Factura #{id_f} anulada.", parent=self.ven_facturas)
        except Exception as e:
            mes.showerror("Error BD", str(e), parent=self.ven_facturas)
        finally:
            if con:
                con.close()

    def _limpiar_factura(self):
        for sv in [self.entry_id_factura, self.entry_id_venta_f, self.entry_fecha_factura,
                   self.entry_cliente_factura, self.entry_subtotal_factura,
                   self.entry_isv_factura, self.entry_total_factura,
                   self.entry_estado_factura, self.entry_descripcion_factura]:
            sv.set("")

    def _get_detalle_factura(self, id_venta):
        con = None
        try:
            con = get_db()
            cur = con.cursor()
            cur.execute("""
                SELECT p.nombre_producto, dv.cantidad, dv.precio_momento,
                       (dv.cantidad * dv.precio_momento) AS subtotal
                FROM detalle_ventas dv
                JOIN productos p ON dv.id_producto = p.id_producto
                WHERE dv.id_venta = ?
            """, (int(id_venta),))
            return cur.fetchall()
        except Exception:
            return []
        finally:
            if con:
                con.close()

    def _imprimir_factura(self):
        id_f = self.entry_id_factura.get().strip()
        if not id_f:
            mes.showwarning("Aviso", "Selecciona una factura primero.", parent=self.ven_facturas)
            return

        id_v     = self.entry_id_venta_f.get()
        cliente  = self.entry_cliente_factura.get()
        fecha    = self.entry_fecha_factura.get()
        subtotal = self.entry_subtotal_factura.get()
        isv      = self.entry_isv_factura.get()
        total    = self.entry_total_factura.get()
        estado   = self.entry_estado_factura.get()
        detalle  = self._get_detalle_factura(id_v)

        ven_print = Toplevel(self.ven_facturas)
        ven_print.title(f"Imprimir Factura #{id_f}")
        ven_print.geometry("500x560")
        ven_print.config(bg="white")
        ven_print.resizable(0, 0)

        Label(ven_print, text="FerreLAB", font=("Tahoma", 22, "bold"),
              bg="white", fg="#CA482F").pack(pady=(15, 0))
        Label(ven_print, text="Ferretería y Laboratorio de Construcción S.A.",
              font=("Tahoma", 9), bg="white", fg="gray").pack()
        Label(ven_print, text="─" * 60, bg="white", fg="gray").pack()

        frame_info = Frame(ven_print, bg="white")
        frame_info.pack(fill=X, padx=20)
        for lbl, val in [("Factura #:", id_f), ("Venta #:", id_v),
                          ("Fecha:", fecha), ("Cliente:", cliente), ("Estado:", estado)]:
            r = frame_info.grid_size()[1]
            Label(frame_info, text=lbl, font=("Tahoma", 9, "bold"),
                  bg="white", anchor=W, width=12).grid(row=r, column=0, sticky=W)
            Label(frame_info, text=val, font=("Tahoma", 9),
                  bg="white", anchor=W).grid(row=r, column=1, sticky=W)

        Label(ven_print, text="─" * 60, bg="white", fg="gray").pack()
        Label(ven_print, text="DETALLE", font=("Tahoma", 10, "bold"), bg="white").pack()

        tree_p = ttk.Treeview(ven_print, columns=("prod", "cant", "precio", "sub"),
                               show="headings", height=7)
        tree_p.heading("prod",   text="Producto")
        tree_p.heading("cant",   text="Cant.")
        tree_p.heading("precio", text="Precio")
        tree_p.heading("sub",    text="Subtotal")
        tree_p.column("prod",   width=200)
        tree_p.column("cant",   width=50,  anchor=CENTER)
        tree_p.column("precio", width=90,  anchor=CENTER)
        tree_p.column("sub",    width=90,  anchor=CENTER)
        tree_p.pack(padx=15, pady=5)
        for row in detalle:
            tree_p.insert("", "end", values=(row[0], row[1], f"L. {row[2]:.2f}", f"L. {row[3]:.2f}"))

        Label(ven_print, text="─" * 60, bg="white", fg="gray").pack()
        for lbl, val in [("Subtotal:", f"L. {subtotal}"),
                          ("ISV 15%:", f"L. {isv}"),
                          ("TOTAL:",   f"L. {total}")]:
            Label(ven_print, text=f"{lbl}  {val}",
                  font=("Tahoma", 11, "bold" if lbl == "TOTAL:" else "normal"),
                  bg="white", fg="#CA482F" if lbl == "TOTAL:" else "black").pack()

        Label(ven_print, text="¡Gracias por su compra!", font=("Tahoma", 9, "italic"),
              bg="white", fg="gray").pack(pady=5)
        Button(ven_print, text="🖨️ Enviar a impresora", bg="#CA482F", fg="white",
               font=("Tahoma", 10, "bold"),
               command=lambda: self._enviar_impresora(ven_print, id_f)).pack(pady=8)

        self._registrar_actividad(f"Imprimió factura #{id_f}")

    def _enviar_impresora(self, ventana, id_f):
        ruta = self._generar_pdf_factura(id_f, silent=True)
        if ruta:
            os.startfile(ruta, "print")
            ventana.destroy()

    def _exportar_pdf(self):
        id_f = self.entry_id_factura.get().strip()
        if not id_f:
            mes.showwarning("Aviso", "Selecciona una factura primero.", parent=self.ven_facturas)
            return
        ruta = self._generar_pdf_factura(id_f, silent=False)
        if ruta:
            self._registrar_actividad(f"Exportó PDF de factura #{id_f}")
            mes.showinfo("PDF Generado", f"Factura guardada en:\n{ruta}", parent=self.ven_facturas)
            os.startfile(ruta)

    def _generar_pdf_factura(self, id_f, silent=False):
        id_v     = self.entry_id_venta_f.get()
        cliente  = self.entry_cliente_factura.get()
        fecha    = self.entry_fecha_factura.get()
        subtotal = self.entry_subtotal_factura.get()
        isv      = self.entry_isv_factura.get()
        total    = self.entry_total_factura.get()
        estado   = self.entry_estado_factura.get()
        detalle  = self._get_detalle_factura(id_v)

        nombre_archivo = f"Factura_{id_f}.pdf"
        try:
            c = pdf_canvas.Canvas(nombre_archivo, pagesize=letter)
            w, h = letter

            c.setFillColor(colors.HexColor("#CA482F"))
            c.rect(0, h - 80, w, 80, fill=True, stroke=False)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 26)
            c.drawString(50, h - 42, "FerreLAB")
            c.setFont("Helvetica", 10)
            c.drawString(50, h - 62, "Ferreteria y Laboratorio de Construccion S.A.")

            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, h - 110, f"FACTURA  #{id_f}")

            y = h - 140
            for lbl, val in [("Venta #:", id_v), ("Fecha:", fecha),
                              ("Cliente:", cliente), ("Estado:", estado)]:
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y, lbl)
                c.setFont("Helvetica", 10)
                c.drawString(160, y, val)
                y -= 18

            y -= 10
            c.setStrokeColor(colors.HexColor("#CA482F"))
            c.setLineWidth(1.5)
            c.line(50, y, w - 50, y)
            y -= 20

            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#CA482F"))
            c.drawString(55,  y, "Producto")
            c.drawString(305, y, "Cant.")
            c.drawString(375, y, "Precio")
            c.drawString(460, y, "Subtotal")
            c.setFillColor(colors.black)
            y -= 5
            c.line(50, y, w - 50, y)
            y -= 15

            c.setFont("Helvetica", 10)
            for row in detalle:
                c.drawString(55,  y, str(row[0])[:35])
                c.drawString(310, y, str(row[1]))
                c.drawString(375, y, f"L. {row[2]:.2f}")
                c.drawString(460, y, f"L. {row[3]:.2f}")
                y -= 16
                if y < 120:
                    c.showPage()
                    y = h - 60

            y -= 10
            c.line(50, y, w - 50, y)
            y -= 20
            c.setFont("Helvetica", 11)
            c.drawString(380, y, f"Subtotal:  L. {subtotal}")
            y -= 18
            c.drawString(380, y, f"ISV 15%:   L. {isv}")
            y -= 18
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(colors.HexColor("#CA482F"))
            c.drawString(380, y, f"TOTAL:     L. {total}")

            c.setFillColor(colors.gray)
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(50, 40, "Gracias por su compra en FerreLab. Este documento es su comprobante de pago.")
            c.save()
            return nombre_archivo
        except Exception as e:
            if not silent:
                mes.showerror("Error PDF", str(e), parent=self.ven_facturas)
            return None


if __name__ == "__main__":
    root = Tk()
    app = menu_empleado(root)
    root.mainloop()