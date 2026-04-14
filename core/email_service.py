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
        if use_tls:
            server = smtplib.SMTP(server_addr, port, timeout=15)
            server.ehlo()
            server.starttls()
        else:
            server = smtplib.SMTP(server_addr, port, timeout=15)

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
    try:
        server_addr = smtp_config.get("server", "")
        port = int(smtp_config.get("port", 587))
        use_tls = smtp_config.get("use_tls", "true").lower() == "true"
        username = smtp_config.get("username", "")
        password = smtp_config.get("password", "")

        if use_tls:
            server = smtplib.SMTP(server_addr, port, timeout=10)
            server.ehlo()
            server.starttls()
        else:
            server = smtplib.SMTP(server_addr, port, timeout=10)

        if username and password:
            server.login(username, password)

        server.quit()
        return True, "Conexion SMTP exitosa"
    except Exception as e:
        return False, f"Error de conexion: {e}"
