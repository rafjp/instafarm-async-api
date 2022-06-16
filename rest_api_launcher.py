from sanic import Blueprint, Sanic
from sanic_openapi import swagger_blueprint
from MBDefine import SANIC_HOST
from controllers.MBAuth import MBAuth
from views.MBUserView import user_api
from views.MBMessageView import message_api
from views.MBItemView import item_api
from views.MBCommodityView import commodity_api
from views.MBFarmFieldView import farm_field_api
from controllers.MBMongo import MBMongo

app = Sanic("coup_async_api")

app.config["API_TITLE"] = "Instafarm API"
app.config["API_CONTACT_EMAIL"] = "rrafaelljob@gmail.com"
app.config["API_SECURITY"] = [{"OAuth2": []}]
app.config["API_SECURITY_DEFINITIONS"] = {
    "OAuth2": {
        "type": "oauth2",
        "flow": "application",
        "tokenUrl": f"{SANIC_HOST}/auth",
        "name": "email",
    }
}

group = Blueprint.group(
    user_api,
    message_api,
    item_api,
    commodity_api,
    farm_field_api,
    url_prefix="/api/"
)


app.blueprint(swagger_blueprint)
app.blueprint(group)


@app.before_server_start
async def setup(_, __):
    MBMongo.connect()


def expose_routers():
    print("Exposing routers...")
    for route in app.router.routes_all:
        print("/".join(route))


if __name__ == '__main__':
    MBAuth.setup(app)
    app.run(port=8383)
