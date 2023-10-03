from enum import Enum

class GuestStatus(Enum):
    UNDEFINED = 0   # Guest hasn't registered for event
    REGISTERED = 1  # Guest accepted invitation
    EXCUSED = 2     # Guest rejected invitation
