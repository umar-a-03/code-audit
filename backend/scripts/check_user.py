"""Script to check existing users and debug login issues."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text
from app.config import get_settings
from app.adapters.persistence.base import async_engine
from app.core.security import get_password_hash, verify_password
from app.adapters.persistence.models.client import Client


async def check_users():
    """Check existing users in the database."""
    settings = get_settings()
    print(f"Database URL: {settings.DATABASE_URL}\n")

    async with async_engine.begin() as conn:
        # Check if clients table exists
        result = await conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'clients')")
        )
        table_exists = result.scalar()
        print(f"Clients table exists: {table_exists}")

        if not table_exists:
            print("\n❌ Clients table does not exist. Run migrations first.")
            return

        # Check if password_hash column exists
        result = await conn.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns
                    WHERE table_name = 'clients' AND column_name = 'password_hash'
                )
            """)
        )
        column_exists = result.scalar()
        print(f"password_hash column exists: {column_exists}")

        if not column_exists:
            print("\n⚠️  password_hash column does not exist. Run migration 002.")
            return

        # Query all clients
        result = await conn.execute(select(Client))
        clients = result.scalars().all()

        print(f"\n{'='*60}")
        print(f"Total clients: {len(clients)}")
        print(f"{'='*60}\n")

        for client in clients:
            print(f"ID: {client.id}")
            print(f"Email: {client.email}")
            print(f"Name: {client.name}")
            print(f"Is Active: {client.is_active}")
            print(f"Has password_hash: {'✓' if client.password_hash else '✗'}")
            if client.password_hash:
                print(f"Password hash (truncated): {client.password_hash[:50]}...")
            print(f"OAuth Provider: {client.oauth_provider}")
            print(f"OAuth ID: {client.oauth_id}")
            print("-" * 60)

        # Check for specific email
        target_email = "chandru003.in@gmail.com"
        result = await conn.execute(select(Client).where(Client.email == target_email))
        target_client = result.scalar_one_or_none()

        if target_client:
            print(f"\n{'='*60}")
            print(f"Found target user: {target_email}")
            print(f"{'='*60}")
            print(f"Has password_hash: {'✓' if target_client.password_hash else '✗'}")
            if target_client.password_hash:
                test_password = "chandru123"
                is_valid = verify_password(test_password, target_client.password_hash)
                print(f"Password verification for '{test_password}': {'✓ Valid' if is_valid else '✗ Invalid'}")
            else:
                print("⚠️  No password_hash set. User cannot login with password.")
        else:
            print(f"\n{'='*60}")
            print(f"User not found: {target_email}")
            print(f"{'='*60}")
            print("⚠️  This user does not exist in the database.")
            print("   Register via POST /api/v1/auth/register")


if __name__ == "__main__":
    asyncio.run(check_users())
