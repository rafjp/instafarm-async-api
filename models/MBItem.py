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

    """
    Seed info
    """
    seed_stage_count = fields.IntegerField()
    seed_stage_images = fields.ListField(fields.StrField())
    seed_item_harvest_id = fields.ObjectIdField()
    seed_item_harvest_quantity = fields.IntegerField()

    # growth time in seconds
    seed_growth_time = fields.IntegerField()

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
            item,
            item_name,
            item_description,
            item_price,
            item_image,
            item_category.lower(),
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
            item.item_category = item_category.lower()
        if item_image is not None:
            item.item_image = item_image
        await item.commit()
        return item

    @staticmethod
    async def edit_category(item: "MBItem", item_category: str, category_body: dict):
        item_category = item_category.lower()
        if item_category == "seed":

            for seed_attr in [
                "seed_stage_count",
                "seed_stage_images",
                "seed_item_harvest_id",
                "seed_item_harvest_quantity",
                "seed_growth_time",
            ]:
                if seed_attr in category_body:

                    if isinstance(category_body[seed_attr], str):
                        category_body[seed_attr] = category_body[seed_attr][:128]

                    setattr(item, seed_attr, category_body[seed_attr])
            await item.commit()
        else:
            item.item_category = item_category

        await item.commit()
        return item

    @staticmethod
    def to_api(item: "MBItem"):
        info_dict = {
            "item_id": str(item.id),
            "item_name": item.item_name,
            "item_description": item.item_description,
            "item_price": item.item_price,
            "item_image": item.item_image,
            "item_category": item.item_category,
        }

        if item.item_category == "seed":
            info_dict.update(
                {
                    "seed_stage_count": item.seed_stage_count,
                    "seed_stage_images": item.seed_stage_images,
                    "seed_item_harvest_id": str(item.seed_item_harvest_id),
                    "seed_item_harvest_quantity": item.seed_item_harvest_quantity,
                    "seed_growth_time": item.seed_growth_time,
                }
            )
        return info_dict
