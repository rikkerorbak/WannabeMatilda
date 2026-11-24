"""
Party client for Matilda Platform.

Handles interaction with Parties (Organizations, Suppliers, Kitchens, Units).
Endpoint: /v1/organization/{organization}/parties
"""

from typing import Any

from matilda_client.client import MatildaClient
from matilda_client.models import PartyPaginationResponse
from matilda_client.utils import clean_dict


class PartiesClient:
    """
    Client for Party operations in Matilda Platform.

    IMPORTANT: Do not instantiate directly. Use MatildaClientManager:
        matilda = MatildaClientManager(...)
        parties = matilda.parties.get_parties(...)
    """

    ENDPOINT = "/v1/organization/{organization}/parties"

    def __init__(self, matilda_client: MatildaClient):
        self.client = matilda_client

    def get_parties(
        self,
        name: str | None = None,
        external_id: str | None = None,
        gln: str | None = None,
        invoice_system_id: int | None = None,
        is_producer: bool | None = None,
        is_active: bool | None = None,
        start_index: int | None = None,
        items_per_page: int | None = None,
    ) -> dict[str, Any]:
        """
        Get paginated list of parties with optional filtering.

        :param name: Filter by party name.
        :param external_id: Filter by external ID.
        :param gln: Filter by Global Location Number (GLN).
        :param invoice_system_id: Filter by invoice system ID.
        :param is_producer: Filter by producer flag.
        :param is_active: Filter by active status.
        :param start_index: Pagination starting index (0-based).
        :param items_per_page: Number of items per page.
        :return: JSON response containing pagination metadata and party items.
        """
        params = clean_dict(
            {
                "Name": name,
                "ExternalId": external_id,
                "Gln": gln,
                "InvoiceSystemId": invoice_system_id,
                "IsProducer": is_producer,
                "IsActive": is_active,
                "StartIndex": start_index,
                "ItemsPerPage": items_per_page,
            }
        )

        response = self.client.get(self.ENDPOINT, params=params)
        return response.json()

    def get_parties_typed(
        self,
        name: str | None = None,
        external_id: str | None = None,
        gln: str | None = None,
        invoice_system_id: int | None = None,
        is_producer: bool | None = None,
        is_active: bool | None = None,
        start_index: int | None = None,
        items_per_page: int | None = None,
    ) -> PartyPaginationResponse:
        """
        Get parties parsed into strongly-typed PartyPaginationResponse model.
        """
        data = self.get_parties(
            name=name,
            external_id=external_id,
            gln=gln,
            invoice_system_id=invoice_system_id,
            is_producer=is_producer,
            is_active=is_active,
            start_index=start_index,
            items_per_page=items_per_page,
        )
        return PartyPaginationResponse.from_dict(data)

    def get_all_parties(
        self,
        is_active: bool | None = None,
        is_producer: bool | None = None,
        page_size: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Fetch ALL parties by automatically iterating through pages.

        :param is_active: Optional filter for active parties.
        :param is_producer: Optional filter for producer parties.
        :param page_size: Items per page to request (default: 100).
        :return: Flat list of all party dictionaries.
        """
        all_items: list[dict[str, Any]] = []
        start_index = 0

        while True:
            page = self.get_parties(
                is_active=is_active,
                is_producer=is_producer,
                start_index=start_index,
                items_per_page=page_size,
            )
            items = page.get("items") or []
            if not items:
                break

            all_items.extend(items)
            total_items = page.get("totalItemsCount")

            start_index += len(items)
            if total_items is not None and start_index >= total_items:
                break
            if len(items) < page_size:
                break

        return all_items

    def get_party_by_id(self, party_id: int) -> dict[str, Any] | None:
        """
        Find a specific party by its numeric ID.

        :param party_id: Numeric ID of the party.
        :return: Party dict or None if not found.
        """
        parties = self.get_all_parties()
        for party in parties:
            if party.get("id") == party_id:
                return party
        return None

    def get_party_by_external_id(self, external_id: str) -> dict[str, Any] | None:
        """
        Find a party by its external identifier.

        :param external_id: External ID string.
        :return: Party dict or None if not found.
        """
        page = self.get_parties(external_id=external_id, items_per_page=10)
        items = page.get("items") or []
        for party in items:
            if str(party.get("externalId")) == str(external_id):
                return party
        return items[0] if items else None

    # Danish / Nordic aliases (matching nexus-client style)
    hent_parter = get_parties
    hent_alle_parter = get_all_parties
    hent_part_via_id = get_party_by_id
    hent_part_via_eksternt_id = get_party_by_external_id


# Class aliases for flexible imports
PartyClient = PartiesClient
ParterClient = PartiesClient
