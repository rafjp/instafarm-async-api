from urllib.parse import quote_plus

import motor.motor_asyncio
from MBDefine import UserSettings
from umongo.frameworks import MotorAsyncIOInstance


class MBMongo:
    instance = MotorAsyncIOInstance()
    mongo_client = None
    db = None

    @staticmethod
    def connect():
        host = f"{UserSettings.INSTAFARM_MONGO_IP}:{UserSettings.INSTAFARM_MONGO_PORT}"
        user = f"{quote_plus(UserSettings.INSTAFARM_MONGO_USER)}:{quote_plus(UserSettings.INSTAFARM_MONGO_PASS)}"
        url = f"mongodb://{user}@{host}/admin"
        MBMongo.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(url)
        MBMongo.db = MBMongo.mongo_client[UserSettings.INSTAFARM_MONGO_DB_NAME]
        MBMongo.instance.set_db(MBMongo.db)
