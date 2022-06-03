def error_message(error: dict):
    """
    Return default error structure
    """

    return {
        "type": "error",
        "call": "error_message",
        "message": error
    }
