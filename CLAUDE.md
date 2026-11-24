# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) and AI coding assistants when working with code in this repository.

## Matilda Client System Documentation

This library provides an idiomatic Python client for the Matilda Platform Gateway API, specifically targeting the **Party**, **ServiceUsers**, and **ServiceUserDocuments** endpoints.

Reference architecture: Inspired by [odense-rpa/nexus-client](https://github.com/odense-rpa/nexus-client.git).

### Key Architecture Concepts:
- **`MatildaClientManager`**: Central facade pattern offering unified, lazy-loaded access to:
  - `matilda.parties` (`PartiesClient`)
  - `matilda.service_users` (`ServiceUsersClient`)
  - `matilda.documents` (`ServiceUserDocumentsClient`)
  - `matilda.client` (`MatildaClient`)
- **Dual Naming Convention**:
  - English primary methods (`get_parties`, `search_service_users`, `get_by_cpr`, `upload_document`)
  - Danish aliases matching Nexus Client (`hent_parter`, `søg_service_brugere`, `hent_via_cpr`, `hent_dokumenter`)
- **Authentication**:
  - Supports `api_key` (`x-api-key` header, default/preferred)
  - Supports `bearer_token` (`Authorization: Bearer ...`)
  - Supports `basic_auth` (`Authorization: Basic ...`)
- **Data Models**:
  - `ServicePeriod`, `ServiceUserRequest`, `ServiceUserResponse`, `Party`, `PartyPaginationResponse`, `AttendanceRequest`, etc. in `matilda_client.models`.
- **Security & Logging**:
  - Sensitive headers and tokens (`x-api-key`, `authorization`, etc.) are automatically sanitized via event hooks in `matilda_client.hooks`.

## Common Commands

### Setup
- Install dependencies: `uv sync`
- Configure environment: Copy `env.example` to `.env` and fill in `ORGANIZATION` and `API_KEY`.

### Tests
- Run all tests: `uv run pytest`
- Run single test: `uv run pytest tests/test_parties.py -k test_get_parties`
- Run with verbose output: `uv run pytest -v`

### Build & Package
- Build sdist and wheel: `uv build`
