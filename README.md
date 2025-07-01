
# Omni Pretest Submission: Building a Robust & Smart Order Management API

Hello Bebit Tech Team,

This repository contains my solution for the Omni Pretest. I've focused on building a secure, efficient, and user-friendly order management API using Django REST Framework. My approach ensures all core requirements are met while also extending functionalities to demonstrate a holistic understanding of system design, data integrity, and best practices.

| 項目說明                                                                 | 狀態  | 備註說明 |
|--------------------------------------------------------------------------|-------|----------|
| Construct Order Model in `api` app                                       | ✅  | 包含 `order_number`, `total_price`, `created_time` |
| Construct `import_order` API (POST /api/import-order/)                  | ✅  | 自動計算 `total_price`、資料驗證、異常處理 |
| Construct API unit tests                                                 | ✅  | 使用 `APITestCase` 覆蓋成功與錯誤情境 |
| Replace access token check with decorator                                | ✅  | 使用 `@token_required` 自定義裝飾器，符合 DRY 原則 |
| Extend Order model                                                       | ✅  | 建立 `OrderItem` 中介模型，支援多商品與數量 |
| Construct Product model & Build relationship with Order                 | ✅  | 使用 `through=OrderItem` 設計，結構彈性可擴充 |
| Get creative and Extend anything you want                                | ✅  | ✅ 強化 Django Admin 管理介面（inline 編輯、唯讀欄位）<br>✅ 使用 `transaction.atomic` 確保資料一致性<br>✅ 整合總價自動更新邏輯於 Admin 中 |

---

## Key Features & Technical Highlights

I've structured the solution to address both the specified requirements and to provide a robust, maintainable foundation:

### 1. **Intelligent Order Import API (`POST /api/import-order/`)**
- **Automated Total Price Calculation**: The API intelligently calculates the `total_price` based on the `product_id` and `quantity` provided in the request payload. This shifts critical business logic to the backend, reducing client-side errors and ensuring data accuracy.
- **Atomic Transactions**: The order creation process (including `Order` and `OrderItem` records) is wrapped in a database transaction (`@transaction.atomic`), guaranteeing data consistency. If any step fails, the entire operation is rolled back.
- **Comprehensive Validation**: Utilizes Django REST Framework Serializers to validate incoming data rigorously, including:
  - Uniqueness checks for `order_number`.
  - Existence checks for all `product_id`s.
  - Quantity validation (`min_value=1`).

### 2. **Robust & Scalable Data Model**
- **`Order` & `Product` Models**: Designed with `DecimalField` for financial precision in `price` and `total_price`.
- **`OrderItem` (Through Model)**: Instead of a simple `ManyToManyField`, a dedicated `OrderItem` model is used as a `through` table. This crucial enhancement allows for storing additional data like `quantity` for each product within an order, accurately reflecting real-world ordering scenarios. It provides a flexible and scalable foundation for future features.

### 3. **Enhanced API Authentication**
- **`@token_required` Decorator**: The access token validation logic has been extracted into a reusable custom decorator (`@token_required`). This cleanly separates authentication concerns from the core business logic in the view, promoting the DRY (Don't Repeat Yourself) principle and improving code readability.
- The accepted token is centrally configured in `settings.py`.

### 4. **Empowered Django Admin Interface**
- **Automatic Total Price Recalculation**: By overriding the `save_related` method in `OrderAdmin`, the `total_price` for an order is **automatically recalculated and updated** whenever an order or its associated `OrderItem`s are saved in the Django Admin.
- **Inline Order Item Management**: `OrderItemInline` allows administrators to intuitively view, add, and modify products and their quantities directly within the Order editing page.
- **Read-Only Critical Fields**: `total_price` and `created_time` are set as read-only in the Admin to prevent accidental manual modifications, safeguarding data integrity.
- **Improved Usability**: Customized `list_display`, `list_filter`, and `search_fields` provide a clear and efficient overview of orders and products in the Admin panel.

### 5. **Comprehensive Unit Testing**
- **`APITestCase`**: A thorough test suite using Django REST Framework's `APITestCase` ensures the reliability of the `import_order` API endpoint.
- **Extensive Coverage**: Tests cover various scenarios including:
  - Successful order creation with correct total price calculation.
  - Invalid product IDs.
  - Duplicate `order_number`s.
  - Missing required fields.
  - Invalid/missing `access_token`.

---

## Setup Environment

Follow these steps to get the project running locally using Docker:

1. **Download and Install Docker**:  
   Ensure Docker Desktop (or Docker Engine) is installed on your system.  
   👉 [https://www.docker.com/get-started](https://www.docker.com/get-started)

2. **Fork the Repository**:
   Fork this pretest project to your own GitHub repository.

3. **Clone Your Fork**:
   ```bash
   git clone https://github.com/[your_own_account]/pretest.git
   ```

4. **Navigate to Project Directory**:
   ```bash
   cd pretest
   ```

5. **Start Docker Containers**:
   This will build the images and start the `web` and `db` services.
   ```bash
   docker-compose up --build -d
   ```

6. **Enter the Web Container**:
   ```bash
   docker exec -it pretest-web-1 bash
   ```

7. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

8. **Create a Superuser (Optional, for Admin Access)**:
   ```bash
   python manage.py createsuperuser
   ```

---

## API Endpoints

### `POST /api/import-order/`

This endpoint allows for importing new orders with multiple products, automatically calculating the total price.

#### Request Body Example
```json
{
  "access_token": "omni_pretest_token", 
  "order_number": "YOUR-UNIQUE-ORDER-NUMBER-123",
  "products_data": [
    { "product_id": 1, "quantity": 2 },
    { "product_id": 3, "quantity": 1 }
  ]
}
```

#### Fields:
- **access_token** (string, required): The API validation token (currently `omni_pretest_token`).
- **order_number** (string, required): A unique identifier for the order.
- **products_data** (list of objects, required): Contains product info.
  - `product_id` (integer, required): The product ID.
  - `quantity` (integer, required): Quantity (> 0).

#### Success Response (`HTTP 201 Created`)
```json
{
  "id": 1,
  "order_number": "YOUR-UNIQUE-ORDER-NUMBER-123",
  "total_price": "5200.75",
  "created_time": "2025-06-30T14:30:00Z",
  "products": [1, 3]
}
```

#### Error Responses:
- `400 Bad Request`: Invalid input (e.g., missing fields, wrong product ID, duplicate order number).
- `401 Unauthorized`: Missing or invalid `access_token`.

---

## Running Tests

To execute the test suite:

```bash
docker exec -it pretest-web-1 bash
python manage.py test api
```

---

## Future Enhancements (Optional)

Potential areas for future development:

- **JWT Authentication**: Replace static token with JWT-based auth for scalability.
- **Full CRUD Operations**: Implement all CRUD endpoints using Django REST Framework’s ModelViewSet.
- **API Versioning**: Use `/api/v1/` to allow backward-compatible changes.
- **Pagination & Filtering**: Add filtering and pagination for scalability.

---

## Submission Notes

- **Deadline**: This pretest was completed within the 7-day timeframe.
- **Pull Request**: Named with my Chinese and English name as shown in my resume.

Thank you for the opportunity to work on this challenge. I believe this submission reflects not just the ability to write code, but to design and architect thoughtful, scalable, and user-centric solutions. I look forward to discussing my approach with you.

Best regards,  
**Kuan (池俊寬)**
