from django.contrib import admin, messages
from .models import Order, Product, OrderItem
from django.db.models import Sum, F


# TabularInline 讓 OrderItem 能在 Order 的編輯頁面中以表格的形式呈現和編輯
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'get_item_price')
    readonly_fields = ('get_item_price',)  # 將單項總價設為唯讀
    extra = 1  # 預設顯示一個空白的項目欄位，方便新增

    # 自訂方法，顯示 "產品單價 * 數量"
    @admin.display(description="單項總價")
    def get_item_price(self, obj):
        # obj 是 OrderItem 的實例
        if obj.pk:  # 確保已經存在資料庫
            return obj.quantity * obj.product.price
        return "N/A"  # 尚未儲存的新項目


# 建立一個繼承自 admin.ModelAdmin 的 class
class OrderAdmin(admin.ModelAdmin):
    # 將 OrderItemInline 加入倒 Order 的編輯頁面中
    inlines = [OrderItemInline]

    # list_display (tuple / list)，放入想要在列表頁顯示的 "欄位名稱" (string)
    list_display = ('id', 'order_number', 'total_price', 'created_time')
    list_filter = ('created_time',)  # 篩選器，時間
    search_fields = ('order_number',)  # 搜尋框，訂單編號
    readonly_fields = ('total_price', 'created_time')  # 總價設為唯讀，避免更改

    # 捨棄 action，因為 save_related 的邏輯會更完善
    def save_related(self, request, form, formsets, change):
        # 先呼叫父類別的原始 save_related 方法，讓 Django 先完成產品關係的儲存
        super().save_related(request, form, formsets, change)

        # form.instance 代表正在被編輯的 Order 物件
        order = form.instance

        aggregation = order.orderitem_set.aggregate(
            calculated_price=Sum(F('quantity') * F('product__price'))
        )

        calculated_price = aggregation.get('calculated_price') or 0

        # 如果價格不一致，舊更新它
        if order.total_price != calculated_price:
            order.total_price = calculated_price
            order.save()


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name',)


admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
