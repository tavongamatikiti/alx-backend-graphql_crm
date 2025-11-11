# ALX Backend GraphQL CRM

A Customer Relationship Management (CRM) system built with Django and GraphQL using `graphene-django`.

## Features

- **GraphQL API** with queries and mutations
- **Customer Management**: Create, bulk create, and query customers
- **Product Management**: Create and manage products with stock tracking
- **Order Management**: Create orders with product associations and automatic total calculation
- **Advanced Filtering**: Filter customers, products, and orders with multiple criteria
- **Validation**: Email uniqueness, phone format validation, price/stock constraints
- **Error Handling**: User-friendly error messages for all operations

## Tech Stack

- **Django 5.2.8**: Web framework
- **graphene-django 3.2.3**: GraphQL integration
- **django-filter 25.2**: Advanced filtering support
- **SQLite**: Database (default)

## Project Structure

```
alx_backend_graphql_crm/
├── alx_backend_graphql_crm/
│   ├── settings.py          # Django settings with GraphQL configuration
│   ├── urls.py              # URL routing with GraphQL endpoint
│   └── schema.py            # Main GraphQL schema
├── crm/
│   ├── models.py            # Customer, Product, Order models
│   ├── schema.py            # GraphQL types, queries, mutations
│   ├── filters.py           # django-filter classes
│   └── migrations/          # Database migrations
├── seed_db.py               # Database seeding script
├── requirements.txt         # Python dependencies
└── manage.py                # Django management script
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd alx_backend_graphql_crm
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Database (Optional)

```bash
python seed_db.py
```

This will create:
- 5 sample customers
- 7 sample products
- 4 sample orders

### 6. Run Development Server

```bash
python manage.py runserver
```

### 7. Access GraphQL Interface

Open your browser and navigate to:
```
http://localhost:8000/graphql
```

You'll see the **GraphiQL** interface for testing queries and mutations.

## GraphQL API Reference

### Task 0: Hello Query

```graphql
{
  hello
}
```

**Response:**
```json
{
  "data": {
    "hello": "Hello, GraphQL!"
  }
}
```

---

### Task 1 & 2: Mutations

#### Create Customer

```graphql
mutation {
  createCustomer(input: {
    name: "Alice",
    email: "alice@example.com",
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
  }
}
```

#### Bulk Create Customers

```graphql
mutation {
  bulkCreateCustomers(input: [
    { name: "Bob", email: "bob@example.com", phone: "123-456-7890" },
    { name: "Carol", email: "carol@example.com" }
  ]) {
    customers {
      id
      name
      email
    }
    errors
  }
}
```

#### Create Product

```graphql
mutation {
  createProduct(input: {
    name: "Laptop",
    price: 999.99,
    stock: 10
  }) {
    product {
      id
      name
      price
      stock
    }
  }
}
```

#### Create Order

```graphql
mutation {
  createOrder(input: {
    customerId: "1",
    productIds: ["1", "2"]
  }) {
    order {
      id
      customer {
        name
      }
      products {
        name
        price
      }
      totalAmount
      orderDate
    }
  }
}
```

---

### Task 3: Queries with Filtering

#### Filter Customers

```graphql
query {
  allCustomers(
    name_Icontains: "Ali",
    createdAt_Gte: "2025-01-01"
  ) {
    edges {
      node {
        id
        name
        email
        createdAt
      }
    }
  }
}
```

#### Filter Products by Price Range

```graphql
query {
  allProducts(
    price_Gte: 100,
    price_Lte: 1000
  ) {
    edges {
      node {
        id
        name
        price
        stock
      }
    }
  }
}
```

#### Filter Orders by Customer Name

```graphql
query {
  allOrders(
    customer_Name_Icontains: "Alice",
    totalAmount_Gte: 500
  ) {
    edges {
      node {
        id
        customer {
          name
        }
        products {
          name
        }
        totalAmount
        orderDate
      }
    }
  }
}
```

## Models

### Customer
- `name`: CharField
- `email`: EmailField (unique)
- `phone`: CharField (optional)
- `created_at`: DateTimeField (auto)

### Product
- `name`: CharField
- `price`: DecimalField (positive, required)
- `stock`: IntegerField (non-negative, default 0)
- `created_at`: DateTimeField (auto)

### Order
- `customer`: ForeignKey to Customer
- `products`: ManyToManyField to Product
- `order_date`: DateTimeField (auto)
- `total_amount`: DecimalField (calculated from products)

## Validation Rules

- **Email**: Must be unique across customers
- **Phone**: Supports formats: `+1234567890` or `123-456-7890`
- **Price**: Must be positive (> 0)
- **Stock**: Must be non-negative (>= 0)
- **Order Products**: At least one product required

## Filtering Capabilities

### Customer Filters
- `name_Icontains`: Case-insensitive partial match
- `email_Icontains`: Case-insensitive partial match
- `createdAt_Gte`: Created after date
- `createdAt_Lte`: Created before date
- `phonePattern`: Phone starts with pattern

### Product Filters
- `name_Icontains`: Case-insensitive partial match
- `price_Gte`: Minimum price
- `price_Lte`: Maximum price
- `stock_Gte`: Minimum stock
- `stock_Lte`: Maximum stock
- `lowStock`: Products with stock < 10

### Order Filters
- `totalAmount_Gte`: Minimum total
- `totalAmount_Lte`: Maximum total
- `orderDate_Gte`: Ordered after date
- `orderDate_Lte`: Ordered before date
- `customer_Name_Icontains`: Filter by customer name
- `products_Name_Icontains`: Filter by product name
- `productId`: Filter by specific product ID

## Testing

Test the GraphQL endpoint using GraphiQL at `http://localhost:8000/graphql`

### Test Checklist

- [x] Task 0: `{ hello }` returns "Hello, GraphQL!"
- [x] Task 1: Create single customer
- [x] Task 1: Bulk create customers
- [x] Task 1: Create product
- [x] Task 1: Create order with products
- [x] Task 2: Validation errors (duplicate email, invalid phone)
- [x] Task 2: Partial success in bulk create
- [x] Task 3: Filter customers by name and date
- [x] Task 3: Filter products by price range
- [x] Task 3: Filter orders by customer/product name

## Development

### Create Superuser

```bash
python manage.py createsuperuser
```

### Access Admin Panel

```
http://localhost:8000/admin
```

### Run Seed Script

```bash
python seed_db.py
```

## Error Handling

All mutations return helpful error messages:

- `"Email already exists"`
- `"Invalid phone number format"`
- `"Customer with ID X does not exist"`
- `"Product with ID X does not exist"`
- `"Price must be positive"`
- `"Stock cannot be negative"`
- `"At least one product is required"`

## Repository

**GitHub**: `alx-backend-graphql_crm`

**Required Files**:
- `settings.py`
- `crm/` (app directory)
- `schema.py` (both main and crm)
- `models.py`
- `filters.py`
- `seed_db.py`

## License

This project is part of the ALX Software Engineering Program.

## Author

ALX Backend Development Track
