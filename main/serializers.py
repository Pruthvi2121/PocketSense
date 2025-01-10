from .models import Expense, Group, GroupExpense, GroupContribution
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

class GroupExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupExpense
        fields = "__all__"  
        read_only_fields = ['created_by', 'group']

class GroupContributionSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()

    class Meta:
        model = GroupContribution
        fields = ["id", "group", "member", "member_name", "amount", "is_paid", "is_verified", "contribution_type"]
       
    def get_member_name(self, obj):
        return f"{obj.member.first_name} {obj.member.last_name}"
