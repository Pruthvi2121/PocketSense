from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 10
    def get_paginated_data(self, serializer, data):
        data = super().get_paginated_data(serializer)
        data[data] = data
        return data

class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    # limit_query_param = 'start'
    max_limit = 40