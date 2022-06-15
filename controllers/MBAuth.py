from sanic_jwt import initialize, exceptions
import bcrypt

from models.MBUser import MBUser


class MBAuth:
    @staticmethod
    def setup(app):
        initialize(app, MBAuth.authenticate)

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

        return await MBUser.to_api(user)
