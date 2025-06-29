from django.contrib import admin
from .models import Order


# 建立一個繼承自 admin.ModelAdmin 的 class
class OrderAdmin(admin.ModelAdmin):
    # list_display (tuple / list)，放入想要在列表頁顯示的 "欄位名稱" (string)
    list_display = ('id', 'order_number', 'total_price', 'created_time')
    list_filter = ('created_time',)  # 篩選器，時間
    search_fields = ('order_number',)  # 搜尋框，訂單編號


admin.site.register(Order, OrderAdmin)
