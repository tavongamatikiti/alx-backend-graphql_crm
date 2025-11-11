import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from decimal import Decimal

from .models import Customer, Product, Order


# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'
        filter_fields = {
            'name': ['icontains', 'exact'],
            'email': ['icontains', 'exact'],
            'created_at': ['gte', 'lte'],
        }
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'
        filter_fields = {
            'name': ['icontains', 'exact'],
            'price': ['gte', 'lte', 'exact'],
            'stock': ['gte', 'lte', 'exact'],
        }
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'
        filter_fields = {
            'total_amount': ['gte', 'lte', 'exact'],
            'order_date': ['gte', 'lte'],
            'customer__name': ['icontains'],
            'products__name': ['icontains'],
        }
        interfaces = (graphene.relay.Node,)


# Mutation Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Validation Functions
def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True
    # Support formats: +1234567890 or 123-456-7890
    pattern = r'^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$'
    return re.match(pattern, phone) is not None


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []

        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append(f"Email '{input.email}' already exists")
            return CreateCustomer(customer=None, message="Failed", errors=errors)

        # Validate phone format
        if input.get('phone') and not validate_phone(input.phone):
            errors.append("Invalid phone number format. Use +1234567890 or 123-456-7890")
            return CreateCustomer(customer=None, message="Failed", errors=errors)

        try:
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.get('phone')
            )
            return CreateCustomer(
                customer=customer,
                message="Customer created successfully",
                errors=None
            )
        except Exception as e:
            errors.append(str(e))
            return CreateCustomer(customer=None, message="Failed", errors=errors)


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    message = graphene.String()

    def mutate(self, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for idx, customer_data in enumerate(input):
                try:
                    # Validate email uniqueness
                    if Customer.objects.filter(email=customer_data.email).exists():
                        errors.append(f"Row {idx+1}: Email '{customer_data.email}' already exists")
                        continue

                    # Validate phone format
                    if customer_data.get('phone') and not validate_phone(customer_data.phone):
                        errors.append(f"Row {idx+1}: Invalid phone number format")
                        continue

                    customer = Customer.objects.create(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.get('phone')
                    )
                    created_customers.append(customer)
                except Exception as e:
                    errors.append(f"Row {idx+1}: {str(e)}")

        message = f"Created {len(created_customers)} customers"
        if errors:
            message += f", {len(errors)} failed"

        return BulkCreateCustomers(
            customers=created_customers,
            errors=errors if errors else None,
            message=message
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []

        # Validate price
        if input.price <= 0:
            errors.append("Price must be positive")
            return CreateProduct(product=None, message="Failed", errors=errors)

        # Validate stock
        stock = input.get('stock', 0)
        if stock < 0:
            errors.append("Stock cannot be negative")
            return CreateProduct(product=None, message="Failed", errors=errors)

        try:
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=stock
            )
            return CreateProduct(
                product=product,
                message="Product created successfully",
                errors=None
            )
        except Exception as e:
            errors.append(str(e))
            return CreateProduct(product=None, message="Failed", errors=errors)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []

        # Validate customer exists
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            errors.append(f"Customer with ID {input.customer_id} does not exist")
            return CreateOrder(order=None, message="Failed", errors=errors)

        # Validate at least one product
        if not input.product_ids or len(input.product_ids) == 0:
            errors.append("At least one product is required")
            return CreateOrder(order=None, message="Failed", errors=errors)

        # Validate products exist
        products = []
        for product_id in input.product_ids:
            try:
                product = Product.objects.get(pk=product_id)
                products.append(product)
            except Product.DoesNotExist:
                errors.append(f"Product with ID {product_id} does not exist")

        if errors:
            return CreateOrder(order=None, message="Failed", errors=errors)

        try:
            # Calculate total amount
            total_amount = sum(product.price for product in products)

            # Create order
            order = Order.objects.create(
                customer=customer,
                total_amount=total_amount
            )

            # Associate products
            order.products.set(products)

            return CreateOrder(
                order=order,
                message="Order created successfully",
                errors=None
            )
        except Exception as e:
            errors.append(str(e))
            return CreateOrder(order=None, message="Failed", errors=errors)


# Query Class
class Query(graphene.ObjectType):
    # Basic queries
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)

    # Single object queries
    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    order = graphene.Field(OrderType, id=graphene.ID(required=True))

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None


# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
