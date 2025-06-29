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
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="總價")
    # 時間： auto_now_add=True 建立就填入當前時間
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    # 建立多對多關係
    products = models.ManyToManyField(Product, verbose_name="包含產品")

    def __str__(self):
        # shell 可讀性
        return self.order_number

    class Meta:
        # Admin 後臺顯示的名字
        verbose_name = "訂單"
        verbose_name_plural = verbose_name
        ordering = ['-created_time']  # 倒序
