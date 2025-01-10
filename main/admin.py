from django.contrib import admin
from .models import Group, GroupExpense, GroupContribution


# Register your models here.
admin.site.register(Group)
admin.site.register(GroupExpense)
admin.site.register(GroupContribution)