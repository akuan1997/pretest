from django.contrib import admin, messages
from .models import Order, Product
from django.db.models import Sum


# 建立一個繼承自 admin.ModelAdmin 的 class
class OrderAdmin(admin.ModelAdmin):
    # list_display (tuple / list)，放入想要在列表頁顯示的 "欄位名稱" (string)
    list_display = ('id', 'order_number', 'total_price', 'created_time')
    list_filter = ('created_time',)  # 篩選器，時間
    search_fields = ('order_number',)  # 搜尋框，訂單編號
    readonly_fields = ('total_price', 'created_time')  # 總價設為唯讀，避免更改

    actions = ['recalculate_total_price']

    @admin.action(description='根據所選產品重新計算總價')
    def recalculate_total_price(self, request, queryset):
        updated_count = 0
        for order in queryset:
            # 計算關聯產品的價格總和
            # .aggregate(total=Sum('price')) 讓資料庫幫我們計算 price 欄位的總和
            # ['total'] or 0: 如果沒有產品，總和為None，我們把它變成0
            calculated_price = order.products.aggregate(total=Sum('price'))['total'] or 0
            if order.total_price != calculated_price:
                order.total_price = calculated_price
                order.save()
                updated_count += 1

            # 只有在價格不一致時才更新，避免不必要的寫入
            if order.total_price != calculated_price:
                order.total_price = calculated_price
                order.save()  # 儲存變更到資料庫
                updated_count += 1

            self.message_user(request, f'{updated_count}筆訂單的總價已成功更新。', messages.SUCCESS)

    def save_related(self, request, form, formsets, change):
        # 先呼叫父類別的原始 save_related 方法，讓 Django 先完成產品關係的儲存
        super().save_related(request, form, formsets, change)

        # form.instance 代表正在被編輯的 Order 物件
        order = form.instance

        # 執行和 action 中完全相同的計算邏輯
        calculated_price = order.products.aggregate(total=Sum('price'))['total'] or 0

        # 如果價格不一致，舊更新它
        if order.total_price != calculated_price:
            order.total_price = calculated_price
            order.save()


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name',)


admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
