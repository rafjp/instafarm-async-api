from sanic import json

from controllers.protocol import PError


class MBRequest:

    @staticmethod
    def response_invalid_params(params: list):
        return json(
            PError.error_message({
                "error": "invalid params",
                "params": params
            }), status=400
        )

    @staticmethod
    def invalid_user_id(user_id: str):
        return json(
            PError.error_message({
                "error": "User id not found",
                "user_id": user_id
            }), status=400
        )
    
    @staticmethod
    def invalid_item_id(item_id: str):
        return json(
            PError.error_message({
                "error": "Item id not found",
                "item_id": item_id
            }), status=400
        )
    
    @staticmethod
    def invalid_commodity_id(commmodity: str):
        return json(
            PError.error_message({
                "error": "Commodity id not found",
                "commodity_id": commmodity
            }), status=400
        )

    @staticmethod
    def invalid_user_channel_id(channel_id: str):
        return json(
            PError.error_message({
                "error": "User message channel id not found",
                "channel_id": channel_id
            }), status=400
        )

    @staticmethod
    def invalid_room_match(user_id: str):
        return json(
            PError.error_message({
                "error": "User can't join this group",
                "user_id": user_id
            }), status=400
        )

    @staticmethod
    def response_invalid_params_data(params: dict):
        return json(
            PError.error_message({
                "error": "invalid params data",
                "params": params
            }), status=400
        )
