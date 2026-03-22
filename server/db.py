from psycopg_pool import AsyncConnectionPool
import os 
import os 
from dotenv import load_dotenv
load_dotenv()

async def get_pool():
    db_uri = os.environ.get("DB_URI")

    pool = AsyncConnectionPool(
        conninfo=db_uri,
        max_size=20,
        kwargs={
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        }
    )

    async with pool:  
        yield pool