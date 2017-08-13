from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination

class TLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 10


class ThreadPageNumberPagination(PageNumberPagination):
    page_size = 50