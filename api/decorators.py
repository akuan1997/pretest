from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


def token_required(view_func):
    """
    一個 decorator，用來驗證 DRF view 請求中的 access token。

    它會檢查 request payload (request.data) 中是否包含一個有效的 'access_token'。
    如果 token 驗證失敗，會直接回傳一個 HTTP 401 Unauthorized 的回應。
    如果驗證成功，則會繼續執行原始的 view 函式。

    :param view_func: 被裝飾的 Django REST Framework view 函式。
    :type view_func: function
    :return: 包裝後的 view 函式，它會先執行 token 驗證。
    :rtype: function
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # 從 request.data 獲得 token
        token = request.data.get('access_token')

        # 驗證 token 是否正確
        if not token or token != settings.ACCEPTED_TOKEN:
            return Response(
                {"error": "Invalid or missing access token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 如果 token 驗證通過，就執行原始的 view func
        return view_func(request, *args, **kwargs)

    return _wrapped_view
