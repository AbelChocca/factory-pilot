import math

class PaginationHelper:
    @staticmethod
    def page_to_offset(
        page: int,
        limit: int,
    ) -> int:
        page = max(page, 1)
        limit = max(limit, 1)

        return (page - 1) * limit

    @staticmethod
    def offset_to_page(
        offset: int,
        limit: int,
    ) -> int:
        if limit <= 0:
            return 1

        return (offset // limit) + 1

    @staticmethod
    def total_pages(
        total_items: int,
        limit: int,
    ) -> int:
        if limit <= 0:
            return 1

        return max(1, math.ceil(total_items / limit))