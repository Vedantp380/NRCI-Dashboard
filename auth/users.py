import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

users = {
    "admin": {
        "password": hash_password("admin123"),
        "role": "global"
    },
    "india_user": {
        "password": hash_password("india123"),
        "role": "india"
    }
}