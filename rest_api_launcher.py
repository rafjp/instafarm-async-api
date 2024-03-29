import os
import sys

from sanic import Blueprint, Sanic
from sanic_openapi import swagger_blueprint

import MBDefine
from controllers.MBAuth import MBAuth
from controllers.MBCors import add_cors_headers
from controllers.MBEnvironment import MBEnvironment
from controllers.MBMongo import MBMongo
from controllers.MBOptions import setup_options
from views.MBCommodityView import commodity_api
from views.MBFarmFieldView import farm_field_api
from views.MBItemView import item_api
from views.MBMessageView import message_api
from views.MBUserView import user_api

app = Sanic("coup_async_api")


@app.before_server_start
async def setup(*args, **kwargs):
    MBMongo.connect()


@app.after_server_start
async def sanic_info(*args, **kwargs):
    print("[MB] Running on: " + str(MBEnvironment.get_env()))
    print("[MB] Host: " + MBDefine.SANIC_HOST)
    print("[MB] Port: " + str(MBDefine.SANIC_PORT))

    if MBDefine.EXPOSE_ROUTERS:
        expose_routers()


def expose_routers():
    print("[MB] Exposing routers...")
    for router in app.router.routes_all:
        if router[0].startswith("swagger"):
            continue
        print("[MB] router -> " + MBDefine.SANIC_HOST + "/" + "/".join(router))


def load_user_settings():
    for key in [
        "INSTAFARM_MONGO_PASS",
        "INSTAFARM_MONGO_IP",
        "INSTAFARM_MONGO_USER",
        "INSTAFARM_MONGO_DB_NAME",
        "INSTAFARM_MONGO_PORT",
    ]:
        if key not in os.environ:
            raise Exception(f"[MB] {key} is not defined in environment variables")

        setattr(MBDefine.UserSettings, key, os.environ[key])


def main():
    MBEnvironment.set_env(MBEnvironment.PRODUCTION)
    load_user_settings()
    if len(sys.argv) > 1:
        if "debug" in sys.argv:
            MBEnvironment.set_env(MBEnvironment.DEVELOPMENT)
            MBDefine.SANIC_HOST = f"http://localhost:{MBDefine.SANIC_PORT}"

        if "routers" in sys.argv:
            MBDefine.EXPOSE_ROUTERS = True

    app.config["API_TITLE"] = "Instafarm API"
    app.config["API_CONTACT_EMAIL"] = "rrafaelljob@gmail.com"
    app.config["API_SECURITY"] = [{"OAuth2": []}]
    app.config["API_SECURITY_DEFINITIONS"] = {
        "OAuth2": {
            "type": "oauth2",
            "flow": "application",
            "tokenUrl": f"{MBDefine.SANIC_HOST}/api/auth",
        }
    }

    group = Blueprint.group(
        user_api,
        message_api,
        item_api,
        commodity_api,
        farm_field_api,
        url_prefix="/api/",
    )

    app.blueprint(swagger_blueprint)
    app.blueprint(group)

    # Add OPTIONS handlers to any route that is missing it
    app.register_listener(setup_options, "before_server_start")

    # Fill in CORS headers
    app.register_middleware(add_cors_headers, "response")

    MBAuth.setup(app)
    app.run(port=MBDefine.SANIC_PORT)


if __name__ == "__main__":
    main()
