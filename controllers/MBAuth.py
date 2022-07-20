from bson import ObjectId
from sanic_jwt import initialize, exceptions
import bcrypt
from base64 import b64decode
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
            url_prefix="/api/auth",
            secret="4312df96-ea96-4046-a355-7138c58cc6a2",
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
        user = await MBUser.find_one({"id": ObjectId(user_id)})
        return (
            user
            if request.raw_url.decode() != "/auth/me"
            else (await MBUser.to_api(user))
        )

    @staticmethod
    async def add_user_scope_payload(user, *args, **kwargs):
        return user["scopes"]

    @staticmethod
    async def authenticate(request, *args, **kwargs) -> MBUser:
        auth_base64 = request.headers.get("Authorization", None)

        username: str
        password: str

        try:
            if auth_base64 is not None:
                auth_type, auth_token = auth_base64.split(" ")
                if auth_type != "Basic":
                    raise exceptions.AuthenticationFailed(
                        "Invalid authorization type, must be Basic"
                    )
                username, password = b64decode(auth_token).decode().split(":")
            else:
                username = request.json.get("email", None)
                password = request.json.get("password", None)
        except Exception as exception:
            raise exceptions.AuthenticationFailed(
                "Invalid authorization header, must be Basic <base64(username:password)>"
            ) from exception

        if username is None or password is None:
            raise exceptions.AuthenticationFailed("Missing email or password.")

        if not username or not password:
            raise exceptions.AuthenticationFailed("Missing email or password.")

        user = await MBUser.find_one({"user_email": username})
        if user is None:
            raise exceptions.AuthenticationFailed("User not found.")

        if not await MBAuth.verify_user_password(password, user.user_password):
            raise exceptions.AuthenticationFailed("Password is incorrect.")

        return {"user_id": str(user.id), "scopes": list(user.auth_scopes)}
