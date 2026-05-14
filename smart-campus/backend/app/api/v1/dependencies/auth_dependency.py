from fastapi import HTTPException
from fastapi import status


async def get_current_user():

    fake_user = {
        "id": 1,
        "name": "Admin User",
        "role": "admin"
    }

    if not fake_user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    return fake_user