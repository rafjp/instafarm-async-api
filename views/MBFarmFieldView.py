from bson import ObjectId
from bson.errors import InvalidId
from controllers.MBAuthScope import MBAuthScope
from controllers.MBRequest import MBRequest
from models.MBCommodity import MBCommodity
from models.MBFarmField import MBFarmField
from models.MBItem import MBItem
from models.MBUser import MBUser
from sanic import Blueprint, json
from sanic.response import Request
from sanic_jwt import inject_user, scoped
from sanic_openapi import doc

farm_field_api = Blueprint("Farm", url_prefix="/farm/")


@doc.summary("Buy new field")
@farm_field_api.post("field/buy")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def buy_field(request: Request, user: MBUser):
    farm_field: MBFarmField = await MBFarmField.create_farm_field(user.id)
    if farm_field is None:
        return MBRequest.response_not_enough_money(str(user.id))

    return json(await MBFarmField.to_api(farm_field))


@doc.summary("List user farm fields")
@farm_field_api.get("field/list")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def list_field(request: Request, user: MBUser):
    farmfields = []
    async for farmfield in MBFarmField.find({"user_id_own": user.id}):
        farmfield: MBFarmField
        farmfields.append(await MBFarmField.to_api(farmfield))

    return json({"user_id": str(user.id), "farmfields": farmfields})


@doc.summary("Prepare new field")
@doc.consumes(
    doc.String(name="field_id", description="Farm field id"),
    doc.String(name="commodity_id", description="Commodity id of seed"),
    required=True,
)
@farm_field_api.put("field/prepare")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def prepare_field(request: Request, user: MBUser):

    commodity_id = request.args.get("commodity_id")
    commodity_object_id: ObjectId
    try:
        commodity_object_id = ObjectId(commodity_id)
    except InvalidId:
        return MBRequest.invalid_commodity_id(commodity_id)

    commodity = await MBCommodity.find_one({"id": commodity_object_id})
    commodity_item = await MBItem.find_one({"id": commodity.item})
    if commodity_item.item_category != "seed":
        return MBRequest.response_invalid_params(["commodity_id"])

    farmfield_id = request.args.get("field_id")
    farmfield_object_id: ObjectId
    try:
        farmfield_object_id = ObjectId(farmfield_id)
    except InvalidId:
        return MBRequest.invalid_field_id(farmfield_id)

    farmfield: MBFarmField = await MBFarmField.prepare_field_from_commodity(
        farmfield_object_id, commodity
    )
    if farmfield is None:
        return MBRequest.response_not_enough_money(farmfield.user_id_own)

    if farmfield.user_id_own != user.id:
        return MBRequest.response_flow_error("User id not match")

    return json(await MBFarmField.to_api(farmfield))


@doc.summary("Irrigate field")
@doc.consumes(
    doc.String(name="field_id", description="Farm field id"),
    location="path",
    required=True,
)
@farm_field_api.post("field/irrigate/<field_id>")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def irrigate_field(request: Request, field_id: str, user: MBUser):

    farmfield_object_id: ObjectId
    try:
        farmfield_object_id = ObjectId(field_id)
    except InvalidId:
        return MBRequest.invalid_field_id(field_id)

    farmfield: MBFarmField = await MBFarmField.find_one({"id": farmfield_object_id})
    if farmfield is None:
        return MBRequest.response_invalid_params(["field_id"])

    await MBFarmField.irrigate_field(farmfield)

    if farmfield.user_id_own != user.id:
        return MBRequest.response_flow_error("User id not match")

    return json(await MBFarmField.to_api(farmfield))


@doc.summary("Harvest field")
@doc.consumes(
    doc.String(name="field_id", description="Farm field id"),
    location="path",
    required=True,
)
@farm_field_api.post("field/harvest/<field_id>")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def harvest_field(request: Request, field_id: str, user: MBUser):

    farmfield_object_id: ObjectId
    try:
        farmfield_object_id = ObjectId(field_id)
    except InvalidId:
        return MBRequest.invalid_field_id(field_id)

    farmfield: MBFarmField = await MBFarmField.find_one({"id": farmfield_object_id})
    if farmfield is None:
        return MBRequest.response_invalid_params(["field_id"])

    if farmfield.user_id_own != user.id:
        return MBRequest.response_flow_error("User id not match")

    return json(await MBFarmField.harvest_field(farmfield))
