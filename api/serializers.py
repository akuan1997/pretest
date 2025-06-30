from django.db import transaction
from rest_framework import serializers
from .models import Order, Product, OrderItem


# 驗證 "products_data" 列表中的每一個項目
class OrderItemRequestSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    # products_data 專門用來接收 API 的輸入
    # write_only=True 代表這個欄位只會在"寫入" (像是建立還有更新) 的時候使用
    products_data = OrderItemRequestSerializer(many=True, write_only=True, required=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'total_price', 'created_time', 'products_data', 'products']
        read_only_fields = ['id', 'total_price', 'created_time', 'products']

    def validate(self, data):
        # 1. 檢查 order_number 是否已經存在
        if Order.objects.filter(order_number=data['order_number']).exists():
            raise serializers.ValidationError(f"Order with order_number '{data['order_number']}' already exists.")

        # 2. 檢查所有傳入的 product_id 是否都已經存在於資料庫當中
        product_ids = [item['product_id'] for item in data['products_data']]
        # 一次性查詢所需要的產品
        existing_products_count = Product.objects.filter(id__in=product_ids).count()

        if existing_products_count != len(product_ids):
            raise serializers.ValidationError("One or more product IDs are invalid or do nto exist.")

        return data

    @transaction.atomic  # 園子性
    def create(self, validated_data):
        # 驗證過的 'products_data' 取出
        products_data = validated_data.pop('products_data')
        # 為了方便計算，一次性把產品價格放到字典當中
        products_ids = [item['product_id'] for item in products_data]
        products = Product.objects.filter(id__in=products_ids)
        product_price_map = {product.id: product.price for product in products}

        # 3. 根據產品價格和數量，計算訂單總價
        total_price = sum(product_price_map[item['product_id']] * item['quantity'] for item in products_data)

        # 4. 建立 Order 物件，把計算好的總價放進去
        order = Order.objects.create(total_price=total_price, **validated_data)

        # 5. 準備要批次建立的 OrderItem 物件列表
        order_items_to_create = [
            OrderItem(
                order=order,
                product_id=item['product_id'],
                quantity=item['quantity']
            ) for item in products_data
        ]
        # 使用 bulk_create 一次性地將所有訂單項目插入資料庫，效能會比迴圈單筆建立好很多
        OrderItem.objects.bulk_create(order_items_to_create)

        return order
