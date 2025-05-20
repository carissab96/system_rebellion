from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.models.optimization import OptimizationProfile
from app.core.config import settings
from app.core.security import get_password_hash

async def init_db(db: AsyncSession) -> None:
    # Check if admin user exists
    query = select(User).where(User.email == settings.FIRST_SUPERUSER)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        # Create initial superuser
        user = User(
            email=settings.FIRST_SUPERUSER,
            username=settings.FIRST_SUPERUSER,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            is_superuser=True,
            is_active=True,
            is_verified=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"Created initial superuser: {user.email}")

    # Create default optimization profiles if they don't exist
    default_profiles = [
        {
            "name": "Balanced Performance",
            "description": "Optimized for balanced performance and power usage",
            "settings": {
                "cpu_governor": "ondemand",
                "swapiness": 60,
                "vm_dirty_ratio": 20,
                "vm_dirty_background_ratio": 10
            }
        },
        {
            "name": "High Performance",
            "description": "Optimized for maximum performance",
            "settings": {
                "cpu_governor": "performance",
                "swapiness": 10,
                "vm_dirty_ratio": 10,
                "vm_dirty_background_ratio": 5
            }
        },
        {
            "name": "Power Saving",
            "description": "Optimized for power efficiency",
            "settings": {
                "cpu_governor": "powersave",
                "swapiness": 80,
                "vm_dirty_ratio": 30,
                "vm_dirty_background_ratio": 20
            }
        }
    ]

    for profile_data in default_profiles:
        query = select(OptimizationProfile).where(
            OptimizationProfile.name == profile_data["name"],
            OptimizationProfile.user_id == user.id
        )
        result = await db.execute(query)
        existing_profile = result.scalars().first()

        if not existing_profile:
            profile = OptimizationProfile(
                name=profile_data["name"],
                description=profile_data["description"],
                settings=profile_data["settings"],
                user_id=user.id
            )
            db.add(profile)
            await db.commit()
            print(f"Created default profile: {profile.name}")
