async def pong_message():
    """
    Return a simple pong to test the network
    """

    return {
        "type": "network",
        "call": "pong_message",
        "message": "pong"
    }
