from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request  # Type Hinting
from rest_framework import status
from .decorators import token_required
from .serializers import OrderSerializer


@api_view(['POST'])  # 指定這個view只接受 POST 請求
@token_required  # 放在api_view下方
def import_order(request):
    """
        匯入包含多個產品的訂單，並自動計算總價。

        這個 API 端點接收一個訂單號和一個產品列表，然後會：
        1. 驗證所有輸入資料的有效性（如產品ID是否存在、數量是否合法）。
        2. 根據產品單價和數量，自動計算整筆訂單的總金額。
        3. 在資料庫中建立一筆新的 "Order" 紀錄以及相關的 "OrderItem" 紀錄。
        4. 這整個過程在一個資料庫事務中完成，確保資料一致性。

        ---

        Request Body (請求內容) 格式:

        "POST /api/import-order/"

    	json
        {
            "access_token": "omni_pretest_token",
            "order_number": "YOUR-UNIQUE-ORDER-NUMBER-123",
            "products_data": [
                { "product_id": 1, "quantity": 2 },
                { "product_id": 3, "quantity": 1 }
            ]
        }

        - access_token (str, required): 用於 API 驗證的令牌。
        - order_number (str, required): 唯一的訂單編號。
        - products_data (list[dict], required): 包含的產品列表。
            - product_id (int, required): 產品在資料庫中的 ID。
            - quantity (int, required): 該產品的購買數量，必須大於 0。

        ---

        Success Response (成功回應) (HTTP 201 Created):

    	json
        {
            "id": 1,
            "order_number": "YOUR-UNIQUE-ORDER-NUMBER-123",
            "total_price": "5200.75",
            "created_time": "2025-06-30T14:30:00Z",
            "products": [1, 3]
        }


        - total_price 會由後端自動計算。
        - products 列表顯示此訂單關聯的所有產品的 ID。

        ---

        Error Responses (錯誤回應):

        - HTTP 400 Bad Request: 輸入資料驗證失敗（例如：缺少欄位、"product_id" 不存在、"order_number" 重複、"quantity" 小於1）。回應內容會包含詳細的錯誤訊息。
        - HTTP 401 Unauthorized: "access_token" 無效或未提供。
    """

    # 1. 將 request.data 交給 Serializer 進行處理 (複雜的驗證和資料處理)
    serializer = OrderSerializer(data=request.data)

    # 2. is_valid() 會自動運行在 Serializer 中定義的所有 validate 方法
    # raise_exception=True 驗證如果失敗 DRF 會自動拋出異常
    serializer.is_valid(raise_exception=True)

    # 3. 驗證通過，呼叫 .save()，觸發 .create() 方法，完成計算與資料庫建立的操作
    serializer.save()

    return Response(serializer.data, status=status.HTTP_201_CREATED)
