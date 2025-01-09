from rest_framework.response import Response

from .models import Expense
from .serializers import ExpenseSerializer
from common.views import BaseViewSet
# Create your views here.



class ExpenseViewSet(BaseViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
   
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

