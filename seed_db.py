# seed_db.py
import os
import django
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buildnowapi.settings')  # Changed to bnpl.settings
django.setup()

from users.models import User
from payments.models import PaymentPlan, Installment  # Changed from payments to plans
from rest_framework.authtoken.models import Token


def create_users():
    # Create merchants
    admin = User.objects.create_superuser(
        email='admin@example.com',
        role='merchant',  # Must be one of the ROLE_CHOICES
        password='admin123'
    )

    merchant1 = User.objects.create_user(
        email='merchant1@example.com',
        password='test123',
        role='merchant'  # Changed to string literal
    )

    merchant2 = User.objects.create_user(
        email='merchant2@example.com',
        password='test123',
        role='merchant'  # Changed to string literal
    )

    # Create regular users
    users = [
        User.objects.create_user(
            email=f'user{i}@example.com',
            password='test123',
            role='user'  # Changed to string literal
        ) for i in range(1, 4)
    ]

    return admin, merchant1, merchant2, users

def create_plans_and_installments(merchants, users):
    test_plans = [
        {
            'total_amount': Decimal('1000.00'),
            'installments_count': 4,  # Matches model field name
            'start_date': timezone.now().date(),
        },
        {
            'total_amount': Decimal('1500.50'),
            'installments_count': 3,
            'start_date': timezone.now().date() + relativedelta(months=1),
        },
        {
            'total_amount': Decimal('799.99'),
            'installments_count': 5,
            'start_date': timezone.now().date() - relativedelta(months=2),
        }
    ]

    for merchant in merchants:
        for idx, plan_data in enumerate(test_plans):
            user = users[idx % len(users)]
            plan = PaymentPlan.objects.create(
                merchant=merchant,
                user_email=user.email,
                total_amount=plan_data['total_amount'],
                installments_count=plan_data['installments_count'],  # Correct field name
                start_date=plan_data['start_date']
            )

            # Create installments
            base_amount = plan.total_amount / plan.installments_count  # Updated field reference
            base_amount = base_amount.quantize(Decimal('0.00'))
            remainder = plan.total_amount - (base_amount * (plan.installments_count - 1))

            for i in range(plan.installments_count):
                amount = base_amount if i < plan.installments_count - 1 else remainder
                due_date = plan.start_date + relativedelta(months=i)

                Installment.objects.create(
                    payment_plan=plan,  # Correct FK field name
                    amount=amount,
                    due_date=due_date,
                    status='paid' if i < 2 else 'pending'  # Lowercase status
                )

def generate_tokens():
    # Get all users
    users = User.objects.all()

    # Create tokens for users without one
    for user in users:
        Token.objects.get_or_create(user=user)

    # Print tokens
    for user in users:
        print(f"Email: {user.email} | Token: {user.auth_token.key}")

def main():
    print("Deleting old data...")
    User.objects.all().delete()
    PaymentPlan.objects.all().delete()
    Installment.objects.all().delete()

    print("Creating new data...")
    admin, merchant1, merchant2, users = create_users()
    create_plans_and_installments([merchant1, merchant2], users)

    print("Seed completed successfully!")
    print(f"Created {User.objects.count()} users")
    print(f"Created {PaymentPlan.objects.count()} plans")  # Correct model name
    print(f"Created {Installment.objects.count()} installments")

    generate_tokens()


if __name__ == '__main__':
    main()