from controllers.MBMongo import MBMongo
from umongo import fields
from models.MBDocument import MBDocument
import hashlib
import random


@MBMongo.instance.register
class MBUser(MBDocument):
    class Meta:
        collection_name = "mb_user"

    def __init__(self, *args, **kwargs):
        super(MBUser, self).__init__(*args, **kwargs)

    name = fields.StrField()
    message_channel = fields.StrField()
    capital = fields.IntegerField()

    @staticmethod
    def __generate_user_message_channel(co_seed: str):
        return hashlib.sha256((co_seed + str(random.uniform(0.0, 1.0))).encode()).hexdigest()

    @staticmethod
    async def create_user(name: str):
        user: MBUser = MBUser()
        user.name = name
        user.message_channel = MBUser.__generate_user_message_channel(user.name)
        await user.commit()
        return user
