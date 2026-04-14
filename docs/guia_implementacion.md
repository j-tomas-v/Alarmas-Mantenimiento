# Guía de Implementación y Configuración
## Sistema de Alarmas de Mantenimiento ATT

---

## Índice

1. [Requisitos del sistema](#1-requisitos-del-sistema)
2. [Instalación en la PC de desarrollo (macOS)](#2-instalación-en-la-pc-de-desarrollo-macos)
3. [Instalación en Windows (producción)](#3-instalación-en-windows-producción)
4. [Configuración inicial](#4-configuración-inicial)
5. [Frecuencias PAMPO](#5-frecuencias-pampo)
6. [Compilar a .exe](#6-compilar-a-exe)
7. [Distribución en la empresa](#7-distribución-en-la-empresa)
8. [Agregar nuevos tipos de alerta](#8-agregar-nuevos-tipos-de-alerta)
9. [Estructura del proyecto](#9-estructura-del-proyecto)
10. [Solución de problemas](#10-solución-de-problemas)

---

## 1. Requisitos del sistema

### PC de desarrollo
- Python 3.10 o superior
- macOS o Windows

### PC destino (Windows, producción)
- Windows 10 u 11
- Python 3.10+ **o** ejecutable `.exe` standalone (no requiere Python)
- **Microsoft Access Database Engine Redistributable** (si no tiene Office instalado)
  - Descargar desde: https://www.microsoft.com/en-us/download/details.aspx?id=54920
  - Instalar la versión que coincida con la arquitectura del sistema (x64 recomendado)

---

## 2. Instalación en la PC de desarrollo (macOS)

### 2.1 Clonar/copiar el proyecto

```bash
# Ubicación del proyecto
cd /Users/tomasvillalon/Documents/Projects/ATT_alarmas_mantenimiento
```

### 2.2 Crear entorno virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.3 Instalar dependencias

```bash
pip install -r requirements.txt
```

Contenido de `requirements.txt`:
```
pyodbc>=4.0.39
schedule>=1.2.0
tkcalendar>=1.6.1
```

> **Nota macOS:** `pyodbc` en macOS no puede conectarse a Access (requiere driver ODBC de Microsoft, solo disponible en Windows). Para desarrollo en Mac podés probar la GUI sin conexión real a la DB, o usar una VM Windows.

### 2.4 Verificar instalación

```bash
python3 -c "import pyodbc, schedule, tkcalendar; print('OK')"
```

---

## 3. Instalación en Windows (producción)

### 3.1 Instalar Python

1. Descargar Python 3.11+ desde https://www.python.org/downloads/
2. Marcar **"Add Python to PATH"** durante la instalación
3. Verificar: abrir CMD y ejecutar `python --version`

### 3.2 Instalar el driver ODBC de Access

Si la PC tiene Microsoft Office instalado, el driver probablemente ya está disponible. Para verificar:

```cmd
python -c "import pyodbc; print([d for d in pyodbc.drivers() if 'Access' in d])"
```

Si el resultado está vacío, instalar el redistribuible:
- Descargar **Microsoft Access Database Engine 2016 Redistributable** (x64)
- Ejecutar el instalador como administrador

### 3.3 Instalar el proyecto

```cmd
:: Crear carpeta en ubicación compartida de red o local
mkdir C:\ATT_Mantenimiento
:: Copiar todo el contenido del proyecto a esa carpeta

:: Instalar dependencias
cd C:\ATT_Mantenimiento
pip install -r requirements.txt

:: Ejecutar
python main.py
```

### 3.4 Crear acceso directo en el escritorio

```cmd
:: Crear un archivo .bat para lanzar fácilmente
echo @echo off > C:\ATT_Mantenimiento\ATT_Mantenimiento.bat
echo cd /d C:\ATT_Mantenimiento >> C:\ATT_Mantenimiento\ATT_Mantenimiento.bat
echo python main.py >> C:\ATT_Mantenimiento\ATT_Mantenimiento.bat
```

Hacer clic derecho en el `.bat` → Crear acceso directo → Mover al escritorio.

---

## 4. Configuración inicial

Al iniciar el sistema por primera vez, hay que configurar los parámetros en la sección **Configuración** de la app, o editar directamente el archivo `config.ini`.

### 4.1 config.ini completo comentado

```ini
[database]
; Ruta completa al archivo .accdb
; En Windows usar barras invertidas dobles o una barra simple
path = C:\Empresa\Base de Datos\Orden_MantenimientoV1.accdb

; Año desde el cual filtrar registros (ignora registros más viejos)
year_from = 2025

[smtp]
; Servidor SMTP de la empresa
server = smtp.tuempresa.com

; Puerto (587 para TLS, 465 para SSL, 25 para sin cifrado)
port = 587

; Usar TLS (recomendado: true)
use_tls = true

; Cuenta de email desde la que se envían las alertas
username = alertas@tuempresa.com

; Contraseña de la cuenta de email
password = tu_contraseña_aqui

; Nombre que aparece como remitente en los emails
from_name = Sistema Mantenimiento ATT

[recipients]
; Destinatarios de alertas de mantenimiento (separar con comas)
mantenimiento = jefe.mant@tuempresa.com, tecnico@tuempresa.com

; Destinatarios para gerencia (mantenimientos críticos)
gerencia = gerente@tuempresa.com

; Conductores de vehículos (reciben solicitudes de km)
conductores = conductor1@tuempresa.com, conductor2@tuempresa.com

[alertas]
; Cada cuántas horas verifica alertas automáticamente (recomendado: 4)
intervalo_check_horas = 4

; Días que deben pasar antes de reenviar la misma alerta (evita spam)
cooldown_dias = 7

; Días de anticipación para alertar sobre mantenimiento próximo
dias_aviso_proximo = 7

; Frecuencia en días usada si un ID PAMPO no tiene frecuencia configurada
frecuencia_default_dias = 30

; Horario laboral en que se envían emails automáticos
horario_inicio = 07:00
horario_fin = 18:00
```

### 4.2 Ruta a la base de datos

La ruta al `.accdb` puede ser:
- **Local:** `C:\Users\usuario\Documents\Orden_MantenimientoV1.accdb`
- **Red compartida:** `\\SERVIDOR\Compartido\Orden_MantenimientoV1.accdb`

Si la DB está en un servidor de red, asegurarse de que la PC tenga permisos de **lectura** sobre esa carpeta compartida.

---

## 5. Frecuencias PAMPO

El archivo `data/pampo_frequencies.json` define cada cuántos días debe realizarse cada actividad. Ya viene pre-cargado con 56 entradas basadas en el PAMPO actual.

### Formato del archivo

```json
{
    "1": {
        "frecuencia_dias": 30,
        "descripcion": "Troqueladora Heidelberg 1 - Engrase y aceite"
    },
    "45": {
        "frecuencia_dias": 7,
        "descripcion": "Vehiculos - Revision tecnica"
    }
}
```

### Editar frecuencias desde la app

1. Ir a **Configuración** → sección **Frecuencias PAMPO**
2. Hacer clic en una fila para seleccionarla
3. Modificar el valor en el campo **"Nueva frecuencia (días)"**
4. Presionar **"Actualizar"**
5. Presionar **"Guardar frecuencias"**

### Editar frecuencias manualmente

Editar `data/pampo_frequencies.json` con cualquier editor de texto. Recordar:
- La clave es el `ID_PAMPO` como string
- `frecuencia_dias` es un entero positivo
- Si un ID no tiene entrada, se usa `frecuencia_default_dias` del `config.ini`

---

## 6. Compilar a .exe

Para distribuir sin necesidad de instalar Python en cada PC.

### 6.1 Instalar PyInstaller

```cmd
pip install pyinstaller
```

### 6.2 Compilar (desde Windows)

```cmd
cd C:\ATT_Mantenimiento

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "ATT_Mantenimiento" ^
  --add-data "templates;templates" ^
  --add-data "data;data" ^
  main.py
```

**Flags explicados:**
- `--onefile`: un único `.exe` (más fácil de distribuir)
- `--windowed`: sin ventana de consola al ejecutar
- `--name`: nombre del ejecutable resultante
- `--add-data`: incluye las carpetas `templates/` y `data/` dentro del exe

### 6.3 Resultado

El `.exe` se genera en `dist/ATT_Mantenimiento.exe`.

> **Importante:** El `config.ini` y los archivos de `data/` deben estar en la **misma carpeta que el .exe** para que sean editables. Si se incluyen dentro del exe con `--add-data`, se extraen a una carpeta temporal y los cambios no se guardan entre sesiones.

### 6.4 Estructura recomendada para distribución

```
ATT_Mantenimiento/           ← carpeta que se copia a cada PC
├── ATT_Mantenimiento.exe    ← ejecutable compilado
├── config.ini               ← configuración (editable)
├── data/
│   ├── pampo_frequencies.json
│   ├── vehicle_mileage.json
│   └── alert_log.json
└── templates/
    ├── overdue_alert.html
    ├── upcoming_alert.html
    └── vehicle_request.html
```

---

## 7. Distribución en la empresa

### Opción A: Carpeta compartida en red (recomendado)

1. Crear carpeta `\\SERVIDOR\Programas\ATT_Mantenimiento\`
2. Copiar el contenido de `dist/` + `config.ini` + `data/` + `templates/`
3. Crear acceso directo en cada escritorio apuntando a `\\SERVIDOR\Programas\ATT_Mantenimiento\ATT_Mantenimiento.exe`

> **Ventaja:** actualizar el sistema en un solo lugar.
> **Desventaja:** requiere conexión de red para ejecutar.

### Opción B: Copia local en cada PC

Copiar toda la carpeta a `C:\ATT_Mantenimiento\` en cada PC y crear acceso directo local.

> **Ventaja:** funciona sin red.
> **Desventaja:** hay que actualizar cada PC por separado.

### Requisitos en cada PC destino

- Windows 10 u 11
- **Microsoft Access Database Engine Redistributable** instalado (o Microsoft Office)
- Acceso de lectura a la carpeta donde está el `.accdb`

---

## 8. Agregar nuevos tipos de alerta

El sistema usa un patrón Strategy + Registry. Agregar un nuevo tipo de alerta requiere solo crear una clase nueva, sin tocar el código existente.

### Ejemplo: alerta de mantenimiento sin observaciones

```python
# En core/alerts.py, agregar esta clase:

class SinObservacionesEvaluator(AlertEvaluator):
    alert_type = "sin_observaciones"
    display_name = "Correctivo sin observaciones"

    def evaluate(self, orders, config):
        alerts = []
        for o in orders:
            if o.correctivo and not o.finalizado and not o.observaciones:
                alerts.append(Alert(
                    tipo=self.alert_type,
                    display_name=self.display_name,
                    orden=o,
                    mensaje=(
                        f"OM #{o.n_om} - {o.maquina}: correctivo sin "
                        f"descripcion de causa de falla"
                    ),
                    severidad=o.severidad,
                ))
        return alerts

    def get_email_template(self):
        return "overdue_alert.html"   # reutiliza template existente
```

Luego registrarla en `create_default_registry()`:

```python
def create_default_registry() -> AlertRegistry:
    registry = AlertRegistry()
    registry.register(OverdueMaintenanceEvaluator())
    registry.register(UpcomingMaintenanceEvaluator())
    registry.register(VehicleMileageRequestEvaluator())
    registry.register(HighPriorityUnassignedEvaluator())
    registry.register(SinObservacionesEvaluator())  # ← nueva línea
    return registry
```

Eso es todo. El nuevo evaluador aparecerá automáticamente en la vista de Alertas y en los envíos automáticos.

---

## 9. Estructura del proyecto

```
ATT_alarmas_mantenimiento/
│
├── main.py                      # Entry point + AppController
├── config.ini                   # Configuración (editar antes de usar)
├── requirements.txt
├── att_mantenimiento.log        # Log de errores (se crea al ejecutar)
│
├── core/
│   ├── models.py                # Dataclasses: OrdenMantenimiento, Alert, etc.
│   ├── database.py              # Conexión pyodbc read-only a Access
│   ├── urgency.py               # Cálculo de estado y severidad
│   ├── alerts.py                # Sistema de alertas extensible
│   └── email_service.py        # Envío SMTP
│
├── gui/
│   ├── app.py                   # Ventana principal y navegación
│   ├── dashboard.py             # Dashboard con tabla color-coded
│   ├── filters.py               # Panel de filtros
│   ├── alerts_view.py           # Vista de alertas
│   ├── vehicle_mileage.py       # Formulario de kilometraje
│   ├── settings_view.py         # Pantalla de configuración
│   ├── styles.py                # Colores y fuentes (editar para cambiar look)
│   └── widgets.py               # Widgets reutilizables
│
├── templates/                   # Templates HTML para emails (editables)
│   ├── overdue_alert.html
│   ├── upcoming_alert.html
│   └── vehicle_request.html
│
├── data/                        # Datos locales (NO son la DB Access)
│   ├── pampo_frequencies.json   # Frecuencias por ID PAMPO
│   ├── vehicle_mileage.json     # Registros de kilometraje
│   └── alert_log.json           # Historial de alertas enviadas
│
└── docs/
    ├── guia_usuario.pdf
    ├── guia_implementacion.md   # Este archivo
    └── generar_guia_usuario.py  # Script para regenerar el PDF
```

### Flujo de datos

```
Archivo .accdb (Access)
        ↓  (read-only, pyodbc)
  database.py  →  lista de OrdenMantenimiento
        ↓
  urgency.py   →  calcula estado, fecha_limite, severidad
        ↓
  alerts.py    →  evalúa condiciones, genera lista de Alert
        ↓                    ↓
  gui/dashboard.py      email_service.py
  (muestra tabla)       (envía notificaciones)
```

---

## 10. Solución de problemas

### Error: "Driver ODBC no encontrado"

```
pyodbc failed: Can't open lib 'Microsoft Access Driver (*.mdb, *.accdb)'
```

**Solución:**
1. Verificar con: `python -c "import pyodbc; print(pyodbc.drivers())"`
2. Si no aparece el driver de Access, instalar **Microsoft Access Database Engine 2016 Redistributable**
3. Reiniciar la PC después de instalar

---

### Error: "Base de datos no encontrada"

La app muestra el mensaje en la barra de estado inferior.

**Solución:**
1. Verificar que la ruta en `config.ini` → `[database]` → `path` sea correcta
2. Si es una ruta de red, verificar que esté accesible: `\\SERVIDOR\Carpeta\archivo.accdb`
3. Configurar desde la app: **Configuración** → **Buscar...** → seleccionar el `.accdb`

---

### Error al enviar emails

El botón "Probar conexión" en Configuración devuelve error.

**Checklist:**
- `server`: dirección correcta del servidor SMTP de la empresa
- `port`: preguntar al área de sistemas (típico: 25, 465 o 587)
- `use_tls`: `true` para puerto 587, `false` para puerto 25
- `username` y `password`: credenciales de la cuenta de email
- Firewall: la PC debe tener salida al puerto SMTP configurado

---

### La tabla del dashboard aparece vacía

**Posibles causas:**
1. El filtro "Estado" está en "Pendientes" pero todos los registros del período están completados → cambiar a "Todos"
2. El `year_from` en `config.ini` excluye todos los registros → reducir el valor
3. La conexión a la DB falló silenciosamente → revisar `att_mantenimiento.log`

---

### Los colores no aparecen en la tabla

Problema conocido con algunos temas de Windows. Verificar que el `ttk` no esté sobreescribiendo los estilos. En `gui/dashboard.py`, la configuración de tags del Treeview se hace en `widgets.py`:

```python
self.tree.tag_configure("vencido", background="#FADBD8")
self.tree.tag_configure("proximo", background="#FEF5E7")
```

Si no funcionan, puede ser necesario cambiar a un tema específico de ttk al inicio en `main.py`:

```python
style = ttk.Style()
style.theme_use("clam")  # o "alt", "default"
```

---

### El .exe no encuentra los templates o data

Al compilar con `--onefile`, PyInstaller extrae los archivos a una carpeta temporal. Para que los archivos de `data/` y `config.ini` sean persistentes, **no incluirlos** en el `--add-data` del exe. En cambio, deben estar **junto al .exe** en la misma carpeta.

Estructura correcta para distribución:
```
carpeta_distribucion/
├── ATT_Mantenimiento.exe   ← compilado sin --add-data para config y data
├── config.ini
├── data/
└── templates/
```

---

### Regenerar el PDF de la guía de usuario

Si se actualiza la guía o se cambia el contenido:

```bash
cd /ruta/al/proyecto
python3 docs/generar_guia_usuario.py
# → genera docs/guia_usuario.pdf
```

---

*Guía de Implementación v1.0 — Abril 2026*
