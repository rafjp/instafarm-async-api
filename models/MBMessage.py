from bson import ObjectId

from controllers.MBMongo import MBMongo
from umongo import fields
from models.MBDocument import MBDocument


@MBMongo.instance.register
class MBMessage(MBDocument):
    class Meta:
        collection_name = "mb_message"

    def __init__(self, *args, **kwargs):
        super(MBMessage, self).__init__(*args, **kwargs)

    """
        The user_id_own is the user who can make a request to see messages sent to him
    """
    user_id_own = fields.ObjectId()
    from_channel = fields.StrField()
    from_user_name = fields.StrField()
    message = fields.StrField()

    @staticmethod
    def register_message(user_id_own: ObjectId, from_channel: str, from_user_name: str, message: str):
        message_channel: MBMessage = MBMessage()
        message_channel.user_id_own = user_id_own
        message_channel.from_channel = from_channel
        message_channel.message = message
        message_channel.from_user_name = from_user_name
        return message_channel
