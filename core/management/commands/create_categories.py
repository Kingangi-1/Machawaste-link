"""""
# core/management/commands/create_categories.py
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction

class Command(BaseCommand):
    help = "Create default waste categories"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate category creation without saving.'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        self.stdout.write("Starting waste category creation...")
        if dry_run:
            self.stdout.write("Dry run mode: no changes will be made.")

        try:
            WasteCategory = apps.get_model("core", "WasteCategory")
            self.stdout.write(self.style.SUCCESS("Found WasteCategory model"))
        except LookupError as e:
            self.stdout.write(self.style.ERROR(f"Model not found: {e}"))
            return

        categories = [
            {"name": "Plastic", "description": "Plastic bottles, containers"},
            {"name": "Paper & Cardboard", "description": "Newspapers, boxes, cartons"},
            {"name": "Metal", "description": "Aluminum cans, tin containers"},
            {"name": "Glass", "description": "Bottles, jars"},
            {"name": "E-Waste", "description": "Electronics, devices"},
            {"name": "Organic Waste", "description": "Food scraps, garden waste"},
            {"name": "Agricultural Residues", "description": "Crop waste, farm residues"},
            {"name": "Clothes", "description": "Old clothes, textiles"},
            {"name": "Hazardous Waste", "description": "Chemicals, batteries"}
        ]

        created_count = 0
        existing_count = 0

        for data in categories:
            try:
                if dry_run:
                    self.stdout.write(f"[Dry Run] Would create: {data['name']}")
                    continue

                with transaction.atomic():
                    category, created = WasteCategory.objects.get_or_create(
                        name=data["name"],
                        defaults={"description": data["description"]}
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"✓ Created: {data['name']}"))
                        created_count += 1
                    else:
                        self.stdout.write(self.style.WARNING(f"○ Exists: {data['name']}"))
                        existing_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error creating {data['name']}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"Completed! Created: {created_count}, Existing: {existing_count}, Total: {len(categories)}"
        ))

"""

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction, IntegrityError

class Command(BaseCommand):
    help = "Create default waste categories for Machawaste Link"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate category creation without saving.'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information about each category.'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        verbose = options.get('verbose', False)
        
        self.stdout.write("=== Machawaste Link - Waste Category Setup ===")
        
        if dry_run:
            self.stdout.write("🚧 DRY RUN MODE - No changes will be made")
        else:
            self.stdout.write("🎯 LIVE MODE - Categories will be created")

        try:
            WasteCategory = apps.get_model("core", "WasteCategory")
            self.stdout.write(self.style.SUCCESS("✓ WasteCategory model loaded"))
        except LookupError as e:
            self.stdout.write(self.style.ERROR(f"✗ Model not found: {e}"))
            return

        categories = [
            {"name": "Plastic", "description": "Plastic bottles, containers"},
            {"name": "Paper & Cardboard", "description": "Newspapers, boxes, cartons"},
            {"name": "Metal", "description": "Aluminum cans, tin containers"},
            {"name": "Glass", "description": "Bottles, jars"},
            {"name": "E-Waste", "description": "Electronics, devices"},
            {"name": "Organic Waste", "description": "Food scraps, garden waste"},
            {"name": "Agricultural Residues", "description": "Crop waste, farm residues"},
            {"name": "Clothes", "description": "Old clothes, textiles"},
            {"name": "Hazardous Waste", "description": "Chemicals, batteries"}
        ]

        if verbose:
            self.stdout.write(f"📋 Processing {len(categories)} waste categories...")

        created_count = 0
        existing_count = 0
        error_count = 0

        for data in categories:
            try:
                if dry_run:
                    self.stdout.write(f"  [DRY RUN] Would create: {data['name']}")
                    continue

                with transaction.atomic():
                    category, created = WasteCategory.objects.get_or_create(
                        name=data["name"],
                        defaults={"description": data["description"]}
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"  ✅ CREATED: {data['name']}"))
                        created_count += 1
                    else:
                        if verbose:
                            self.stdout.write(self.style.WARNING(f"  ⚠️ EXISTS: {data['name']}"))
                        existing_count += 1

            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"  ❌ DUPLICATE: {data['name']} - {e}"))
                error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ ERROR: {data['name']} - {e}"))
                error_count += 1

        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("🎉 CATEGORY CREATION COMPLETE!"))
        self.stdout.write(f"📊 Created: {created_count} | Existing: {existing_count} | Errors: {error_count}")
        self.stdout.write(f"📦 Total in system: {WasteCategory.objects.count()}")
        
        if dry_run:
            self.stdout.write("💡 Run without --dry-run to actually create categories")