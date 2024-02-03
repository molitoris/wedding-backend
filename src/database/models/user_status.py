from enum import Enum


class UserStatus(Enum):
    UNSEEN = 0      # User did not start registration
    UNVERIFIED = 1  # User did registration but did not verify email
    VERIFIED = 2    # User verified email
    DISABLED = 3    # User is disabled due to too many login attempts
    DELETED = 4     # User is deleted
