#!/usr/bin/env python3
"""
Export Results Script for red-tide-algal-bloom-monitoring Skill
Format and export analysis results in various formats
"""

import sys
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import argparse


@dataclass
class ExportConfig:
    """Configuration for export operations"""
    format: str = "json"  # json, csv, markdown, html
    include_metadata: bool = True
    include_timestamp: bool = True
    output_dir: Optional[Path] = None
    filename_prefix: str = "red_tide_analysis"


class ResultsExporter:
    """Handles export of analysis results in multiple formats"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.export_dir = project_root / "exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def load_result(self, result_path: Path) -> Optional[Dict[str, Any]]:
        """Load result from JSON file"""
        try:
            with open(result_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"ERROR loading result: {e}")
            return None

    def export_json(self, data: Dict[str, Any], config: ExportConfig) -> Path:
        """Export as formatted JSON"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S") if config.include_timestamp else ""
        filename = f"{config.filename_prefix}_{timestamp}.json" if timestamp else f"{config.filename_prefix}.json"
        output_path = config.output_dir / filename if config.output_dir else self.export_dir / filename

        # Export with pretty formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return output_path

    def export_csv(self, data: Dict[str, Any], config: ExportConfig) -> Path:
        """Export as CSV (flat structure for tabular data)"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S") if config.include_timestamp else ""
        filename = f"{config.filename_prefix}_{timestamp}.csv" if timestamp else f"{config.filename_prefix}.csv"
        output_path = config.output_dir / filename if config.output_dir else self.export_dir / filename

        # Flatten the data structure for CSV
        flat_data = self._flatten_data(data, config)

        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if flat_data:
                writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
                writer.writeheader()
                writer.writerows(flat_data)

        return output_path

    def export_markdown(self, data: Dict[str, Any], config: ExportConfig) -> Path:
        """Export as formatted Markdown"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S") if config.include_timestamp else ""
        filename = f"{config.filename_prefix}_{timestamp}.md" if timestamp else f"{config.filename_prefix}.md"
        output_path = config.output_dir / filename if config.output_dir else self.export_dir / filename

        # Generate markdown content
        md_content = self._generate_markdown(data, config)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return output_path

    def export_html(self, data: Dict[str, Any], config: ExportConfig) -> Path:
        """Export as formatted HTML"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S") if config.include_timestamp else ""
        filename = f"{config.filename_prefix}_{timestamp}.html" if timestamp else f"{config.filename_prefix}.html"
        output_path = config.output_dir / filename if config.output_dir else self.export_dir / filename

        # Generate HTML content
        html_content = self._generate_html(data, config)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _flatten_data(self, data: Dict[str, Any], config: ExportConfig) -> List[Dict[str, Any]]:
        """Flatten nested data structure for CSV export.

        ``config`` controls whether per-case metadata is expanded into columns
        when exporting batch ('cases') results.
        """
        # Handle different data structures
        if 'cases' in data:
            # Batch results format
            flat_data = []
            for case in data['cases']:
                row = {
                    'case_id': case.get('case_id', ''),
                    'success': case.get('success', ''),
                    'duration_seconds': case.get('duration_seconds', ''),
                    'error': case.get('error_message', ''),
                }

                if config.include_metadata and case.get('metadata'):
                    row.update(case['metadata'])

                flat_data.append(row)
            return flat_data
        else:
            # Single analysis format
            return [self._flatten_dict(data)]

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten a nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, ', '.join(str(x) for x in v)))
            else:
                items.append((new_key, v))
        return dict(items)

    def _generate_markdown(self, data: Dict[str, Any], config: ExportConfig) -> str:
        """Generate markdown content from data"""
        md_lines = []

        # Title
        md_lines.append("# Red Tide Analysis Results\n")

        # Metadata
        if config.include_metadata and 'metadata' in data:
            md_lines.append("## Metadata\n")
            for key, value in data['metadata'].items():
                md_lines.append(f"- **{key}**: {value}\n")
            md_lines.append("")

        # Analysis section
        if 'analysis' in data:
            md_lines.append("## Analysis\n")
            analysis = data['analysis']

            if 'detection' in analysis:
                md_lines.append("### Detection\n")
                for key, value in analysis['detection'].items():
                    md_lines.append(f"- **{key}**: {value}\n")
                md_lines.append("")

            if 'triggers' in analysis:
                md_lines.append("### Environmental Triggers\n")
                for key, value in analysis['triggers'].items():
                    md_lines.append(f"- **{key}**: {value}\n")
                md_lines.append("")

        # Conclusion
        if 'conclusion' in data:
            md_lines.append("## Conclusion\n")
            conclusion = data['conclusion']
            md_lines.append(f"**Category**: {conclusion.get('category', 'N/A')}\n\n")
            md_lines.append(f"{conclusion.get('summary', '')}\n\n")

        # Recommendations
        if 'recommendations' in data:
            md_lines.append("## Recommendations\n")
            for i, rec in enumerate(data['recommendations'], 1):
                md_lines.append(f"{i}. {rec.get('action', '')} (Priority: {rec.get('priority', 'N/A')})\n")
            md_lines.append("")

        # Evidence chain
        if 'evidence_chain' in data:
            md_lines.append("## Evidence Chain\n")
            for claim in data['evidence_chain']:
                md_lines.append(f"- {claim.get('claim', '')}\n")
                for evidence in claim.get('evidence', []):
                    md_lines.append(f"  - {evidence}\n")
            md_lines.append("")

        # Disclosure
        if 'disclosure' in data:
            md_lines.append("## Limitations & Disclosure\n")
            disclosure = data['disclosure']

            if 'limitations' in disclosure:
                md_lines.append("### Limitations\n")
                for lim in disclosure['limitations']:
                    md_lines.append(f"- {lim}\n")
                md_lines.append("")

            if 'uncertainties' in disclosure:
                md_lines.append("### Uncertainties\n")
                for unc in disclosure['uncertainties']:
                    md_lines.append(f"- {unc}\n")
                md_lines.append("")

        # Footer
        md_lines.append("---\n")
        md_lines.append(f"*Generated: {datetime.utcnow().isoformat()}*\n")
        md_lines.append(f"*Skill: red-tide-algal-bloom-monitoring*\n")

        return ''.join(md_lines)

    def _generate_html(self, data: Dict[str, Any], config: ExportConfig) -> str:
        """Generate HTML content from data"""
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Red Tide Analysis Results</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .metadata {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .conclusion {{
            background-color: #d5f4e6;
            padding: 20px;
            border-left: 4px solid #27ae60;
            margin: 20px 0;
        }}
        .recommendation {{
            background-color: #fff9c4;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #f39c12;
        }}
        .disclosure {{
            background-color: #fadbd8;
            padding: 15px;
            border-left: 4px solid #e74c3c;
            margin: 20px 0;
        }}
        .evidence {{
            background-color: #e8f4f8;
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid #3498db;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌊 Red Tide Analysis Results</h1>
        {content}
        <div class="footer">
            <p>Generated: {timestamp}</p>
            <p>Skill: red-tide-algal-bloom-monitoring</p>
        </div>
    </div>
</body>
</html>"""

        # Generate content sections
        content = self._generate_html_content(data, config)

        return html_template.format(
            content=content,
            timestamp=datetime.utcnow().isoformat()
        )

    def _generate_html_content(self, data: Dict[str, Any], config: ExportConfig) -> str:
        """Generate HTML content sections"""
        sections = []

        # Metadata
        if config.include_metadata and 'metadata' in data:
            sections.append('<div class="metadata">')
            sections.append('<h2>Metadata</h2>')
            sections.append('<ul>')
            for key, value in data['metadata'].items():
                sections.append(f'<li><strong>{key}:</strong> {value}</li>')
            sections.append('</ul>')
            sections.append('</div>')

        # Conclusion
        if 'conclusion' in data:
            conclusion = data['conclusion']
            sections.append('<div class="conclusion">')
            sections.append(f'<h2>Conclusion: {conclusion.get("category", "N/A")}</h2>')
            sections.append(f'<p>{conclusion.get("summary", "")}</p>')
            if 'confidence' in conclusion:
                sections.append(f'<p><strong>Confidence:</strong> {conclusion["confidence"]}</p>')
            sections.append('</div>')

        # Recommendations
        if 'recommendations' in data:
            sections.append('<h2>Recommendations</h2>')
            for i, rec in enumerate(data['recommendations'], 1):
                sections.append('<div class="recommendation">')
                sections.append(f'<h3>{i}. {rec.get("action", "")}</h3>')
                sections.append(f'<p><strong>Priority:</strong> {rec.get("priority", "N/A")}</p>')
                if 'evidence' in rec:
                    sections.append('<p><strong>Evidence:</strong></p>')
                    sections.append('<ul>')
                    for ev in rec['evidence']:
                        sections.append(f'<li>{ev}</li>')
                    sections.append('</ul>')
                sections.append('</div>')

        # Evidence Chain
        if 'evidence_chain' in data:
            sections.append('<h2>Evidence Chain</h2>')
            for claim in data['evidence_chain']:
                sections.append('<div class="evidence">')
                sections.append(f'<p><strong>Claim:</strong> {claim.get("claim", "")}</p>')
                if 'evidence' in claim:
                    sections.append('<p><strong>Evidence:</strong></p>')
                    sections.append('<ul>')
                    for ev in claim['evidence']:
                        sections.append(f'<li>{ev}</li>')
                    sections.append('</ul>')
                sections.append('</div>')

        # Disclosure
        if 'disclosure' in data:
            disclosure = data['disclosure']
            sections.append('<div class="disclosure">')
            sections.append('<h2>Limitations & Disclosure</h2>')

            if 'limitations' in disclosure:
                sections.append('<h3>Limitations</h3>')
                sections.append('<ul>')
                for lim in disclosure['limitations']:
                    sections.append(f'<li>{lim}</li>')
                sections.append('</ul>')

            if 'uncertainties' in disclosure:
                sections.append('<h3>Uncertainties</h3>')
                sections.append('<ul>')
                for unc in disclosure['uncertainties']:
                    sections.append(f'<li>{unc}</li>')
                sections.append('</ul>')

            if 'data_quality' in disclosure:
                sections.append(f'<p><strong>Data Quality:</strong> {disclosure["data_quality"]}</p>')

            sections.append('</div>')

        return '\n'.join(sections)

    def export(self, data: Dict[str, Any], config: ExportConfig) -> Path:
        """Export data in specified format"""
        format_handlers = {
            'json': self.export_json,
            'csv': self.export_csv,
            'markdown': self.export_markdown,
            'md': self.export_markdown,
            'html': self.export_html
        }

        handler = format_handlers.get(config.format.lower())
        if not handler:
            raise ValueError(f"Unsupported format: {config.format}")

        return handler(data, config)


# Global config for CLI access
config = ExportConfig()


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description="Export Red Tide Analysis Results"
    )
    parser.add_argument(
        "input",
        help="Path to input JSON file"
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "markdown", "html"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Custom output directory"
    )
    parser.add_argument(
        "--filename-prefix",
        type=str,
        default="red_tide_analysis",
        help="Filename prefix for output"
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Exclude metadata from export"
    )
    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        help="Exclude timestamp from filename"
    )

    args = parser.parse_args()

    # Configure export
    config = ExportConfig(
        format=args.format,
        include_metadata=not args.no_metadata,
        include_timestamp=not args.no_timestamp,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        filename_prefix=args.filename_prefix
    )

    # Load input data
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load input: {e}")
        sys.exit(1)

    # Export
    try:
        project_root = Path(__file__).parent.parent
        exporter = ResultsExporter(project_root)
        output_path = exporter.export(data, config)

        print(f"Exported to: {output_path}")

    except Exception as e:
        print(f"ERROR: Export failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
