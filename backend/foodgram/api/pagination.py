from rest_framework.pagination import PageNumberPagination


class LimitPagePagination(PageNumberPagination):
    """
    Переопределения имени поля в стандартном пажинаторе, для корректной работы
    с frontend-частью проекта
    """
    page_size_query_param = 'limit'
