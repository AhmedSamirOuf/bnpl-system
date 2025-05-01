# serializers.py
from decimal import Decimal, ROUND_DOWN

from dateutil.relativedelta import relativedelta
from rest_framework import serializers
from .models import PaymentPlan, Installment


class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        fields = '__all__'
        read_only_fields = ('status',)
        extra_kwargs = {
            'paid_at': {'required': True}
        }

class PlanSerializer(serializers.ModelSerializer):
    installments = InstallmentSerializer(many=True, read_only=True)

    class Meta:
        model = PaymentPlan
        fields = ['id', 'user_email', 'total_amount', 'installments_count', 'start_date', 'created_at',
                  'installments','status','merchant']
        read_only_fields = ['id', 'created_at', 'installments','merchant']

    def create(self, validated_data):
        merchant = self.context['merchant']
        total = validated_data['total_amount']
        num = validated_data['installments_count']
        start_date = validated_data['start_date']

        # Calculate installments
        installment_amount = (total / num).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        remainder = total - (installment_amount * (num - 1))

        # Create Plan
        plan = PaymentPlan.objects.create(merchant=merchant,**validated_data)

        # Generate Installments
        installments = []
        for i in range(num):
            due_date = start_date + relativedelta(months=+i)
            amount = installment_amount if i < num - 1 else remainder
            installments.append(Installment(
                payment_plan=plan,
                amount=amount,
                due_date=due_date,
            ))
        Installment.objects.bulk_create(installments)
        return plan


class PlanDetailSerializer(PlanSerializer):
    installments = InstallmentSerializer(many=True, read_only=True)

    class Meta(PlanSerializer.Meta):
        fields = PlanSerializer.Meta.fields + ['installments']