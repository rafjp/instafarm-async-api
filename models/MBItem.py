from bson import ObjectId
from pkg_resources import require

from controllers.MBMongo import MBMongo
from umongo import fields
from models.MBDocument import MBDocument


@MBMongo.instance.register
class MBItem(MBDocument):
    class Meta:
        collection_name = "mb_item"

    def __init__(self, *args, **kwargs):
        super(MBItem, self).__init__(*args, **kwargs)

    """
        The user_id_own is the user who can make a request to see messages sent to him
    """
    item_name = fields.StrField(require=True, unique=True)
    item_description = fields.StrField(require=True)
    item_price = fields.FloatField(require=True)
    item_image = fields.StrField()
    item_category = fields.StrField()

    @staticmethod
    async def create_item(
        item_name: str,
        item_description: str,
        item_price: float,
        item_image: str = None,
        item_category: str = None,
    ):
        item: MBItem = MBItem()
        return await MBItem.edit_item(
            item, item_name, item_description, item_price, item_image, item_category
        )

    @staticmethod
    async def edit_item(
        item: "MBItem",
        item_name: str,
        item_description: str,
        item_price: float,
        item_image: str = None,
        item_category: str = None,
    ):
        item.item_name = item_name
        item.item_description = item_description
        item.item_price = float(item_price)
        if item_category is not None:
            item.item_category = item_category
        if item_image is not None:
            item.item_image = item_image
        await item.commit()
        return item

    @staticmethod
    def to_api(item: "MBItem"):
        return {
            "item_name": item.item_name,
            "item_description": item.item_description,
            "item_price": item.item_price,
            "item_image": item.item_image,
            "item_category": item.item_category,
        }