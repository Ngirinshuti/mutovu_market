"""
Django Management Command: fix_duplicate_variants
Location: product/management/commands/fix_duplicate_variants.py

This command removes duplicate ProductVariant records that have the same 
product_id, size_id, and color_id combination (which violates the unique_together constraint).
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from product.models import ProductVariant


class Command(BaseCommand):
    help = 'Remove duplicate ProductVariant records (same product/size/color combination)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.WARNING('Starting duplicate variant detection...'))
        
        # Find duplicates
        duplicates = (
            ProductVariant.objects
            .values('product', 'size', 'color')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        duplicate_count = duplicates.count()
        
        if duplicate_count == 0:
            self.stdout.write(
                self.style.SUCCESS('✓ No duplicate variants found!')
            )
            return

        self.stdout.write(
            self.style.WARNING(f'Found {duplicate_count} duplicate combination(s)')
        )
        self.stdout.write('')

        deleted_count = 0
        kept_count = 0

        # Process each duplicate
        for dup in duplicates:
            # Get all variants matching this combo, ordered by ID
            variants = ProductVariant.objects.filter(
                product_id=dup['product'],
                size_id=dup['size'],
                color_id=dup['color']
            ).order_by('id')

            # Keep the first one (lowest ID), mark others for deletion
            to_keep = variants.first()
            to_delete = variants.exclude(id=to_keep.id)

            delete_ids = list(to_delete.values_list('id', flat=True))
            delete_count = to_delete.count()

            # Display info
            product_id = dup['product']
            size_id = dup['size']
            color_id = dup['color']
            
            self.stdout.write(
                f'Product ID {product_id}, Size ID {size_id}, Color ID {color_id}:'
            )
            self.stdout.write(
                f'  Keeping: Variant #{to_keep.id} (SKU: {to_keep.sku})'
            )
            self.stdout.write(
                f'  Deleting: {delete_count} variant(s) - IDs: {delete_ids}'
            )

            if not dry_run:
                # Delete the duplicates
                to_delete.delete()
                deleted_count += delete_count
                kept_count += 1
            
            self.stdout.write('')

        # Summary
        self.stdout.write(self.style.WARNING('─' * 60))
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {deleted_count} duplicate variant(s) '
                    f'(from {kept_count} duplicate combination(s))'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Run without --dry-run flag to actually delete duplicates'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully deleted {deleted_count} duplicate variant(s) '
                    f'(from {kept_count} duplicate combination(s))'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    'You can now safely run: python manage.py migrate'
                )
            )