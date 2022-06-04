from bson import InvalidDocument, ObjectId
from sanic import Blueprint
from sanic.response import Request, json
from sanic_openapi import doc

from controllers import MBUtil
from controllers.MBRequest import MBRequest
from models.MBUser import MBUser

user_api = Blueprint("User", url_prefix="/user/")


@doc.summary("Create/edit user")
@doc.consumes(
    doc.String(name="user_id", description="User id"),
    doc.Float(name="user_capital", description="User capital"),
    doc.String(name="user_name", description="User name"),
    required=False,
)
@user_api.put("edit")
async def create_user(request: Request):

    user_name = request.args.get("user_name")
    user_capital = request.args.get("user_capital")
    user_id = request.args.get("user_id")

    user: MBUser
    if user_id is not None:
        try:
            user_object_id = ObjectId(user_id)
        except InvalidDocument:
            return MBRequest.invalid_user_id(user_id)

        user = await MBUser.find_one({"id": user_object_id})
        if user is None:
            return MBRequest.invalid_user_id(user_id)

        if user_name is not None:
            if not MBUtil.is_a_valid_name(user_name):
                return MBRequest.response_invalid_params_data({"user_name": user_name})

        user = await MBUser.edit_user(
            user,
            user_name if user_name is not None else None,
            user_capital if user_capital is not None else None,
        )

    else:
        if not MBUtil.is_a_valid_name(user_name):
            return MBRequest.response_invalid_params_data({"user_name": user_name})
        user = await MBUser.create_user(user_name)

    return json(await MBUser.to_api(user))
