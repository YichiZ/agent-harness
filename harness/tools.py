"""Agentic tools (the "schedule meeting / CRM / payments" box), over an in-memory backend.

The backend is a stand-in for real CRM, calendar and payment APIs. Its state is
inspectable, so tests can check outcomes in code ("was the meeting actually
booked?") instead of trusting the model's reply.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Callable

APPROVAL_LIMIT_USD = 500.0

SEED_COMPLAINTS = [
    {"id": "C-1", "customer_id": "cust-ana", "order_id": "A-1001", "days_ago": 12, "summary": "Blender arrived cracked", "refunded": False, "status": "open"},
    {"id": "C-2", "customer_id": "cust-ben", "order_id": "A-1002", "days_ago": 30, "summary": "Wrong colour sofa cover", "refunded": False, "status": "open"},
    {"id": "C-3", "customer_id": "cust-cho", "order_id": "A-1003", "days_ago": 45, "summary": "Late delivery", "refunded": True, "status": "closed"},
    {"id": "C-4", "customer_id": "cust-dee", "order_id": "A-1004", "days_ago": 90, "summary": "Missing screws", "refunded": False, "status": "open"},
]
SEED_PAYMENTS = {"A-1001": 89.0, "A-1002": 129.0, "A-1003": 42.0, "A-1004": 640.0}


@dataclass
class Backend:
    complaints: list[dict] = field(default_factory=lambda: copy.deepcopy(SEED_COMPLAINTS))
    payments: dict[str, float] = field(default_factory=lambda: dict(SEED_PAYMENTS))
    meetings: list[dict] = field(default_factory=list)
    notes: list[dict] = field(default_factory=list)
    refunds: list[dict] = field(default_factory=list)


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    run: Callable[[Backend, dict], Any]
    # Returns a reason string when this call must wait for a human, else None.
    needs_approval: Callable[[Backend, dict], str | None] = lambda b, a: None
    ends_turn: bool = False  # ask_user: the loop stops and the question becomes the reply

    def spec(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description,
                "input_schema": self.input_schema}


def _obj(props: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


def _list_complaints(b: Backend, a: dict) -> list[dict]:
    days = a.get("days", 60)
    return [c for c in b.complaints if c["days_ago"] <= days]


def _get_payment(b: Backend, a: dict) -> dict:
    if a["order_id"] not in b.payments:
        raise ValueError(f"unknown order {a['order_id']}")
    return {"order_id": a["order_id"], "amount_usd": b.payments[a["order_id"]]}


def _schedule(b: Backend, a: dict) -> dict:
    when = a.get("date") or (date.today() + timedelta(days=1)).isoformat()
    m = {"id": f"M-{len(b.meetings) + 1}", "customer_id": a["customer_id"], "date": when, "minutes": a.get("minutes", 30)}
    b.meetings.append(m)
    return m


def _note(b: Backend, a: dict) -> dict:
    n = {"complaint_id": a["complaint_id"], "note": a["note"]}
    b.notes.append(n)
    return {"ok": True}


def _refund(b: Backend, a: dict) -> dict:
    paid = b.payments.get(a["order_id"])
    if paid is None:
        raise ValueError(f"unknown order {a['order_id']}")
    if a["amount_usd"] > paid:
        raise ValueError(f"refund {a['amount_usd']} exceeds amount paid {paid}")
    r = {"order_id": a["order_id"], "amount_usd": a["amount_usd"]}
    b.refunds.append(r)
    for c in b.complaints:
        if c["order_id"] == a["order_id"]:
            c["refunded"] = True
    return {"ok": True, **r}


def _refund_needs_approval(b: Backend, a: dict) -> str | None:
    if a.get("amount_usd", 0) > APPROVAL_LIMIT_USD:
        return f"refund of ${a['amount_usd']:.2f} on {a.get('order_id')} is over the ${APPROVAL_LIMIT_USD:.0f} limit"
    return None


TOOLS: list[Tool] = [
    Tool("list_complaints", "List customer complaints from the last N days, with refund status.",
         _obj({"days": {"type": "integer", "description": "Look-back window in days."}}, ["days"]), _list_complaints),
    Tool("get_payment", "Get the amount paid for an order.",
         _obj({"order_id": {"type": "string"}}, ["order_id"]), _get_payment),
    Tool("schedule_meeting", "Book a follow-up meeting with a customer.",
         _obj({"customer_id": {"type": "string"},
               "date": {"type": "string", "description": "ISO date; omit for next day."},
               "minutes": {"type": "integer"}}, ["customer_id"]), _schedule),
    Tool("add_crm_note", "Add a note to a complaint in the CRM.",
         _obj({"complaint_id": {"type": "string"}, "note": {"type": "string"}}, ["complaint_id", "note"]), _note),
    Tool("refund_payment", "Refund an order (moves money; irreversible).",
         _obj({"order_id": {"type": "string"}, "amount_usd": {"type": "number"}}, ["order_id", "amount_usd"]),
         _refund, needs_approval=_refund_needs_approval),
    Tool("ask_user", "Ask the operator one clarifying question when the request is ambiguous. Ends your turn.",
         _obj({"question": {"type": "string"}}, ["question"]), lambda b, a: {"asked": a["question"]}, ends_turn=True),
]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}
