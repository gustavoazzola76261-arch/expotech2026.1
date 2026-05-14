from enum import Enum


class UserRole(str, Enum):
    PROFESSOR = "professor"
    MASTER = "master"
    ADMIN = "admin"