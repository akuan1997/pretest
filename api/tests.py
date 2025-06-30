from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Order
from django.conf import settings
from .models import Order, Product, OrderItem
from decimal import Decimal


# Create your tests here.
class OrderAPITestCase(APITestCase):
    def setUp(self):
        """在每個測試執行前，先準備好環境"""
        self.url = reverse('import_order')

        # 建立一些測試用的產品，讓我們可以引用它們的 ID
        self.product1 = Product.objects.create(name="高階鍵盤", price="2500.50")
        self.product2 = Product.objects.create(name="人體工學滑鼠", price="1200.00")

        # 準備一個符合新 API 格式的有效 payload
        self.valid_payload = {
            'access_token': settings.ACCEPTED_TOKEN,
            'order_number': 'TEST-ORDER-001',
            'products_data': [
                {'product_id': self.product1.id, 'quantity': 2},  # 2500.50 * 2 = 5001.00
                {'product_id': self.product2.id, 'quantity': 3}  # 1200.00 * 3 = 3600.00
            ]
        }
        # 預期總價: 5001.00 + 3600.00 = 8601.00

    def test_import_order_success(self):
        """測試：成功建立訂單，並驗證自動計算的總價和關聯"""
        response = self.client.post(self.url, self.valid_payload, format='json')

        # 1. 斷言回應狀態碼為 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2. 斷言資料庫中確實建立了一筆訂單和兩筆訂單項目
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 2)

        # 3. 斷言訂單的總價被正確計算
        order = Order.objects.get()
        self.assertEqual(order.order_number, self.valid_payload['order_number'])
        self.assertEqual(order.total_price, Decimal('8601.00'))

        # 4. 斷言關聯的產品數量也正確
        self.assertEqual(order.products.count(), 2)

        # 5. 斷言 API 回應的資料也正確
        self.assertEqual(Decimal(response.data['total_price']), Decimal('8601.00'))

    def test_import_order_invalid_product_id(self):
        """測試：當提供了不存在的 product_id 時，應回傳 400"""
        payload = self.valid_payload.copy()
        # 999 是一個不存在的 product_id
        payload['products_data'] = [{'product_id': 999, 'quantity': 1}]

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)  # 確保沒有建立任何髒資料

    def test_import_order_duplicate_number(self):
        """測試：當使用重複的 order_number 時，應回傳 400"""
        # 先成功建立一筆訂單
        self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(Order.objects.count(), 1)

        # 再次嘗試用同一個 order_number 建立
        response = self.client.post(self.url, self.valid_payload, format='json')

        # 因為驗證邏輯移到了 Serializer，DRF 預設會回傳 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 1)  # 資料庫中訂單數沒變

    def test_import_order_missing_products_data(self):
        """測試：當缺少 'products_data' 欄位時，應回傳 400"""
        payload = {
            'access_token': settings.ACCEPTED_TOKEN,
            'order_number': 'TEST-ORDER-002',
        }
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 檢查 DRF 的錯誤訊息是否指出 'products_data' 是必要欄位
        self.assertIn('products_data', response.data)
        self.assertEqual(response.data['products_data'][0].code, 'required')

    def test_import_order_invalid_token(self):
        """測試：使用無效 token 的情況"""
        payload = self.valid_payload.copy()
        payload['access_token'] = 'wrong_token'
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 0)
