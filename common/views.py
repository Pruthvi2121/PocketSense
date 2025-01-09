from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from rest_framework import status

from .pagination import CustomPagination  
from .permissions import IsSuperAdmin, IsActiveUser
from rest_framework.permissions import IsAuthenticated
from .functions import serailizer_errors 
import logging

logger = logging.getLogger(__name__)

class BaseViewSet(ModelViewSet):
    pagination = True
    pagination_class = CustomPagination

    def get_permissions(self):
        permission_classes = []
        if self.action in ["list", "retrieve", "create", "update", "destroy"]:
            permission_classes = [IsAuthenticated]
        # elif self.action == "update":
        #     permission_classes = [IsSuperAdmin]
        else:
            permission_classes = [IsSuperAdmin]

        permission_classes += [IsActiveUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Generic filtering logic (if needed)
        return self.queryset.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if self.pagination:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response({"results":serializer.data})
        except Exception as ex:
            logger.error("An error occurred while listing objects", exc_info=ex)
            raise APIException(detail="An error occurred while retrieving data.")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"results":serializer.data})

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {"detail": "Successfully Created!", "results": serializer.data},
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        except ValidationError as e:
            field_name, error_message = serailizer_errors(e)
            return Response(
                {"detail": f"{field_name} - {error_message}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.created_by != request.user:
                raise PermissionDenied("You don't have permission to update this object.")
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"detail": "Successfully Updated!", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            field_name, error_message = serailizer_errors(e)
            return Response(
                {"detail": f"{field_name} - {error_message}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by != request.user:
            raise PermissionDenied("You don't have permission to perform this action.")
        instance.delete()
        return Response(
            {"detail": "Successfully Deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )

   