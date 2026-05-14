from app.core.security.password_handler import (
    hash_password,
    verify_password
)

from app.core.security.jwt_handler import (
    create_access_token
)


password = "123456"

hashed = hash_password(password)

print("HASH:")
print(hashed)

print("\nPASSWORD VALID:")

print(
    verify_password(
        password,
        hashed
    )
)

token = create_access_token(
    {
        "sub": "1",
        "role": "admin"
    }
)

print("\nJWT TOKEN:")
print(token)