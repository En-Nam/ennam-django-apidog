# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-11-28

### Added
- Initial release
- Management command `apidog` with subcommands:
  - `export` - Export OpenAPI schema from Django
  - `validate` - Validate OpenAPI schema files
  - `push` - Push local schema to APIDOG Cloud
  - `pull` - Pull schema from APIDOG Cloud
  - `compare` - Compare local schema with APIDOG Cloud
  - `env-config` - Generate environment configuration
  - `init` - Initialize apidog directory with templates
- Schema hooks for drf-spectacular (`BaseSerializerExtension`)
- Configurable settings via `APIDOG_SETTINGS`
- Templates for Makefile, Docker Compose, and gitignore
- Full documentation and examples

[Unreleased]: https://github.com/ennam/ennam-django-apidog/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ennam/ennam-django-apidog/releases/tag/v0.1.0
