from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ExpenseViewSet, GroupViewSet, GroupAnalysisViewSet

router = SimpleRouter()
router.register(r'expenses', ExpenseViewSet)
router.register(r'group', GroupViewSet)
router.register(r'group-stats', GroupAnalysisViewSet, basename="group-stats")

urlpatterns = [
   
]+router.urls