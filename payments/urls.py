from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentPlanViewSet, InstallmentViewSet

router = DefaultRouter()
router.register(r'plans', PaymentPlanViewSet, basename='plan')

urlpatterns = [
    path('', include(router.urls)),
    path('installments/<int:pk>/pay/', InstallmentViewSet.as_view({'post': 'pay'}), name='installment-pay'),
]