from sanic import Blueprint
from sanic.response import Request, json
from sanic_openapi import doc

from controllers import MBUtil
from controllers.MBRequest import MBRequest
from models.MBUser import MBUser

user_api = Blueprint("User", url_prefix="/user/")


@doc.summary("Create new user")
@doc.consumes(
    doc.String(name="user_name", description="User name", required=True)
)
@user_api.post("register")
async def create_user(request: Request):

    if "user_name" not in request.args:
        return MBRequest.response_invalid_params(["user_name"])

    user_name = request.args.get("user_name")
    if not MBUtil.is_a_valid_name(user_name):
        return MBRequest.response_invalid_params_data({"user_name": user_name})

    user: MBUser = await MBUser.create_user(user_name)
    
    return json({
        "user_id": str(user.id)
    })
