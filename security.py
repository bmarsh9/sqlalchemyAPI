from password_strength import PasswordPolicy
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],

    ## pbkdf2_sha256__rounds = 29000,
    )

policy = PasswordPolicy.from_names(
    length=10,  # min length: 8
    uppercase=1,  # need min. 2 uppercase letters
    numbers=1,  # need min. 2 digits
    special=1,  # need min. 2 special characters
    nonletters=2,  # need min. 2 non-letter characters (digits, specials, anything)
)
