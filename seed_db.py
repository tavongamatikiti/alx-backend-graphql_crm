#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Seed script to populate the CRM database with test data.
Usage: python seed_db.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order
from decimal import Decimal

def seed_customers():
    """Create sample customers"""
    customers = [
        {'name': 'Alice Johnson', 'email': 'alice@example.com', 'phone': '+1234567890'},
        {'name': 'Bob Smith', 'email': 'bob@example.com', 'phone': '123-456-7890'},
        {'name': 'Carol Williams', 'email': 'carol@example.com', 'phone': '+9876543210'},
        {'name': 'David Brown', 'email': 'david@example.com', 'phone': ''},
        {'name': 'Eve Davis', 'email': 'eve@example.com', 'phone': '555-123-4567'},
    ]

    created = []
    for customer_data in customers:
        customer, created_flag = Customer.objects.get_or_create(
            email=customer_data['email'],
            defaults={'name': customer_data['name'], 'phone': customer_data['phone']}
        )
        if created_flag:
            created.append(customer)
            print(f" Created customer: {customer.name}")
        else:
            print(f"�  Customer already exists: {customer.name}")

    return created


def seed_products():
    """Create sample products"""
    products = [
        {'name': 'Laptop', 'price': Decimal('999.99'), 'stock': 10},
        {'name': 'Mouse', 'price': Decimal('29.99'), 'stock': 50},
        {'name': 'Keyboard', 'price': Decimal('79.99'), 'stock': 30},
        {'name': 'Monitor', 'price': Decimal('299.99'), 'stock': 15},
        {'name': 'Webcam', 'price': Decimal('89.99'), 'stock': 20},
        {'name': 'Headphones', 'price': Decimal('149.99'), 'stock': 5},  # Low stock
        {'name': 'USB Cable', 'price': Decimal('9.99'), 'stock': 100},
    ]

    created = []
    for product_data in products:
        product, created_flag = Product.objects.get_or_create(
            name=product_data['name'],
            defaults={'price': product_data['price'], 'stock': product_data['stock']}
        )
        if created_flag:
            created.append(product)
            print(f" Created product: {product.name}")
        else:
            print(f"�  Product already exists: {product.name}")

    return created


def seed_orders():
    """Create sample orders"""
    customers = list(Customer.objects.all())
    products = list(Product.objects.all())

    if not customers or not products:
        print("�  No customers or products found. Run seed_customers() and seed_products() first.")
        return []

    orders_data = [
        {'customer': customers[0], 'product_ids': [products[0].id, products[1].id]},  # Laptop + Mouse
        {'customer': customers[1], 'product_ids': [products[2].id, products[3].id]},  # Keyboard + Monitor
        {'customer': customers[2], 'product_ids': [products[4].id]},  # Webcam
        {'customer': customers[0], 'product_ids': [products[5].id, products[6].id]},  # Headphones + USB Cable
    ]

    created = []
    for order_data in orders_data:
        order_products = Product.objects.filter(id__in=order_data['product_ids'])
        total = sum(p.price for p in order_products)

        order = Order.objects.create(
            customer=order_data['customer'],
            total_amount=total
        )
        order.products.set(order_products)
        created.append(order)
        print(f" Created order #{order.id} for {order.customer.name} - ${order.total_amount}")

    return created


def main():
    """Main seeding function"""
    print("=" * 60)
    print("Starting database seeding...")
    print("=" * 60)

    print("\n=� Seeding Customers...")
    customers = seed_customers()
    print(f"Created {len(customers)} new customers\n")

    print("=� Seeding Products...")
    products = seed_products()
    print(f"Created {len(products)} new products\n")

    print("=� Seeding Orders...")
    orders = seed_orders()
    print(f"Created {len(orders)} new orders\n")

    print("=" * 60)
    print("Database seeding completed!")
    print("=" * 60)

    # Print summary
    print("\n=� Database Summary:")
    print(f"   Total Customers: {Customer.objects.count()}")
    print(f"   Total Products: {Product.objects.count()}")
    print(f"   Total Orders: {Order.objects.count()}")
    print("\n Ready to test at: http://localhost:8000/graphql")


if __name__ == '__main__':
    main()
