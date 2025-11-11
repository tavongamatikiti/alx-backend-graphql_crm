import django_filters
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    """Filter class for Customer model"""
    # Case-insensitive partial match
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')

    # Date range filters
    created_at_gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = django_filters.CharFilter(field_name='created_at', lookup_expr='lte')

    # Custom phone pattern filter (starts with specific pattern)
    phone_pattern = django_filters.CharFilter(method='filter_phone_pattern')

    def filter_phone_pattern(self, queryset, name, value):
        """Filter customers with phone numbers starting with specific pattern"""
        return queryset.filter(phone__startswith=value)

    class Meta:
        model = Customer
        fields = {
            'name': ['icontains', 'exact'],
            'email': ['icontains', 'exact'],
            'phone': ['exact'],
            'created_at': ['gte', 'lte', 'exact'],
        }


class ProductFilter(django_filters.FilterSet):
    """Filter class for Product model"""
    # Case-insensitive partial match
    name = django_filters.CharFilter(lookup_expr='icontains')

    # Price range filters
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    # Stock range filters
    stock_gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')

    # Low stock filter (less than 10)
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')

    def filter_low_stock(self, queryset, name, value):
        """Filter products with low stock (stock < 10)"""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

    class Meta:
        model = Product
        fields = {
            'name': ['icontains', 'exact'],
            'price': ['gte', 'lte', 'exact'],
            'stock': ['gte', 'lte', 'exact'],
        }


class OrderFilter(django_filters.FilterSet):
    """Filter class for Order model"""
    # Total amount range filters
    total_amount_gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')

    # Order date range filters
    order_date_gte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='lte')

    # Related field filters (customer name)
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')

    # Related field filters (product name)
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')

    # Specific product ID filter
    product_id = django_filters.NumberFilter(field_name='products__id', lookup_expr='exact')

    class Meta:
        model = Order
        fields = {
            'total_amount': ['gte', 'lte', 'exact'],
            'order_date': ['gte', 'lte', 'exact'],
            'customer': ['exact'],
        }
