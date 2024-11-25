import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import win32print
import win32api

# Archivo JSON para almacenar el historial de pedidos
DATABASE_FILE = "historial.json"

# Cargar o inicializar la base de datos
if not os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, "w") as db:
        json.dump([], db)

# Función para cargar el historial de pedidos
def cargar_historial():
    with open(DATABASE_FILE, "r") as db:
        return json.load(db)

# Función para guardar un nuevo pedido
def guardar_pedido(pedido):
    historial = cargar_historial()
    historial.append(pedido)
    with open(DATABASE_FILE, "w") as db:
        json.dump(historial, db, indent=4)

# Clase principal del sistema
class FacturacionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Facturación")
        self.root.geometry("800x600")

        # Variables
        self.producto_var = tk.StringVar()
        self.cantidad_var = tk.IntVar(value=1)
        self.precio_var = tk.DoubleVar(value=0.0)
        self.pedido_actual = []

        # Frame para agregar elementos al pedido
        frame_agregar = tk.LabelFrame(root, text="Agregar Producto")
        frame_agregar.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_agregar, text="Producto:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_producto = tk.Entry(frame_agregar, textvariable=self.producto_var)
        self.entry_producto.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_agregar, text="Cantidad:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_cantidad = tk.Entry(frame_agregar, textvariable=self.cantidad_var)
        self.entry_cantidad.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame_agregar, text="Precio:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_precio = tk.Entry(frame_agregar, textvariable=self.precio_var)
        self.entry_precio.grid(row=0, column=5, padx=5, pady=5)

        tk.Button(frame_agregar, text="Agregar", command=self.agregar_producto).grid(row=0, column=6, padx=5, pady=5)

        # Tabla de pedido actual
        self.tabla_pedido = ttk.Treeview(root, columns=("Producto", "Cantidad", "Precio", "Subtotal"), show="headings")
        self.tabla_pedido.heading("Producto", text="Producto")
        self.tabla_pedido.heading("Cantidad", text="Cantidad")
        self.tabla_pedido.heading("Precio", text="Precio Unitario")
        self.tabla_pedido.heading("Subtotal", text="Subtotal")
        self.tabla_pedido.pack(fill="both", padx=10, pady=10, expand=True)

        # Botones de control
        frame_botones = tk.Frame(root)
        frame_botones.pack(fill="x", padx=10, pady=10)

        tk.Button(frame_botones, text="Guardar Pedido", command=self.guardar_pedido_actual).pack(side="left", padx=5)
        tk.Button(frame_botones, text="Guardar como PDF", command=self.guardar_pdf).pack(side="left", padx=5)
        tk.Button(frame_botones, text="Imprimir", command=self.imprimir_pedido).pack(side="left", padx=5)

        # Historial de pedidos
        tk.Label(root, text="Historial de Pedidos").pack(pady=10)
        self.tabla_historial = ttk.Treeview(root, columns=("Producto", "Cantidad", "Precio"), show="headings")
        self.tabla_historial.heading("Producto", text="Producto")
        self.tabla_historial.heading("Cantidad", text="Cantidad")
        self.tabla_historial.heading("Precio", text="Precio Total")
        self.tabla_historial.pack(fill="both", padx=10, pady=10, expand=True)

        self.cargar_historial()

    def agregar_producto(self):
        producto = self.producto_var.get()
        cantidad = self.cantidad_var.get()
        precio = self.precio_var.get()
        if not producto or cantidad <= 0 or precio <= 0:
            messagebox.showerror("Error", "Por favor, ingresa datos válidos.")
            return
        subtotal = cantidad * precio
        self.pedido_actual.append({"producto": producto, "cantidad": cantidad, "precio": precio, "subtotal": subtotal})
        self.tabla_pedido.insert("", "end", values=(producto, cantidad, precio, subtotal))
        self.producto_var.set("")
        self.cantidad_var.set(1)
        self.precio_var.set(0.0)

    def guardar_pedido_actual(self):
        if not self.pedido_actual:
            messagebox.showerror("Error", "El pedido está vacío.")
            return
        guardar_pedido(self.pedido_actual)
        self.pedido_actual = []
        self.tabla_pedido.delete(*self.tabla_pedido.get_children())
        messagebox.showinfo("Éxito", "Pedido guardado con éxito.")
        self.cargar_historial()

    def cargar_historial(self):
        self.tabla_historial.delete(*self.tabla_historial.get_children())
        historial = cargar_historial()
        for pedido in historial:
            for item in pedido:
                self.tabla_historial.insert("", "end", values=(item["producto"], item["cantidad"], item["subtotal"]))

    def guardar_pdf(self):
        if not self.pedido_actual:
            messagebox.showerror("Error", "El pedido está vacío.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return
        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(100, 750, "Factura")
        y = 700
        for item in self.pedido_actual:
            c.drawString(100, y, f"{item['producto']} - {item['cantidad']} x {item['precio']} = {item['subtotal']}")
            y -= 20
        c.save()
        messagebox.showinfo("Éxito", "Factura guardada como PDF.")

    def imprimir_pedido(self):
        if not self.pedido_actual:
            messagebox.showerror("Error", "El pedido está vacío.")
            return
        temp_file = tempfile.mktemp(".txt")
        with open(temp_file, "w") as f:
            f.write("""
                Factura\n
                ============== Franklin O&M ==============
""")
            for item in self.pedido_actual:
                f.write(f"""
                Producto {item['producto']} - Cantidad {item['cantidad']}\n
                ================ Detalles ================
                Precicio {item['precio']} 
                Subtotal {item['subtotal']}\n
""")
        win32api.ShellExecute(0, "print", temp_file, None, ".", 0)


# Crear la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = FacturacionApp(root)
    root.mainloop()
