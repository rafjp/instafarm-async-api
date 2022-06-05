from bson import ObjectId
from controllers.MBMongo import MBMongo
from umongo import fields
from models.MBDocument import MBDocument
from models.MBItem import MBItem
from models.MBUser import MBUser


@MBMongo.instance.register
class MBCommodity(MBDocument):
    class Meta:
        collection_name = "mb_commodity"

    def __init__(self, *args, **kwargs):
        super(MBCommodity, self).__init__(*args, **kwargs)

    item = fields.ObjectIdField()
    quantity = fields.IntegerField()
    price = fields.FloatField()
    user_id_own = fields.ObjectIdField()

    @staticmethod
    def create_object_from_dict(commodity_dict: dict):
        commodity = MBCommodity()
        commodity.id = commodity_dict["id"]
        commodity.item = commodity_dict["item"]
        commodity.quantity = commodity_dict["quantity"]
        commodity.price = commodity_dict["price"]
        commodity.user_id_own = commodity_dict["user_id_own"]
        return commodity

    @staticmethod
    async def create_commodity(
        item: ObjectId,
        quantity: int,
        price: float,
        user_id_own: ObjectId,
    ):
        commodity: MBCommodity = MBCommodity()
        return await MBCommodity.edit_commodity(
            commodity=commodity,
            item=item,
            quantity=quantity,
            price=price,
            user_id_own=user_id_own,
        )

    @staticmethod
    async def edit_commodity(
        commodity: "MBCommodity",
        item: ObjectId,
        quantity: int,
        price: float,
        user_id_own: ObjectId,
    ):
        commodity.item = item
        commodity.quantity = quantity
        commodity.price = price
        commodity.user_id_own = user_id_own
        await commodity.commit()
        return commodity
    
    @staticmethod
    async def sell_commodity(
        commodity: "MBCommodity",
    ):
        user = await MBUser.find_one({"id": commodity.user_id_own})
        assert user is not None
        user.capital += commodity.price
        await user.commit()
        await commodity.delete()
        return await MBUser.to_api(user)

    @staticmethod
    async def to_api(commodity: "MBCommodity"):
        item = await MBItem.find_one({"id": commodity.item})

        return {
            "commodity_id": str(commodity.id),
            "item": MBItem.to_api(item),
            "quantity": commodity.quantity,
            "price": commodity.price,
            "user_id_own": str(commodity.user_id_own),
        }
