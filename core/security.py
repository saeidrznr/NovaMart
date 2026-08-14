from pwdlib import PasswordHash

passwordHash = PasswordHash.recommended()

def hash_password(password):
    return passwordHash.hash(password)

def verify_password(password, hashed_password):
    return passwordHash.verify(password, hashed_password)