"""
Cron jobs for the CRM application
"""
from datetime import datetime
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Log a heartbeat message to confirm CRM application health.
    Runs every 5 minutes via django-crontab.
    """
    # Generate timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    message = f"{timestamp} CRM is alive\n"

    # Append to heartbeat log file
    log_file = '/tmp/crm_heartbeat_log.txt'
    with open(log_file, 'a') as f:
        f.write(message)

    # Optional: Query GraphQL hello field to verify endpoint is responsive
    try:
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            use_json=True,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql('{ hello }')
        result = client.execute(query)

        if result.get('hello'):
            with open(log_file, 'a') as f:
                f.write(f"{timestamp} GraphQL endpoint responsive\n")
    except Exception as e:
        # Log error but don't fail the heartbeat
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} GraphQL check failed: {str(e)}\n")


def update_low_stock():
    """
    Update low-stock products using GraphQL mutation.
    Runs every 12 hours via django-crontab.
    """
    # GraphQL mutation to update low-stock products
    mutation = """
    mutation {
        updateLowStockProducts {
            success
            message
            updatedCount
            products {
                id
                name
                stock
            }
        }
    }
    """

    log_file = '/tmp/low_stock_updates_log.txt'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Execute mutation via GraphQL endpoint
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': mutation},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {}).get('updateLowStockProducts', {})

            success = data.get('success', False)
            message = data.get('message', 'No response')
            products = data.get('products', [])

            # Log the update
            with open(log_file, 'a') as f:
                f.write(f"[{timestamp}] {message}\n")

                if success and products:
                    for product in products:
                        product_name = product.get('name', 'Unknown')
                        new_stock = product.get('stock', 0)
                        f.write(f"[{timestamp}] Product: {product_name}, New Stock: {new_stock}\n")
        else:
            # Log HTTP error
            with open(log_file, 'a') as f:
                f.write(f"[{timestamp}] HTTP Error: {response.status_code}\n")

    except Exception as e:
        # Log exception
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] ERROR: {str(e)}\n")
