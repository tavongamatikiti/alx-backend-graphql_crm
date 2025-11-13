#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to project directory
cd "$PROJECT_DIR"

# Execute Django command to delete inactive customers
PYTHON_CODE="
from crm.models import Customer, Order
from datetime import datetime, timedelta
from django.utils import timezone

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders in the past year
inactive_customers = Customer.objects.filter(
    order__isnull=True
) | Customer.objects.exclude(
    order__order_date__gte=one_year_ago
)

# Get distinct customers and count
inactive_customers = inactive_customers.distinct()
count = inactive_customers.count()

# Delete inactive customers
if count > 0:
    inactive_customers.delete()
    print(f'{count} inactive customer(s) deleted')
else:
    print('No inactive customers found')
"

# Run the Python command and capture output
OUTPUT=$(python manage.py shell -c "$PYTHON_CODE" 2>&1)

# Log the result with timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
echo "[$TIMESTAMP] $OUTPUT" >> /tmp/customer_cleanup_log.txt
