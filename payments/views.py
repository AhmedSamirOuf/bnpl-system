from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from .serializers import InstallmentSerializer,PlanSerializer
from .permissions import IsPlanUser, IsMerchant

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PaymentPlan, Installment
from .serializers import PlanSerializer, PlanDetailSerializer


class PaymentPlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]  # Base permission

    def get_serializer_context(self):
        """Add request user to serializer context"""
        context = super().get_serializer_context()
        context.update({'merchant': self.request.user})
        return context

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PlanDetailSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsMerchant()]
        elif self.action in ['retrieve', 'list']:
            return [IsAuthenticated(), IsPlanUser()]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.role == 'merchant':
            return PaymentPlan.objects.filter(merchant=self.request.user)
        return PaymentPlan.objects.filter(user_email=self.request.user.email)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        response_data = serializer.data
        response_data['total_paid'] = instance.installments.filter(status='paid').aggregate(
            Sum('amount'))['amount__sum'] or 0
        response_data['progress_percentage'] = int(
            (response_data['total_paid'] / instance.total_amount * 100))

        return Response(response_data)


class InstallmentViewSet(viewsets.GenericViewSet):
    queryset = Installment.objects.all()
    serializer_class = InstallmentSerializer

    def get_permissions(self):
        if self.action == 'pay':
            self.permission_classes = [IsAuthenticated, IsPlanUser]
        return super().get_permissions()

    @action(detail=True, methods=['PATCH'], url_path='pay')
    def pay(self, request, pk=None):
        installment = self.get_object()

        if installment.status == 'paid':
            return Response(
                {'error': 'Already paid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(installment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(status='paid', paid_at=serializer.validated_data.get('paid_at'))

        return Response({'status': 'success'})