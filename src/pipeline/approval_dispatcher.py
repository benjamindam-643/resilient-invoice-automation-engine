"""Human-in-the-Loop Approval & Escalation Dispatcher.

Routes invoice exceptions (GST errors, over-limit, duplicate flags) to approvers
via Microsoft Teams / Slack / Telegram webhooks with interactive decision buttons.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import requests

logger = logging.getLogger(__name__)


class ApprovalDispatcher:
    """Dispatches approval requests and handles human-in-the-loop review routing."""

    def __init__(self, teams_webhook_url: Optional[str] = None) -> None:
        self.webhook_url = teams_webhook_url

    def build_teams_card(self, invoice_data: Dict[str, Any], flags: list[str]) -> Dict[str, Any]:
        """Builds an adaptive card payload for Microsoft Teams / Slack."""
        flag_summary = "\n- ".join(flags) if flags else "No anomalies detected."
        return {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": f"⚠️ Invoice Approval Required: #{invoice_data.get('invoice_number', 'N/A')}",
                                "weight": "Bolder",
                                "size": "Medium",
                                "color": "Attention",
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {"title": "Supplier:", "value": invoice_data.get("supplier_name", "Unknown")},
                                    {"title": "Amount:", "value": f"${invoice_data.get('total', 0.0):.2f}"},
                                    {"title": "Anomalies:", "value": f"- {flag_summary}"},
                                ],
                            },
                        ],
                        "actions": [
                            {"type": "Action.Submit", "title": "✅ Approve", "data": {"action": "approve"}},
                            {"type": "Action.Submit", "title": "❌ Reject", "data": {"action": "reject"}},
                        ],
                    },
                }
            ],
        }

    def dispatch_for_review(self, invoice_data: Dict[str, Any], flags: list[str]) -> bool:
        """Sends the approval card to the configured channel."""
        payload = self.build_teams_card(invoice_data, flags)
        logger.info(f"[Approval Gate] Invoice #{invoice_data.get('invoice_number')} routed for manual review.")

        if not self.webhook_url:
            logger.warning("[Approval Gate] Webhook URL not set; simulated dispatch successful.")
            return True

        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            return resp.status_code in (200, 202)
        except Exception as e:
            logger.error(f"[Approval Gate] Failed to dispatch review card: {e}")
            return False
