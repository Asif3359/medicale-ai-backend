from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.models import PredictionResult, User
from app.config import MONGODB_URL, DATABASE_NAME


class Database:
    """Database connection and initialization"""

    def __init__(self):
        self.client = None
        self.database = None

    async def connect(self):
        """Connect to MongoDB"""
        try:
            # Create motor client
            self.client = AsyncIOMotorClient(MONGODB_URL)
            self.database = self.client[DATABASE_NAME]

            # Initialize beanie with our models
            await init_beanie(
                database=self.database,
                document_models=[PredictionResult, User],
            )

            print(f"✅ Connected to MongoDB: {MONGODB_URL}")
            print(f"✅ Database: {DATABASE_NAME}")

        except Exception as e:
            print(f"❌ Database connection error: {e}")
            raise

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Disconnected from MongoDB")

    async def health_check(self):
        """Check database health"""
        try:
            # Test connection
            await self.database.command("ping")
            return {"status": "healthy", "message": "Database connection successful"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Database error: {e}"}


# Global database instance
db = Database()


