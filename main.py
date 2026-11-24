"""
Example usage script for Matilda Platform Client.
"""

import os

from dotenv import load_dotenv

from matilda_client import MatildaClientManager

# Load credentials from .env
load_dotenv()


def main():
    # If ORGANIZATION is not in .env, fallback to a demo identifier for preview
    if not os.getenv("ORGANIZATION"):
        os.environ["ORGANIZATION"] = "demo-org"
        os.environ["API_KEY"] = "demo-api-key"

    # Hybrid initialization (reads from env vars or constructor arguments)
    matilda = MatildaClientManager()

    print(f"Connecting to Matilda Platform ({matilda.client.base_url}) for organization: '{matilda.organization}'...")

    print("\n1. Exploring Parties (PartiesClient):")
    try:
        parties_page = matilda.parties.get_parties(items_per_page=5)
        print(f"   Found {parties_page.get('totalItemsCount', 0)} total parties.")
        for p in parties_page.get("items", []):
            print(f"   - [{p.get('id')}] {p.get('name')} (GLN: {p.get('gln')})")
    except Exception as e:
        print(f"   Note (API call not executed with live credentials): {e}")

    print("\n2. Exploring Service Users (ServiceUsersClient):")
    try:
        users = matilda.service_users.search_service_users(
            customer_external_id="DEP01"
        )
        print(f"   Found {len(users)} service users.")
    except Exception as e:
        print(f"   Note (API call not executed with live credentials): {e}")

    print("\nMatilda Client successfully initialized!")


if __name__ == "__main__":
    main()
