"""
Celery tasks for the CRM application
"""
from celery import shared_task
from datetime import datetime
import requests


@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report summarizing:
    - Total number of customers
    - Total number of orders
    - Total revenue (sum of total_amount from orders)

    Logs the report to /tmp/crm_report_log.txt
    Scheduled to run every Monday at 6:00 AM
    """
    # GraphQL query to fetch report data
    query = """
    query {
        allCustomers {
            edges {
                node {
                    id
                }
            }
        }
        allOrders {
            edges {
                node {
                    id
                    totalAmount
                }
            }
        }
    }
    """

    log_file = '/tmp/crm_report_log.txt'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Execute GraphQL query
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': query},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})

            # Count customers
            customers = data.get('allCustomers', {}).get('edges', [])
            total_customers = len(customers)

            # Count orders and calculate revenue
            orders = data.get('allOrders', {}).get('edges', [])
            total_orders = len(orders)
            total_revenue = sum(
                float(order['node']['totalAmount'])
                for order in orders
                if order['node'].get('totalAmount')
            )

            # Format report message
            report_message = (
                f"{timestamp} - Report: {total_customers} customers, "
                f"{total_orders} orders, ${total_revenue:.2f} revenue"
            )

            # Log the report
            with open(log_file, 'a') as f:
                f.write(f"{report_message}\n")

            return report_message
        else:
            error_msg = f"{timestamp} - HTTP Error: {response.status_code}"
            with open(log_file, 'a') as f:
                f.write(f"{error_msg}\n")
            return error_msg

    except Exception as e:
        error_msg = f"{timestamp} - ERROR: {str(e)}"
        with open(log_file, 'a') as f:
            f.write(f"{error_msg}\n")
        return error_msg
