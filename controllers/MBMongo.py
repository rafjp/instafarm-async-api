from urllib.parse import quote_plus
import motor.motor_asyncio
from umongo.frameworks import MotorAsyncIOInstance

from MBDefine import (
    MONGO_IP,
    MONGO_DB_NAME,
    MONGO_PASS,
    MONGO_USER,
    MONGO_PORT
)


class MBMongo:
    instance = MotorAsyncIOInstance()
    mongo_client = None
    db = None

    @staticmethod
    def connect():
        url = f"mongodb://{quote_plus(MONGO_USER)}:{quote_plus(MONGO_PASS)}@{MONGO_IP}:{MONGO_PORT}/admin"
        MBMongo.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(url)
        MBMongo.db = MBMongo.mongo_client[MONGO_DB_NAME]
        MBMongo.instance.set_db(MBMongo.db)
