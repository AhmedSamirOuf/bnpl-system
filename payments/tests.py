from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from .models import PaymentPlan, Installment
from rest_framework_simplejwt.tokens import RefreshToken  # Changed to JWT


class PlanAPITest(APITestCase):
    def setUp(self):
        # Create test users
        self.merchant = User.objects.create_user(
            email='merchant@test.com',
            password='testpass123',
            role='merchant'
        )
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            role='user'
        )
        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123',
            role='user'
        )

        # Generate JWT tokens
        self.merchant_token = str(RefreshToken.for_user(self.merchant).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.other_user_token = str(RefreshToken.for_user(self.other_user).access_token)

        # Create test plan
        self.plan = PaymentPlan.objects.create(
            merchant=self.merchant,
            user_email=self.user.email,
            total_amount=1000.00,
            installments_count=4,
            start_date=timezone.now().date()
        )

        # Create installments
        for i in range(4):
            Installment.objects.create(
                payment_plan=self.plan,
                amount=250.00,
                due_date=self.plan.start_date + relativedelta(months=i),
                status='pending'
            )

        # Create another plan that shouldn't be accessible
        self.other_plan = PaymentPlan.objects.create(
            merchant=self.merchant,
            user_email=self.other_user.email,
            total_amount=2000.00,
            installments_count=3,
            start_date=timezone.now().date()
        )

    def test_list_user_plans(self):
        """Test user can only see their own plans"""
        url = reverse('plan-list')
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user_email'], self.user.email)

    def test_user_cannot_access_other_plans(self):
        """Test user cannot see other users' plans"""
        url = reverse('plan-detail', kwargs={'pk': self.other_plan.id})
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_merchant_plans(self):
        """Test merchant can see all plans they created"""
        url = reverse('plan-list')
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.merchant_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_plan_success(self):
        """Test merchant can create a new plan"""
        url = reverse('plan-list')
        data = {
            'user_email': self.user.email,
            'total_amount': '1500.00',
            'installments_count': 3,
            'start_date': timezone.now().date().isoformat()
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=f'Bearer {self.merchant_token}',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PaymentPlan.objects.count(), 3)

    def test_create_plan_invalid_payload(self):
        """Test plan creation fails with invalid data"""
        url = reverse('plan-list')
        data = {
            'user_email': 'invalid-email',
            'total_amount': 'not-a-number',
            'installments_count': 4
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=f'Bearer {self.merchant_token}',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user_email', response.data)
        self.assertIn('total_amount', response.data)

    def test_create_plan_unauthorized(self):
        """Test regular user cannot create plans"""
        url = reverse('plan-list')
        data = {
            'user_email': self.user.email,
            'total_amount': '1500.00',
            'installments_count': 3,
            'start_date': timezone.now().date().isoformat()
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pay_installment(self):
        """Test user can pay an installment"""
        installment = self.plan.installments.first()
        url = reverse('installment-pay', kwargs={'pk': installment.id})
        response = self.client.patch(
            url,
            {'status': 'paid'},
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        installment.refresh_from_db()
        self.assertEqual(installment.status, 'paid')

    def test_pay_already_paid_installment(self):
        """Test cannot pay an already paid installment"""
        installment = self.plan.installments.first()
        installment.status = 'paid'
        installment.save()

        url = reverse('installment-pay', kwargs={'pk': installment.id})
        response = self.client.patch(
            url,
            {'status': 'paid'},
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Already paid', response.data['error'])

    def test_plan_marked_completed(self):
        """Test plan is marked completed when all installments are paid"""
        # Pay all installments
        for installment in self.plan.installments.all():
            url = reverse('installment-pay', kwargs={'pk': installment.id})
            self.client.patch(
                url,
                {'status': 'paid'},
                HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
                format='json'
            )

        self.plan.refresh_from_db()
        self.assertEqual(self.plan.installments.filter(status='paid').count(), 4)
        self.assertEqual(self.plan.status, 'completed')
