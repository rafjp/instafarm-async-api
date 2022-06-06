from re import I
from this import d
from tkinter.font import families
from bson import ObjectId
from bson.errors import InvalidId
from sanic import Blueprint, json
from sanic.response import Request
from sanic_openapi import doc
from models.MBCommodity import MBCommodity
from models.MBFarmField import MBFarmField

from models.MBItem import MBItem
from controllers.MBRequest import MBRequest
from controllers import MBUtil
from models.MBUser import MBUser

farm_field_api = Blueprint("Farm", url_prefix="/farm/")


@doc.summary("Buy new field")
@doc.consumes(
    doc.String(name="user_id", description="User"),
    required=True,
)
@farm_field_api.post("field/buy")
async def buy_field(request: Request):

    user_id = request.args.get("user_id")
    user_object_id: ObjectId
    if user_id is not None:
        try:
            user_object_id = ObjectId(user_id)
        except InvalidId:
            return MBRequest.invalid_user_id(user_id)

    user_count = await MBUser.count_documents({"id": user_object_id})
    if user_count <= 0:
        return MBRequest.invalid_user_id(user_id)

    farmfield:MBFarmField  = await MBFarmField.create_farm_field(user_object_id)
    if farmfield is None:
        return MBRequest.response_not_enough_money(user_id)

    return json(await MBFarmField.to_api(farmfield))

@doc.summary("List user farm fields")
@doc.consumes(
    doc.String(name="user_id", description="User"),
    required=True,
)
@farm_field_api.get("field/list")
async def list_field(request: Request):

    user_id = request.args.get("user_id")
    user_object_id: ObjectId
    if user_id is not None:
        try:
            user_object_id = ObjectId(user_id)
        except InvalidId:
            return MBRequest.invalid_user_id(user_id)

    farmfields = []
    async for farmfield in MBFarmField.find({"user_id_own": user_object_id}):
        farmfield: MBFarmField
        farmfields.append(await MBFarmField.to_api(farmfield))

    return json({"user_id": user_id, "farmfields": farmfields})


@doc.summary("Prepare new field")
@doc.consumes(
    doc.String(name="field_id", description="Farm field id"),
    doc.String(name="commodity_id", description="Commodity id of seed"),
    required=True,
)
@farm_field_api.put("field/prepare")
async def prepare_field(request: Request):
    
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
    
    farmfield:MBFarmField  = await MBFarmField.prepare_field_from_commodity(farmfield_object_id, commodity)
    if farmfield is None:
        return MBRequest.response_not_enough_money(farmfield.user_id_own)

    return json(await MBFarmField.to_api(farmfield))


@doc.summary("Irrigate field")
@doc.consumes(
    doc.String(name="field_id", description="Farm field id"),
    location="path",
    required=True,
)
@farm_field_api.post("field/irrigate/<field_id>")
async def irrigate_field(request: Request, field_id: str):
    
    farmfield_object_id: ObjectId
    try:
        farmfield_object_id = ObjectId(field_id)
    except InvalidId:
        return MBRequest.invalid_field_id(field_id)

    farmfield: MBFarmField  = await MBFarmField.find_one({"id": farmfield_object_id})
    if farmfield is None:
        return MBRequest.response_invalid_params(["field_id"])
    
    await MBFarmField.irrigate_field(farmfield)

    return json(await MBFarmField.to_api(farmfield))

@doc.summary("Harvest field")
@doc.consumes(
    doc.String(name="field_id", description="Farm field id"),
    location="path",
    required=True,
)
@farm_field_api.post("field/harvest/<field_id>")
async def harvest_field(request: Request, field_id: str):
    
    farmfield_object_id: ObjectId
    try:
        farmfield_object_id = ObjectId(field_id)
    except InvalidId:
        return MBRequest.invalid_field_id(field_id)

    farmfield: MBFarmField  = await MBFarmField.find_one({"id": farmfield_object_id})
    if farmfield is None:
        return MBRequest.response_invalid_params(["field_id"])

    return json(await MBFarmField.harvest_field(farmfield))