"""Populate development data: 5 rooms, 3 lamps each, demo users."""

from sqlalchemy import select

from app.core.security import hash_password
from app.database import SessionLocal
from app.models import AirConditioner, Lamp, Room, User, UserRole, UserRoom
from app.models.air_conditioner import DEFAULT_AC_TEMP_C


def main() -> None:
    db = SessionLocal()
    try:
        if db.scalars(select(User).limit(1)).first():
            print("Database already seeded; skipping.")
            return

        rooms: list[Room] = []
        for i in range(1, 6):
            r = Room(name=f"Sala {i}", code=f"S{i}")
            db.add(r)
            rooms.append(r)
        db.flush()

        for r in rooms:
            for slot in range(1, 4):
                db.add(
                    Lamp(
                        room_id=r.id,
                        name=f"Lâmpada {slot}",
                        slot=slot,
                        power_watts=20,
                        is_on=False,
                    )
                )
            db.add(
                AirConditioner(
                    room_id=r.id,
                    name="Ar 1",
                    slot=1,
                    power_watts=1500,
                    is_on=False,
                    target_temp_c=DEFAULT_AC_TEMP_C,
                )
            )

        admin = User(
            email="admin@fecaf.local",
            hashed_password=hash_password("Admin12345!"),
            full_name="Administrador",
            role=UserRole.admin,
        )
        mestre = User(
            email="mestre@fecaf.local",
            hashed_password=hash_password("Mestre12345!"),
            full_name="Mestre",
            role=UserRole.mestre,
        )
        prof = User(
            email="professor@fecaf.local",
            hashed_password=hash_password("Professor123!"),
            full_name="Professor Demo",
            role=UserRole.professor,
        )
        db.add_all([admin, mestre, prof])
        db.flush()

        first_room_id = rooms[0].id
        db.add(UserRoom(user_id=prof.id, room_id=first_room_id))
        db.commit()
        print("Seed completed.")
        print("  admin@fecaf.local / Admin12345!")
        print("  mestre@fecaf.local / Mestre12345!")
        print("  professor@fecaf.local / Professor123! (sala 1)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
