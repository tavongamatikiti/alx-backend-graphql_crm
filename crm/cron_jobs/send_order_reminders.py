#!/usr/bin/env python
"""
Order Reminders Script
Queries GraphQL endpoint for pending orders from the last 7 days
and logs reminders to /tmp/order_reminders_log.txt
"""

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta
import sys
import os

# Add project directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_dir)

def send_order_reminders():
    """Query GraphQL for recent orders and log reminders"""

    # Configure GraphQL client
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql',
        use_json=True,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Calculate date 7 days ago
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # GraphQL query for orders from the last 7 days
    query = gql("""
        query GetRecentOrders($dateAfter: DateTime!) {
            allOrders(orderDate_Gte: $dateAfter) {
                edges {
                    node {
                        id
                        orderDate
                        totalAmount
                        customer {
                            id
                            name
                            email
                        }
                    }
                }
            }
        }
    """)

    try:
        # Execute the query
        result = client.execute(query, variable_values={"dateAfter": seven_days_ago})

        # Process results
        orders = result.get('allOrders', {}).get('edges', [])

        # Log reminders
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file = '/tmp/order_reminders_log.txt'

        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] Processing {len(orders)} order(s)\n")

            for order_edge in orders:
                order = order_edge['node']
                order_id = order['id']
                customer = order['customer']
                customer_email = customer['email']
                order_date = order['orderDate']

                log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}, Order Date: {order_date}\n"
                f.write(log_entry)

        print("Order reminders processed!")

    except Exception as e:
        # Log errors
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/order_reminders_log.txt', 'a') as f:
            f.write(f"[{timestamp}] ERROR: {str(e)}\n")
        print(f"Error processing order reminders: {e}")
        sys.exit(1)

if __name__ == '__main__':
    send_order_reminders()
