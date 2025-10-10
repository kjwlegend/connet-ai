"""Pagination helper dependency."""

from fastapi import HTTPException, status


def get_pagination_params(
    page: int = 1,
    size: int = 20,
    max_size: int = 100,
) -> dict:
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1",
        )

    if size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Size must be >= 1",
        )

    if size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Size must be <= {max_size}",
        )

    offset = (page - 1) * size

    return {
        "page": page,
        "size": size,
        "offset": offset,
        "limit": size,
    }


__all__ = ["get_pagination_params"]
