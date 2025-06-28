from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Order
from .views import ACCEPTED_TOKEN

# Create your tests here.
class OrderTestCase(APITestCase):
    def setUp(self):
        # 先設定好要測試的URL以及有效的payload
        self.url = reverse('import_order')
        self.valid_payload = {
            'access_token': ACCEPTED_TOKEN,
            'order_number': 'TEST-ORDER-001',
            'total_price': '99.99'
        }
        self.invalid_payload_token = {
            'access_token': 'wrong_token',
            'order_number': 'TEST-ORDER-002',
            'total_price': '150.00'
        }

    def test_import_order_success(self):
        """測試成功建立訂單"""
        response = self.client.post(self.url, self.valid_payload, format='json')

        # 1. 斷言回應狀態碼為 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2. 斷言資料庫中確實建立了一筆訂單
        self.assertEqual(Order.objects.count(), 1)

        # 3. 斷言建立的訂單資料與我們發送的相符
        order = Order.objects.get()
        self.assertEqual(order.order_number, self.valid_payload['order_number'])
        self.assertEqual(str(order.total_price), self.valid_payload['total_price'])

    def test_import_order_invalid_token(self):
        """測試使用無效 token 的情況"""
        response = self.client.post(self.url, self.invalid_payload_token, format='json')

        # 1. 斷言回應狀態碼為 401 UNAUTHORIZED
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 2. 斷言資料庫中沒有建立任何訂單
        self.assertEqual(Order.objects.count(), 0)

    def test_import_order_missing_field(self):
        """測試缺少必要欄位的情況"""
        payload = {
            'access_token': ACCEPTED_TOKEN,
            # 'order_number' is missing
            'total_price': '50.00'
        }
        response = self.client.post(self.url, payload, format='json')

        # 1. 斷言回應狀態碼為 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 2. 斷言資料庫中沒有建立任何訂單
        self.assertEqual(Order.objects.count(), 0)

    def test_import_order_duplicate_number(self):
        """測試重複訂單號的情況"""
        # 先建立一筆訂單
        self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(Order.objects.count(), 1)

        # 再次嘗試用同一個 order_number 建立
        response = self.client.post(self.url, self.valid_payload, format='json')

        # 1. 斷言回應狀態碼為 409 CONFLICT
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # 2. 斷言資料庫中仍然只有一筆訂單
        self.assertEqual(Order.objects.count(), 1)
