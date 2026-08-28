from starlette import status


def _already_exists(resource_name: str):
    return {status.HTTP_409_CONFLICT: {
        "description": "Integrity Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": f"{resource_name} already exists"
                }
            }
        }
    }}


def _not_found(resource_name: str):
    return {status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {
                    "detail": f"{resource_name} not found"
                }
            }
        }
    }}


DUPLICATE_ATTRIBUTES = {status.HTTP_400_BAD_REQUEST: {
    "description": "Duplicate Attributes",
    "content": {
        "application/json": {
            "example": {
                "detail": "Duplicate attributes are not allowed"
            }
        }
    }
}}

# conflict
CATEGORY_ALREADY_EXISTS = _already_exists("Category")
ATTRIBUTE_ALREADY_EXISTS = _already_exists("Attribute")

# not found
CATEGORY_NOT_FOUND = _not_found("Category")
ATTRIBUTE_NOT_FOUND = _not_found("Attribute")
PRODUCT_NOT_FOUND = _not_found("Product")
VARIANT_NOT_FOUND = _not_found("Variant")
