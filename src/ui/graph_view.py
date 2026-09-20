"""
Interactive Regulatory Graph Explorer using Vis.js.
Renders force-directed knowledge graph of AI system specifications,
regulatory requirements, and SHACL validation status.
"""

import json
from typing import Dict, Any, List
from src.core.models import ConformityReport, AssertionStatus


class RegulatoryGraphView:
    def generate_html_graph(self, report: ConformityReport) -> str:
        """
        Generates an interactive Vis.js HTML graph visualization embedded in an iframe.
        """
        meta = report.system_metadata
        nodes = []
        edges = []

        # 1. Central System Node
        sys_id = f"sys_{meta.system_id}"
        sys_color = "#10b981" if report.overall_conforms else "#ef4444"
        nodes.append({
            "id": sys_id,
            "label": f"AI SYSTEM\n{meta.name}\n(v{meta.version})",
            "shape": "hexagon",
            "size": 35,
            "color": {
                "background": sys_color,
                "border": "#0f172a",
                "highlight": {"background": sys_color, "border": "#3b82f6"},
            },
            "font": {"color": "#ffffff", "face": "Segoe UI", "size": 14, "bold": True},
            "title": f"<b>{meta.name}</b><br>Risk Class: {meta.eu_risk_classification}<br>Domain: {meta.domain}",
        })

        # 2. Regulatory Article Nodes (EU AI Act Title III)
        articles = [
            {"id": "art_9", "label": "Art 9: Risk\nManagement", "desc": "Continuous risk management system"},
            {"id": "art_10", "label": "Art 10: Data\nGovernance", "desc": "Training/validation dataset governance"},
            {"id": "art_10_bias", "label": "Art 10(2)(f):\nBias Mitigation", "desc": "Demographic parity and bias audits"},
            {"id": "art_12", "label": "Art 12: Automated\nLogging", "desc": "Inference and event logging"},
            {"id": "art_13", "label": "Art 13:\nTransparency", "desc": "Instructions for use and model cards"},
            {"id": "art_14", "label": "Art 14: Human\nOversight", "desc": "Human-in-the-loop and manual override"},
            {"id": "art_15", "label": "Art 15:\nCybersecurity", "desc": "Adversarial robustness and resilience"},
        ]

        # Check which articles have violations
        violated_articles = set()
        for v in report.violations:
            for art in articles:
                art_num = art["label"].split(":")[0].replace("Art ", "").strip()
                if art_num in v.regulatory_article:
                    violated_articles.add(art["id"])

        for art in articles:
            is_violated = art["id"] in violated_articles
            art_color = "#fca5a5" if is_violated else "#bfdbfe"
            art_border = "#dc2626" if is_violated else "#2563eb"
            
            nodes.append({
                "id": art["id"],
                "label": art["label"],
                "shape": "box",
                "margin": 10,
                "color": {
                    "background": art_color,
                    "border": art_border,
                    "highlight": {"background": "#e2e8f0", "border": art_border},
                },
                "font": {"color": "#0f172a", "face": "Segoe UI", "size": 12, "bold": True},
                "title": f"<b>{art['label']}</b><br>{art['desc']}<br>Status: {'❌ VIOLATION DETECTED' if is_violated else '✅ SATISFIED'}",
            })

            # Edge from System to Article
            edges.append({
                "from": sys_id,
                "to": art["id"],
                "color": {"color": "#dc2626" if is_violated else "#94a3b8", "highlight": "#2563eb"},
                "width": 2 if not is_violated else 3,
                "dashes": is_violated,
            })

        # 3. Extracted Claim / Control Nodes
        article_mapping = {
            "RISK_MANAGEMENT": "art_9",
            "DATA_GOVERNANCE": "art_10",
            "BIAS_MITIGATION": "art_10_bias",
            "RECORD_KEEPING": "art_12",
            "TRANSPARENCY": "art_13",
            "HUMAN_OVERSIGHT": "art_14",
            "FAIL_SAFE": "art_14",
            "ACCURACY_ROBUSTNESS": "art_15",
            "CYBERSECURITY": "art_15",
        }

        for idx, claim in enumerate(report.claims_analyzed):
            claim_node_id = f"claim_{claim.claim_id}"
            
            if claim.assertion_status == AssertionStatus.IMPLEMENTED:
                c_color = "#34d399"
                c_border = "#059669"
                status_icon = "🟢"
            elif claim.assertion_status == AssertionStatus.PLANNED:
                c_color = "#fcd34d"
                c_border = "#d97706"
                status_icon = "🟡"
            else:
                c_color = "#f87171"
                c_border = "#b91c1c"
                status_icon = "🔴"

            nodes.append({
                "id": claim_node_id,
                "label": f"{status_icon} {claim.entity_text[:20]}\n[{claim.assertion_status.value}]",
                "shape": "ellipse",
                "color": {
                    "background": c_color,
                    "border": c_border,
                    "highlight": {"background": "#ffffff", "border": c_border},
                },
                "font": {"color": "#0f172a", "face": "Segoe UI", "size": 11},
                "title": (
                    f"<b>{claim.claim_id}: {claim.entity_text}</b><br>"
                    f"Status: <b>{claim.assertion_status.value}</b> (Confidence: {claim.confidence:.2f})<br>"
                    f"Target: {claim.normative_article}<br>"
                    f"<i>\"{claim.evidence_quote}\"</i>"
                ),
            })

            # Connect Claim to its Regulatory Article
            target_art = article_mapping.get(claim.category.value, "art_9")
            edges.append({
                "from": target_art,
                "to": claim_node_id,
                "color": {"color": c_border},
                "width": 1.5,
            })

        nodes_json = json.dumps(nodes)
        edges_json = json.dumps(edges)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
            <style type="text/css">
                body, html {{
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    background: #f8fafc;
                }}
                #network {{
                    width: 100%;
                    height: 520px;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    background: #ffffff;
                }}
                .legend {{
                    position: absolute;
                    bottom: 12px;
                    left: 12px;
                    background: rgba(255, 255, 255, 0.95);
                    border: 1px solid #cbd5e1;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 11px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    display: flex;
                    gap: 12px;
                    z-index: 10;
                    color: #1e293b;
                }}
                @media (prefers-color-scheme: dark) {{
                    body, html {{
                        background: #0f172a;
                        color: #f8fafc;
                    }}
                    #network {{
                        background: #1e293b;
                        border-color: #334155;
                    }}
                    .legend {{
                        background: rgba(30, 41, 59, 0.95);
                        border-color: #475569;
                        color: #f1f5f9;
                    }}
                }}
                .legend-item {{
                    display: flex;
                    align-items: center;
                    gap: 5px;
                }}
                .dot {{
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                }}
            </style>
        </head>
        <body>
            <div id="network"></div>
            <div class="legend">
                <div class="legend-item"><div class="dot" style="background: #10b981;"></div> Implemented / Conforming</div>
                <div class="legend-item"><div class="dot" style="background: #f59e0b;"></div> Planned / Borderline</div>
                <div class="legend-item"><div class="dot" style="background: #ef4444;"></div> Absent / SHACL Violation</div>
                <div class="legend-item"><div class="dot" style="background: #3b82f6;"></div> Regulatory Article</div>
            </div>

            <script type="text/javascript">
                var container = document.getElementById('network');
                var data = {{
                    nodes: new vis.DataSet({nodes_json}),
                    edges: new vis.DataSet({edges_json})
                }};
                var options = {{
                    nodes: {{
                        borderWidth: 2,
                        shadow: true
                    }},
                    edges: {{
                        smooth: {{
                            type: 'cubicBezier',
                            forceDirection: 'none',
                            roundness: 0.3
                        }}
                    }},
                    physics: {{
                        solver: 'forceAtlas2Based',
                        forceAtlas2Based: {{
                            gravitationalConstant: -70,
                            centralGravity: 0.015,
                            springLength: 95,
                            springConstant: 0.08
                        }},
                        minVelocity: 0.75
                    }},
                    interaction: {{
                        hover: true,
                        tooltipDelay: 100,
                        zoomView: true
                    }}
                }};
                var network = new vis.Network(container, data, options);
            </script>
        </body>
        </html>
        """
        return html
