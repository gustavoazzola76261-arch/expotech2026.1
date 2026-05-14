from fastapi import HTTPException
from fastapi import status


def require_admin(user):

    if user["role"] != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )

    return True


def require_master(user):

    if user["role"] not in [
        "admin",
        "master"
    ]:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )

    return True