from django.shortcuts import render
from django.http import HttpResponseBadRequest
from rest_framework.decorators import api_view
from rest_framework.request import Request  # Type Hinting
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .decorators import token_required

# # 通常這個會放在settings.py或是環境變數
ACCEPTED_TOKEN = ('omni_pretest_token')


@api_view(['POST'])  # 指定這個view只接受 POST 請求
@token_required  # 放在api_view下方
def import_order(request):
    """ 匯入訂單的API

    透過 POST 請求接收訂單資料，經過驗證後建立新的訂單紀錄

    Args:
        request (Request) : DRF 的 Request 物件
            request.data 應該包含以下欄位：
            - access-token (str) 用於驗證
            - order_number (str) 唯一訂單編號
            - total_price (Decimal / float / int) 訂單總金額
    Returns:
        Response:
            - 成功 (HTTP 201 Created):
                {
                    "message": "Order created successfully",
                    "order": {
                        "id": int,
                        "order_number": str,
                        "total_price": str,
                        "created_time": ISO-8601"
                    }
                }
            - 失敗 (HTTP 4xx):
                { "error": "錯誤描述訊息" }
                400 (請求無效) / 401 (未授權) / 409 (資源衝突)
    """

    # 2. 解析資料
    order_number = request.data.get('order_number')
    total_price = request.data.get('total_price')

    # 2.1 檢查必要的欄位是否exist
    if not order_number or total_price is None:
        return Response(
            {"error": "Missing required fields: order_number or total_price"},
            status=status.HTTP_400_BAD_REQUEST  # Bad Request
        )

    # 2.2 檢查訂單是否已經存在
    if Order.objects.filter(order_number=order_number).exists():
        return Response(
            {"error": f"Order with order_number '{order_number} already exists."},
            status=status.HTTP_409_CONFLICT  # 409 衝突
        )

    # 3. 儲存到對應欄位
    try:
        order = Order.objects.create(
            order_number=order_number,
            total_price=total_price
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to create order. Error: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 4. 回傳成功的回應
    response_data = {
        "message": "Order created successfully!",
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "total_price": str(order.total_price),  # Decimal 轉為字串，方便後面做JSON序列化
            "created_time": order.created_time.isoformat()
        }
    }
    return Response(response_data, status=status.HTTP_201_CREATED)
