# Guía de Implementación y Configuración
## Sistema de Alarmas de Mantenimiento ATT

---

## Índice

1. [Requisitos del sistema](#1-requisitos-del-sistema)
2. [Instalación en la PC de desarrollo (macOS)](#2-instalación-en-la-pc-de-desarrollo-macos)
3. [Instalación en Windows (producción)](#3-instalación-en-windows-producción)
4. [Configuración inicial](#4-configuración-inicial)
5. [Dashboard Web (pantalla de planta)](#5-dashboard-web-pantalla-de-planta)
6. [Cierre y auto-creación de OM](#6-cierre-y-auto-creación-de-om)
7. [Frecuencias PAMPO](#7-frecuencias-pampo)
8. [Compilar a .exe](#8-compilar-a-exe)
9. [Distribución en la empresa](#9-distribución-en-la-empresa)
10. [Agregar nuevos tipos de alerta](#10-agregar-nuevos-tipos-de-alerta)
11. [Estructura del proyecto](#11-estructura-del-proyecto)
12. [Solución de problemas](#12-solución-de-problemas)
13. [Directorio de personal y asignación de emails](#13-directorio-de-personal-y-asignación-de-emails)

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
flask>=3.0.0
pywin32>=306
```

> **Nota macOS:** `pyodbc` en macOS no puede conectarse a Access (requiere driver ODBC de Microsoft, solo disponible en Windows). `pywin32` directamente no se instala en macOS. Para desarrollo en Mac podés probar la GUI sin conexión real a la DB, o usar una VM Windows.

> **¿Por qué `pywin32`?** El cierre de OM y la creación automática de la siguiente orden no se pueden hacer con pyodbc por un conflicto de marcadores `?` en el nombre de columna `[¿Finalizado?]` de Access. La solución usa ADODB vía `win32com` (parte de `pywin32`).

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

:: Si COM/ADODB falla al cerrar OM, ejecutar el post-install de pywin32:
python -m pywin32_postinstall -install

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

; Puerto:
;   587 → STARTTLS (TLS habilitado)
;   465 → SSL implícito (TLS habilitado)
;   25  → sin cifrado (TLS deshabilitado)
port = 587

; Usar TLS (recomendado: true)
; El sistema detecta automáticamente si usar STARTTLS (587) o SSL directo (465)
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

[web]
; Puerto del dashboard web
port = 5000

; 0.0.0.0 = accesible desde otras PC en la red. 127.0.0.1 = solo local.
host = 0.0.0.0

; Cada cuántos segundos auto-actualiza el navegador
refresh_seconds = 60

; Si true, arranca el servidor web automáticamente al abrir la app.
; Si false, hay que iniciarlo con el botón "🌐 Abrir Dashboard Web".
auto_start = false
```

### 4.2 Ruta a la base de datos

La ruta al `.accdb` puede ser:
- **Local:** `C:\Users\usuario\Documents\Orden_MantenimientoV1.accdb`
- **Red compartida:** `\\SERVIDOR\Compartido\Orden_MantenimientoV1.accdb`

Si la DB está en un servidor de red, asegurarse de que la PC tenga permisos de **lectura y escritura** sobre esa carpeta compartida. El sistema puede actualizar los campos PM1, PM2, PM3 de las órdenes directamente desde la vista de Alertas.

---

## 5. Dashboard Web (pantalla de planta)

Además del dashboard de escritorio (Tkinter), el sistema incluye un dashboard web servido por Flask, pensado para mostrarse permanentemente en una TV o monitor industrial vía navegador.

### 5.1 Cómo arrancarlo

**Opción A — Botón en la app (recomendado para uso diario):**

1. Abrir la app Tkinter
2. En el dashboard hacer clic en el botón "🌐 Abrir Dashboard Web" (esquina superior derecha)
3. Se abre el navegador automáticamente en `http://localhost:5000/`

**Opción B — Standalone (sin abrir la app gráfica):**

```cmd
cd C:\ATT_Mantenimiento
python -m web.server
```

**Opción C — Auto-arranque al abrir la app:**

Setear en `config.ini`:
```ini
[web]
auto_start = true
```

### 5.2 Acceder desde otra PC

Si `host = 0.0.0.0` (default), el dashboard es accesible desde cualquier dispositivo en la misma red:

```
http://<ip-de-la-pc-server>:5000
```

Para conocer la IP en Windows: ejecutar `ipconfig` y buscar "Dirección IPv4" (típicamente `192.168.x.x`).

### 5.3 Vistas disponibles

- **Por defecto:** muestra solo la última orden de cada PAMPO (vista de "estado actual de cada equipo")
- **Toggle "Ver todas las ordenes":** link en la esquina superior derecha. Muestra todas las órdenes pendientes
- **Auto-refresh:** cada 60 segundos (configurable en `refresh_seconds`)

### 5.4 Mostrar el dashboard en pantalla externa vía HDMI

Caso típico: conectar la PC de Control de Calidad a una TV/monitor de planta por cable HDMI.

**Pasos:**

1. **Conectar el cable HDMI** entre la PC y la pantalla de planta
2. **Configurar Windows** para usar dos pantallas:
   - Presionar `Win + P` → seleccionar **"Extender"** (recomendado, no "Duplicar")
   - Esto permite que la pantalla de planta sea independiente de la principal
3. **Abrir el dashboard web** desde la app (botón "🌐 Abrir Dashboard Web")
   - Se abre en la pantalla principal
4. **Arrastrar la ventana del navegador** hacia la pantalla de planta
5. **Pantalla completa:** presionar `F11` → el navegador entra en modo full screen y oculta toolbars
6. *(Opcional)* Ajustar resolución/escalado en **Configuración → Sistema → Pantalla** para que sea legible a distancia

**Tips operativos:**

- Dejar la PC y el navegador siempre abiertos. El auto-refresh actualiza solo cada 60s, no hay que tocar nada
- Si la pantalla de planta muestra **"localhost rechazó la conexión"**: significa que el server no está corriendo. Volver a la PC y hacer clic en "🌐 Abrir Dashboard Web"
- Para que el server arranque automáticamente al prender la PC: poner `auto_start = true` en la sección `[web]` de `config.ini`
- Si la pantalla externa se queda en negro tras un rato: deshabilitar suspensión del monitor en **Configuración → Sistema → Energía → Pantalla**
- El dashboard funciona en cualquier navegador moderno (Chrome, Edge, Firefox)

---

## 6. Cierre y auto-creación de OM

### 6.1 Cerrar una orden manualmente

1. En el Dashboard, hacer **doble-clic** sobre la fila de la orden a cerrar
2. En el popup de detalle, presionar el botón verde **"Finalizar Orden"**
3. Confirmar el diálogo
4. La orden queda marcada como completada en Access (`¿Finalizado?` = Sí, `Fecha realización` = hoy)

### 6.2 Auto-creación de la siguiente OM

Si la orden cerrada **era la última registrada para ese ID PAMPO**, el sistema crea automáticamente la siguiente:
- `Fecha` = hoy
- `Realizar el día` = hoy + frecuencia (de `data/pampo_frequencies.json`)
- `Preventivo` / `Correctivo` = mismos valores que la cerrada
- Resto de campos vacíos/default

### 6.3 Diálogo de personal en auto-creación

Si la orden cerrada tenía personal asignado (PM1/PM2/PM3), el sistema abre un popup precargado con esos nombres para que el usuario los confirme/edite para la nueva orden.
- Botón **"Guardar"**: asigna el personal a la nueva OM
- Botón **"Omitir"**: la nueva OM queda sin personal

Si la orden cerrada no tenía personal, no se muestra ningún diálogo (la nueva OM queda sin personal sin preguntar).

### 6.4 Limitación técnica — pywin32 obligatorio

El UPDATE para cerrar una orden referencia la columna `[¿Finalizado?]` que tiene caracteres `¿` y `?`. El driver Access ODBC y pyodbc cuentan estos caracteres distinto como marcadores de parámetro, generando un conflicto irresoluble. Por eso, `close_order()` y `create_order()` usan ADODB vía `win32com.client` (de la librería `pywin32`), que envía el SQL como string puro sin procesamiento de marcadores.

Si al cerrar una orden aparece el error `"pywin32 no instalado"`, ejecutar:
```cmd
pip install pywin32
```

---

## 7. Frecuencias PAMPO

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

## 8. Compilar a .exe

Para distribuir sin necesidad de instalar Python en cada PC.

### 8.1 Instalar PyInstaller

```cmd
pip install pyinstaller
```

### 8.2 Compilar (desde Windows)

```cmd
cd C:\ATT_Mantenimiento

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "ATT_Mantenimiento" ^
  --add-data "templates;templates" ^
  --add-data "data;data" ^
  --add-data "web/templates;web/templates" ^
  --hidden-import "win32com.client" ^
  main.py
```

**Flags explicados:**
- `--onefile`: un único `.exe` (más fácil de distribuir)
- `--windowed`: sin ventana de consola al ejecutar
- `--name`: nombre del ejecutable resultante
- `--add-data`: incluye las carpetas `templates/` y `data/` dentro del exe

### 8.3 Resultado

El `.exe` se genera en `dist/ATT_Mantenimiento.exe`.

> **Importante:** El `config.ini` y los archivos de `data/` deben estar en la **misma carpeta que el .exe** para que sean editables. Si se incluyen dentro del exe con `--add-data`, se extraen a una carpeta temporal y los cambios no se guardan entre sesiones.

### 8.4 Estructura recomendada para distribución

```
ATT_Mantenimiento/           ← carpeta que se copia a cada PC
├── ATT_Mantenimiento.exe    ← ejecutable compilado
├── config.ini               ← configuración (editable)
├── data/
│   ├── pampo_frequencies.json
│   ├── vehicle_mileage.json
│   ├── alert_log.json
│   └── personal_directory.json  ← directorio nombre→email del personal
└── templates/
    ├── overdue_alert.html
    ├── upcoming_alert.html
    └── vehicle_request.html
```

---

## 9. Distribución en la empresa

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

## 10. Agregar nuevos tipos de alerta

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
    registry.register(SinObservacionesEvaluator())  # ← nueva línea
    return registry
```

Eso es todo. El nuevo evaluador aparecerá automáticamente en la vista de Alertas y en los envíos automáticos.

---

## 11. Estructura del proyecto

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
│   ├── database.py              # Conexión pyodbc a Access (lectura/escritura)
│   ├── urgency.py               # Cálculo de estado y severidad
│   ├── alerts.py                # Sistema de alertas extensible
│   ├── email_service.py         # Envío SMTP (STARTTLS y SSL)
│   └── personal_directory.py   # Directorio nombre→email del personal
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
├── web/                          # Dashboard web (Flask) para pantalla de planta
│   ├── __init__.py
│   ├── server.py                 # Servidor Flask + rutas / y /api/orders
│   └── templates/
│       └── dashboard.html        # Template Jinja2 — auto-refresh 60s, tema oscuro
│
├── data/                            # Datos locales (NO son la DB Access)
│   ├── pampo_frequencies.json       # Frecuencias por ID PAMPO
│   ├── vehicle_mileage.json         # Registros de kilometraje
│   ├── alert_log.json               # Historial de alertas enviadas
│   └── personal_directory.json      # Directorio nombre→email del personal
│
└── docs/
    ├── guia_usuario.pdf
    ├── guia_implementacion.md   # Este archivo
    └── generar_guia_usuario.py  # Script para regenerar el PDF
```

### Flujo de datos

```
Archivo .accdb (Access)
        ↓↑  (lectura/escritura, pyodbc)
  database.py  →  lista de OrdenMantenimiento
        ↓                         ↑ update_personal() (PM1/PM2/PM3)
  urgency.py   →  calcula estado, fecha_limite, severidad
        ↓
  alerts.py    →  evalúa condiciones, genera lista de Alert
        ↓                    ↓
  gui/dashboard.py      email_service.py
  (muestra tabla)       (envía notificaciones)
                              ↑
                   personal_directory.py
                   (resuelve emails del personal asignado)
```

---

## 12. Solución de problemas

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
- `server`: dirección correcta del servidor SMTP (ej: `mail.empresa.com`)
- `port` y `use_tls`:
  - Puerto **465** + TLS activado → SSL directo (cPanel, algunos proveedores)
  - Puerto **587** + TLS activado → STARTTLS (Gmail, Office 365)
  - Puerto **25** + TLS desactivado → sin cifrado (redes internas)
- `username` y `password`: credenciales de la cuenta de email
- Firewall: la PC debe tener salida al puerto SMTP configurado
- Para verificar conectividad desde CMD: `telnet mail.empresa.com 465`

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

### "localhost rechazó la conexión" al abrir el dashboard web

El servidor Flask no está corriendo. Soluciones:
- Hacer clic en el botón **"🌐 Abrir Dashboard Web"** en la app
- O ejecutar manualmente: `python -m web.server` desde la raíz del proyecto
- O setear `auto_start = true` en `config.ini` → `[web]` para que arranque solo

---

### Error "pywin32 no instalado" al cerrar una OM

```
ERROR: pywin32 no instalado. Ejecute: pip install pywin32
```

**Solución:**
```cmd
pip install pywin32
python -m pywin32_postinstall -install
```

Reiniciar la app después.

---

### "No module named 'web'" al ejecutar `python -m web.server`

El comando se está ejecutando desde la carpeta equivocada. **Solución:**
```cmd
cd C:\ATT_Mantenimiento
python -m web.server
```

Desde la raíz del proyecto (donde está `main.py` y la carpeta `web/`).

---

### El dashboard web no muestra datos / muestra datos viejos

El servidor lee el `.accdb` cada vez que se abre la página. Si los datos no se actualizan:
- Verificar que `[database] path` en `config.ini` apunte al archivo correcto
- Verificar que el navegador no esté cacheando: usar `Ctrl + F5` para forzar refresco
- Verificar que el auto-refresh esté activo (debería recargarse cada 60s)
- Revisar `att_mantenimiento.log` por errores de conexión a la DB

---

### Regenerar el PDF de la guía de usuario

Si se actualiza la guía o se cambia el contenido:

```bash
cd /ruta/al/proyecto
python3 docs/generar_guia_usuario.py
# → genera docs/guia_usuario.pdf
```

---

## 13. Directorio de personal y asignación de emails

### 13.1 Archivo `data/personal_directory.json`

Mapea el nombre de cada técnico con su dirección de email. Se crea automáticamente al guardar desde la app.

```json
{
    "Juan Lopez": "juan@empresa.com",
    "Pedro Gomez": "pedro@empresa.com"
}
```

### 13.2 Gestionar desde la app

1. Ir a **Configuración** → sección **Directorio de Personal**
2. Ingresar nombre y email en los campos inferiores
3. Presionar **"Agregar / Actualizar"** para guardar
4. Para eliminar: seleccionar una fila y presionar **"Eliminar seleccionado"**

### 13.3 Asignar personal a una orden desde Alertas

1. Ir a **Alertas** → presionar **"Evaluar alertas"**
2. Seleccionar una alerta con orden asociada
3. Presionar **"Asignar personal"**
4. En el diálogo, seleccionar PM1/PM2/PM3 de los dropdowns (se autocompletan con los nombres del directorio)
5. Presionar **"Guardar"** — escribe PM1/PM2/PM3 directamente en Access y actualiza la UI

### 13.4 Flujo de destinatarios al enviar una alerta

Cuando se envía una alerta de una orden, los destinatarios son:
1. El grupo base configurado en `config.ini` → `[recipients]` → `mantenimiento`
2. Los emails del personal asignado (PM1/PM2/PM3) resueltos desde `personal_directory.json`

Si un técnico no tiene email registrado en el directorio, simplemente se omite.

### 13.5 Módulo `core/personal_directory.py`

| Función | Descripción |
|---|---|
| `load_directory()` | Carga `data/personal_directory.json`. Retorna `dict[str, str]`. |
| `save_directory(d)` | Guarda el diccionario en el archivo. |
| `get_emails_for(names)` | Recibe lista de nombres, retorna lista de emails registrados. |

---

*Guía de Implementación v1.2 — Mayo 2026*
