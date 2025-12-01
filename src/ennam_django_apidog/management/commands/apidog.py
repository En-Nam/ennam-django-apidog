"""
Django management command for APIDOG integration.

This command provides tools to export, validate, sync, pull, and compare
OpenAPI schemas between Django and APIDOG Cloud.

Usage:
    python manage.py apidog init
    python manage.py apidog export [--format json|yaml] [--output DIR]
    python manage.py apidog validate [--file FILE]
    python manage.py apidog push [--project-id ID] [--token TOKEN]
    python manage.py apidog pull [--project-id ID] [--token TOKEN] [--output FILE]
    python manage.py apidog compare [--project-id ID] [--token TOKEN]
    python manage.py apidog env-config

Install:
    pip install ennam-django-apidog
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import yaml
from django.core.management.base import BaseCommand, CommandError
from django.test import Client

from ennam_django_apidog.settings import apidog_settings


class Command(BaseCommand):
    help = "APIDOG integration - Export, sync, and compare OpenAPI schemas"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.client = Client()

    @property
    def output_dir(self) -> str:
        """Get the output directory from settings."""
        return apidog_settings.get_output_dir()

    @property
    def templates_dir(self) -> Path:
        """Get the templates directory within the package."""
        return Path(__file__).parent.parent.parent / "templates"

    def add_arguments(self, parser: Any) -> None:
        subparsers = parser.add_subparsers(
            dest="subcommand",
            title="subcommands",
            description="Available commands",
        )

        # Init subcommand
        init_parser = subparsers.add_parser(
            "init",
            help="Initialize apidog directory with templates",
        )
        init_parser.add_argument(
            "--force",
            "-f",
            action="store_true",
            help="Overwrite existing files",
        )

        # Export subcommand
        export_parser = subparsers.add_parser(
            "export",
            help="Export OpenAPI schema from Django",
        )
        export_parser.add_argument(
            "--format",
            "-f",
            type=str,
            default="json",
            choices=["json", "yaml"],
            help="Output format (default: json)",
        )
        export_parser.add_argument(
            "--output",
            "-o",
            type=str,
            help="Output directory (default: apidog/)",
        )
        export_parser.add_argument(
            "--filename",
            type=str,
            help="Custom filename (default: timestamped)",
        )
        export_parser.add_argument(
            "--indent",
            type=int,
            default=2,
            help="JSON indentation (default: 2)",
        )

        # Validate subcommand
        validate_parser = subparsers.add_parser(
            "validate",
            help="Validate an OpenAPI schema file",
        )
        validate_parser.add_argument(
            "--file",
            "-f",
            type=str,
            help="Schema file to validate (default: latest)",
        )

        # Push subcommand
        push_parser = subparsers.add_parser(
            "push",
            help="Push local schema to APIDOG Cloud",
        )
        push_parser.add_argument(
            "--project-id",
            type=str,
            help="APIDOG project ID (or set APIDOG_PROJECT_ID env var)",
        )
        push_parser.add_argument(
            "--token",
            type=str,
            help="APIDOG API token (or set APIDOG_TOKEN env var)",
        )
        push_parser.add_argument(
            "--file",
            "-f",
            type=str,
            help="Schema file to push (default: export new)",
        )

        # Pull subcommand
        pull_parser = subparsers.add_parser(
            "pull",
            help="Pull schema from APIDOG Cloud",
        )
        pull_parser.add_argument(
            "--project-id",
            type=str,
            help="APIDOG project ID (or set APIDOG_PROJECT_ID env var)",
        )
        pull_parser.add_argument(
            "--token",
            type=str,
            help="APIDOG API token (or set APIDOG_TOKEN env var)",
        )
        pull_parser.add_argument(
            "--output",
            "-o",
            type=str,
            help="Output file path",
        )

        # Compare subcommand
        compare_parser = subparsers.add_parser(
            "compare",
            help="Compare local schema with APIDOG Cloud",
        )
        compare_parser.add_argument(
            "--project-id",
            type=str,
            help="APIDOG project ID (or set APIDOG_PROJECT_ID env var)",
        )
        compare_parser.add_argument(
            "--token",
            type=str,
            help="APIDOG API token (or set APIDOG_TOKEN env var)",
        )
        compare_parser.add_argument(
            "--local-file",
            type=str,
            help="Local schema file (default: latest)",
        )

        # Env-config subcommand
        subparsers.add_parser(
            "env-config",
            help="Generate environment configuration",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        subcommand = options.get("subcommand")

        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        if subcommand == "init":
            self.handle_init(options)
        elif subcommand == "export":
            self.handle_export(options)
        elif subcommand == "validate":
            self.handle_validate(options)
        elif subcommand == "push":
            self.handle_push(options)
        elif subcommand == "pull":
            self.handle_pull(options)
        elif subcommand == "compare":
            self.handle_compare(options)
        elif subcommand == "env-config":
            self.handle_env_config(options)
        else:
            # No subcommand - show help
            self.print_help("manage.py", "apidog")

    # =========================================================================
    # Init Command
    # =========================================================================
    def handle_init(self, options: Dict[str, Any]) -> None:
        """Initialize apidog directory with templates."""
        force = options.get("force", False)

        self.stdout.write("Initializing APIDOG integration...")

        # Create output directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.stdout.write(f"  Created: {self.output_dir}/")

        # Copy templates
        templates = [
            ("Makefile.apidog", "Makefile.apidog"),
            ("docker-compose.apidog.yml", "docker-compose.apidog.yml"),
            ("environments.json", "environments.json"),
            (".gitignore.apidog", ".gitignore.apidog"),
        ]

        # Get project root (parent of output_dir)
        project_root = os.path.dirname(self.output_dir)

        for template_name, dest_name in templates:
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                self.stdout.write(
                    self.style.WARNING(f"  Template not found: {template_name}")
                )
                continue

            # Special handling for different destinations
            if template_name == "environments.json":
                dest_path = os.path.join(self.output_dir, dest_name)
            elif template_name == ".gitignore.apidog":
                # Append to existing .gitignore or create new
                dest_path = os.path.join(project_root, ".gitignore")
                self._append_gitignore(template_path, dest_path)
                continue
            else:
                dest_path = os.path.join(project_root, dest_name)

            if os.path.exists(dest_path) and not force:
                self.stdout.write(f"  Skipped (exists): {dest_name}")
            else:
                shutil.copy(template_path, dest_path)
                self.stdout.write(self.style.SUCCESS(f"  Created: {dest_name}"))

        # Create README in apidog directory
        readme_path = os.path.join(self.output_dir, "README.md")
        if not os.path.exists(readme_path) or force:
            self._create_apidog_readme(readme_path)
            self.stdout.write(self.style.SUCCESS("  Created: apidog/README.md"))

        self.stdout.write(self.style.SUCCESS("\nAPIDAG initialization complete!"))
        self.stdout.write("\nNext steps:")
        self.stdout.write("  1. Configure APIDOG_SETTINGS in your settings.py")
        self.stdout.write("  2. Run: python manage.py apidog export")
        self.stdout.write("  3. Run: python manage.py apidog push")

    def _append_gitignore(self, template_path: Path, gitignore_path: str) -> None:
        """Append APIDOG gitignore rules to existing .gitignore."""
        marker = "# APIDOG generated files"
        rules = template_path.read_text()

        if os.path.exists(gitignore_path):
            existing = open(gitignore_path).read()
            if marker in existing:
                self.stdout.write("  Skipped (exists): .gitignore rules")
                return
            with open(gitignore_path, "a") as f:
                f.write(f"\n{rules}")
        else:
            with open(gitignore_path, "w") as f:
                f.write(rules)

        self.stdout.write(self.style.SUCCESS("  Updated: .gitignore"))

    def _create_apidog_readme(self, path: str) -> None:
        """Create a README for the apidog directory."""
        content = """# APIDOG Integration

This directory contains APIDOG-related files for API documentation and testing.

## Directory Structure

```
apidog/
├── README.md                       # This file
├── environments.json               # Environment configurations
├── openapi_schema_latest.json      # Latest exported schema (gitignored)
├── openapi_schema_*.json           # Timestamped exports (gitignored)
└── openapi_from_apidog_*.json      # Pulled from cloud (gitignored)
```

## Quick Commands

```bash
# Export schema
python manage.py apidog export

# Push to APIDOG Cloud
python manage.py apidog push

# Pull from APIDOG Cloud
python manage.py apidog pull

# Compare local vs cloud
python manage.py apidog compare
```

## Documentation

See the full documentation at: https://github.com/ennam/ennam-django-apidog
"""
        with open(path, "w") as f:
            f.write(content)

    # =========================================================================
    # Export Command
    # =========================================================================
    def handle_export(self, options: Dict[str, Any]) -> str:
        """Export OpenAPI schema from Django."""
        fmt = options.get("format", "json")
        output_dir = options.get("output") or self.output_dir
        custom_filename = options.get("filename")
        indent = options.get("indent", 2)

        schema_endpoint = apidog_settings.SCHEMA_ENDPOINT
        self.stdout.write(f"Fetching OpenAPI schema from {schema_endpoint}...")

        # Get schema from drf-spectacular endpoint
        response = self.client.get(schema_endpoint, HTTP_ACCEPT="application/json")

        if response.status_code != 200:
            raise CommandError(f"Failed to fetch schema. Status: {response.status_code}")

        schema = response.json()

        # Add metadata
        schema["info"]["x-generated-at"] = datetime.now().isoformat()
        schema["info"]["x-generated-by"] = "ennam-django-apidog"

        # Determine filename
        if custom_filename:
            filename = custom_filename
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"openapi_schema_{timestamp}.{fmt}"

        filepath = os.path.join(output_dir, filename)

        # Write schema to file
        self._write_schema(filepath, schema, fmt, indent)
        self.stdout.write(self.style.SUCCESS(f"Schema exported to: {filepath}"))

        # Also save a "latest" version
        latest_filepath = os.path.join(output_dir, f"openapi_schema_latest.{fmt}")
        self._write_schema(latest_filepath, schema, fmt, indent)
        self.stdout.write(self.style.SUCCESS(f"Latest schema: {latest_filepath}"))

        # Display statistics
        self._print_schema_stats(schema)

        return filepath

    def _write_schema(
        self, filepath: str, schema: Dict[str, Any], fmt: str, indent: int = 2
    ) -> None:
        """Write schema to file in specified format."""
        with open(filepath, "w", encoding="utf-8") as f:
            if fmt == "json":
                json.dump(schema, f, indent=indent, ensure_ascii=False)
            else:
                yaml.dump(schema, f, default_flow_style=False, allow_unicode=True)

    def _print_schema_stats(self, schema: Dict[str, Any]) -> None:
        """Print schema statistics."""
        self.stdout.write("\nSchema Statistics:")
        self.stdout.write(f'  API Version: {schema.get("info", {}).get("version", "N/A")}')
        self.stdout.write(f'  Endpoints: {len(schema.get("paths", {}))}')
        self.stdout.write(
            f'  Components: {len(schema.get("components", {}).get("schemas", {}))}'
        )

    # =========================================================================
    # Validate Command
    # =========================================================================
    def handle_validate(self, options: Dict[str, Any]) -> bool:
        """Validate an OpenAPI schema file."""
        schema_file = options.get("file")

        if not schema_file:
            schema_file = os.path.join(self.output_dir, "openapi_schema_latest.json")

        if not os.path.exists(schema_file):
            raise CommandError(f"Schema file not found: {schema_file}")

        self.stdout.write(f"Validating: {schema_file}")

        with open(schema_file, encoding="utf-8") as f:
            schema = json.load(f)

        # Basic validation
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            if field not in schema:
                raise CommandError(f"Missing required field: {field}")

        self._print_schema_stats(schema)
        self.stdout.write(self.style.SUCCESS("Schema is valid!"))

        return True

    # =========================================================================
    # Push Command
    # =========================================================================
    def handle_push(self, options: Dict[str, Any]) -> bool:
        """Push local schema to APIDOG Cloud."""
        project_id, token = apidog_settings.get_credentials(
            options.get("project_id"),
            options.get("token"),
        )
        schema_file = options.get("file")

        if not project_id or not token:
            self._print_credentials_help()
            raise CommandError("APIDOG credentials required")

        # Export if no file specified
        if not schema_file:
            self.stdout.write("No schema file specified, exporting...")
            schema_file = self.handle_export(
                {"format": "json", "output": self.output_dir, "indent": 2}
            )

        self.stdout.write(f"Pushing to APIDOG project {project_id}...")

        with open(schema_file, encoding="utf-8") as f:
            schema_content = f.read()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Apidog-Api-Version": apidog_settings.API_VERSION,
        }

        payload = {
            "input": {"data": schema_content},
            "options": {
                "endpointOverwriteBehavior": "MERGE_KEEP_NEWER",
                "schemaOverwriteBehavior": "MERGE_KEEP_NEWER",
                "updateFolderOfChangedEndpoint": True,
            },
        }

        url = f"{apidog_settings.API_BASE_URL}/projects/{project_id}/import-openapi"

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=apidog_settings.TIMEOUT
            )

            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("Successfully pushed to APIDOG!"))
                return True
            else:
                self.stdout.write(self.style.ERROR(f"Failed: {response.status_code}"))
                self.stdout.write(response.text[:500])
                return False
        except requests.exceptions.RequestException as e:
            raise CommandError(f"Request failed: {e}") from e

    # =========================================================================
    # Pull Command
    # =========================================================================
    def handle_pull(self, options: Dict[str, Any]) -> Optional[str]:
        """Pull schema from APIDOG Cloud."""
        project_id, token = apidog_settings.get_credentials(
            options.get("project_id"),
            options.get("token"),
        )
        output_file = options.get("output")

        if not project_id or not token:
            self._print_credentials_help()
            raise CommandError("APIDOG credentials required")

        self.stdout.write(f"Pulling from APIDOG project {project_id}...")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Apidog-Api-Version": apidog_settings.API_VERSION,
        }

        payload = {
            "scope": {"type": "ALL"},
            "options": {
                "includeApidogExtensionProperties": False,
                "addFoldersToTags": False,
            },
            "oasVersion": "3.0",
            "exportFormat": "JSON",
        }

        url = f"{apidog_settings.API_BASE_URL}/projects/{project_id}/export-openapi"

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=apidog_settings.TIMEOUT
            )

            if response.status_code == 200:
                schema = response.json()

                if not output_file:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = os.path.join(
                        self.output_dir, f"openapi_from_apidog_{timestamp}.json"
                    )

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(schema, f, indent=2, ensure_ascii=False)

                self.stdout.write(self.style.SUCCESS(f"Schema pulled to: {output_file}"))
                self._print_schema_stats(schema)
                return output_file

            elif response.status_code == 401:
                raise CommandError("Unauthorized - Invalid token")
            elif response.status_code == 404:
                raise CommandError("Project not found - Check project ID")
            else:
                raise CommandError(
                    f"Failed: {response.status_code} - {response.text[:200]}"
                )

        except requests.exceptions.RequestException as e:
            raise CommandError(f"Request failed: {e}") from e

    # =========================================================================
    # Compare Command
    # =========================================================================
    def handle_compare(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Compare local schema with APIDOG Cloud."""
        project_id, token = apidog_settings.get_credentials(
            options.get("project_id"),
            options.get("token"),
        )
        local_file = options.get("local_file")

        # Get local schema
        if not local_file:
            local_file = os.path.join(self.output_dir, "openapi_schema_latest.json")
            if not os.path.exists(local_file):
                self.stdout.write("No local schema found, exporting...")
                local_file = self.handle_export(
                    {"format": "json", "output": self.output_dir, "indent": 2}
                )

        # Get cloud schema
        cloud_file = self.handle_pull({"project_id": project_id, "token": token})

        # Load both schemas
        if cloud_file is None:
            raise CommandError("Failed to pull schema from cloud")

        with open(local_file, encoding="utf-8") as f:
            local_schema = json.load(f)
        with open(cloud_file, encoding="utf-8") as f:
            cloud_schema = json.load(f)

        # Compare endpoints
        local_paths = set(local_schema.get("paths", {}).keys())
        cloud_paths = set(cloud_schema.get("paths", {}).keys())

        only_local = local_paths - cloud_paths
        only_cloud = cloud_paths - local_paths
        common = local_paths & cloud_paths

        # Print report
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("SCHEMA COMPARISON REPORT")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Local endpoints:  {len(local_paths)}")
        self.stdout.write(f"Cloud endpoints:  {len(cloud_paths)}")
        self.stdout.write(f"Common endpoints: {len(common)}")
        self.stdout.write("=" * 60)

        if only_local:
            self.stdout.write(
                self.style.SUCCESS(f"\n[+] Only in LOCAL ({len(only_local)}):")
            )
            for path in sorted(only_local)[:20]:
                self.stdout.write(f"    {path}")
            if len(only_local) > 20:
                self.stdout.write(f"    ... and {len(only_local) - 20} more")

        if only_cloud:
            self.stdout.write(
                self.style.WARNING(f"\n[-] Only in CLOUD ({len(only_cloud)}):")
            )
            for path in sorted(only_cloud)[:20]:
                self.stdout.write(f"    {path}")
            if len(only_cloud) > 20:
                self.stdout.write(f"    ... and {len(only_cloud) - 20} more")

        if not only_local and not only_cloud:
            self.stdout.write(self.style.SUCCESS("\nSchemas are in sync!"))

        self.stdout.write("\n" + "=" * 60)

        return {
            "local_only": list(only_local),
            "cloud_only": list(only_cloud),
            "common": len(common),
        }

    # =========================================================================
    # Env-Config Command
    # =========================================================================
    def handle_env_config(self, options: Dict[str, Any]) -> str:
        """Generate environment configuration."""
        self.stdout.write("Generating environment configuration...")

        environments = apidog_settings.ENVIRONMENTS

        config_file = os.path.join(self.output_dir, "apidog_environments.json")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(environments, f, indent=2, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"Config saved to: {config_file}"))
        return config_file

    # =========================================================================
    # Helpers
    # =========================================================================
    def _print_credentials_help(self) -> None:
        """Print help for APIDOG credentials."""
        self.stdout.write(self.style.WARNING("\nAPIDAG credentials required:"))
        self.stdout.write("  Option 1 - Django settings.py:")
        self.stdout.write("    APIDOG_SETTINGS = {")
        self.stdout.write("        'PROJECT_ID': 'your-project-id',")
        self.stdout.write("        'TOKEN': 'your-api-token',")
        self.stdout.write("    }")
        self.stdout.write("")
        self.stdout.write("  Option 2 - Environment variables:")
        self.stdout.write('    export APIDOG_PROJECT_ID="your-project-id"')
        self.stdout.write('    export APIDOG_TOKEN="your-api-token"')
        self.stdout.write("")
        self.stdout.write("  Option 3 - Command arguments:")
        self.stdout.write("    --project-id=xxx --token=xxx")
