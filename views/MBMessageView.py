from controllers.MBAuthScope import MBAuthScope
from controllers.MBRequest import MBRequest
from controllers.protocol import PMessage
from models.MBUser import MBUser
from sanic import Blueprint, json
from sanic.response import Request
from sanic_jwt import inject_user, scoped
from sanic_openapi import doc

message_api = Blueprint("Message", url_prefix="/message/")


@doc.summary("Send new message")
@doc.consumes(
    doc.String(
        name="to_message_channel",
        description="User message channel (to)",
        required=True,
    ),
    doc.String(name="message", description="Message to send", required=True),
)
@message_api.post("send")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def send_message(request: Request, user: MBUser):
    if "to_message_channel" not in request.args:
        return MBRequest.response_invalid_params(["to_message_channel"])

    if "message" not in request.args:
        return MBRequest.response_invalid_params(["message"])

    user_to: MBUser = await MBUser.find_one(
        {"message_channel": request.args.get("to_message_channel")}
    )
    if user_to is None:
        return MBRequest.invalid_user_channel_id(request.args.get("to_message_channel"))

    return json(
        await PMessage.send_message(
            user_from=user, user_to=user_to, message=request.args.get("message")
        )
    )


@doc.summary("Get user messages")
@message_api.get("/")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def get_massages(request: Request, user: MBUser):
    return json(await PMessage.get_massages(user=user))


@doc.summary("Delete all messages for the user")
@message_api.delete("clean")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def remove_message(request: Request, user: MBUser):
    return json(await PMessage.clean_messages(user=user))
