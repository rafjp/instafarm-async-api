from bson import ObjectId
from bson.errors import InvalidId
from sanic import Blueprint, json
from sanic.response import Request
from sanic_jwt import inject_user, scoped
from sanic_openapi import doc

from controllers import MBUtil
from controllers.MBAuthScope import MBAuthScope
from controllers.MBRequest import MBRequest
from models.MBCommodity import MBCommodity
from models.MBItem import MBItem
from models.MBUser import MBUser

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
@scoped(MBAuthScope.ADMIN, require_all=False)
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
@scoped(MBAuthScope.USER, require_all=False)
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
@scoped(MBAuthScope.USER, require_all=False)
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


@doc.summary("Register item category")
@doc.consumes(
    doc.String(name="item_id", description="Item id"),
    location="path",
)
@doc.consumes(
    doc.JsonBody(
        {
            "seed_stage_count": doc.Integer(description="Item stage count"),
            "seed_stage_images": doc.List(
                items=doc.String(description="Item stage images")
            ),
            "seed_item_harvest_id": doc.String(description="Item harvest id"),
            "seed_item_harvest_quantity": doc.Integer(
                description="Item harvest quantity"
            ),
            "seed_growth_time": doc.Integer(description="Item growth time"),
        },
    ),
    location="body",
)
@item_api.put("category/seed/<item_id>")
@scoped(MBAuthScope.ADMIN, require_all=False)
async def edit_item_category(request: Request, item_id: str):
    item_category = "seed"
    try:
        item_object_id = ObjectId(item_id)
    except InvalidId:
        return MBRequest.invalid_item_id(item_id)

    item = await MBItem.find_one({"id": item_object_id})
    if item is None:
        return MBRequest.invalid_item_id(item_id)

    item = await MBItem.edit_category(item, item_category, request.json)

    return json(MBItem.to_api(item))


@doc.summary("Buy item by id")
@doc.consumes(
    doc.String(name="item_id", description="Item id"),
    location="path",
    required=True,
)
@doc.consumes(
    doc.Integer(name="quantity", description="Quantity"),
    required=False,
)
@item_api.post("/<item_id>")
@inject_user()
@scoped(MBAuthScope.USER, require_all=False)
async def buy_item(request: Request, item_id: str, user: MBUser):
    try:
        item_object_id = ObjectId(item_id)
    except InvalidId:
        return MBRequest.invalid_item_id(item_id)

    item: MBItem = await MBItem.find_one({"id": item_object_id})
    if item is None:
        return MBRequest.invalid_item_id(item_id)

    quantity = request.args.get("quantity")
    if quantity is not None:
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            MBRequest.response_invalid_params_data({"quantity": quantity})
    else:
        quantity = 1
        
    total_price = item.item_price * quantity

    if total_price > user.capital:
        return MBRequest.response_not_enough_money(str(user.id))

    commodity = await MBCommodity.create_commodity(
        item.id,
        quantity,
        item.item_price,
        user.id,
    )

    user.capital -= total_price
    await user.commit()

    return json(await MBCommodity.to_api(commodity))
