from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import tkinter as tk
from tkinter import ttk

# Configuración de la base de datos
engine = create_engine('mysql+pymysql://root:Woodkid35712/@127.0.0.1/registro_ORM')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Definición de las tablas
class Envio(Base):
    __tablename__ = 'envios'
    id = Column(Integer, primary_key=True)
    remitente = Column(String(100))
    destinatario = Column(String(100))
    dni_destinatario = Column(String(8))
    codigo_envio = Column(String(5))
    fecha_envio = Column(DateTime, default=datetime.now)

class HistorialEnvio(Base):
    __tablename__ = 'historial_envios'
    id = Column(Integer, primary_key=True)
    remitente = Column(String(100))
    destinatario = Column(String(100))
    dni_destinatario = Column(String(8))
    codigo_envio = Column(String(5))
    fecha_envio = Column(DateTime)

Base.metadata.create_all(engine)

# Variables globales
envio_id_editar = None

# Función para mover un envío al historial
def completar_envio(envio_id):
    envio = session.query(Envio).filter_by(id=envio_id).first()
    if envio:
        historial = HistorialEnvio(
            remitente=envio.remitente,
            destinatario=envio.destinatario,
            dni_destinatario=envio.dni_destinatario,
            codigo_envio=envio.codigo_envio,
            fecha_envio=envio.fecha_envio
        )
        session.add(historial)
        session.delete(envio)
        session.commit()
        actualizar_lista_envios()

# Función para actualizar la lista de envíos
def actualizar_lista_envios():
    for item in tree.get_children():
        tree.delete(item)
    envios = session.query(Envio).all()
    for envio in envios:
        tree.insert("", "end", values=(envio.id, envio.remitente, envio.destinatario, envio.dni_destinatario, envio.codigo_envio, envio.fecha_envio))

# Función para guardar un nuevo envío o actualizar uno existente
def guardar_envio():
    global envio_id_editar
    remitente = entry_remitente.get()
    destinatario = entry_destinatario.get()
    dni_destinatario = entry_dni.get()
    codigo_envio = entry_codigo.get()

    if envio_id_editar:  # Si estamos editando un envío existente
        envio = session.query(Envio).filter_by(id=envio_id_editar).first()
        if envio:
            envio.remitente = remitente
            envio.destinatario = destinatario
            envio.dni_destinatario = dni_destinatario
            envio.codigo_envio = codigo_envio
        envio_id_editar = None
    else:  # Si estamos agregando un nuevo envío
        envio = Envio(remitente=remitente, destinatario=destinatario, dni_destinatario=dni_destinatario, codigo_envio=codigo_envio)
        session.add(envio)
    
    session.commit()
    actualizar_lista_envios()
    limpiar_campos()

# Función para generar un código de envío aleatorio
def generar_codigo():
    import random
    entry_codigo.delete(0, tk.END)
    entry_codigo.insert(0, f"{random.randint(10000, 99999)}")

# Función para mostrar el historial
def mostrar_historial():
    historial_window = tk.Toplevel(root)
    historial_window.title("Historial de Envíos")

    tree_historial = ttk.Treeview(historial_window, columns=("ID", "Remitente", "Destinatario", "DNI Destinatario", "Código", "Fecha"), show="headings")
    tree_historial.heading("ID", text="ID")
    tree_historial.heading("Remitente", text="Remitente")
    tree_historial.heading("Destinatario", text="Destinatario")
    tree_historial.heading("DNI Destinatario", text="DNI Destinatario")
    tree_historial.heading("Código", text="Código")
    tree_historial.heading("Fecha", text="Fecha")

    tree_historial.pack(fill=tk.BOTH, expand=True)

    envios_historial = session.query(HistorialEnvio).all()
    for envio in envios_historial:
        tree_historial.insert("", "end", values=(envio.id, envio.remitente, envio.destinatario, envio.dni_destinatario, envio.codigo_envio, envio.fecha_envio))

# Función para cargar datos en los campos para edición
def editar_envio():
    global envio_id_editar
    selected_item = tree.selection()
    if selected_item:
        envio_id = tree.item(selected_item[0], "values")[0]
        envio = session.query(Envio).filter_by(id=envio_id).first()
        if envio:
            envio_id_editar = envio.id
            entry_remitente.delete(0, tk.END)
            entry_remitente.insert(0, envio.remitente)
            entry_destinatario.delete(0, tk.END)
            entry_destinatario.insert(0, envio.destinatario)
            entry_dni.delete(0, tk.END)
            entry_dni.insert(0, envio.dni_destinatario)
            entry_codigo.delete(0, tk.END)
            entry_codigo.insert(0, envio.codigo_envio)

# Función para limpiar los campos de entrada
def limpiar_campos():
    entry_remitente.delete(0, tk.END)
    entry_destinatario.delete(0, tk.END)
    entry_dni.delete(0, tk.END)
    entry_codigo.delete(0, tk.END)

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Gestión de Envíos")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Remitente:").grid(row=0, column=0)
entry_remitente = tk.Entry(frame)
entry_remitente.grid(row=0, column=1)

tk.Label(frame, text="Destinatario:").grid(row=1, column=0)
entry_destinatario = tk.Entry(frame)
entry_destinatario.grid(row=1, column=1)

tk.Label(frame, text="DNI Destinatario:").grid(row=2, column=0)
entry_dni = tk.Entry(frame)
entry_dni.grid(row=2, column=1)

tk.Label(frame, text="Código de Envío:").grid(row=3, column=0)
entry_codigo = tk.Entry(frame)
entry_codigo.grid(row=3, column=1)

tk.Button(frame, text="Generar Código", command=generar_codigo).grid(row=3, column=2)
tk.Button(frame, text="Guardar Envío", command=guardar_envio).grid(row=4, column=0, columnspan=3)

# Tabla de envíos
columns = ("ID", "Remitente", "Destinatario", "DNI Destinatario", "Código", "Fecha")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)

tree.pack(fill=tk.BOTH, expand=True)

# Botones de acciones adicionales
tk.Button(root, text="Completado", command=lambda: completar_envio(tree.item(tree.selection()[0], "values")[0]) if tree.selection() else None).pack(side=tk.LEFT, padx=10)
tk.Button(root, text="Editar", command=editar_envio).pack(side=tk.LEFT, padx=10)
tk.Button(root, text="Ver Historial", command=mostrar_historial).pack(side=tk.LEFT, padx=10)

actualizar_lista_envios()
root.mainloop()


