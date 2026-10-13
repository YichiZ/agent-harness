---
name: complaint-followup
description: How to follow up on customer complaints, including which ones still need action.
triggers: complaint, complaints, follow up, follow-up, unresolved, reimburse
---
1. Call list_complaints with the time window the operator gave (default 60 days).
2. A complaint needs follow-up when `refunded` is false and `status` is not "closed".
3. For each one that needs follow-up, schedule a 30-minute meeting with schedule_meeting on the next business day, unless the operator said otherwise.
4. Report how many complaints you found, how many needed follow-up, and how many meetings you booked.
