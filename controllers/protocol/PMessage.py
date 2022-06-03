from pymongo.cursor import Cursor
from models.MBMessage import MBMessage
from models.MBUser import MBUser


async def send_message(user_from: MBUser, user_to: MBUser, message: str) -> dict:
    """
    A user send a message to another using the message channel.
    """

    message: MBMessage = MBMessage.register_message(
        message=message, from_channel=user_from.message_channel,
        user_id_own=user_to.id, from_user_name=user_from.name
    )
    await message.commit()

    return {
        "type": "message",
        "call": "send_message",
        "message_id": str(message.id),
        "at": message.create_at.isoformat()
    }


async def get_massages(user: MBUser):
    """
    Return the user messages.
    """

    message_cursor: Cursor = MBMessage.find({'user_id_own': user.id})
    messages = []

    async for message in message_cursor:
        messages.append({
            "at": message.create_at.isoformat(),
            "contact_message_channel": message.from_channel,
            "contact_name": message.from_user_name,
            "message_id": str(message.id),
            "message": message.message
        })

    return {
        "type": "message",
        "call": "get_massages",
        "user_id": str(user.id),
        "messages": messages
    }


async def clean_messages(user: MBUser):
    """
    Erases all user messages.
    """

    message_cursor: Cursor = MBMessage.find({'user_id_own': user.id})

    count = 0
    async for message in message_cursor:
        await message.delete()
        count += 1

    return {
        "type": "message",
        "call": "clean_messages",
        "message_count": count
    }
