from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from payments.views import PaymentPlanViewSet, InstallmentViewSet
from users.views import (
    UserRegistrationView,
    CustomTokenObtainPairView,
    TokenRefreshView
)

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
    permission_classes=(permissions.AllowAny,)
)

# API URL Patterns
api_urlpatterns = [
    # Authentication endpoints
    path('user/register/', UserRegistrationView.as_view(), name='register'),
    path('user/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    # Include router URLs
    path('', include(router.urls)),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns)),  # All API endpoints under /api/

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Health Check
    path('health/', lambda request: HttpResponse("OK")),
]