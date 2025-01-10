from rest_framework.response import Response
from users.models import User
from .models import Expense, Group,  GroupExpense, GroupContribution
from .serializers import ExpenseSerializer, GroupSerializer, GroupExpenseSerializer, GroupContributionSerializer
from common.views import BaseViewSet
from common.permissions import IsGroupAdmin, IsGroupMember
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from common.functions import serailizer_errors
from rest_framework.exceptions import ValidationError,  APIException
from django.db import transaction
# Create your views here.

import logging
logger = logging.getLogger(__name__)


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
    



    @action(detail=True, methods=["post"] )
    def add_expense(self, request, pk=None):
        try:   
            group = self.get_object()
            serializer = GroupExpenseSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            expense_amount = serializer.validated_data.get('amount')
            serializer.save(group=group, created_by=request.user)
            group.actual_amount+=expense_amount
            group.save()
            return Response({"deatil":"Expense added", "results":serializer.data}, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            field_name, error_message = serailizer_errors(e)
            return Response({'detail': f"{field_name.capitalize()} - {error_message}"}, status=status.HTTP_400_BAD_REQUEST) 
        except Exception as ex:
            logger.info("Something went wrong", exc_info=ex)
            raise APIException(detail=ex)
    
    @action(detail=True, methods=["get"])
    def list_expenses(self, request, pk=None):
        try:
            group = self.get_object()
            expenses = group.expenses.all()  # Assuming related_name='expenses' in GroupExpense model
            serializer = GroupExpenseSerializer(expenses, many=True)
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)

        except Exception as ex:
            logger.info("Something went wrong", exc_info=ex)
            raise APIException(detail=str(ex))
        


    @action(detail=True, methods=["delete"])
    def delete_expense(self, request, pk=None):
        try:
            group = self.get_object()
            expense_id = request.data.get("expense_id", None)
            expense = group.expenses.get(pk=expense_id)  
            if request.user!= expense.created_by:
                return Response({"detail":"You don't have permission to perform this action."}, status=status.HTTP_400_BAD_REQUEST)
            expense.delete()
            group.actual_amount-=expense.amount
            group.save()

            return Response({"detail": "Expense deleted"}, status=status.HTTP_204_NO_CONTENT)

        except GroupExpense.DoesNotExist:
            return Response({"detail": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.info("Something went wrong", exc_info=ex)
            raise APIException(detail=str(ex))
                
    

    @action(detail=True, methods=["get"])
    def calculate_contributions(self, request, pk=None):
        """
        Calculate contributions or refunds for a group.
        """
        group = self.get_object()
        contributions = group.calculate_contributions()
        if not contributions:
            return Response({"detail": "No contributions to calculate."}, status=status.HTTP_400_BAD_REQUEST)

        data = []
        for contribution in contributions:
            data.append({
                "member": contribution["member"].id,
                "amount": contribution["amount"],
                "type": contribution["type"],
            })
        return Response({"results":data}, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=["post"])
    def share_contribution_amount(self, request, pk=None):
        group = self.get_object()
        estimated_amount = group.estimated_amount
        if estimated_amount == 0:
            return Response({"detail":"Please set the estimated amount."}, status=status.HTTP_400_BAD_REQUEST)
        members = group.members.all()
        if not members.exists():
            return Response({"detail": "No members in the group to share contributions."}, status=status.HTTP_400_BAD_REQUEST)
        
        per_member_contribution = estimated_amount / len(members)

        for member in members:
            GroupContribution.objects.create(
                group=group,
                member=member,
                amount=per_member_contribution,
                contribution_type="initial",
            )

        return Response({"detail": f"Contribution for {group.name} is shared successfully."},status=status.HTTP_201_CREATED )
    
    @action(detail=True, methods=["get"])
    def contribution_list(self, request, pk=None):
        group = self.get_object()
        contribution = group.contributions.all()
        serailizer = GroupContributionSerializer(contribution, many=True)
        return Response({"results":serailizer.data}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["put"])
    def pay_contribution(self, request, pk=None):
        try:
            contribution_id = request.data.get("contribution_id", None)

            contribution = contribution = GroupContribution.objects.get(id=contribution_id)
            if request.user != contribution.member:
                return Response({"detail":"You don't have permission to perform this action"}, status=status.HTTP_400_BAD_REQUEST)  
            contribution.is_paid = True 
            contribution.save()  

            return Response({"detail":"Contribution mark paid successfully!"}, status=status.HTTP_200_OK)  # Return the updated data
        except GroupContribution.DoesNotExist:
            return Response({"detail": "Contribution not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    @action(detail=True, methods=["put"])
    def verify_contribution_pay(self, request, pk=None):
        group = self.get_object()
        contribution_ids = request.data.get("contribution_ids", [])
        if not contribution_ids:
            return Response({"detail": "No contribution IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
           
            with transaction.atomic():
                contributions = GroupContribution.objects.filter(id__in=contribution_ids, is_verified=False, group=group)
                if not contributions:
                    return Response({"detail": "No unverified contributions found."}, status=status.HTTP_404_NOT_FOUND)
                 
                total_verified_amount = sum(contribution.amount for contribution in contributions)
                contributions.update(is_verified=True) 
                group.collected_amount += total_verified_amount
                group.save()

                return Response({"detail": f"Contributions verified successfully.", "total_verified_amount": total_verified_amount},
                                status=status.HTTP_200_OK)

        except GroupContribution.DoesNotExist:
            return Response({"detail": "Contribution not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": "Something went wrong"}, status=status.HTTP_404_NOT_FOUND)
        