from email.policy import default
from bson import ObjectId
from controllers.MBMongo import MBMongo
from umongo import fields
from models.MBCommodity import MBCommodity
from models.MBDocument import MBDocument
from models.MBItem import MBItem
from datetime import datetime, timedelta
import MBDefine
from models.MBUser import MBUser


@MBMongo.instance.register
class MBFarmField(MBDocument):
    class Meta:
        collection_name = "mb_farm_field"

    def __init__(self, *args, **kwargs):
        super(MBFarmField, self).__init__(*args, **kwargs)

    seed_item = fields.ObjectIdField()
    user_id_own = fields.ObjectIdField()
    last_irrigation = fields.DateTimeField(
        default=datetime.utcnow() - timedelta(days=30)
    )
    total_irrigation_computed = fields.IntegerField(default=0)

    # inteval in seconds
    irrigation_interval = fields.IntegerField(default=10)

    # time left in seconds
    time_left = fields.IntegerField()
    ready_to_harvest = fields.BooleanField(default=False)
    harvested = fields.BooleanField(default=False)
    growing = fields.BooleanField(default=False)

    @staticmethod
    async def create_farm_field(
        user_id_own: ObjectId,
    ):
        farm_field: MBFarmField = MBFarmField()
        farm_field.user_id_own = user_id_own
        user_field_count = await MBFarmField.count_documents(
            {"user_id_own": user_id_own}
        )
        user: MBUser = await MBUser.find_one({"id": user_id_own})
        current_field_price = (
            user_field_count + 1
        ) ** 2 * MBDefine.FARM_FIELD_BASE_PRICE
        if user.capital < current_field_price:
            return None
        user.capital -= current_field_price
        await user.commit()
        await farm_field.commit()
        return farm_field

    @staticmethod
    async def prepare_field(field: "MBFarmField", seed_item: ObjectId):
        item: MBItem = await MBItem.find_one({"id": seed_item})
        field.seed_item = seed_item
        field.time_left = item.seed_growth_time
        field.harvested = False
        field.ready_to_harvest = False
        field.growing = True
        await field.commit()
        return field

    @staticmethod
    async def prepare_field_from_commodity(field: ObjectId, commodity: MBCommodity):
        if commodity.quantity <= 0:
            return None
        commodity.quantity -= 1
        if commodity.quantity > 0:
            await commodity.commit()
        else:
            await commodity.delete()
        farmfield: MBFarmField = await MBFarmField.find_one({"id": field})
        return await MBFarmField.prepare_field(
            field=farmfield, seed_item=commodity.item
        )

    @staticmethod
    async def update_field(
        field: "MBFarmField",
    ):
        if not field.ready_to_harvest and not field.harvested:
            useful_time = (datetime.utcnow() - field.last_irrigation).total_seconds()
            useful_time -= field.total_irrigation_computed
            if useful_time > field.irrigation_interval:
                useful_time = field.irrigation_interval

            if field.total_irrigation_computed < field.irrigation_interval:
                field.time_left -= useful_time
                if field.time_left < 0:
                    field.time_left = 0
                    field.ready_to_harvest = True
                    field.growing = False

                field.total_irrigation_computed += useful_time
                await field.commit()

    @staticmethod
    async def irrigate_field(
        field: "MBFarmField",
    ):
        field.last_irrigation = datetime.utcnow()
        field.total_irrigation_computed = 0
        await field.commit()

    @staticmethod
    async def harvest_field(
        field: "MBFarmField",
    ):
        await MBFarmField.update_field(field)
        if field.ready_to_harvest and not field.harvested:
            item: MBItem = await MBItem.find_one({"id": field.seed_item})
            user: MBUser = await MBUser.find_one({"id": field.user_id_own})
            commodity = await MBCommodity.create_commodity(
                item.seed_item_harvest_id,
                item.seed_item_harvest_quantity,
                item.item_price,
                user.id,
            )
            field.harvested = True
            field.ready_to_harvest = False
            field.growing = False
            await field.commit()
            field_dict = await MBFarmField.to_api(field)
            commodity_dict = await MBCommodity.to_api(commodity)
            field_dict.update(commodity_dict)
            return field_dict
        return await MBFarmField.to_api(field)

    @staticmethod
    async def to_api(
        field: "MBFarmField",
    ):
        await MBFarmField.update_field(field)

        irrigated = True
        useful_time = (datetime.utcnow() - field.last_irrigation).total_seconds()
        if useful_time > field.irrigation_interval:
            irrigated = False

        dict_info = {
            "id": str(field.id),
            "seed_item": str(field.seed_item),
            "user_id_own": str(field.user_id_own),
            "growing": field.growing,
            "harvested": field.harvested,
            "irrigated": irrigated,
        }

        if field.ready_to_harvest:
            dict_info["ready_to_harvest"] = True

        if field.growing:
            dict_info.update(
                {
                    "last_irrigation": field.last_irrigation.isoformat(),
                    "irrigation_interval": field.irrigation_interval,
                    "time_left": field.time_left,
                }
            )

        item = await MBItem.find_one({"id": field.seed_item})
        if item is not None:
            dict_info["item"] = MBItem.to_api(item)

        return dict_info
