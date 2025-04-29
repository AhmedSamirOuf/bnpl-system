from rest_framework import permissions

class IsMerchant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'merchant'

class IsPlanUser(permissions.BasePermission):
    def has_permission(self, request, view):
        """Check at the view level"""
        return True  # Object permission will handle the actual check

    def has_object_permission(self, request, view, obj):
        """Check if user matches payment plan's user_email"""
        # For Installment objects
        if hasattr(obj, 'payment_plan'):
            return request.user.email == obj.payment_plan.user_email
        # For PaymentPlan objects
        return request.user.email == obj.user_email

class IsMerchantOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.merchant

