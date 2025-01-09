from rest_framework.response import Response

from .models import Expense, Group
from .serializers import ExpenseSerializer, GroupSerializer
from common.views import BaseViewSet
from common.permissions import IsGroupAdmin, IsGroupMember
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
# Create your views here.



class ExpenseViewSet(BaseViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
   
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)




class GroupViewSet(BaseViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    
    def get_permissions(self):
       
        if self.action in ['create', 'update', 'destroy']:
            
            permission_classes = [IsAuthenticated, IsGroupAdmin]
        else:
            permission_classes = [IsAuthenticated, IsGroupMember]

        return [permission() for permission in permission_classes]
    

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user, created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        group = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            group.members.add(user)
            return Response({"detail": f"User {user.username} added to the group."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        group = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            if user == group.admin:
                return Response({"detail": "Admin cannot be removed from the group."}, status=status.HTTP_400_BAD_REQUEST)
            group.members.remove(user)
            return Response({"detail": f"User {user.username} removed from the group."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

