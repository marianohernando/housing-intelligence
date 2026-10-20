# Notifications Delivery Architecture

## Components
- event;
- eligibility/alert rule;
- deduplication;
- preference;
- delivery;
- status.

## Rules
- idempotent;
- no duplicate spam;
- quiet/digest modes;
- retry;
- unsubscribe.

## Privacy
Notification payloads should not expose sensitive profile data on lock screen/email subject.
