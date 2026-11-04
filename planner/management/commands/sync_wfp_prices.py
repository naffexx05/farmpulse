"""
Management command: sync_wfp_prices
Fetches current agricultural input prices from WFP Malawi food price data
published on the Humanitarian Data Exchange (HDX) — no API key required.

Run: python manage.py sync_wfp_prices
Run with dry-run: python manage.py sync_wfp_prices --dry-run
"""

from django.core.management.base import BaseCommand
from planner.sync_service import execute_hdx_price_sync


class Command(BaseCommand):
    help = (
        'Sync InputCostBenchmark prices from WFP Malawi market prices '
        '(HDX public dataset — no API key required).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Preview what would be updated without saving.',
        )
        parser.add_argument(
            '--season', type=int, default=2025,
            help='Season year to update (default: 2025)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        season  = options['season']

        self.stdout.write('Connecting to WFP / HDX market surveillance stream...')
        result = execute_hdx_price_sync(season_year=season, dry_run=dry_run)

        if not result['ok']:
            self.stdout.write(self.style.WARNING(
                f"\n[Offline Notice] {result['message']}\n"
                f"Retaining active {result['source']}."
            ))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"\nDry run complete — {result['skipped']} record(s) checked. "
                "Run without --dry-run to apply."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\nHDX price sync complete: {result['updated']} benchmark record(s) "
                f"updated from {result['source']} at {result['timestamp']}."
            ))
