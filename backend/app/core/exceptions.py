from fastapi import HTTPException, status

class ProductNotFound(HTTPException):
    def __init__(self, product_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found")

class ReviewNotFound(HTTPException):
    def __init__(self, review_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID {review_id} not found")

class InvalidRating(HTTPException):
    def __init__(self, rating: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rating must be between 1 and 5, got {rating}")

class InvalidReviewLength(HTTPException):
    def __init__(self, min_length: int, max_length: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Review must be between {min_length} and {max_length} characters")

class DatabaseError(Exception):
    pass

