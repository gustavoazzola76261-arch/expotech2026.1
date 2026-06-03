import re

# Aceita domínios de desenvolvimento (.local, .test) rejeitados pelo EmailStr do Pydantic.
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", re.IGNORECASE)


def normalize_email(value: str) -> str:
    email = value.strip().lower()
    if not EMAIL_PATTERN.match(email):
        raise ValueError("Formato de e-mail inválido")
    if len(email) > 255:
        raise ValueError("E-mail muito longo")
    return email
