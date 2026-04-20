"""SMTP email service for sending alert notifications."""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

from core.models import Alert

logger = logging.getLogger(__name__)


def _load_template(template_name: str) -> str:
    """Load an HTML email template from the templates directory."""
    path = os.path.join("templates", template_name)
    if not os.path.exists(path):
        logger.warning("Template not found: %s", path)
        return "$mensaje"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _render_template(template_str: str, alert: Alert) -> str:
    """Render a template with alert data."""
    orden = alert.orden
    variables = {
        "mensaje": alert.mensaje,
        "tipo": alert.display_name,
        "severidad": f"{alert.severidad:.1f}",
        "timestamp": alert.timestamp.strftime("%d/%m/%Y %H:%M"),
        "n_om": orden.n_om if orden else "N/A",
        "maquina": orden.maquina if orden else "N/A",
        "actividad": orden.actividad if orden else "N/A",
        "prioridad": orden.prioridad.value if orden else "N/A",
        "fecha_limite": orden.fecha_limite.strftime("%d/%m/%Y") if orden and orden.fecha_limite else "N/A",
        "dias_restantes": str(orden.dias_restantes) if orden else "N/A",
        "estado": orden.estado.value if orden else "N/A",
        "personal": ", ".join(orden.personal) if orden and orden.personal else "Sin asignar",
    }
    try:
        return Template(template_str).safe_substitute(variables)
    except Exception as e:
        logger.error("Error rendering template: %s", e)
        return alert.mensaje


def _connect_smtp(server_addr: str, port: int, use_tls: bool) -> smtplib.SMTP:
    """Create and return an authenticated-ready SMTP connection."""
    if use_tls and port == 465:
        # Implicit SSL (SMTPS)
        server = smtplib.SMTP_SSL(server_addr, port, timeout=15)
        server.ehlo()
    elif use_tls:
        # STARTTLS (typically port 587)
        server = smtplib.SMTP(server_addr, port, timeout=15)
        server.ehlo()
        server.starttls()
        server.ehlo()
    else:
        server = smtplib.SMTP(server_addr, port, timeout=15)
    return server


def send_email(
    smtp_config: dict,
    recipients: list[str],
    subject: str,
    body_html: str,
) -> bool:
    """Send an email via SMTP. Returns True on success."""
    if not recipients:
        logger.warning("No recipients specified, skipping email")
        return False

    server_addr = smtp_config.get("server", "")
    port = int(smtp_config.get("port", 587))
    use_tls = smtp_config.get("use_tls", "true").lower() == "true"
    username = smtp_config.get("username", "")
    password = smtp_config.get("password", "")
    from_name = smtp_config.get("from_name", "Sistema Mantenimiento")
    from_addr = username

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_addr}>"
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    try:
        server = _connect_smtp(server_addr, port, use_tls)
        if username and password:
            server.login(username, password)
        server.sendmail(from_addr, recipients, msg.as_string())
        server.quit()
        logger.info("Email sent to %s: %s", recipients, subject)
        return True
    except Exception as e:
        logger.error("Failed to send email: %s", e)
        return False


def send_alert_email(alert: Alert, smtp_config: dict, recipients: list[str], template_name: str) -> bool:
    """Send an alert email using the specified template."""
    template_str = _load_template(template_name)
    body = _render_template(template_str, alert)
    subject = f"[Mantenimiento ATT] {alert.display_name}: {alert.mensaje[:80]}"
    return send_email(smtp_config, recipients, subject, body)


def test_smtp_connection(smtp_config: dict) -> tuple[bool, str]:
    """Test SMTP connection. Returns (success, message)."""
    server_addr = smtp_config.get("server", "")
    port_str = smtp_config.get("port", "587")
    use_tls = smtp_config.get("use_tls", "true").lower() == "true"
    username = smtp_config.get("username", "")
    password = smtp_config.get("password", "")

    if not server_addr:
        return False, "El campo Servidor esta vacio."

    try:
        port = int(port_str)
    except ValueError:
        return False, f"Puerto invalido: '{port_str}'"

    ssl_mode = "SSL (puerto 465)" if port == 465 else "STARTTLS"
    try:
        server = _connect_smtp(server_addr, port, use_tls)
        if username and password:
            server.login(username, password)
        server.quit()
        return True, f"Conexion SMTP exitosa ({ssl_mode})"
    except smtplib.SMTPAuthenticationError:
        return False, "Autenticacion fallida. Verifique usuario y contrasena."
    except (TimeoutError, OSError) as e:
        hint = (
            " Verifique que el servidor y puerto sean correctos, y que el firewall permita la conexion."
        )
        return False, f"Error de conexion: {e}.{hint}"
    except Exception as e:
        return False, f"Error de conexion: {e}"
