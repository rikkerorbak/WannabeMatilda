"""
Example usage script for Matilda Platform Client.
"""

import os

from dotenv import load_dotenv

from matilda_client import MatildaClientManager

# Load credentials from .env
load_dotenv()


def main():
    organization = os.getenv("ORGANIZATION", "demo-org")
    api_key = os.getenv("API_KEY", "demo-api-key")

    print(f"Connecting to Matilda Platform for organization: '{organization}'...")

    # Initialize via MatildaClientManager (recommended)
    matilda = MatildaClientManager(
        organization=organization,
        api_key=api_key,
    )

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
