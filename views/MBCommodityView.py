from re import I
from this import d
from bson import ObjectId
from bson.errors import InvalidId
from sanic import Blueprint, json
from sanic.response import Request
from sanic_openapi import doc
from models.MBCommodity import MBCommodity

from models.MBItem import MBItem
from controllers.MBRequest import MBRequest
from controllers import MBUtil
from models.MBUser import MBUser

commodity_api = Blueprint("Commodities", url_prefix="/commodity/")


@doc.summary("Register/edit commodity")
@doc.consumes(
    doc.String(name="item_id", description="Commodity item"),
    doc.Float(name="quandity", description="Commodity quandity"),
    doc.Float(name="price", description="Commodity price"),
    doc.String(name="user_id", description="Commodity user owner"),
    required=True,
)
@doc.consumes(
    doc.String(name="commodity_id", description="Commodity id"),
    required=False,
)
@commodity_api.put("edit")
async def edit_commodity(request: Request):

    required = ["item_id", "quandity", "price", "user_id"]
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

    user_id = request.args.get("user_id")
    user_object_id: ObjectId
    if user_id is not None:
        try:
            user_object_id = ObjectId(user_id)
        except InvalidId:
            return MBRequest.invalid_user_id(user_id)

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

    user = await MBUser.find_one(user_object_id)

    if user is None:
        return MBRequest.invalid_user_id(user_id)

    item = await MBItem.find_one(item_object_id)
    if item is None:
        return MBRequest.invalid_item_id(item_id)

    if commodity is None:
        commodity = await MBCommodity.create_commodity(item.id, quandity, price, user.id)
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
async def get_item(request: Request, commodity_id: str):

    try:
        commodity_object_id = ObjectId(commodity_id)
    except InvalidId:
        return MBRequest.invalid_commodity_id(commodity_id)

    commodity = await MBCommodity.find_one({"id": commodity_object_id})
    if commodity is None:
        return MBRequest.invalid_commodity_id(commodity_id)

    return json(await MBCommodity.to_api(commodity))


@doc.summary("Get all commodities")
@doc.consumes(doc.String(name="user_id", description="User owner"), required=True)
@commodity_api.get("list")
async def list_items(request: Request):

    user_id = request.args.get("user_id")
    user_object_id: ObjectId
    if user_id is not None:
        try:
            user_object_id = ObjectId(user_id)
        except InvalidId:
            return MBRequest.invalid_user_id(user_id)
    else:
        return MBRequest.response_invalid_params(["user_id"])

    user = await MBUser.find_one(user_object_id)

    if user is None:
        return MBRequest.invalid_user_id(user_id)

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
async def remove_commodity(request: Request, commodity_id: str):
    try:
        commodity_object_id = ObjectId(commodity_id)
    except InvalidId:
        return MBRequest.invalid_commodity_id(commodity_id)

    commodity = await MBCommodity.find_one({"id": commodity_object_id})
    await commodity.delete()

    return json({"deleted": commodity_id})

@doc.summary("Sell commodity by id")
@doc.consumes(
    doc.String(name="commodity_id", description="Commodity id"),
    location="path",
    required=True,
)
@commodity_api.post("/<commodity_id>")
async def sell_commodity(request: Request, commodity_id: str):

    try:
        commodity_object_id = ObjectId(commodity_id)
    except InvalidId:
        return MBRequest.invalid_commodity_id(commodity_id)
    
    commodity = await MBCommodity.find_one({"id": commodity_object_id})
    if commodity is None:
        return MBRequest.invalid_commodity_id(commodity_id)
    
    return json(await MBCommodity.sell_commodity(commodity))
