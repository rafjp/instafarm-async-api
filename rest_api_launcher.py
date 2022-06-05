from sanic import Sanic
from sanic_openapi import swagger_blueprint
from views.MBUserView import user_api
from views.MBMessageView import message_api
from views.MBItemView import item_api
from views.MBCommodityView import commodity_api
from views.MBFarmFieldView import farm_field_api

from controllers.MBMongo import MBMongo

app = Sanic("coup_async_api")
app.blueprint(swagger_blueprint)
app.blueprint(user_api)
app.blueprint(message_api)
app.blueprint(item_api)
app.blueprint(commodity_api)
app.blueprint(farm_field_api)


@app.before_server_start
async def setup(_, __):
    MBMongo.connect()


if __name__ == '__main__':
    app.run(port=8000)
