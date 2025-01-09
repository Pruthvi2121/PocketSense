from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ExpenseViewSet, GroupViewSet

router = SimpleRouter()
router.register(r'expenses', ExpenseViewSet)
router.register(r'group', GroupViewSet)

urlpatterns = [
   
]+router.urls