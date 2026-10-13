---
name: refunds
description: Policy for issuing refunds through the payment tool.
triggers: refund, refunds, reimburse, money back, chargeback
---
- Look up the order amount with get_payment before refunding; never invent an amount.
- Refund the full order amount unless the operator names a partial amount.
- Refunds over $500 need the operator's approval; the harness pauses and asks for it automatically.
- After refunding, add a CRM note on the complaint saying the refund was issued.
