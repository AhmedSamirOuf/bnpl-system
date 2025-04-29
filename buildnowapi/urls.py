# bnpu/urls.py
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from payments.views import PaymentPlanViewSet, InstallmentViewSet

router = routers.DefaultRouter()
router.register(r'plans', PaymentPlanViewSet, basename='plan')
router.register(r'installments', InstallmentViewSet, basename='installment')

schema_view = get_schema_view(
    openapi.Info(
        title="BNPU API",
        default_version='v1',
        description="BNPU Payment Plan System",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    # Authentication Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Health Check
    path('health/', lambda request: HttpResponse("OK")),
]