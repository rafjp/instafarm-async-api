from bson import ObjectId
from bson.errors import InvalidId
from controllers.MBAuthScope import MBAuthScope
from controllers.MBRequest import MBRequest
from models.MBCommodity import MBCommodity
from models.MBItem import MBItem
from models.MBUser import MBUser
from sanic import Blueprint, json
from sanic.response import Request
from sanic_jwt import inject_user, scoped
from sanic_openapi import doc

commodity_api = Blueprint("Commodities", url_prefix="/commodity/")


@doc.summary("Register/edit commodity")
@doc.consumes(
    doc.String(name="item_id", description="Commodity item"),
    doc.Float(name="quandity", description="Commodity quandity"),
    doc.Float(name="price", description="Commodity price"),
    required=True,
)
@doc.consumes(
    doc.String(name="commodity_id", description="Commodity id"),
    required=False,
)
@commodity_api.put("edit")
@inject_user()
@scoped(MBAuthScope.ADMIN, require_all=False)
async def edit_commodity(request: Request, user: MBUser):

    required = ["item_id", "quandity", "price"]
    for param in required:
        if param not in request.args:
            return MBRequest.response_invalid_params([param])

    try:
        price = float(request.args.get("price"))
    except ValueError:
        return MBRequest.response_invalid_params_data(
            {"price": request.args.get("price")}
        )

    try:
        quandity = float(request.args.get("quandity"))
    except ValueError:
        return MBRequest.response_invalid_params_data(
            {"quandity": request.args.get("quandity")}
        )

    item_id = request.args.get("item_id")
    item_object_id: ObjectId
    if item_id is not None:
        try:
            item_object_id = ObjectId(item_id)
        except InvalidId:
            return MBRequest.invalid_item_id(item_id)

    commodity_id = request.args.get("commodity_id")
    commodity: MBCommodity = None

    if commodity_id is not None:
        commodity_object_id: ObjectId
        if commodity_id is not None:
            try:
                commodity_object_id = ObjectId(commodity_id)
            except InvalidId:
                return MBRequest.invalid_user_id(commodity_id)

        commodity = await MBCommodity.find_one(commodity_object_id)

        if commodity is None:
            return MBRequest.invalid_commodity_id(commodity_id)

    item = await MBItem.find_one(item_object_id)
    if item is None:
        return MBRequest.invalid_item_id(item_id)

    if commodity is None:
        commodity = await MBCommodity.create_commodity(
            item.id, quandity, price, user.id
        )
    else:
        await MBCommodity.edit_commodity(commodity, item.id, quandity, price, user.id)

    return json(await MBCommodity.to_api(commodity))


@doc.summary("Get commodity by id")
@doc.consumes(
    doc.String(name="commodity_id", description="Commodity id"),
    location="path",
    required=True,
)
@commodity_api.get("/<commodity_id>")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def get_item(request: Request, commodity_id: str, user: MBUser):
    try:
        commodity_object_id = ObjectId(commodity_id)
    except InvalidId:
        return MBRequest.invalid_commodity_id(commodity_id)

    commodity = await MBCommodity.find_one({"id": commodity_object_id, "user_id_own": user.id})
    if commodity is None:
        return MBRequest.invalid_commodity_id(commodity_id)

    return json(await MBCommodity.to_api(commodity))


@doc.summary("Get all commodities")
@commodity_api.get("list")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def list_items(request: Request, user: MBUser):
    commodities = []
    async for commodity in MBCommodity.find({"user_id_own": user.id}):
        commodity_object = MBCommodity.create_object_from_dict(commodity)
        commodities.append(await MBCommodity.to_api(commodity_object))
    return json({"commodities": commodities, "user": await MBUser.to_api(user)})


@doc.summary("Remove commodity by id")
@doc.consumes(
    doc.String(name="commodity_id", description="Commodity id"),
    location="path",
    required=True,
)
@commodity_api.delete("/<commodity_id>")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def remove_commodity(request: Request, commodity_id: str, user: MBUser):
    try:
        commodity_object_id = ObjectId(commodity_id)
    except InvalidId:
        return MBRequest.invalid_commodity_id(commodity_id)

    commodity = await MBCommodity.find_one(
        {"id": commodity_object_id, "user_id_own": user.id}
    )
    if commodity is None:
        return MBRequest.invalid_commodity_id(commodity_id)

    await commodity.delete()
    return json({"deleted": commodity_id})


@doc.summary("Sell commodity by id")
@doc.consumes(
    doc.String(name="commodity_id", description="Commodity id"),
    location="path",
    required=True,
)
@commodity_api.post("/<commodity_id>")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def sell_commodity(request: Request, commodity_id: str, user: MBUser):
    try:
        commodity_object_id = ObjectId(commodity_id)
    except InvalidId:
        return MBRequest.invalid_commodity_id(commodity_id)

    commodity = await MBCommodity.find_one(
        {"id": commodity_object_id, "user_id_own": user.id}
    )
    if commodity is None:
        return MBRequest.invalid_commodity_id(commodity_id)

    return json(await MBCommodity.sell_commodity(commodity))
