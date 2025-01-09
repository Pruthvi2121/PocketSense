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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.admin not in self.members.all():
            self.members.add(self.admin)
  

# class GroupMember(BaseModel):
#     group = models.ForeignKey(Group, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     role = models.CharField(max_length=20, default='member')  # 'admin' or 'member'
#     joined_at = models.DateTimeField(auto_now_add=True)

# class GroupExpense(BaseModel):
#     group = models.ForeignKey(Group, on_delete=models.CASCADE)
#     description = models.TextField()
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
    

# class GroupExpenseContribution(BaseModel):
#     group_expense = models.ForeignKey(GroupExpense, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='unpaid')