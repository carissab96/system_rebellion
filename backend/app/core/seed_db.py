from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.core import config
from app.core.database import AsyncSessionLocal
from app.models import (
    SystemAlert,
    SystemConfiguration,
    SystemMetrics,
    OptimizationProfile,
    TuningHistory,
    User,
    UserProfile,
)

async def seed_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == "admin@example.com"))
        user = result.scalars().first()
        if not user:
            user = User(email="admin@example.com", is_active=True)
            session.add(user)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()

async def seed_user_profiles():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserProfile).where(UserProfile.user_id == 1))
        user_profile = result.scalars().first()
        if not user_profile:
            user_profile = UserProfile(user_id=1)
            session.add(user_profile)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()

async def seed_system_metrics():
    async with AsyncSessionLocal() as session:
        # Just insert a test metric if table is empty
        result = await session.execute(select(SystemMetrics))
        system_metric = result.scalars().first()
        if not system_metric:
            system_metric = SystemMetrics(cpu_usage=0.5, memory_usage=0.6, disk_usage=0.7, network_usage={}, process_count=42)
            session.add(system_metric)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()

async def seed_system_alerts():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(SystemAlert).where(SystemAlert.title == "High CPU Usage"))
        system_alert = result.scalars().first()
        if not system_alert:
            system_alert = SystemAlert(user_id="admin", title="High CPU Usage", message="CPU usage exceeded 80%", severity="HIGH")
            session.add(system_alert)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()

async def seed_tuning_history():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(TuningHistory).where(TuningHistory.parameter == "tuning_param"))
        tuning_history = result.scalars().first()
        if not tuning_history:
            tuning_history = TuningHistory(user_id=1, parameter="tuning_param", old_value="old", new_value="new", success=True)
            session.add(tuning_history)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()

async def seed_system_configuration():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(SystemConfiguration).where(SystemConfiguration.name == "Default Config"))
        system_configuration = result.scalars().first()
        if not system_configuration:
            system_configuration = SystemConfiguration(user_id="admin", name="Default Config", config_type="system", settings={"param1": 1, "param2": 2})
            session.add(system_configuration)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()

async def seed_optimization_profile():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(OptimizationProfile).where(OptimizationProfile.name == "Default Profile"))
        optimization_profile = result.scalars().first()
        if not optimization_profile:
            optimization_profile = OptimizationProfile(user_id="admin", name="Default Profile", settings={"param1": 1, "param2": 2})
            session.add(optimization_profile)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()

async def seed_db():
    await seed_users()
    await seed_user_profiles()
    await seed_system_metrics()
    await seed_system_alerts()
    await seed_tuning_history()
    await seed_system_configuration()
    await seed_optimization_profile()

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_db())