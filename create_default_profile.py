#!/usr/bin/env python3
import asyncio
import sys
import os
import json

# Add the backend directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from app.models.system import OptimizationProfile
from app.models.user import User
from app.core.config import settings

async def create_default_profile():
    print("Starting default profile creation script...")
    
    # Create engine and session
    engine = create_async_engine('sqlite+aiosqlite:///./system_rebellion.db', echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Find a user to associate the profile with
        query = select(User)
        result = await session.execute(query)
        user = result.scalars().first()
        
        if not user:
            print('No user found in the database. Please create a user first.')
            return
            
        print(f"Found user: {user.username} (ID: {user.id})")
        
        # Check if profiles already exist for this user
        query = select(OptimizationProfile).where(OptimizationProfile.user_id == user.id)
        result = await session.execute(query)
        profiles = result.scalars().all()
        
        if profiles:
            print(f'Found {len(profiles)} existing profiles for user {user.username}:')
            for profile in profiles:
                print(f"  - {profile.name} (Active: {profile.is_active})")
        else:
            print('No profiles found, creating default profiles...')
            
            # Create a balanced performance profile
            balanced_profile = OptimizationProfile(
                name='Balanced Performance',
                description='Default profile with balanced settings for performance and power usage',
                settings={
                    'cpu_governor': 'ondemand',
                    'swapiness': 60,
                    'vm_dirty_ratio': 20,
                    'vm_dirty_background_ratio': 10,
                    'cpuThreshold': 80,
                    'memoryThreshold': 80,
                    'diskThreshold': 90,
                    'networkThreshold': 70,
                    'enableAutoTuning': True,
                    'cpuPriority': 'medium',
                    'backgroundProcessLimit': 25,
                    'memoryAllocation': {
                        'applications': 70,
                        'systemCache': 30
                    },
                    'diskPerformance': 'balance',
                    'networkOptimization': {
                        'prioritizeStreaming': False,
                        'prioritizeDownloads': False,
                        'lowLatencyMode': False
                    },
                    'powerProfile': 'balanced'
                },
                user_id=user.id,
                is_active=True
            )
            session.add(balanced_profile)
            
            # Create a high performance profile
            high_perf_profile = OptimizationProfile(
                name='High Performance',
                description='Optimized for maximum performance at the cost of power efficiency',
                settings={
                    'cpu_governor': 'performance',
                    'swapiness': 10,
                    'vm_dirty_ratio': 10,
                    'vm_dirty_background_ratio': 5,
                    'cpuThreshold': 90,
                    'memoryThreshold': 85,
                    'diskThreshold': 95,
                    'networkThreshold': 60,
                    'enableAutoTuning': True,
                    'cpuPriority': 'high',
                    'backgroundProcessLimit': 10,
                    'memoryAllocation': {
                        'applications': 85,
                        'systemCache': 15
                    },
                    'diskPerformance': 'speed',
                    'networkOptimization': {
                        'prioritizeStreaming': True,
                        'prioritizeDownloads': True,
                        'lowLatencyMode': True
                    },
                    'powerProfile': 'performance'
                },
                user_id=user.id,
                is_active=False
            )
            session.add(high_perf_profile)
            
            # Create a power saving profile
            power_save_profile = OptimizationProfile(
                name='Power Saving',
                description='Optimized for maximum battery life and power efficiency',
                settings={
                    'cpu_governor': 'powersave',
                    'swapiness': 80,
                    'vm_dirty_ratio': 30,
                    'vm_dirty_background_ratio': 20,
                    'cpuThreshold': 60,
                    'memoryThreshold': 70,
                    'diskThreshold': 80,
                    'networkThreshold': 50,
                    'enableAutoTuning': True,
                    'cpuPriority': 'low',
                    'backgroundProcessLimit': 50,
                    'memoryAllocation': {
                        'applications': 60,
                        'systemCache': 40
                    },
                    'diskPerformance': 'powersave',
                    'networkOptimization': {
                        'prioritizeStreaming': False,
                        'prioritizeDownloads': False,
                        'lowLatencyMode': False
                    },
                    'powerProfile': 'powersave'
                },
                user_id=user.id,
                is_active=False
            )
            session.add(power_save_profile)
            
            # Commit the changes
            await session.commit()
            print('Created default optimization profiles')

if __name__ == "__main__":
    asyncio.run(create_default_profile())
