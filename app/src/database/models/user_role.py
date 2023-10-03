from enum import Enum

class UserRole(Enum):
    GUEST = 1,
    WITNESS = 2,  # Witnesses can be contacted
    ADMIN = 3,