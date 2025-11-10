"""
Common views.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from issues.models import Customer


class UserListView(APIView):
    """用戶列表（用於下拉選單）"""
    
    def get(self, request):
        users = User.objects.filter(is_active=True).order_by('username')
        return Response([
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
            for user in users
        ])


class CustomerListView(APIView):
    """客戶列表（用於下拉選單和 Custom 頁面）"""
    
    def get(self, request):
        customers = Customer.objects.all().order_by('name')
        return Response([
            {
                'id': customer.id,
                'name': customer.name,
                'code': customer.code,
                'contact_person': customer.contact_person,
                'contact_email': customer.contact_email,
                'business_owner': customer.business_owner,
                'handover_completed': customer.handover_completed,
                'training_completed': customer.training_completed,
                'internal_network_connected': customer.internal_network_connected,
                'warranty_due': customer.warranty_due,
                'created_at': customer.created_at,
                'updated_at': customer.updated_at,
            }
            for customer in customers
        ])
    
    def post(self, request):
        """創建客戶"""
        from issues.serializers import CustomerSerializer
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetailView(APIView):
    """客戶詳細（更新/刪除）"""
    
    def get(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        from issues.serializers import CustomerSerializer
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """更新客戶"""
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        from issues.serializers import CustomerSerializer
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """刪除客戶"""
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        customer.delete()
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)
