import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_mongodb_connection():
    uri = os.getenv("MONGODB_URL", "mongodb://localhost:27017/as_project")
    db_name = os.getenv("DB_NAME", "as_project")
    
    print(f"Connecting to MongoDB at: {uri}...")
    
    try:
        # Create a client with a short timeout for testing
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        
        # The ismaster command is cheap and does not require auth.
        await client.admin.command('ismaster')
        
        print("SUCCESS: Connection to MongoDB established!")
        
        # List databases to verify access
        databases = await client.list_database_names()
        print(f"Available Databases: {', '.join(databases)}")
        
        # Check if our specific DB exists or can be accessed
        print(f"Target Database: {db_name}")
        
    except Exception as e:
        print(f"ERROR: Could not connect to MongoDB.")
        print(f"Details: {e}")
        print("\nTip: Make sure your MongoDB service is running or check your MONGODB_URL in .env")

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection())
