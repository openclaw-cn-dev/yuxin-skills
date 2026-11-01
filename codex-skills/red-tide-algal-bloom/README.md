# red-tide-algal-bloom-monitoring

**Red Tide (Harmful Algal Bloom) Monitoring & Early Warning**

[![Claude Skill](https://img.shields.io/badge/Claude-Skill-blue)](https://claude.ai/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version: 2.0.0](https://img.shields.io/badge/Version-2.0.0-brightgreen.svg)](https://github.com/972026)

A production-grade Claude Code harness for **Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety** — gathers real-time
authoritative data, applies recognized domain methods, integrates academic
research, and delivers evidence-backed, risk-disclosed outputs.

## Features

### Core Capabilities (v2.1.0)
- **Real-time Data Aggregation**: Satellite (Copernicus, NOAA), in-situ sensors, authoritative sources
- **Domain Analysis**: Species identification, toxin risk assessment, aquaculture impact evaluation
- **Knowledge Integration**: Auto-updating knowledge base with academic research
- **Risk Disclosure**: Explicit limitation flags and uncertainty quantification
- **Multi-language Support**: English, Vietnamese, with extensible language system

### Production Enhancements (v2.1.0)
- **Modular Architecture**: Flexible agent/skill design with comprehensive registry
- **Context Management**: Token optimization, compression, and multi-level caching
- **Structured Logging**: Performance tracking, tool execution, and quality monitoring
- **Graceful Degradation**: 5-level failure handling with automatic recovery
- **Configuration Management**: Type-safe, environment-aware configuration system
- **Automation Tools**: Batch processing, export utilities, data ingestion, and environment setup

## Installation

### Quick Start
```bash
# Clone repository
git clone https://github.com/972026/308-red-tide-algal-bloom-monitoring.git
cd 308-red-tide-algal-bloom-monitoring

# Run setup script
python scripts/setup.py

# Install dependencies
pip install -r requirements.txt
```

### Skill Installation
Copy to `~/.claude/skills/red-tide-algal-bloom-monitoring/` or use via project CLAUDE.md.

### Environment Setup
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Basic Usage
```bash
/red-tide-algal-bloom-monitoring [your query]
```

### Example Queries
```bash
# Analyze red tide risk for aquaculture
/red-tide-algal-bloom-monitoring Analyze red tide risk for oyster farms in Apalachicola Bay for the next week

# Assess bloom status
/red-tide-algal-bloom-monitoring What is the current harmful algal bloom status off the coast of Maine?

# Toxin risk evaluation
/red-tide-algal-bloom-monitoring Assess toxin risk for shellfish harvest in Puget Sound

# Environmental trigger analysis
/red-tide-algal-bloom-monitoring Evaluate environmental conditions that could trigger a bloom in the Gulf of Mexico
```

## Architecture

### Harness Flow
```
User Input
    |
[Language Detection]
    |
[Sub-skills Execution]
    |-- sub-gather-requirements (Clarify analysis parameters)
    |-- sub-evidence-collector (Fetch authoritative data)
    |-- sub-core-analysis (HAB monitoring and assessment)
    |-- sub-knowledge-updater (Query knowledge base)
    |-- sub-advisor (Synthesize and recommend)
    |
[Quality Gates] (U1-U6 + G1-G4)
    |
[Risk-Disclosed Output]
```

### Directory Structure
```
308-red-tide-algal-bloom-monitoring/
|-- config/              # Configuration management
|   |-- default_config.yaml
|   |-- local_config.example.yaml
|   |-- config_loader.py
|-- references/          # Domain knowledge and templates
|   |-- hab_species_reference.md
|   |-- toxin_profiles.md
|   |-- detection_methods.md
|   |-- prompt_templates.md
|   |-- quality_standards.md
|-- assets/              # Static resources and schemas
|   |-- diagrams/        # Mermaid architecture diagrams
|   |-- schemas/         # JSON schemas for validation
|   |-- templates/       # Output templates
|-- scripts/             # Automation utilities
|   |-- setup.py
|   |-- batch_analysis.py
|   |-- export_results.py
|   |-- data_ingestion.py
|   |-- context_manager.py
|   |-- structured_logger.py
|   |-- graceful_degradation.py
|-- skills/              # Sub-skill definitions
|   |-- main.md
|   |-- sub-gather-requirements.md
|   |-- sub-evidence-collector.md
|   |-- sub-core-analysis.md
|   |-- sub-knowledge-updater.md
|   |-- sub-advisor.md
|-- tools/               # Python utilities
|-- tests/               # Test suites
|-- logs/                # Structured logging output
```

## Configuration

### Environment Variables
```bash
# LLM Configuration
export RED_TIDE_SKILL_LLM_MODEL_DEFAULT="claude-sonnet-4-6"
export RED_TIDE_SKILL_LLM_TEMPERATURE="0.7"

# Logging
export RED_TIDE_SKILL_LOGGING_LEVEL="INFO"

# Features
export RED_TIDE_SKILL_FEATURES_ENABLE_ML_PREDICTIONS="true"
```

### Configuration Files
- `config/default_config.yaml`: Base configuration
- `config/local_config.yaml`: Environment overrides (copy from example)
- `.env.example`: Environment variable reference

## Automation

### Setup
```bash
python scripts/setup.py
```

### Data Ingestion
```bash
# List available data sources
python scripts/data_ingestion.py --list-sources

# Ingest all enabled sources
python scripts/data_ingestion.py

# Ingest specific source types
python scripts/data_ingestion.py --type satellite in_situ

# Show ingestion statistics
python scripts/data_ingestion.py --stats
```

### Batch Processing
```bash
# Create sample manifest
python scripts/batch_analysis.py sample

# Run batch analysis
python scripts/batch_analysis.py manifest.json --parallel
```

### Export Results
```bash
# Export as JSON
python scripts/export_results.py input.json --format json

# Export as Markdown
python scripts/export_results.py input.json --format markdown

# Export as HTML
python scripts/export_results.py input.json --format html
```

## Development

### Testing
```bash
# Full automated test suite (pytest) - 64 tests, <1s, offline
python -m pytest tests/

# Run knowledge updater unit tests
python tools/test_knowledge_updater.py

# Run harness test scenarios (84 structural/content checks)
python tools/run_test_scenarios.py

# Run setup verification
python scripts/setup.py
```

The pytest suite in `tests/` provides deterministic, offline regression coverage
for configuration, context/token management, graceful degradation, data
ingestion, result export, and the knowledge-base crawl pipeline. Run it from
the repository root; `tests/conftest.py` resolves the import paths.

### Knowledge Pipeline
```bash
# Update knowledge base (weekly academic)
python tools/knowledge_updater.py

# Update with news only (daily)
python tools/knowledge_updater.py --news-only

# Dry run
python tools/knowledge_updater.py --dry-run
```

## Documentation

- [SKILL.md](SKILL.md): Complete skill registry and execution flow
- [PROJECT-detail.md](PROJECT-detail.md): Full technical specification
- [PROJECT-DEVELOPMENT-PHASE-TRACKING.md](PROJECT-DEVELOPMENT-PHASE-TRACKING.md): Development roadmap and v2.0.0 enhancements
- [references/hab_species_reference.md](references/hab_species_reference.md): Comprehensive HAB species guide
- [references/toxin_profiles.md](references/toxin_profiles.md): Detailed toxin chemistry and effects
- [references/detection_methods.md](references/detection_methods.md): Satellite and in-situ detection methods
- [references/quality_standards.md](references/quality_standards.md): Quality gate specifications
- [assets/diagrams/architecture.mermaid](assets/diagrams/architecture.mermaid): System architecture diagram
- [assets/diagrams/harness_flow.mermaid](assets/diagrams/harness_flow.mermaid): Harness execution sequence

## Quality Assurance

### Quality Gates
- **Universal (U1-U6)**: Evidence citations, disclosure, traceability
- **Domain (G1-G4)**: Multi-method detection, regulatory limits, species-specific impact

### Performance Metrics
- Token estimation accuracy
- Cache hit rates
- Context compression ratios
- Operation duration tracking

### Error Handling
- Graceful degradation (5 levels)
- Automatic fallback chains
- Recovery mechanisms
- Explicit limitation flags

## Data Sources
- IOC-UNESCO HAB references
- NOAA HAB-OFS references
- Copernicus satellite (Sentinel-3 OLCI) references
- Phytoplankton/toxin references (WOAH)
- Aquaculture safety references
- Sensor (chl-a fluorometer) references

## Roadmap

- [x] Phase 0: Architecture & Design
- [x] Phase 1: Core Sub-Skills (5)
- [x] Phase 2: Main Harness + Quality Gates
- [x] Phase 3: Knowledge Pipeline + Cron
- [x] Phase 4: Testing & Validation
- [x] Phase 5: Integration & Polish — PRODUCTION READY v2.0.0

## Contributing

This is a production-grade skill following the 972026 Skill Library standard. See `SKILL-STANDARD.md` for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details

## Citation

```bibtex
@software{red-tide-algal-bloom-monitoring,
  title = {red-tide-algal-bloom-monitoring: Red Tide (Harmful Algal Bloom) Monitoring & Early Warning},
  year = {2026},
  version = {2.0.0}
}
```

## Acknowledgments

- 972026 Skill Library
- IOC-UNESCO HAB Programme
- NOAA HAB-OFS
- Copernicus Marine Service
- Academic research community
