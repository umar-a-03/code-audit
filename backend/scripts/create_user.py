"""Script to create or update a user with password."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update, insert
from app.config import get_settings
from app.adapters.persistence.session import engine, get_db_session_context
from app.core.security import get_password_hash
from app.adapters.persistence.models.client import Client


async def create_or_update_user(email: str, password: str, name: str = None):
    """Create a new user or update password for existing user."""
    settings = get_settings()
    print(f"Database URL: {settings.DATABASE_URL}\n")

    password_hash = get_password_hash(password)

    async with engine.begin() as conn:
        # Check if user exists
        result = await conn.execute(select(Client).where(Client.email == email))
        existing_client = result.scalar_one_or_none()

        if existing_client:
            # Update existing user
            print(f"{'='*60}")
            print(f"Updating existing user: {email}")
            print(f"{'='*60}")
            await conn.execute(
                update(Client)
                .where(Client.email == email)
                .values(
                    password_hash=password_hash,
                    is_active=True,
                    name=name if name else existing_client.name
                )
            )
            await conn.commit()
            print(f"✓ Password updated for user: {email}")
            print(f"✓ User is active")
        else:
            # Create new user
            print(f"{'='*60}")
            print(f"Creating new user: {email}")
            print(f"{'='*60}")
            await conn.execute(
                insert(Client)
                .values(
                    email=email,
                    name=name or email.split("@")[0],
                    password_hash=password_hash,
                    is_active=True,
                )
            )
            await conn.commit()
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
