"""Reusable CLI to seed or re-sync a tenant's product catalog (products +
items) into the Feature Store from a JSON file.

Safe to re-run repeatedly against the same file or an updated one:
CatalogService.upsert_product is idempotent by content, so a record that's
identical to what's already stored is skipped entirely (no DB write, no
embedding call). A record whose price/stock/etc. changed but whose title/
description didn't gets its row updated but reuses its existing embedding.
Only a genuine title/description change pays for a new Voyage call. This
matters because embedding calls are the slow, rate-limited, costly part of
any catalog sync - re-running this against an unmodified file should be
near-instant and free.

One bad record does not abort the run: each record is its own transaction,
logged and counted, and the run ends with a summary. Exits non-zero if any
record failed, so it composes cleanly in CI/cron.

Usage:
    uv run python scripts/seed/cli.py <path-to-catalog.json> --tenant-id demo --env dev
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError
from shopping_agent_common.catalog import CatalogService, ProductUpsert, UpsertOutcome
from shopping_agent_common.db.session import get_session_factory
from shopping_agent_common.embeddings import get_embedding_client
from shopping_agent_common.exceptions import ShoppingAgentError
from shopping_agent_common.logging import configure_logging

logger = logging.getLogger(__name__)


@dataclass
class SeedSummary:
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    failed: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.created + self.updated + self.unchanged + len(self.failed)

    def record(self, outcome: UpsertOutcome) -> None:
        if outcome is UpsertOutcome.CREATED:
            self.created += 1
        elif outcome is UpsertOutcome.UPDATED:
            self.updated += 1
        else:
            self.unchanged += 1

    def print_report(self) -> None:
        print()
        print("Seed summary")
        print("------------")
        print(f"  created:   {self.created}")
        print(f"  updated:   {self.updated}")
        print(f"  unchanged: {self.unchanged}")
        print(f"  failed:    {len(self.failed)}")
        if self.failed:
            print(f"    -> {', '.join(self.failed)}")
        print(f"  total:     {self.total}")


def seed_catalog(path: Path, tenant_id: str, env: str) -> SeedSummary:
    entries = json.loads(path.read_text())
    logger.info(
        "seed.starting path=%s tenant_id=%s env=%s record_count=%d",
        path,
        tenant_id,
        env,
        len(entries),
    )

    embedding_client = get_embedding_client()
    session_factory = get_session_factory()
    summary = SeedSummary()

    for entry in entries:
        external_id = entry.get("external_product_id", "<missing external_product_id>")
        session = session_factory()
        try:
            payload = ProductUpsert.model_validate(entry)
            catalog_service = CatalogService(session, embedding_client)
            product, outcome = catalog_service.upsert_product(tenant_id, env, payload)
            session.commit()
            summary.record(outcome)
            logger.info(
                "seed.record external_product_id=%s outcome=%s",
                product.external_product_id,
                outcome.value,
            )
        except ValidationError as exc:
            session.rollback()
            summary.failed.append(external_id)
            logger.error("seed.record_invalid external_product_id=%s error=%s", external_id, exc)
        except ShoppingAgentError as exc:
            session.rollback()
            summary.failed.append(external_id)
            logger.error("seed.record_failed external_product_id=%s error=%s", external_id, exc)
        finally:
            session.close()

    logger.info(
        "seed.finished created=%d updated=%d unchanged=%d failed=%d",
        summary.created,
        summary.updated,
        summary.unchanged,
        len(summary.failed),
    )
    return summary


def main() -> None:
    configure_logging("seed-cli")

    parser = argparse.ArgumentParser(
        description=(
            "Seed or re-sync a tenant's product catalog from a JSON file. "
            "Safe to re-run: unchanged products are skipped, changed ones are "
            "updated, and only a title/description change triggers a new embedding."
        )
    )
    parser.add_argument("path", type=Path, help="Path to a catalog JSON file")
    parser.add_argument("--tenant-id", required=True, help="Tenant to seed")
    parser.add_argument("--env", default="dev", help="Environment (default: dev)")
    args = parser.parse_args()

    if not args.path.exists():
        logger.error("seed.file_not_found path=%s", args.path)
        sys.exit(1)

    summary = seed_catalog(args.path, args.tenant_id, args.env)
    summary.print_report()

    if summary.failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
