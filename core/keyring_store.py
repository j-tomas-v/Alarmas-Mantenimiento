"""Secure credential storage using the OS keyring.

Falls back to returning an empty string if keyring is not installed,
so the rest of the app continues working without this dependency.
Install with: pip install keyring
"""

import logging

logger = logging.getLogger(__name__)

_SERVICE = "att_mantenimiento_smtp"


def get_smtp_password(username: str) -> str:
    """Retrieve the SMTP password from the OS keyring."""
    if not username:
        return ""
    try:
        import keyring
        password = keyring.get_password(_SERVICE, username)
        return password or ""
    except ImportError:
        logger.warning("keyring no instalado. Ejecute: pip install keyring")
        return ""
    except Exception as e:
        logger.error("Error leyendo contrasena del keyring: %s", e)
        return ""


def set_smtp_password(username: str, password: str) -> bool:
    """Store the SMTP password in the OS keyring. Returns True on success."""
    if not username:
        return False
    try:
        import keyring
        keyring.set_password(_SERVICE, username, password)
        return True
    except ImportError:
        logger.warning("keyring no instalado. La contrasena se guardara en texto plano.")
        return False
    except Exception as e:
        logger.error("Error guardando contrasena en el keyring: %s", e)
        return False


def keyring_available() -> bool:
    try:
        import keyring  # noqa: F401
        return True
    except ImportError:
        return False
