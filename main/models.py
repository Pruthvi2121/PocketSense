from django.db import models
from users.models import User
from common.models import BaseModel
# Create your models here.




class Expense(BaseModel):
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('travel', 'Travel'),
        ('books', 'Books'),
        ('other', 'Others'),
        
    ]
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.category} {self.amount}/-"


class Group(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="admin_groups")
    members = models.ManyToManyField(User, related_name="member_groups", blank=True)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estimated_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_to_refund = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.admin not in self.members.all():
            self.members.add(self.admin)
    
  

    def calculate_contributions(self):
        """
        Calculate contributions or refunds for each member, considering individual payments.
        """
        members_count = self.members.count()
        if members_count == 0:
            return None

        # Fetch all expenses and calculate total spent by each member
        total_group_expense = sum(expense.amount for expense in self.expenses.all())
        member_expenses = {member: 0 for member in self.members.all()}

        for expense in self.expenses.all():
            member_expenses[expense.created_by] += expense.amount

        # Calculate the share each member owes
        per_member_share = total_group_expense / members_count

        contributions = []
        for member, spent in member_expenses.items():
            if spent > per_member_share:
                # Member has overpaid; calculate refund
                refund_amount = spent - per_member_share
                contributions.append({
                    'member': member,
                    'amount': refund_amount,
                    'type': 'refund'
                })
            elif spent < per_member_share:
                # Member owes money; calculate additional amount
                additional_amount = per_member_share - spent
                contributions.append({
                    'member': member,
                    'amount': additional_amount,
                    'type': 'additional'
                })
            else:
                # Member's payments match their share; no action needed
                contributions.append({
                    'member': member,
                    'amount': 0,
                    'type': 'settled'
                })

        return contributions

class GroupExpense(BaseModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="expenses")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.group.name} - {self.amount}/-"


class GroupContribution(BaseModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="contributions")
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    contribution_type = models.CharField(max_length=50, choices=[('initial', 'Initial'), ('additional', 'Additional'), ('refund', 'Refund')], default='initial')

    def __str__(self):
        return f"{self.member.first_name} - {self.contribution_type} - {self.amount}/-"