import enum


class UserRole(str, enum.Enum):
    professor = "professor"
    mestre = "mestre"
    admin = "admin"


class LampAction(str, enum.Enum):
    on = "on"
    off = "off"
