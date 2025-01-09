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
    estimated_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_to_refund = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.admin not in self.members.all():
            self.members.add(self.admin)
    
    def calculate_contributions(self):
        """
        Calculate contributions or refunds for each member.
        """
        members_count = self.members.count()
        if members_count == 0:
            return None

        contributions = []
        if self.actual_amount > self.estimated_amount:
            # Additional amount to be paid by each member
            additional_amount = (self.actual_amount - self.estimated_amount) / members_count
            for member in self.members.all():
                contributions.append({
                    'member': member,
                    'amount': additional_amount,
                    'type': 'additional'
                })
        elif self.actual_amount < self.estimated_amount:
            # Refund amount to be given to each member
            refund_amount = (self.estimated_amount - self.actual_amount) / members_count
            for member in self.members.all():
                contributions.append({
                    'member': member,
                    'amount': refund_amount,
                    'type': 'refund'
                })
        return contributions


class GroupExpense(BaseModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="expenses")
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
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