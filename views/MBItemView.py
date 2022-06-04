from re import I
from this import d
from bson import ObjectId
from bson.errors import InvalidId
from sanic import Blueprint, json
from sanic.response import Request
from sanic_openapi import doc

from models.MBItem import MBItem
from controllers.MBRequest import MBRequest
from controllers import MBUtil

item_api = Blueprint("Items", url_prefix="/item/")


@doc.summary("Register new item")
@doc.consumes(
    doc.String(name="item_id", description="Item id"),
    doc.String(name="item_image", description="Item image"),
    doc.String(name="item_category", description="Item category"),
)
@doc.consumes(
    doc.String(name="item_name", description="Item name"),
    doc.String(name="item_description", description="Item description"),
    doc.Float(name="item_price", description="Item price"),
    required=True,
)
@item_api.put("edit")
async def create_new_item(request: Request):

    required = ["item_name", "item_description", "item_price"]
    for param in required:
        if param not in request.args:
            return MBRequest.response_invalid_params([param])

    item_name = request.args.get("item_name")

    if not MBUtil.is_a_valid_product_name(item_name):
        return MBRequest.response_invalid_params_data({"user_name": item_name})

    item_description = request.args.get("item_description")
    item_price = request.args.get("item_price")
    item_image = request.args.get("item_image")
    item_category = request.args.get("item_category")

    item_id = request.args.get("item_id")
    if item_id is not None:
        try:
            item_object_id = ObjectId(item_id)
        except InvalidId:
            return MBRequest.invalid_item_id(item_id)

        item = await MBItem.find_one({"id": item_object_id})
        if item is None:
            return MBRequest.invalid_item_id(item_id)

        item = await MBItem.edit_item(
            item,
            item_name,
            item_description,
            item_price,
            item_image,
            item_category,
        )

    else:
        item = await MBItem.create_item(
            item_name, item_description, item_price, item_image, item_category
        )

    return json({"item_id": str(item.id)})


@doc.summary("Get item by id")
@doc.consumes(
    doc.String(name="item_id", description="Item id"),
    location="path",
    required=True,
)
@item_api.get("/<item_id>")
async def get_item(request: Request, item_id: str):

    try:
        item_object_id = ObjectId(item_id)
    except InvalidId:
        return MBRequest.invalid_item_id(item_id)

    item = await MBItem.find_one({"id": item_object_id})
    if item is None:
        return MBRequest.invalid_item_id(item_id)

    return json(MBItem.to_api(item))


@doc.summary("Get all items")
@doc.consumes(
    doc.String(name="item_category", description="Item category"),
)
@item_api.get("list")
async def list_items(request: Request):

    item_category = request.args.get("item_category")
    query = {}
    if item_category is not None:
        query["item_category"] = item_category

    items = []

    db_items = MBItem.find(query)
    async for item in db_items:
        items.append(MBItem.to_api(item))

    return json({"items": items})
