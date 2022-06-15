from bson import ObjectId
from sanic_jwt import initialize, exceptions
import bcrypt

from models.MBUser import MBUser


class MBAuth:
    @staticmethod
    def setup(app):
        initialize(
            app,
            MBAuth.authenticate,
            add_scopes_to_payload=MBAuth.add_user_scope_payload,
            retrieve_user=MBAuth.retrieve_user,
            blueprint_name="Auth",
            secret="4312df96-ea96-4046-a355-7138c58cc6a2"
        )

    @staticmethod
    async def user_password_token(user_password: str):
        if len(user_password) < 8:
            raise exceptions.AuthenticationFailed(
                "Password must be at least 8 characters long"
            )
        return bcrypt.hashpw(user_password.encode(), bcrypt.gensalt())

    @staticmethod
    async def verify_user_password(user_password: str, hashed_password: str):
        return bcrypt.checkpw(user_password.encode(), hashed_password.encode())

    @staticmethod
    async def retrieve_user(request, payload, *args, **kwargs):
        if not payload:
            return None
        user_id = payload.get("user_id", None)
        return await MBUser.find_one({"id": ObjectId(user_id)})

    @staticmethod
    async def add_user_scope_payload(user, *args, **kwargs):
        return user["scopes"]

    @staticmethod
    async def authenticate(request, *args, **kwargs) -> MBUser:
        try:
            username = request.json.get("email", None)
            password = request.json.get("password", None)
        except Exception as exception:
            raise exceptions.AuthenticationFailed(
                "Missing email or password."
            ) from exception

        if not username or not password:
            raise exceptions.AuthenticationFailed("Missing email or password.")

        user = await MBUser.find_one({"user_email": username})
        if user is None:
            raise exceptions.AuthenticationFailed("User not found.")

        if not await MBAuth.verify_user_password(password, user.user_password):
            raise exceptions.AuthenticationFailed("Password is incorrect.")

        return {"user_id": str(user.id), "scopes": list(user.auth_scopes)}
