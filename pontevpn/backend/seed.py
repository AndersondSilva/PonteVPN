import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Import models from app
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models import Server, PlanType, Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/pontevpn")

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def seed():
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if servers already exist
        from sqlalchemy import select
        result = await session.execute(select(Server))
        if result.scalars().first():
            print("Database already seeded.")
            return

        servers = [
            Server(
                name="São Paulo - Prime",
                country="Brasil",
                country_code="BR",
                city="São Paulo",
                ip="1.1.1.1", # Mock IP
                wg_public_key="SERVER_PUBLIC_KEY_BR_MOCK",
                agent_url="http://1.1.1.1:8080",
                agent_secret="secret_ponte_br_2026",
                min_plan=PlanType.free,
                capacity=1000
            ),
            Server(
                name="Lisboa - Tejo",
                country="Portugal",
                country_code="PT",
                city="Lisboa",
                ip="2.2.2.2", # Mock IP
                wg_public_key="SERVER_PUBLIC_KEY_PT_MOCK",
                agent_url="http://2.2.2.2:8080",
                agent_secret="secret_ponte_pt_2026",
                min_plan=PlanType.pro,
                capacity=500
            ),
            Server(
                name="Frankfurt - Rhine",
                country="Alemanha",
                country_code="DE",
                city="Frankfurt",
                ip="3.3.3.3", # Mock IP
                wg_public_key="SERVER_PUBLIC_KEY_DE_MOCK",
                agent_url="http://3.3.3.3:8080",
                agent_secret="secret_ponte_de_2026",
                min_plan=PlanType.pro,
                capacity=800
            ),
             Server(
                name="New York - Liberty",
                country="EUA",
                country_code="US",
                city="New York",
                ip="4.4.4.4", # Mock IP
                wg_public_key="SERVER_PUBLIC_KEY_US_MOCK",
                agent_url="http://4.4.4.4:8080",
                agent_secret="secret_ponte_us_2026",
                min_plan=PlanType.pro,
                capacity=1000
            )
        ]

        session.add_all(servers)
        await session.commit()
        print("✅ Database seeded with initial servers.")

if __name__ == "__main__":
    asyncio.run(seed())
