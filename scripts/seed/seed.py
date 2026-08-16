"""Seed a tenant's catalog into the Feature Store from a JSON file.

Runs against the shared workspace environment - `common` is a workspace
member, so it's already installed alongside this script. This is an
operational script, not a deployed service.
"""

import argparse
import json
from pathlib import Path

from shopping_agent_common.catalog import CatalogService, ProductUpsert
from shopping_agent_common.db import get_session
from shopping_agent_common.embeddings import get_embedding_client


def seed_from_file(path: Path, tenant_id: str, env: str) -> None:
    catalog = json.loads(path.read_text())

    with get_session() as session:
        catalog_service = CatalogService(session, get_embedding_client())
        for entry in catalog:
            payload = ProductUpsert.model_validate(entry)
            product = catalog_service.upsert_product(tenant_id, env, payload)
            print(f"upserted {product.external_product_id} -> {product.id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed a tenant's catalog from a JSON file")
    parser.add_argument("path", type=Path)
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--env", default="dev")
    args = parser.parse_args()

    seed_from_file(args.path, args.tenant_id, args.env)


if __name__ == "__main__":
    main()
