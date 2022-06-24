from rest_framework.pagination import LimitOffsetPagination


class LimitPagePagination(LimitOffsetPagination):
    offset_query_param = 'page'
