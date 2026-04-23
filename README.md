# CREBLITRA - Sistema de Gestión

Sistema de gestión de datos para CREBLITRA con interfaz CLI y GUI.

## Características

- Gestión completa de usuarios, ASIC, Estado, Curso, PNF y BAJLIC
- Generación de reportes
- Exportación/Importación de datos (JSON, Excel, Word, PDF)
- Gráficos con Plotext
- Interfaz de línea de comandos (CLI)
- Interfaz gráfica de usuario (GUI) para Windows

## Requisitos

- Python 3.8+
- Dependencias: ver `requirements.txt`

## Instalación

1. Clona o copia el proyecto
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Interfaz Gráfica (Windows)

Ejecuta sin argumentos para abrir la interfaz gráfica:
```bash
python main.py
```

La GUI proporciona botones para todas las operaciones principales.

### Interfaz de Línea de Comandos (CLI)

#### Gestión de Usuarios
```bash
# Crear usuario
python main.py auth create --username admin --password 123 --role admin

# Login
python main.py auth login --username admin --password 123

# Listar usuarios
python main.py auth read

# Actualizar usuario
python main.py auth update --id 1 --username newadmin

# Eliminar usuario
python main.py auth delete --id 1
```

#### Gestión de ASIC/Estado/Curso/PNF
```bash
# Crear
python main.py asic create --codigo 123 --descripcion "Descripción"

# Leer todos
python main.py asic read

# Leer específico
python main.py asic read --id 1

# Actualizar
python main.py asic update --id 1 --codigo 456 --descripcion "Nueva desc"

# Eliminar
python main.py asic delete --id 1
```

#### Gestión de BAJLIC
```bash
# Crear
python main.py bajlic create --caso 123 --estado_id 1 --asic_id 1 --documento_identidad 12345678 --apellido1 Perez --nombres Juan

# Leer
python main.py bajlic read

# Actualizar
python main.py bajlic update --id 1 --nombres "Juan Carlos"

# Eliminar
python main.py bajlic delete --id 1
```

#### Reportes
```bash
python main.py report --table bajlic --filters '{"estado_id": 1}'
```

#### Exportar Datos
```bash
python main.py export --table bajlic --format json --filename datos.json
python main.py export --table bajlic --format excel --filename datos.xlsx
```

#### Importar Datos
```bash
python main.py import --table bajlic --filename datos.json
```

#### Gráficos
```bash
python main.py chart --table asic --type bar --x_column descripcion --y_column codigo
```

## Compilación para Windows

Ver `README_COMPILACION.md` para instrucciones detalladas.

## Estructura del Proyecto

- `main.py`: Punto de entrada principal
- `controllers/`: Controladores para cada entidad
- `models/`: Modelos de base de datos
- `database/`: Configuración de base de datos
- `reports/`: Módulos de reportes
- `utils/`: Utilidades de exportación/importación
- `tests/`: Pruebas unitarias

## Base de Datos

Utiliza SQLite (`creblitra.db`). Las tablas se crean automáticamente al ejecutar el programa.

## Desarrollo

Para ejecutar pruebas:
```bash
python -m pytest tests/ -v
```

## Notas

- La interfaz gráfica requiere Windows con Tkinter instalado
- En Linux/Mac, utiliza únicamente la interfaz CLI
- Los gráficos utilizan Plotext para compatibilidad multiplataforma</content>
<parameter name="filePath">/home/ramses/Público/PROYECTOS/CREBLITRA/README.md
