from bson import ObjectId
from bson.errors import InvalidId
from sanic import Blueprint
from sanic.response import Request, json
from sanic_jwt import inject_user, scoped
from sanic_openapi import doc

from controllers import MBUtil
from controllers.MBAuth import MBAuth
from controllers.MBAuthScope import MBAuthScope
from controllers.MBRequest import MBRequest
from models.MBUser import MBUser
import re

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

user_api = Blueprint("User", url_prefix="/user/")


@doc.summary("Edit user")
@doc.consumes(
    doc.String(name="user_name", description="User name"),
    doc.String(name="user_email", description="User email"),
    doc.String(name="user_password", description="User password"),
    required=False,
)
@user_api.put("/")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def edit_user(request: Request, user: MBUser):
    user_email = request.args.get("user_email")

    if user_email is not None:
        if not EMAIL_REGEX.match(user_email):
            return MBRequest.invalid_user_email(user_email)
    
    user_password = request.args.get("user_password")
    if user_password is not None:
        if not MBUtil.is_a_valid_password(user_password):
            return MBRequest.invalid_user_password(user_password)

    user_name = request.args.get("user_name")

    if user_name is not None:
        if not MBUtil.is_a_valid_name(user_name):
            return MBRequest.response_invalid_params_data({"user_name": user_name})

    new_user = await MBUser.edit_user(
        user,
        user_name,
        user_email,
        await MBAuth.user_password_token(user_password) if user_password is not None else None,
    )

    return json(await MBUser.to_api(new_user))

@doc.summary("Create user")
@doc.consumes(
    doc.String(name="user_name", description="User name"),
    doc.String(name="user_email", description="User email"),
    doc.String(name="user_password", description="User password"),
    required=False,
)
@user_api.post("/")
async def edit_user(request: Request):
    user_email = request.args.get("user_email")

    if not EMAIL_REGEX.match(user_email):
        return MBRequest.invalid_user_email(user_email)
    
    user_password = request.args.get("user_password")
    if not MBUtil.is_a_valid_password(user_password):
        return MBRequest.invalid_user_password(user_password)

    user = await MBUser.find_one({"user_email": user_email})
    if user is not None:
        return MBRequest.invalid_user_email("user already exists")

    user_name = request.args.get("user_name")
    if not MBUtil.is_a_valid_name(user_name):
        return MBRequest.response_invalid_params_data({"user_name": user_name})
    user = await MBUser.create_user(user_name, user_email, await MBAuth.user_password_token(user_password))

    return json(await MBUser.to_api(user))

@doc.summary("Get user info")
@user_api.get("/")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def get_user(request: Request, user: MBUser):
    return json(await MBUser.to_api(user))