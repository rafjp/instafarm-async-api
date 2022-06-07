from sanic import Blueprint, Sanic
from sanic_openapi import swagger_blueprint
from views.MBUserView import user_api
from views.MBMessageView import message_api
from views.MBItemView import item_api
from views.MBCommodityView import commodity_api
from views.MBFarmFieldView import farm_field_api

from controllers.MBMongo import MBMongo

app = Sanic("coup_async_api")

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


if __name__ == '__main__':
    for route in app.router.routes_all:
            print(route)
    app.run(port=8383)
