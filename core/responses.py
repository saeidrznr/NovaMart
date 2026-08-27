from starlette import status

CATEGORY_ALREADY_EXISTS = {status.HTTP_409_CONFLICT: {
    "description": "Integrity Error",
    "content": {
        "application/json": {
            "example": {
                "detail": "Category already exists"
            }
        }
    }
}}

CATEGORY_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {
    "description": "Not Found",
    "content": {
        "application/json": {
            "example": {
                "detail": "Category not found"
            }
        }
    }
}}
