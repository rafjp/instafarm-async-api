from MBDefine import USER_BASE_CAPITAL
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
    capital = fields.FloatField()
    user_email = fields.StrField()
    user_password = fields.StrField()
    auth_scopes = fields.ListField(fields.StrField())

    @staticmethod
    def __generate_user_message_channel(co_seed: str):
        return hashlib.sha256(
            (co_seed + str(random.uniform(0.0, 1.0))).encode()
        ).hexdigest()

    @staticmethod
    async def create_user(name: str, user_email: str, user_password: str):
        user: MBUser = MBUser()
        user.name = name
        user.capital = USER_BASE_CAPITAL
        user.message_channel = MBUser.__generate_user_message_channel(user.name)
        if user_email is None:
            return None
        if user_password is None:
            return None
        user.auth_scopes = ["user"]
        return await MBUser.edit_user(user, name, user_email, user_password)

    @staticmethod
    async def edit_user(
        user: "MBUser",
        name: str = None,
        user_email: str = None,
        user_password: str = None,
        capital: float = None,
    ):
        if name is not None:
            user.name = name
        if capital is not None:
            user.capital = capital
        if user_email is not None:
            user.user_email = user_email
        if user_password is not None:
            user.user_password = user_password
        await user.commit()
        return user

    @staticmethod
    async def to_api(user: "MBUser"):
        return {
            "id": str(user.id),
            "name": user.name,
            "message_channel": user.message_channel,
            "capital": user.capital,
            "user_email": user.user_email,
        }
