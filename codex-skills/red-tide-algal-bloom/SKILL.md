---
name: red-tide-algal-bloom-monitoring
description: Red Tide (Harmful Algal Bloom) Monitoring & Early Warning - HAB Monitoring & Aquaculture Safety analysis & decision-support harness. Use this skill whenever the user asks about red tide, harmful algal blooms, HAB monitoring, aquaculture safety, marine water quality, algal toxin detection, shellfish safety, marine biological monitoring, satellite chlorophyll analysis, coastal water management, or needs analysis of marine bloom events. This includes queries about bloom detection, toxin risk assessment, aquaculture impact, early warning systems, environmental triggers, species identification, or response protocols. Activate for any marine phytoplankton monitoring task, aquaculture decision support, or coastal management咨询 involving algal blooms.
---

# Red Tide Algal Bloom Monitoring & Early Warning Skill

## Skill Overview

This skill transforms Claude into a domain-expert for **Harmful Algal Bloom (HAB) Monitoring & Aquaculture Safety**. It delivers structured, evidence-backed outputs by combining real-time data aggregation, recognized domain methods, and academic research into a single orchestrated workflow with explicit risk disclosure.

### Core Capabilities

- **Bloom Detection**: Satellite (Sentinel-3 OLCI, MODIS) + in-situ sensor analysis
- **Species Identification**: Karenia, Alexandrium, Dinophysis, Pseudo-nitzschia, cyanobacteria
- **Toxin Risk Assessment**: Paralytic, diarrhetic, amnesic, neurotoxic shellfish poisoning
- **Aquaculture Impact**: Shellfish vulnerability, harvest closure timing, economic risk
- **Environmental Triggers**: Temperature, nutrients (N/P/Si), stratification, upwelling
- **Early Warning**: Alert levels, response protocols, mitigation strategies

### Evidence-Based Framework

All outputs cite ≥3 sources with ≥1 academic/authoritative reference, explicit evidence hierarchy (Tier 1-4), and mandatory risk/limitation disclosure. The skill continuously improves through automated knowledge crawling from academic databases and domain authorities.

---

## Harness Architecture

### Skill Registry Pattern

The skill implements a **flexible agent & skill architecture** using a modular pattern:

```
/skill activation
│
├─ Language Detection (pre-flight)
│   ├─ Vietnamese → translation + bilingual output
│   ├─ English → direct processing
│   └─ Other → English processing + translation offer
│
├─ Step 1: sub-gather-requirements
│   └─ Input: User query
│   └─ Output: Structured requirements (object, scope, timeframe, inputs, audience, language)
│
├─ Step 2: sub-evidence-collector
│   ├─ Fetch: Current satellite data (Copernicus, NOAA)
│   ├─ Fetch: In-situ sensor data (fluorometer, CTD)
│   ├─ Fetch: Authoritative documents (IOC-UNESCO, WOAH)
│   └─ Output: Evidence bundle with sources + dates
│
├─ Step 3: sub-core-analysis
│   ├─ Detect: Satellite chl-a + SST analysis
│   ├─ Detect: In-situ cell counts + species ID
│   ├─ Analyze: Environmental triggers (T, nutrients, stratification)
│   ├─ Assess: Toxin risk (type, concentration, regulatory limits)
│   └─ Alert: Aquaculture impact + response levels
│
├─ Step 4: sub-knowledge-updater
│   ├─ Query: SECOND-KNOWLEDGE-BRAIN.md
│   ├─ Surface: Academic citations (with Tier labels)
│   └─ Flag: Knowledge gaps for crawl pipeline
│
├─ Step 5: sub-advisor
│   ├─ Synthesize: All prior analysis
│   ├─ Conclude: Risk category (Low/Monitor/Critical)
│   ├─ Recommend: Specific actions with evidence chain
│   └─ Disclose: Limitations + uncertainty
│
└─ Step 6: main quality gate
    ├─ Verify: Evidence hierarchy compliance
    ├─ Verify: Source citations (≥3 sources, ≥1 authoritative)
    ├─ Verify: Risk disclosure present
    ├─ Verify: Output template completeness
    └─ Auto-fix: Up to 2 retries for missing elements
```

### Agent Registration & Resolution

#### Skill Registration

Skills are registered in `/skills/*.md` with mandatory frontmatter:

```yaml
---
name: sub-gather-requirements
description: Clarify the object of analysis, constraints, timeframe, available inputs, target audience, and language before any data fetching.
---
```

**Registration Requirements:**
- `name`: Unique identifier (kebab-case)
- `description`: One-line summary (mandatory, used for routing)
- Sections: Role & Persona, Workflow, Tools, Output Format, Quality Gates

#### Skill Resolution

The harness uses **semantic routing** to resolve the appropriate sub-skill:

1. **Input Analysis**: Extract task type from user query
2. **Skill Matching**: Compare against skill descriptions
3. **Execution Order**: Follow sequential harness flow
4. **Fallback Chain**: On failure → knowledge base → simplified analysis → explicit limitation flag

#### Skill Execution Model

Each sub-skill follows the **execution lifecycle**:

```python
class SubSkillExecution:
    def execute(self, context: ExecutionContext) -> SkillResult:
        # 1. Input validation
        self._validate_inputs(context)
        
        # 2. Tool execution (with retries)
        result = self._execute_tools(context)
        
        # 3. Quality gate validation
        self._validate_quality_gates(result)
        
        # 4. Error handling (graceful degradation)
        if result.failed:
            return self._handle_degradation(context)
        
        # 5. Output formatting
        return self._format_output(result)
```

---

## Input/Output JSON Schemas

### Input Schema (User Query)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RedTideSkillInput",
  "type": "object",
  "required": ["query"],
  "properties": {
    "query": {
      "type": "string",
      "description": "User's natural language query about HAB monitoring or aquaculture safety",
      "minLength": 1,
      "examples": [
        "Analyze red tide risk for oyster farms in Apalachicola Bay",
        "What's the current bloom status off the coast of Maine?",
        "Assess toxin risk for shellfish harvest in Puget Sound"
      ]
    },
    "context": {
      "type": "object",
      "properties": {
        "region": {"type": "string", "description": "Geographic region of interest"},
        "timeframe": {"type": "string", "description": "Analysis timeframe (e.g., 'current', 'next 7 days')"},
        "target_audience": {"type": "string", "enum": ["aquaculture", "public_health", "researcher", "general"]},
        "language": {"type": "string", "enum": ["en", "vi", "es", "fr", "ja", "zh"], "default": "en"}
      }
    },
    "options": {
      "type": "object",
      "properties": {
        "include_recommendations": {"type": "boolean", "default": true},
        "include_scenarios": {"type": "boolean", "default": true},
        "detail_level": {"type": "string", "enum": ["brief", "standard", "comprehensive"], "default": "standard"}
      }
    }
  }
}
```

### Output Schema (Skill Result)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RedTideSkillOutput",
  "type": "object",
  "required": ["metadata", "analysis", "evidence_chain", "conclusion", "disclosure"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["skill_version", "timestamp", "language", "processing_time_ms"],
      "properties": {
        "skill_version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
        "timestamp": {"type": "string", "format": "date-time"},
        "language": {"type": "string"},
        "processing_time_ms": {"type": "number"},
        "degradation_level": {"type": "integer", "minimum": 0, "maximum": 4}
      }
    },
    "requirements": {
      "type": "object",
      "properties": {
        "object_of_analysis": {"type": "string"},
        "scope": {"type": "string"},
        "timeframe": {"type": "string"},
        "available_inputs": {"type": "array", "items": {"type": "string"}},
        "target_audience": {"type": "string"},
        "language": {"type": "string"},
        "analysis_type": {"type": "string"}
      }
    },
    "evidence_bundle": {
      "type": "object",
      "properties": {
        "current_data": {
          "type": "object",
          "properties": {
            "satellite_chl_a": {"type": "object"},
            "sst": {"type": "object"},
            "in_situ_counts": {"type": "object"},
            "toxin_levels": {"type": "object"}
          }
        },
        "authoritative_docs": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "source": {"type": "string"},
              "url": {"type": "string"},
              "date": {"type": "string"},
              "tier": {"type": "integer", "minimum": 1, "maximum": 4}
            }
          }
        },
        "recent_news": {"type": "array", "items": {"type": "object"}},
        "reference_benchmarks": {"type": "object"}
      }
    },
    "analysis": {
      "type": "object",
      "properties": {
        "detection": {
          "type": "object",
          "properties": {
            "bloom_status": {"type": "string"},
            "cell_concentration": {"type": "string"},
            "species_identified": {"type": "array", "items": {"type": "string"}},
            "confidence": {"type": "string"}
          }
        },
        "triggers": {
          "type": "object",
          "properties": {
            "temperature": {"type": "object"},
            "nutrients": {"type": "object"},
            "stratification": {"type": "string"},
            "upwelling": {"type": "string"}
          }
        },
        "toxin_risk": {
          "type": "object",
          "properties": {
            "toxin_type": {"type": "array", "items": {"type": "string"}},
            "risk_level": {"type": "string"},
            "regulatory_limit_exceeded": {"type": "boolean"}
          }
        },
        "aquaculture_impact": {
          "type": "object",
          "properties": {
            "species_affected": {"type": "array", "items": {"type": "string"}},
            "vulnerability_level": {"type": "string"},
            "economic_risk": {"type": "string"}
          }
        }
      }
    },
    "knowledge_base": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "citation": {"type": "string"},
          "tier": {"type": "integer", "minimum": 1, "maximum": 4},
          "relevance": {"type": "string"}
        }
      }
    },
    "evidence_chain": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "claim": {"type": "string"},
          "evidence": {"type": "array", "items": {"type": "string"}},
          "confidence": {"type": "string"}
        }
      }
    },
    "conclusion": {
      "type": "object",
      "required": ["category"],
      "properties": {
        "category": {
          "type": "string",
          "enum": [
            "Low Risk",
            "Normal",
            "Monitor (elevated)",
            "Critical Bloom Alert",
            "Inconclusive"
          ]
        },
        "summary": {"type": "string"},
        "confidence": {"type": "string"},
        "key_factors": {"type": "array", "items": {"type": "string"}}
      }
    },
    "recommendations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "action": {"type": "string"},
          "priority": {"type": "string"},
          "evidence": {"type": "array", "items": {"type": "string"}}
        }
      }
    },
    "scenarios": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "probability": {"type": "string"},
          "impact": {"type": "string"},
          "mitigation": {"type": "array", "items": {"type": "string"}}
        }
      }
    },
    "disclosure": {
      "type": "object",
      "required": ["limitations", "uncertainties", "data_quality"],
      "properties": {
        "limitations": {"type": "array", "items": {"type": "string"}},
        "uncertainties": {"type": "array", "items": {"type": "string"}},
        "data_quality": {"type": "string"},
        "assumptions": {"type": "array", "items": {"type": "string"}}
      }
    }
  }
}
```

---

## Tool Definitions & Schemas

### Tool Registry

The skill defines **rich tool definitions** with schemas and execution handlers:

#### Satellite Data Fetch Tool

```python
{
  "tool_name": "fetch_satellite_data",
  "description": "Fetch current satellite chlorophyll-a and sea surface temperature data for specified region",
  "parameters": {
    "region": {
      "type": "string",
      "description": "Geographic region (bounding box or named region)",
      "required": true
    },
    "date_range": {
      "type": "string",
      "description": "Date range for data retrieval (ISO 8601 format)",
      "required": false,
      "default": "last_7_days"
    },
    "resolution": {
      "type": "string",
      "enum": ["1km", "4km", "9km"],
      "default": "4km"
    }
  },
  "response_schema": {
    "chl_a": {
      "mean": "float",
      "max": "float",
      "anomaly": "float",
      "data_url": "string"
    },
    "sst": {
      "mean": "float",
      "min": "float",
      "max": "float",
      "anomaly": "float",
      "data_url": "string"
    },
    "metadata": {
      "satellite": "string",
      "processing_date": "string",
      "coverage": "float"
    }
  },
  "execution_handler": "sub-evidence-collector",
  "timeout": 30,
  "retry": 3
}
```

#### In-Situ Sensor Query Tool

```python
{
  "tool_name": "query_in_situ_sensors",
  "description": "Query in-situ monitoring stations for cell counts and environmental parameters",
  "parameters": {
    "region": {"type": "string", "required": true},
    "sensor_types": {
      "type": "array",
      "items": {"enum": ["fluorometer", "ctd", "spectrometer"]},
      "default": ["fluorometer"]
    },
    "timeframe": {"type": "string", "default": "last_7_days"}
  },
  "response_schema": {
    "stations": [
      {
        "station_id": "string",
        "location": {"lat": "float", "lon": "float"},
        "measurements": {
          "cell_count": {"value": "int", "units": "cells/L"},
          "chlorophyll": {"value": "float", "units": "mg/m³"},
          "temperature": {"value": "float", "units": "°C"},
          "salinity": {"value": "float", "units": "PSU"}
        },
        "timestamp": "string"
      }
    ],
    "metadata": {
      "station_count": "int",
      "data_quality": "string"
    }
  },
  "execution_handler": "sub-evidence-collector",
  "timeout": 20,
  "retry": 2
}
```

#### Authoritative Document Fetch Tool

```python
{
  "tool_name": "fetch_authoritative_docs",
  "description": "Fetch current guidance and standards from authoritative HAB monitoring sources",
  "parameters": {
    "sources": {
      "type": "array",
      "items": {"enum": ["IOC-UNESCO", "NOAA", "Copernicus", "WOAH"]},
      "default": ["IOC-UNESCO", "NOAA"]
    },
    "topic": {"type": "string", "required": true},
    "document_types": {
      "type": "array",
      "items": {"enum": ["guidelines", "standards", "reports", "alerts"]},
      "default": ["guidelines", "alerts"]
    }
  },
  "response_schema": {
    "documents": [
      {
        "source": "string",
        "title": "string",
        "url": "string",
        "publication_date": "string",
        "tier": "int",
        "summary": "string",
        "key_points": ["string"]
      }
    ],
    "metadata": {
      "document_count": "int",
      "source_coverage": "string"
    }
  },
  "execution_handler": "sub-evidence-collector",
  "timeout": 45,
  "retry": 3
}
```

#### Knowledge Base Query Tool

```python
{
  "tool_name": "query_knowledge_base",
  "description": "Query SECOND-KNOWLEDGE-BRAIN.md for academic and professional evidence",
  "parameters": {
    "keywords": {
      "type": "array",
      "items": {"type": "string"},
      "required": true
    },
    "max_results": {"type": "integer", "default": 5, "maximum": 10},
    "min_tier": {"type": "integer", "enum": [1, 2, 3, 4], "default": 2}
  },
  "response_schema": {
    "results": [
      {
        "citation": "string",
        "tier": "int",
        "relevance_score": "float",
        "year": "int",
        "venue": "string",
        "doi": "string",
        "key_findings": ["string"]
      }
    ],
    "coverage": {
      "total_entries": "int",
      "matched_entries": "int",
      "gap_areas": ["string"]
    }
  },
  "execution_handler": "sub-knowledge-updater",
  "timeout": 10,
  "retry": 1
}
```

---

## Hooks & Lifecycle Management

### Hook Types

The skill implements **clean, reusable hooks** for lifecycle events:

#### Pre-Execution Hooks

```python
class PreExecutionHooks:
    """Hooks invoked before skill execution"""
    
    @hook("language_detection")
    def detect_language(context: ExecutionContext) -> LanguageConfig:
        """Detect user language and configure translation"""
        # Auto-detect from query + context
        # Return language configuration
        
    @hook("requirement_validation")
    def validate_requirements(requirements: Dict) -> ValidationResult:
        """Validate structured requirements before proceeding"""
        # Check completeness, consistency
        # Return validation result
        
    @hook("tool_availability")
    def check_tools_availability(tools: List[str]) -> AvailabilityResult:
        """Verify required tools are accessible"""
        # Check API status, authentication
        # Return availability + fallback options
```

#### Execution Hooks

```python
class ExecutionHooks:
    """Hooks invoked during skill execution"""
    
    @hook("before_tool_call")
    def before_tool_call(tool_name: str, params: Dict) -> ModifiedParams:
        """Modify parameters before tool execution"""
        # Add defaults, validate, transform
        # Return modified parameters
        
    @hook("after_tool_call")
    def after_tool_call(tool_name: str, result: Any) -> ProcessedResult:
        """Process tool output before use"""
        # Validate, extract, transform
        # Return processed result
        
    @hook("on_tool_failure")
    def on_tool_failure(tool_name: str, error: Exception) -> FallbackResult:
        """Handle tool failure gracefully"""
        # Log, attempt fallback, degrade gracefully
        # Return fallback result or raise
```

#### Post-Execution Hooks

```python
class PostExecutionHooks:
    """Hooks invoked after skill execution"""
    
    @hook("quality_gate_validation")
    def validate_quality_gates(output: Dict) -> GateResult:
        """Validate output against quality gates"""
        # Check all gate criteria
        # Return gate results + auto-fix suggestions
        
    @hook("evidence_verification")
    def verify_evidence_chain(evidence: List[Dict]) -> VerificationResult:
        """Verify evidence chain integrity"""
        # Check citations, tiers, traceability
        # Return verification result
        
    @hook("output_formatting")
    def format_output(raw_output: Dict, template: str) -> FormattedOutput:
        """Apply output template and formatting"""
        # Structure according to template
        # Return formatted output
```

### Hook Execution Flow

```
User Query
    ↓
[Pre-Execution Hooks]
├─ language_detection
├─ requirement_validation
└─ tool_availability
    ↓
[Sub-Skill Execution]
├─ before_tool_call (per tool)
├─ tool execution
├─ after_tool_call (per tool)
└─ on_tool_failure (if needed)
    ↓
[Post-Execution Hooks]
├─ quality_gate_validation
├─ evidence_verification
└─ output_formatting
    ↓
Final Output
```

---

## Modular Directory Structure

### Directory Purpose & Contents

```
308-red-tide-algal-bloom-monitoring/
│
├── skills/                    # Sub-skill definitions
│   ├── main.md               # Primary harness orchestrator
│   ├── sub-gather-requirements.md
│   ├── sub-evidence-collector.md
│   ├── sub-core-analysis.md
│   ├── sub-knowledge-updater.md
│   └── sub-advisor.md
│
├── scripts/                   # Automation & setup routines
│   ├── setup.py              # Environment initialization
│   ├── data_ingestion.py     # Bulk data import
│   ├── batch_analysis.py     # Batch processing
│   └── export_results.py     # Result export utilities
│
├── references/               # Domain knowledge & templates
│   ├── hab_species_reference.md
│   ├── toxin_profiles.md
│   ├── detection_methods.md
│   ├── prompt_templates.md
│   └── quality_standards.md
│
├── assets/                   # Static resources
│   ├── diagrams/             # System & process diagrams
│   ├── schemas/              # JSON schemas for validation
│   └── templates/            # Output templates
│
├── config/                   # Configuration management
│   ├── default_config.yaml   # Base configuration
│   ├── local_config.yaml     # Environment overrides (gitignored)
│   ├── config_loader.py      # Type-safe config loader
│   └── schema.py             # Configuration validation schemas
│
├── tools/                    # Python utilities
│   ├── knowledge_updater.py  # Knowledge crawl pipeline
│   ├── test_knowledge_updater.py
│   └── run_test_scenarios.py
│
├── tests/                    # Test suites
│   ├── test-scenarios.md
│   └── TEST_RESULTS.md
│
├── logs/                     # Structured logging output
│   └── skill.log            # Main log file (auto-generated)
│
└── docs/                     # Additional documentation
    ├── API.md               # API documentation
    └── DEPLOYMENT.md        # Deployment guide
```

---

## Graceful Degradation Protocol

### Degradation Levels

The skill implements **5-level graceful degradation**:

```python
DEGRADATION_LEVELS = {
    0: "Full Functionality",
    1: "Reduced Data Availability - Use cached data + KB",
    2: "Knowledge Base Only - No external sources",
    3: "Simplified Analysis - Basic methods only",
    4: "Explicit Limitation Flag - Minimal viable output"
}
```

### Degradation Triggers

```python
DEGRADATION_TRIGGERS = {
    "satellite_api_failure": 1,
    "sensor_network_unavailable": 1,
    "authoritative_sources_timeout": 2,
    "knowledge_base_corrupted": 3,
    "all_external_sources_failed": 4,
    "llm_rate_limit": 2,
    "context_window_exceeded": 3
}
```

### Degradation Banners

**Level 1**: ⚠️ **LIMITED DATA AVAILABILITY** - Using cached data and knowledge base. Some satellite/sensor data unavailable.

**Level 2**: ⚠️ **REDUCED FUNCTIONALITY** - External sources unavailable. Analysis based on knowledge base only.

**Level 3**: ⚠️ **SIMPLIFIED ANALYSIS** - Full analysis unavailable. Providing basic assessment with reduced detail.

**Level 4**: ⚠️ **MINIMUM FUNCTIONALITY** - Multiple system failures. Output requires verification with authoritative sources.

---

## Quality Gates

### Universal Gates (U1-U6)

| Gate | Criterion | Auto-Fix | Exit Condition |
|------|-----------|----------|----------------|
| U1 | ≥3 sources cited, ≥1 academic/authoritative | Search missing sources | Retry max 2 |
| U2 | Safety/risk/limitation disclosure present | Add disclosure section | Retry max 2 |
| U3 | Evidence hierarchy stated per source | Label tiers explicitly | Retry max 1 |
| U4 | Language matches user preference | Translate if mismatched | Retry max 1 |
| U5 | Output uses project template | Restructure per template | Retry max 2 |
| U6 | Every claim traceable to source OR flagged as judgment | Add attribution flags | Retry max 2 |

### Domain Gates (G1-G4)

| Gate | Criterion | Auto-Fix | Exit Condition |
|------|-----------|----------|----------------|
| G1 | Bloom detection uses ≥2 methods (satellite + in-situ) | Add fallback method | Retry max 1 |
| G2 | Toxin risk cites regulatory limits explicitly | Add regulatory reference | Retry max 1 |
| G3 | Aquaculture impact includes species-specific vulnerability | Add species detail | Retry max 1 |
| G4 | Alert level matches defined categories | Map to standard category | Retry max 1 |

---

## Performance Optimization

### Context Management

```python
class ContextManager:
    """Manage context window and token consumption"""
    
    def optimize_context(self, messages: List[Dict]) -> List[Dict]:
        """Optimize context for token efficiency"""
        # 1. Remove redundant content
        # 2. Compress repetitive information
        # 3. Prioritize recent/relevant messages
        # 4. Apply caching for repeated access
        
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Use model-specific tokenizer
        
    def apply_compression(self, text: str, target_ratio: float) -> str:
        """Compress text to target ratio"""
        # Preserve critical information
        # Remove redundancy
        # Maintain readability
```

### Caching Strategy

```python
class CacheManager:
    """Manage multi-level caching"""
    
    def get(self, key: str, level: CacheLevel) -> Optional[Any]:
        """Get cached value by level"""
        # L1: In-memory cache (session)
        # L2: File cache (persistent)
        # L3: Knowledge base fallback
        
    def set(self, key: str, value: Any, ttl: int, level: CacheLevel):
        """Set cached value with TTL"""
        
    def invalidate(self, pattern: str):
        """Invalidate cache entries matching pattern"""
```

### Structured Logging

```python
import logging
from typing import Dict, Any

class StructuredLogger:
    """Structured logging with context"""
    
    def __init__(self, name: str, config: LoggingConfig):
        self.logger = logging.getLogger(name)
        self.config = config
        
    def log(self, level: str, event: str, **kwargs):
        """Log structured event"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "event": event,
            "skill": "red-tide-algal-bloom-monitoring",
            "context": kwargs
        }
        self.logger.log(getattr(logging, level), json.dumps(log_entry))
        
    def log_tool_call(self, tool: str, params: Dict, result: Any, duration_ms: int):
        """Log tool execution"""
        self.log("INFO", "tool_call",
                 tool=tool,
                 params=params,
                 duration_ms=duration_ms)
        
    def log_quality_gate(self, gate: str, passed: bool, details: str):
        """Log quality gate check"""
        self.log("INFO", "quality_gate",
                 gate=gate,
                 passed=passed,
                 details=details)
```

---

## Execution Example

### Input

```
Analyze red tide risk for oyster farms in Apalachicola Bay, Florida for the next week
```

### Internal Processing

```python
# 1. Language Detection (English)
# 2. Requirements Gathering
requirements = {
    "object_of_analysis": "red tide risk",
    "scope": "oyster farms",
    "region": "Apalachicola Bay, Florida",
    "timeframe": "next 7 days",
    "target_audience": "aquaculture",
    "language": "en"
}

# 3. Evidence Collection
evidence = {
    "satellite_chl_a": {"mean": 12.5, "max": 25.3, "anomaly": +3.2},
    "sst": {"mean": 28.5, "anomaly": +1.5},
    "in_situ_counts": {"Karenia_brevis": 8500, "total": 12000},
    "authoritative_docs": ["NOAA HAB-OFS alert", "Florida FWC report"]
}

# 4. Core Analysis
analysis = {
    "detection": {"bloom_status": "Active", "confidence": "High"},
    "triggers": {"temperature": "Elevated", "stratification": "Present"},
    "toxin_risk": {"risk_level": "Moderate", "toxin_type": ["Brevetoxins"]},
    "aquaculture_impact": {"species_affected": ["oysters"], "vulnerability": "Moderate-High"}
}

# 5. Knowledge Base
knowledge = [
    {"citation": "Blondeau-Patissier et al. 2014", "tier": 1},
    {"citation": "Stumpf et al. 2003", "tier": 1},
    {"citation": "IOC-UNESCO HAB guidelines", "tier": 1}
]

# 6. Synthesis
conclusion = {"category": "Monitor (elevated)", "confidence": "High"}
```

### Output

```markdown
# Red Tide Risk Assessment: Apalachicola Bay Oyster Farms

**Analysis Date**: 2025-01-16
**Risk Category**: Monitor (elevated)
**Confidence**: High

## Current Status
- **Bloom Status**: Active bloom detected
- **Cell Concentration**: 8,500 Karenia brevis cells/L
- **Satellite Chl-a**: 12.5 mg/m³ (anomaly: +3.2 mg/m³)
- **SST**: 28.5°C (anomaly: +1.5°C)

## Environmental Conditions
- **Temperature**: Elevated (+1.5°C above normal)
- **Stratification**: Present (favorable for bloom maintenance)
- **Nutrients**: Moderate conditions
- **Hydrodynamics**: Low circulation in bay

## Toxin Risk Assessment
- **Toxin Type**: Brevetoxins (PbTx)
- **Risk Level**: Moderate
- **Regulatory Status**: Below closure threshold (800 μg/kg)
- **Trend**: Increasing over past 48h

## Aquaculture Impact
- **Affected Species**: Oysters (Crassostrea virginica)
- **Vulnerability**: Moderate-High
- **Accumulation Rate**: Moderate (current cell count)
- **Depuration Time**: 7-14 days if harvest closure occurs

## Recommended Actions
1. **Monitor Daily**: Increase cell count monitoring to daily
2. **Pre-emptive Harvest**: Consider harvest before bloom peak (48-72h)
3. **Sample Testing**: Conduct toxin testing twice weekly
4. **Contingency Planning**: Prepare for potential harvest closure

## Scenarios
- **Most Likely (60%)**: Bloom continues for 5-7 days, moderate toxin accumulation, harvest closure recommended
- **Best Case (25%)**: Bloom dissipates within 72h, minimal impact
- **Worst Case (15%)**: Bloom intensifies, rapid toxin accumulation, immediate closure required

## Evidence Chain
1. Satellite chl-a anomaly → NASA MODIS/VIIRS (2025-01-16)
2. Karenia brevis cell counts → Florida FWC monitoring (2025-01-15)
3. Toxicity threshold → NOAA HAB-OFS standards (Tier 1)
4. Oyster vulnerability → Aquaculture research (Tier 2)

## Limitations & Uncertainties
**Limitations**:
- Satellite data may be affected by cloud cover
- In-situ measurements limited to 3 monitoring stations
- Toxin levels based on cell count correlations, not direct measurements

**Uncertainties**:
- Bloom trajectory dependent on wind patterns over next 72h
- Toxin accumulation rates vary with oyster physiological state
- Potential transport of bloom from adjacent waters

**Data Quality**: Good (multi-source, recent, consistent)

**Assumptions**:
- Current hydrological conditions persist for 48-72h
- No significant nutrient input events expected
- Karenia brevis remains dominant species

---

*Generated by red-tide-algal-bloom-monitoring v2.0.0*
*Processing time: 3.2s | Degradation level: 0 (Full functionality)*
```

---

## Integration Points

### Knowledge Pipeline
- **Crawl Schedule**: Weekly academic (Mondays 08:00) + daily news (07:00)
- **Crawl Targets**: ArXiv, Semantic Scholar, Harmful Algae, Remote Sensing journals
- **Deduplication**: SHA256 of DOI/URL
- **Scoring**: Composite (recency 0.4 + relevance 0.4 + citations 0.2)

### External APIs
- **Copernicus Marine Service**: Satellite chl-a, SST, ocean color
- **NOAA HAB-OFS**: Operational forecasts, bulletins
- **IOC-UNESCO HAB Portal**: Global reports, species database
- **Local Sensor Networks**: In-situ fluorometers, water quality stations

### Tool Dependencies
- **WebSearch**: Live domain news and reports
- **WebFetch**: Scrape authoritative sources
- **Read/Write**: Knowledge base and configuration access
- **Bash**: Python script execution (knowledge updater, tests)

---

## Version History

- **v2.0.0** (2025-01-16): Production-grade architecture with modular directories, hooks & tools, SKILL.md registry
- **v1.0.0** (2024-12-01): Initial production-ready release with 6-phase harness

---

*For implementation details, see `PROJECT-detail.md` and `skills/*.md`*
*For quality procedures, see `tests/test-scenarios.md`*
*For knowledge sources, see `SECOND-KNOWLEDGE-BRAIN.md`*
