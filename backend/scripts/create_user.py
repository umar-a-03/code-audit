"""Script to create or update a user with password."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.config import get_settings
from app.adapters.persistence.base import async_engine, get_async_session
from app.core.security import get_password_hash
from app.adapters.persistence.models.client import Client


async def create_or_update_user(email: str, password: str, name: str = None):
    """Create a new user or update password for existing user."""
    settings = get_settings()
    print(f"Database URL: {settings.DATABASE_URL}\n")

    async with async_engine.begin() as conn:
        # Check if user exists
        result = await conn.execute(select(Client).where(Client.email == email))
        existing_client = result.scalar_one_or_none()

        password_hash = get_password_hash(password)

        if existing_client:
            # Update existing user
            print(f"{'='*60}")
            print(f"Updating existing user: {email}")
            print(f"{'='*60}")
            await conn.execute(
                select(Client).where(Client.email == email).with_for_update()
            )
            existing_client.password_hash = password_hash
            existing_client.is_active = True
            if name:
                existing_client.name = name
            await conn.flush()
            print(f"✓ Password updated for user: {email}")
            print(f"✓ User is active")
        else:
            # Create new user
            print(f"{'='*60}")
            print(f"Creating new user: {email}")
            print(f"{'='*60}")
            new_client = Client(
                email=email,
                name=name or email.split("@")[0],
                password_hash=password_hash,
                is_active=True,
            )
            conn.add(new_client)
            await conn.flush()
            print(f"✓ User created: {email}")
            print(f"✓ Password set")
            print(f"✓ User is active")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_user.py <email> <password> [name]")
        print("Example: python create_user.py chandru003.in@gmail.com chandru123 \"Chandru\"")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else None

    asyncio.run(create_or_update_user(email, password, name))
