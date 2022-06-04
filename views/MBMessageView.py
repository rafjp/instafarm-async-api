from bson import ObjectId
from bson.errors import InvalidId
from sanic import Blueprint, json
from sanic.response import Request
from sanic_openapi import doc

from controllers.protocol import PMessage
from models.MBUser import MBUser
from controllers.MBRequest import MBRequest

message_api = Blueprint("Message", url_prefix="/message/")


@doc.summary("Send new message")
@doc.consumes(
    doc.String(name="from_user_id", description="User id (from)", required=True),
    doc.String(name="to_message_channel", description="User message channel (to)", required=True),
    doc.String(name="message", description="Message to send", required=True)
)
@message_api.post("send")
async def send_message(request: Request):

    if "from_user_id" not in request.args:
        return MBRequest.response_invalid_params(["from_user_id"])

    if "to_message_channel" not in request.args:
        return MBRequest.response_invalid_params(["to_message_channel"])

    if "message" not in request.args:
        return MBRequest.response_invalid_params(["message"])


    from_user_id = request.args.get("from_user_id")
    if from_user_id is None:
        return MBRequest.invalid_user_id(from_user_id)
    
    user_from: MBUser

    try:
        user_from = await MBUser.find_one({'id': ObjectId(from_user_id)})
    except InvalidId:
        return MBRequest.invalid_user_id(from_user_id)

    if user_from is None:
        return MBRequest.invalid_user_id(from_user_id)

    user_to: MBUser = await MBUser.find_one({'message_channel': request.args.get("to_message_channel")})
    if user_to is None:
        return MBRequest.invalid_user_channel_id(request.args.get("to_message_channel"))

    return json(await PMessage.send_message(user_from=user_from, user_to=user_to, message=request.args.get("message")))


@doc.summary("Get user messages")
@doc.consumes(
    doc.String(name="user_id", description="User id"),
    location="path",
    required=True
)
@message_api.get("/<user_id>")
async def get_massages(request: Request, user_id: str):

    user: MBUser
    try:
        user = await MBUser.find_one({'id': ObjectId(user_id)})
    except InvalidId:
        return MBRequest.invalid_user_id(user_id)

    if user is None:
        return MBRequest.invalid_user_id(user_id)

    return json(await PMessage.get_massages(user=user))


@doc.summary("Delete all messages for the user")
@doc.consumes(
    doc.String(name="user_id", description="User id"),
    location="path",
    required=True
)
@message_api.delete("clean/<user_id>")
async def remove_message(request: Request, user_id: str):

    user: MBUser
    try:
        user = await MBUser.find_one({'id': ObjectId(user_id)})
    except InvalidId:
        return MBRequest.invalid_user_id(user_id)

    if user is None:
        return MBRequest.invalid_user_id(user_id)

    return json(await PMessage.clean_messages(user=user))
