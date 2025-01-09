from .models import Expense, Group
from users.models import User
from rest_framework import serializers

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = "__all__"  
        read_only_fields = ['created_by', 'created_on', 'updated_on'] 



class GroupSerializer(serializers.ModelSerializer):
   
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )

    class Meta:
        model = Group
        fields = "__all__"  
        read_only_fields = ['created_by','created_on', 'updated_on', 'admin']

   