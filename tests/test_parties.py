"""
Unit tests for PartiesClient functionality.
"""

from matilda_client.models import PartyPaginationResponse


def test_get_parties(manager):
    res = manager.parties.get_parties(items_per_page=5)
    assert "items" in res
    assert len(res["items"]) == 2
    assert res["totalItemsCount"] == 2
    assert res["items"][0]["name"] == "Central Kitchen A"


def test_get_parties_typed(manager):
    res = manager.parties.get_parties_typed()
    assert isinstance(res, PartyPaginationResponse)
    assert len(res.items) == 2
    assert res.items[0].id == 101
    assert res.items[0].name == "Central Kitchen A"
    assert res.items[0].gln == "5790000111222"
    assert res.items[0].isProducer is True


def test_get_all_parties(manager):
    all_parties = manager.parties.get_all_parties()
    assert len(all_parties) == 2
    names = [p["name"] for p in all_parties]
    assert "Central Kitchen A" in names
    assert "Supplier B" in names


def test_get_party_by_id(manager):
    p = manager.parties.get_party_by_id(101)
    assert p is not None
    assert p["name"] == "Central Kitchen A"

    p_none = manager.parties.get_party_by_id(9999)
    assert p_none is None


def test_get_party_by_external_id(manager):
    p = manager.parties.get_party_by_external_id("EXT-CK-01")
    assert p is not None
    assert p["id"] == 101


def test_danish_aliases(manager):
    res = manager.parter.hent_parter()
    assert len(res["items"]) == 2
    all_p = manager.parter.hent_alle_parter()
    assert len(all_p) == 2
