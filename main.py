#!/usr/bin/env python3
import argparse
import json
import sys
from database.database import engine, Base
from controllers import auth_controller, asic_controller, estado_controller, curso_controller, pnf_controller, bajlic_controller
from reports.report_module import generate_report
from utils.export_import import export_to_json, export_to_excel, export_to_word, export_to_pdf, import_from_json
from database.database import SessionLocal

def launch_gui():
    try:
        import tkinter as tk
        from tkinter import messagebox, scrolledtext
    except ImportError:
        print("Error: Tkinter no está disponible. La interfaz gráfica requiere Windows.")
        print("Use los comandos CLI en su lugar.")
        return
    root = tk.Tk()
    root.title("CREBLITRA - Sistema de Gestión")
    root.geometry("800x600")
    
    # Título
    title_label = tk.Label(root, text="Sistema CREBLITRA", font=("Arial", 18, "bold"))
    title_label.pack(pady=10)
    
    # Frame principal
    main_frame = tk.Frame(root)
    main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
    
    # Área de output
    output_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
    output_text.pack(pady=10, fill=tk.BOTH, expand=True)
    
    # Frame para botones
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=10)
    
    # Botones para módulos
    modules = [
        ("Usuarios", lambda: open_auth_window(output_text)),
        ("ASIC", lambda: open_module_window("asic", output_text)),
        ("Estado", lambda: open_module_window("estado", output_text)),
        ("Curso", lambda: open_module_window("curso", output_text)),
        ("PNF", lambda: open_module_window("pnf", output_text)),
        ("BAJLIC", lambda: open_bajlic_window(output_text)),
        ("Reportes", lambda: open_report_window(output_text)),
        ("Exportar", lambda: open_export_window(output_text)),
        ("Importar", lambda: open_import_window(output_text)),
        ("Gráficos", lambda: open_chart_window(output_text))
    ]
    
    for name, cmd in modules:
        btn = tk.Button(button_frame, text=name, command=cmd, width=12, height=2)
        btn.pack(side=tk.LEFT, padx=5)
    
    # Botón salir
    exit_btn = tk.Button(main_frame, text="Salir", command=root.quit, bg="red", fg="white", width=10)
    exit_btn.pack(pady=10)
    
    root.mainloop()

def open_auth_window(output):
    window = tk.Toplevel()
    window.title("Gestión de Usuarios")
    window.geometry("500x400")
    
    tk.Label(window, text="Gestión de Usuarios", font=("Arial", 14)).pack(pady=10)
    
    actions = [
        ("Crear Usuario", lambda: create_user_dialog(window, output)),
        ("Login", lambda: login_dialog(window, output)),
        ("Listar Usuarios", lambda: list_users(output)),
        ("Actualizar Usuario", lambda: update_user_dialog(window, output)),
        ("Eliminar Usuario", lambda: delete_user_dialog(window, output))
    ]
    
    for name, cmd in actions:
        tk.Button(window, text=name, command=cmd, width=20).pack(pady=5)
    
    tk.Button(window, text="Cerrar", command=window.destroy).pack(pady=10)

def create_user_dialog(parent, output):
    dialog = tk.Toplevel(parent)
    dialog.title("Crear Usuario")
    dialog.geometry("300x200")
    
    tk.Label(dialog, text="Username:").pack()
    username_entry = tk.Entry(dialog)
    username_entry.pack()
    
    tk.Label(dialog, text="Password:").pack()
    password_entry = tk.Entry(dialog, show="*")
    password_entry.pack()
    
    tk.Label(dialog, text="Role:").pack()
    role_entry = tk.Entry(dialog)
    role_entry.pack()
    
    def create():
        db = SessionLocal()
        try:
            user = auth_controller.create_user(db, username_entry.get(), password_entry.get(), role_entry.get())
            output.insert(tk.END, f"Usuario creado: {user.username}\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Crear", command=create).pack(pady=10)

def login_dialog(parent, output):
    dialog = tk.Toplevel(parent)
    dialog.title("Login")
    dialog.geometry("300x150")
    
    tk.Label(dialog, text="Username:").pack()
    username_entry = tk.Entry(dialog)
    username_entry.pack()
    
    tk.Label(dialog, text="Password:").pack()
    password_entry = tk.Entry(dialog, show="*")
    password_entry.pack()
    
    def login():
        db = SessionLocal()
        try:
            user = auth_controller.authenticate_user(db, username_entry.get(), password_entry.get())
            if user:
                output.insert(tk.END, f"Login exitoso: {user.username}\n")
            else:
                output.insert(tk.END, "Credenciales inválidas\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Login", command=login).pack(pady=10)

def list_users(output):
    db = SessionLocal()
    try:
        users = auth_controller.get_users(db)
        output.insert(tk.END, "Usuarios:\n")
        for u in users:
            output.insert(tk.END, f"ID: {u.id}, Username: {u.username}, Role: {u.role}\n")
    finally:
        db.close()

def update_user_dialog(parent, output):
    dialog = tk.Toplevel(parent)
    dialog.title("Actualizar Usuario")
    dialog.geometry("300x200")
    
    tk.Label(dialog, text="User ID:").pack()
    id_entry = tk.Entry(dialog)
    id_entry.pack()
    
    tk.Label(dialog, text="Nuevo Username:").pack()
    username_entry = tk.Entry(dialog)
    username_entry.pack()
    
    tk.Label(dialog, text="Nuevo Role:").pack()
    role_entry = tk.Entry(dialog)
    role_entry.pack()
    
    def update():
        db = SessionLocal()
        try:
            success = auth_controller.update_user(db, int(id_entry.get()), username_entry.get() or None, None, role_entry.get() or None)
            output.insert(tk.END, "Usuario actualizado\n" if success else "Usuario no encontrado\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Actualizar", command=update).pack(pady=10)

def delete_user_dialog(parent, output):
    dialog = tk.Toplevel(parent)
    dialog.title("Eliminar Usuario")
    dialog.geometry("300x100")
    
    tk.Label(dialog, text="User ID:").pack()
    id_entry = tk.Entry(dialog)
    id_entry.pack()
    
    def delete():
        db = SessionLocal()
        try:
            success = auth_controller.delete_user(db, int(id_entry.get()))
            output.insert(tk.END, "Usuario eliminado\n" if success else "Usuario no encontrado\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Eliminar", command=delete).pack(pady=10)

def open_module_window(module, output):
    window = tk.Toplevel()
    window.title(f"Gestión de {module.upper()}")
    window.geometry("500x400")
    
    tk.Label(window, text=f"Gestión de {module.upper()}", font=("Arial", 14)).pack(pady=10)
    
    actions = [
        ("Crear", lambda: create_module_dialog(window, module, output)),
        ("Leer", lambda: read_module(module, output)),
        ("Actualizar", lambda: update_module_dialog(window, module, output)),
        ("Eliminar", lambda: delete_module_dialog(window, module, output))
    ]
    
    for name, cmd in actions:
        tk.Button(window, text=name, command=cmd, width=20).pack(pady=5)
    
    tk.Button(window, text="Cerrar", command=window.destroy).pack(pady=10)

def create_module_dialog(parent, module, output):
    dialog = tk.Toplevel(parent)
    dialog.title(f"Crear {module.upper()}")
    dialog.geometry("300x150")
    
    tk.Label(dialog, text="Código:").pack()
    codigo_entry = tk.Entry(dialog)
    codigo_entry.pack()
    
    tk.Label(dialog, text="Descripción:").pack()
    desc_entry = tk.Entry(dialog)
    desc_entry.pack()
    
    def create():
        db = SessionLocal()
        try:
            controller = globals()[f"{module}_controller"]
            item = getattr(controller, f"create_{module}")(db, int(codigo_entry.get()), desc_entry.get())
            output.insert(tk.END, f"{module.upper()} creado: {item.id}\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Crear", command=create).pack(pady=10)

def read_module(module, output):
    db = SessionLocal()
    try:
        controller = globals()[f"{module}_controller"]
        items = getattr(controller, f"get_{module}s")(db)
        output.insert(tk.END, f"{module.upper()}s:\n")
        for i in items[:20]:
            output.insert(tk.END, f"ID: {i.id}, Código: {i.codigo}, Descripción: {i.descripcion}\n")
    finally:
        db.close()

def update_module_dialog(parent, module, output):
    dialog = tk.Toplevel(parent)
    dialog.title(f"Actualizar {module.upper()}")
    dialog.geometry("300x200")
    
    tk.Label(dialog, text="ID:").pack()
    id_entry = tk.Entry(dialog)
    id_entry.pack()
    
    tk.Label(dialog, text="Nuevo Código:").pack()
    codigo_entry = tk.Entry(dialog)
    codigo_entry.pack()
    
    tk.Label(dialog, text="Nueva Descripción:").pack()
    desc_entry = tk.Entry(dialog)
    desc_entry.pack()
    
    def update():
        db = SessionLocal()
        try:
            controller = globals()[f"{module}_controller"]
            success = getattr(controller, f"update_{module}")(db, int(id_entry.get()), int(codigo_entry.get()) if codigo_entry.get() else None, desc_entry.get() or None)
            output.insert(tk.END, f"{module.upper()} actualizado\n" if success else f"{module.upper()} no encontrado\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Actualizar", command=update).pack(pady=10)

def delete_module_dialog(parent, module, output):
    dialog = tk.Toplevel(parent)
    dialog.title(f"Eliminar {module.upper()}")
    dialog.geometry("300x100")
    
    tk.Label(dialog, text="ID:").pack()
    id_entry = tk.Entry(dialog)
    id_entry.pack()
    
    def delete():
        db = SessionLocal()
        try:
            controller = globals()[f"{module}_controller"]
            success = getattr(controller, f"delete_{module}")(db, int(id_entry.get()))
            output.insert(tk.END, f"{module.upper()} eliminado\n" if success else f"{module.upper()} no encontrado\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Eliminar", command=delete).pack(pady=10)

def open_bajlic_window(output):
    window = tk.Toplevel()
    window.title("Gestión de BAJLIC")
    window.geometry("600x400")
    
    tk.Label(window, text="Gestión de BAJLIC", font=("Arial", 14)).pack(pady=10)
    
    actions = [
        ("Crear", lambda: create_bajlic_dialog(window, output)),
        ("Leer", lambda: read_bajlic(output)),
        ("Actualizar", lambda: update_bajlic_dialog(window, output)),
        ("Eliminar", lambda: delete_bajlic_dialog(window, output))
    ]
    
    for name, cmd in actions:
        tk.Button(window, text=name, command=cmd, width=20).pack(pady=5)
    
    tk.Button(window, text="Cerrar", command=window.destroy).pack(pady=10)

def create_bajlic_dialog(parent, output):
    dialog = tk.Toplevel(parent)
    dialog.title("Crear BAJLIC")
    dialog.geometry("400x300")
    
    fields = ["Caso", "Estado ID", "ASIC ID", "Documento", "Apellido1", "Apellido2", "Nombres", "Causa", "Fecha Tram", "An Curso", "Curso ID", "Traslado", "PNF ID"]
    entries = {}
    
    for field in fields:
        tk.Label(dialog, text=f"{field}:").pack()
        entry = tk.Entry(dialog)
        entry.pack()
        entries[field.lower().replace(" ", "_")] = entry
    
    def create():
        db = SessionLocal()
        try:
            bajlic = bajlic_controller.create_bajlic(
                db,
                int(entries["caso"].get()),
                int(entries["estado_id"].get()),
                int(entries["asic_id"].get()),
                entries["documento"].get(),
                entries["apellido1"].get(),
                entries["apellido2"].get() or None,
                entries["nombres"].get(),
                entries["causa"].get() or None,
                entries["fecha_tram"].get() or None,
                int(entries["an_curso"].get()) if entries["an_curso"].get() else None,
                int(entries["curso_id"].get()) if entries["curso_id"].get() else None,
                entries["traslado"].get() or None,
                int(entries["pnf_id"].get()) if entries["pnf_id"].get() else None
            )
            output.insert(tk.END, f"BAJLIC creado: {bajlic.id}\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Crear", command=create).pack(pady=10)

def read_bajlic(output):
    db = SessionLocal()
    try:
        bajlics = bajlic_controller.get_bajlics(db)
        output.insert(tk.END, "BAJLICs:\n")
        for b in bajlics[:20]:
            output.insert(tk.END, f"ID: {b.id}, Caso: {b.caso}, Nombres: {b.nombres}\n")
    finally:
        db.close()

def update_bajlic_dialog(parent, output):
    dialog = tk.Toplevel(parent)
    dialog.title("Actualizar BAJLIC")
    dialog.geometry("400x200")
    
    tk.Label(dialog, text="ID:").pack()
    id_entry = tk.Entry(dialog)
    id_entry.pack()
    
    tk.Label(dialog, text="Nombres:").pack()
    nombres_entry = tk.Entry(dialog)
    nombres_entry.pack()
    
    def update():
        db = SessionLocal()
        try:
            success = bajlic_controller.update_bajlic(db, int(id_entry.get()), nombres=nombres_entry.get())
            output.insert(tk.END, "BAJLIC actualizado\n" if success else "BAJLIC no encontrado\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Actualizar", command=update).pack(pady=10)

def delete_bajlic_dialog(parent, output):
    dialog = tk.Toplevel(parent)
    dialog.title("Eliminar BAJLIC")
    dialog.geometry("300x100")
    
    tk.Label(dialog, text="ID:").pack()
    id_entry = tk.Entry(dialog)
    id_entry.pack()
    
    def delete():
        db = SessionLocal()
        try:
            success = bajlic_controller.delete_bajlic(db, int(id_entry.get()))
            output.insert(tk.END, "BAJLIC eliminado\n" if success else "BAJLIC no encontrado\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Eliminar", command=delete).pack(pady=10)

def open_report_window(output):
    dialog = tk.Toplevel()
    dialog.title("Generar Reporte")
    dialog.geometry("300x150")
    
    tk.Label(dialog, text="Tabla:").pack()
    table_entry = tk.Entry(dialog)
    table_entry.pack()
    
    tk.Label(dialog, text="Filtros JSON:").pack()
    filters_entry = tk.Entry(dialog)
    filters_entry.pack()
    
    def generate():
        db = SessionLocal()
        try:
            filters = json.loads(filters_entry.get() or "{}")
            rows = generate_report(db, table_entry.get(), filters)
            output.insert(tk.END, f"Reporte generado. Total: {len(rows)}\n")
            for row in rows[:10]:
                output.insert(tk.END, f"{row}\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Generar", command=generate).pack(pady=10)

def open_export_window(output):
    dialog = tk.Toplevel()
    dialog.title("Exportar Datos")
    dialog.geometry("300x150")
    
    tk.Label(dialog, text="Tabla:").pack()
    table_entry = tk.Entry(dialog)
    table_entry.pack()
    
    tk.Label(dialog, text="Formato:").pack()
    format_var = tk.StringVar(value="json")
    tk.OptionMenu(dialog, format_var, "json", "excel", "word", "pdf").pack()
    
    tk.Label(dialog, text="Archivo:").pack()
    file_entry = tk.Entry(dialog)
    file_entry.pack()
    
    def export():
        db = SessionLocal()
        try:
            fmt = format_var.get()
            if fmt == "json":
                export_to_json(db, table_entry.get(), file_entry.get())
            elif fmt == "excel":
                export_to_excel(db, table_entry.get(), file_entry.get())
            elif fmt == "word":
                export_to_word(db, table_entry.get(), file_entry.get())
            elif fmt == "pdf":
                export_to_pdf(db, table_entry.get(), file_entry.get())
            output.insert(tk.END, f"Datos exportados a {file_entry.get()}\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Exportar", command=export).pack(pady=10)

def open_import_window(output):
    dialog = tk.Toplevel()
    dialog.title("Importar Datos")
    dialog.geometry("300x100")
    
    tk.Label(dialog, text="Tabla:").pack()
    table_entry = tk.Entry(dialog)
    table_entry.pack()
    
    tk.Label(dialog, text="Archivo JSON:").pack()
    file_entry = tk.Entry(dialog)
    file_entry.pack()
    
    def import_data():
        db = SessionLocal()
        try:
            import_from_json(db, table_entry.get(), file_entry.get())
            output.insert(tk.END, f"Datos importados desde {file_entry.get()}\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Importar", command=import_data).pack(pady=10)

def open_chart_window(output):
    dialog = tk.Toplevel()
    dialog.title("Generar Gráfico")
    dialog.geometry("300x200")
    
    tk.Label(dialog, text="Tabla:").pack()
    table_var = tk.StringVar(value="asic")
    tk.OptionMenu(dialog, table_var, "asic", "estado", "curso", "pnf", "bajlic").pack()
    
    tk.Label(dialog, text="Tipo:").pack()
    type_var = tk.StringVar(value="bar")
    tk.OptionMenu(dialog, type_var, "bar", "line", "pie").pack()
    
    tk.Label(dialog, text="Columna X:").pack()
    x_entry = tk.Entry(dialog)
    x_entry.insert(0, "descripcion")
    x_entry.pack()
    
    tk.Label(dialog, text="Columna Y:").pack()
    y_entry = tk.Entry(dialog)
    y_entry.insert(0, "codigo")
    y_entry.pack()
    
    def generate_chart():
        import plotext as plt
        db = SessionLocal()
        try:
            table = table_var.get()
            controller = globals()[f"{table}_controller"]
            data = getattr(controller, f"get_{table}s")(db)
            
            if not data:
                output.insert(tk.END, "No hay datos para graficar\n")
                return
            
            x_labels = [str(getattr(d, x_entry.get())) for d in data]
            y_values = [float(getattr(d, y_entry.get())) for d in data]
            
            plt.title(f"Gráfico de {table}")
            if type_var.get() == "bar":
                plt.bar(x_labels, y_values)
            elif type_var.get() == "line":
                plt.plot(x_labels, y_values)
            plt.show()
            output.insert(tk.END, "Gráfico generado\n")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    tk.Button(dialog, text="Generar", command=generate_chart).pack(pady=10)

# Crear tablas
Base.metadata.create_all(bind=engine)

def run_auth_menu():
    print("\n--- Gestión de Usuarios ---")
    print("1. Crear usuario")
    print("2. Login")
    print("3. Listar usuarios")
    print("4. Actualizar usuario")
    print("5. Eliminar usuario")
    
    choice = input("Seleccione: ").strip()
    db = SessionLocal()
    try:
        if choice == "1":
            username = input("Username: ")
            password = input("Password: ")
            role = input("Role: ")
            user = auth_controller.create_user(db, username, password, role)
            print(f"Usuario creado: {user.username}")
        elif choice == "2":
            username = input("Username: ")
            password = input("Password: ")
            user = auth_controller.authenticate_user(db, username, password)
            print("Login OK" if user else "Credenciales inválidas")
        elif choice == "3":
            users = auth_controller.get_users(db)
            for u in users:
                print(f"ID: {u.id}, Username: {u.username}, Role: {u.role}")
        elif choice == "4":
            user_id = int(input("ID del usuario: "))
            username = input("Nuevo username (opcional): ") or None
            password = input("Nueva password (opcional): ") or None
            role = input("Nuevo role (opcional): ") or None
            success = auth_controller.update_user(db, user_id, username, password, role)
            print("Actualizado" if success else "No encontrado")
        elif choice == "5":
            user_id = int(input("ID del usuario: "))
            success = auth_controller.delete_user(db, user_id)
            print("Eliminado" if success else "No encontrado")
    finally:
        db.close()

def run_module_menu(module):
    print(f"\n--- Gestión de {module.upper()} ---")
    print("1. Crear")
    print("2. Leer")
    print("3. Actualizar")
    print("4. Eliminar")
    
    choice = input("Seleccione: ").strip()
    db = SessionLocal()
    try:
        controller = globals()[f"{module}_controller"]
        if choice == "1":
            codigo = int(input("Código: "))
            descripcion = input("Descripción: ")
            item = getattr(controller, f"create_{module}")(db, codigo, descripcion)
            print(f"{module.upper()} creado: {item.id}")
        elif choice == "2":
            item_id = input("ID (opcional): ").strip()
            if item_id:
                item = getattr(controller, f"get_{module}")(db, int(item_id))
                print(f"ID: {item.id}, Código: {item.codigo}, Descripción: {item.descripcion}" if item else "No encontrado")
            else:
                items = getattr(controller, f"get_{module}s")(db)
                for i in items[:10]:
                    print(f"ID: {i.id}, Código: {i.codigo}, Descripción: {i.descripcion}")
        elif choice == "3":
            item_id = int(input("ID: "))
            codigo = input("Nuevo código (opcional): ").strip()
            descripcion = input("Nueva descripción (opcional): ").strip()
            success = getattr(controller, f"update_{module}")(db, item_id, int(codigo) if codigo else None, descripcion or None)
            print("Actualizado" if success else "No encontrado")
        elif choice == "4":
            item_id = int(input("ID: "))
            success = getattr(controller, f"delete_{module}")(db, item_id)
            print("Eliminado" if success else "No encontrado")
    finally:
        db.close()

def run_bajlic_menu():
    print("\n--- Gestión de BAJLIC ---")
    print("1. Crear")
    print("2. Leer")
    print("3. Actualizar")
    print("4. Eliminar")
    
    choice = input("Seleccione: ").strip()
    db = SessionLocal()
    try:
        if choice == "1":
            caso = int(input("Caso: "))
            estado_id = int(input("Estado ID: "))
            asic_id = int(input("ASIC ID: "))
            documento = input("Documento: ")
            apellido1 = input("Apellido 1: ")
            nombres = input("Nombres: ")
            bajlic = bajlic_controller.create_bajlic(db, caso, estado_id, asic_id, documento, apellido1, None, nombres)
            print(f"BAJLIC creado: {bajlic.id}")
        elif choice == "2":
            bajlic_id = input("ID (opcional): ").strip()
            if bajlic_id:
                bajlic = bajlic_controller.get_bajlic(db, int(bajlic_id))
                print(f"ID: {bajlic.id}, Caso: {bajlic.caso}, Nombres: {bajlic.nombres}" if bajlic else "No encontrado")
            else:
                bajlics = bajlic_controller.get_bajlics(db)
                for b in bajlics[:10]:
                    print(f"ID: {b.id}, Caso: {b.caso}, Nombres: {b.nombres}")
        elif choice == "3":
            bajlic_id = int(input("ID: "))
            nombres = input("Nuevos nombres (opcional): ").strip() or None
            success = bajlic_controller.update_bajlic(db, bajlic_id, nombres=nombres)
            print("Actualizado" if success else "No encontrado")
        elif choice == "4":
            bajlic_id = int(input("ID: "))
            success = bajlic_controller.delete_bajlic(db, bajlic_id)
            print("Eliminado" if success else "No encontrado")
    finally:
        db.close()

def run_report_menu():
    table = input("Tabla para reporte: ").strip()
    filters = input("Filtros JSON (opcional): ").strip() or "{}"
    db = SessionLocal()
    try:
        rows = generate_report(db, table, json.loads(filters))
        print(f"Total registros: {len(rows)}")
        for row in rows[:10]:
            print(row)
    finally:
        db.close()

def run_export_menu():
    table = input("Tabla a exportar: ").strip()
    format_type = input("Formato (json/excel/word/pdf): ").strip()
    filename = input("Nombre del archivo: ").strip()
    db = SessionLocal()
    try:
        if format_type == "json":
            export_to_json(db, table, filename)
        elif format_type == "excel":
            export_to_excel(db, table, filename)
        elif format_type == "word":
            export_to_word(db, table, filename)
        elif format_type == "pdf":
            export_to_pdf(db, table, filename)
        print(f"Exportado a {filename}")
    finally:
        db.close()

def run_import_menu():
    table = input("Tabla a importar: ").strip()
    filename = input("Archivo JSON: ").strip()
    db = SessionLocal()
    try:
        import_from_json(db, table, filename)
        print(f"Importado desde {filename}")
    finally:
        db.close()

def run_chart_menu():
    table = input("Tabla para gráfico: ").strip()
    chart_type = input("Tipo (bar/line/pie): ").strip()
    x_column = input("Columna X: ").strip()
    y_column = input("Columna Y: ").strip()
    db = SessionLocal()
    try:
        # Similar al chart command
        if table == "asic":
            data = asic_controller.get_asics(db)
        elif table == "estado":
            data = estado_controller.get_estados(db)
        elif table == "curso":
            data = curso_controller.get_cursos(db)
        elif table == "pnf":
            data = pnf_controller.get_pnfs(db)
        elif table == "bajlic":
            data = bajlic_controller.get_bajlics(db)
        
        if not data:
            print("No hay datos")
            return
        
        import plotext as plt
        x_labels = [str(getattr(d, x_column)) for d in data]
        y_values = [float(getattr(d, y_column)) for d in data]
        
        plt.title(f"Gráfico de {table}")
        if chart_type == "bar":
            plt.bar(x_labels, y_values)
        elif chart_type == "line":
            plt.plot(x_labels, y_values)
        plt.show()
    finally:
        db.close()

# Crear tablas
Base.metadata.create_all(bind=engine)

def validate_required_args(args, required_fields):
    """Valida que los campos requeridos estén presentes"""
    missing = [field for field in required_fields if not getattr(args, field, None)]
    if missing:
        print(f"Error: Campos requeridos faltantes: {', '.join(missing)}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="CREBLITRA CLI")
    subparsers = parser.add_subparsers(dest="command", required=False)

    # Autenticación
    auth_parser = subparsers.add_parser("auth")
    auth_parser.add_argument("action", choices=["create", "login", "list", "update", "delete"])
    auth_parser.add_argument("--username")
    auth_parser.add_argument("--password")
    auth_parser.add_argument("--role")
    auth_parser.add_argument("--id", type=int)

    # ASIC
    asic_parser = subparsers.add_parser("asic")
    asic_parser.add_argument("action", choices=["create", "read", "update", "delete"])
    asic_parser.add_argument("--id", type=int)
    asic_parser.add_argument("--codigo", type=int)
    asic_parser.add_argument("--descripcion")

    # ESTADO
    estado_parser = subparsers.add_parser("estado")
    estado_parser.add_argument("action", choices=["create", "read", "update", "delete"])
    estado_parser.add_argument("--id", type=int)
    estado_parser.add_argument("--codigo", type=int)
    estado_parser.add_argument("--descripcion")

    # CURSO
    curso_parser = subparsers.add_parser("curso")
    curso_parser.add_argument("action", choices=["create", "read", "update", "delete"])
    curso_parser.add_argument("--id", type=int)
    curso_parser.add_argument("--codigo", type=int)
    curso_parser.add_argument("--descripcion")

    # PNF
    pnf_parser = subparsers.add_parser("pnf")
    pnf_parser.add_argument("action", choices=["create", "read", "update", "delete"])
    pnf_parser.add_argument("--id", type=int)
    pnf_parser.add_argument("--codigo", type=int)
    pnf_parser.add_argument("--descripcion")

    # BAJLIC
    bajlic_parser = subparsers.add_parser("bajlic")
    bajlic_parser.add_argument("action", choices=["create", "read", "update", "delete"])
    bajlic_parser.add_argument("--id", type=int)
    bajlic_parser.add_argument("--caso", type=int)
    bajlic_parser.add_argument("--estado_id", type=int)
    bajlic_parser.add_argument("--asic_id", type=int)
    bajlic_parser.add_argument("--documento_identidad")
    bajlic_parser.add_argument("--apellido1")
    bajlic_parser.add_argument("--apellido2")
    bajlic_parser.add_argument("--nombres")
    bajlic_parser.add_argument("--causa")
    bajlic_parser.add_argument("--fecha_tram")
    bajlic_parser.add_argument("--an_curso", type=int)
    bajlic_parser.add_argument("--curso_id", type=int)
    bajlic_parser.add_argument("--traslado")
    bajlic_parser.add_argument("--pnf_id", type=int)

    # Reportes
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("table")
    report_parser.add_argument("--filters", type=str, default="{}")

    # Export
    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("table")
    export_parser.add_argument("format", choices=["json", "excel", "word", "pdf"])
    export_parser.add_argument("filename")

    # Import
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("table")
    import_parser.add_argument("filename")

    # Gráficos
    chart_parser = subparsers.add_parser("chart")
    chart_parser.add_argument("table", choices=["asic", "estado", "curso", "pnf", "bajlic"])
    chart_parser.add_argument("--type", choices=["bar", "pie", "line"], default="bar")
    chart_parser.add_argument("--x_column", default="descripcion")
    chart_parser.add_argument("--y_column", default="codigo")

    args = parser.parse_args()
    
    if not args.command:
        launch_gui()
        sys.exit(0)
    
    # Procesar filters como JSON
    if args.command == "report":
        try:
            args.filters = json.loads(args.filters)
        except json.JSONDecodeError:
            print("Error: filters debe ser un JSON válido")
            return

    db = None
    try:
        db = SessionLocal()
        
        if args.command == "auth":
            if args.action == "create":
                if not validate_required_args(args, ['username', 'password', 'role']):
                    return
                user = auth_controller.create_user(db, args.username, args.password, args.role)
                print("Usuario creado:", user.id, user.username, user.role)
                
            elif args.action == "login":
                if not validate_required_args(args, ['username', 'password']):
                    return
                user = auth_controller.authenticate_user(db, args.username, args.password)
                if user:
                    print("Login OK:", user.username, user.role)
                else:
                    print("Credenciales invalidas")
                    
            elif args.action == "list":
                users = auth_controller.get_users(db)
                for user in users:
                    print(f"ID: {user.id}, Username: {user.username}, Role: {user.role}")
                    
            elif args.action == "update":
                if not args.id:
                    print("Error: Se requiere --id para actualizar")
                    return
                updated = auth_controller.update_user(db, args.id, args.username, args.password, args.role)
                print("Actualizado:", updated)
                
            elif args.action == "delete":
                if not args.id:
                    print("Error: Se requiere --id para eliminar")
                    return
                deleted = auth_controller.delete_user(db, args.id)
                print("Eliminado:", deleted)

        elif args.command == "asic":
            if args.action == "create":
                if not validate_required_args(args, ['codigo', 'descripcion']):
                    return
                created = asic_controller.create_asic(db, args.codigo, args.descripcion)
                print("ASIC creado", created.id)
                
            elif args.action == "read":
                if args.id:
                    asic = asic_controller.get_asic(db, args.id)
                    print(f"ID: {asic.id}, Código: {asic.codigo}, Descripción: {asic.descripcion}" if asic else "No encontrado")
                else:
                    asics = asic_controller.get_asics(db)
                    for a in asics:
                        print(f"ID: {a.id}, Código: {a.codigo}, Descripción: {a.descripcion}")
                        
            elif args.action == "update":
                if not args.id:
                    print("Error: Se requiere --id para actualizar")
                    return
                updated = asic_controller.update_asic(db, args.id, args.codigo, args.descripcion)
                print("Actualizado", updated)
                
            elif args.action == "delete":
                if not args.id:
                    print("Error: Se requiere --id para eliminar")
                    return
                deleted = asic_controller.delete_asic(db, args.id)
                print("Eliminado", deleted)

        elif args.command == "estado":
            if args.action == "create":
                if not validate_required_args(args, ['codigo', 'descripcion']):
                    return
                created = estado_controller.create_estado(db, args.codigo, args.descripcion)
                print("ESTADO creado", created.id)
                
            elif args.action == "read":
                if args.id:
                    estado = estado_controller.get_estado(db, args.id)
                    print(f"ID: {estado.id}, Código: {estado.codigo}, Descripción: {estado.descripcion}" if estado else "No encontrado")
                else:
                    estados = estado_controller.get_estados(db)
                    for e in estados:
                        print(f"ID: {e.id}, Código: {e.codigo}, Descripción: {e.descripcion}")
                        
            elif args.action == "update":
                if not args.id:
                    print("Error: Se requiere --id para actualizar")
                    return
                updated = estado_controller.update_estado(db, args.id, args.codigo, args.descripcion)
                print("Actualizado", updated)
                
            elif args.action == "delete":
                if not args.id:
                    print("Error: Se requiere --id para eliminar")
                    return
                deleted = estado_controller.delete_estado(db, args.id)
                print("Eliminado", deleted)

        elif args.command == "curso":
            if args.action == "create":
                if not validate_required_args(args, ['codigo', 'descripcion']):
                    return
                created = curso_controller.create_curso(db, args.codigo, args.descripcion)
                print("CURSO creado", created.id)
                
            elif args.action == "read":
                if args.id:
                    curso = curso_controller.get_curso(db, args.id)
                    print(f"ID: {curso.id}, Código: {curso.codigo}, Descripción: {curso.descripcion}" if curso else "No encontrado")
                else:
                    cursos = curso_controller.get_cursos(db)
                    for c in cursos:
                        print(f"ID: {c.id}, Código: {c.codigo}, Descripción: {c.descripcion}")
                        
            elif args.action == "update":
                if not args.id:
                    print("Error: Se requiere --id para actualizar")
                    return
                updated = curso_controller.update_curso(db, args.id, args.codigo, args.descripcion)
                print("Actualizado", updated)
                
            elif args.action == "delete":
                if not args.id:
                    print("Error: Se requiere --id para eliminar")
                    return
                deleted = curso_controller.delete_curso(db, args.id)
                print("Eliminado", deleted)

        elif args.command == "pnf":
            if args.action == "create":
                if not validate_required_args(args, ['codigo', 'descripcion']):
                    return
                created = pnf_controller.create_pnf(db, args.codigo, args.descripcion)
                print("PNF creado", created.id)
                
            elif args.action == "read":
                if args.id:
                    pnf = pnf_controller.get_pnf(db, args.id)
                    print(f"ID: {pnf.id}, Código: {pnf.codigo}, Descripción: {pnf.descripcion}" if pnf else "No encontrado")
                else:
                    pnfs = pnf_controller.get_pnfs(db)
                    for p in pnfs:
                        print(f"ID: {p.id}, Código: {p.codigo}, Descripción: {p.descripcion}")
                        
            elif args.action == "update":
                if not args.id:
                    print("Error: Se requiere --id para actualizar")
                    return
                updated = pnf_controller.update_pnf(db, args.id, args.codigo, args.descripcion)
                print("Actualizado", updated)
                
            elif args.action == "delete":
                if not args.id:
                    print("Error: Se requiere --id para eliminar")
                    return
                deleted = pnf_controller.delete_pnf(db, args.id)
                print("Eliminado", deleted)

        elif args.command == "bajlic":
            if args.action == "create":
                required_fields = ['caso', 'estado_id', 'asic_id', 'documento_identidad', 
                                  'apellido1', 'nombres']
                if not validate_required_args(args, required_fields):
                    return
                    
                created = bajlic_controller.create_bajlic(
                    db,
                    args.caso,
                    args.estado_id,
                    args.asic_id,
                    args.documento_identidad,
                    args.apellido1,
                    args.apellido2,
                    args.nombres,
                    args.causa,
                    args.fecha_tram,
                    args.an_curso,
                    args.curso_id,
                    args.traslado,
                    args.pnf_id,
                )
                print("BAJLIC creado", created.id)
                
            elif args.action == "read":
                if args.id:
                    bajlic = bajlic_controller.get_bajlic(db, args.id)
                    if bajlic:
                        print(f"ID: {bajlic.id}, Caso: {bajlic.caso}, Nombres: {bajlic.nombres}")
                    else:
                        print("No encontrado")
                else:
                    bajlics = bajlic_controller.get_bajlics(db)
                    for b in bajlics[:10]:  # Limitar a 10 registros
                        print(f"ID: {b.id}, Caso: {b.caso}, Nombres: {b.nombres}")
                    if len(bajlics) > 10:
                        print(f"... y {len(bajlics) - 10} más")
                        
            elif args.action == "update":
                if not args.id:
                    print("Error: Se requiere --id para actualizar")
                    return
                    
                # Filtrar solo campos de BAJLIC que no sean None
                bajlic_fields = ['caso', 'estado_id', 'asic_id', 'documento_identidad', 
                                'apellido1', 'apellido2', 'nombres', 'causa', 'fecha_tram',
                                'an_curso', 'curso_id', 'traslado', 'pnf_id']
                update_data = {k: v for k, v in vars(args).items() 
                              if k in bajlic_fields and v is not None}
                
                if not update_data:
                    print("Error: No se proporcionaron campos para actualizar")
                    return
                    
                updated = bajlic_controller.update_bajlic(db, args.id, **update_data)
                print("Actualizado", updated)
                
            elif args.action == "delete":
                if not args.id:
                    print("Error: Se requiere --id para eliminar")
                    return
                deleted = bajlic_controller.delete_bajlic(db, args.id)
                print("Eliminado", deleted)

        elif args.command == "report":
            rows = generate_report(db, args.table, args.filters)
            count = 0
            for r in rows:
                print(r)
                count += 1
            print(f"\nTotal de registros: {count}")

        elif args.command == "export":
            try:
                if args.format == "json":
                    export_to_json(db, args.table, args.filename)
                elif args.format == "excel":
                    export_to_excel(db, args.table, args.filename)
                elif args.format == "word":
                    export_to_word(db, args.table, args.filename)
                elif args.format == "pdf":
                    export_to_pdf(db, args.table, args.filename)
                print(f"Exportación completada a {args.filename}")
            except Exception as e:
                print(f"Error en exportación: {str(e)}")
                return

        elif args.command == "import":
            try:
                import_from_json(db, args.table, args.filename)
                print(f"Importación completada desde {args.filename}")
            except Exception as e:
                print(f"Error en importación: {str(e)}")
                return

        elif args.command == "chart":
            import plotext as plt
            
            # Obtener datos
            if args.table == "asic":
                data = asic_controller.get_asics(db)
            elif args.table == "estado":
                data = estado_controller.get_estados(db)
            elif args.table == "curso":
                data = curso_controller.get_cursos(db)
            elif args.table == "pnf":
                data = pnf_controller.get_pnfs(db)
            elif args.table == "bajlic":
                data = bajlic_controller.get_bajlics(db)
            
            if not data:
                print("No hay datos para graficar")
                return
            
            # Para simplicidad, graficar y_column vs x_column
            x_labels = [str(getattr(d, args.x_column)) for d in data]
            y_values = [float(getattr(d, args.y_column)) for d in data]
            
            plt.title(f"Gráfico de {args.table} - Tipo: {args.type}")
            if args.type == "bar":
                plt.bar(x_labels, y_values)
            elif args.type == "line":
                plt.plot(x_labels, y_values)
            elif args.type == "pie":
                # Plotext no tiene pie, usar bar
                plt.bar(x_labels, y_values)
            
            plt.show()

        else:
            print("Comando no reconocido")
            
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        if db:
            db.rollback()
        sys.exit(1)
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main()