from rest_framework.response import Response

from .models import Expense, Group
from .serializers import ExpenseSerializer, GroupSerializer
from common.views import BaseViewSet
from common.permissions import IsGroupAdmin, IsGroupMember
from rest_framework.permissions import IsAuthenticated
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