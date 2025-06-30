from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="產品名稱")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="產品單價")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "產品"
        verbose_name_plural = verbose_name


class Order(models.Model):
    # 訂單編號：使用CharField 訂單通常是字串且唯一
    order_number = models.CharField(max_length=255, unique=True, verbose_name="訂單編號")
    # 金錢使用 DecimalField
    # 後續由程式自動計算價格，因此我們給予一個預設值
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="總價", default=0.00)
    # 時間： auto_now_add=True 建立就填入當前時間
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    # 建立多對多關係
    # 指定中介模型，Order & Product 的關係是透過一個叫做 "OrderItem" 的模型來維護的
    products = models.ManyToManyField(
        Product,
        through='OrderItem',
        through_fields=('order', 'product'),
        verbose_name="包含產品"
    )

    def __str__(self):
        # shell 可讀性
        return self.order_number

    class Meta:
        # Admin 後臺顯示的名字
        verbose_name = "訂單"
        verbose_name_plural = verbose_name
        ordering = ['-created_time']  # 倒序


# 中介模型
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="所屬訂單")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="產品")
    quantity = models.PositiveIntegerField(default=1, verbose_name="數量")

    class Meta:
        verbose_name = "訂單項目"
        verbose_name_plural = verbose_name
        unique_together = ('order', 'product')  # 確保一筆訂單，同一個產品只會出現一次

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name} (x{self.quantity})"
