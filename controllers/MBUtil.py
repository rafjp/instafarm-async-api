
def is_a_valid_name(name: str):
    if name is None:
        return False
    if len(name) < 1:
        return False
    if not name.isalnum():
        return False
    if name[0].isdigit():
        return False
    return True

def is_a_valid_product_name(name: str):
    if len(name) < 2:
        return False

    if name[0].isdigit():
        return False
    
    if len(name) > 30:
        return False
    return True
