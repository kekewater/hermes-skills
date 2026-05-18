# AgentMail API Endpoints (Discovered 2026-05-16)

## Base URL
`https://api.agentmail.to/v0/`

## Authentication
Authorization: Bearer `$AGENTMAIL_API_KEY`
Content-Type: application/json

## Inboxes
```bash
# List all inboxes
GET /v0/inboxes
→ {"inboxes": [{"inbox_id": "xiao-mo-keke@agentmail.to", "email": "...", ...}]}

# Get single inbox
GET /v0/inboxes/{inbox_id}

# Create inbox
POST /v0/inboxes
{"email_prefix": "my-name", "display_name": "My Display Name"}

# Update inbox
PATCH /v0/inboxes/{inbox_id}

# Delete inbox
DEL  /v0/inboxes/{inbox_id}
```

## Messages (under an inbox)
```bash
# List messages in an inbox
GET /v0/inboxes/{inbox_id}/messages

# Get single message (by message_id, URL-encoded!)
GET /v0/inboxes/{inbox_id}/messages/{message_id_url_encoded}

# Get raw message
GET /v0/inboxes/{inbox_id}/messages/raw/{message_id_url_encoded}

# Get attachment
GET /v0/inboxes/{inbox_id}/messages/attachments/{attachment_id}

# Update message labels
PATCH /v0/inboxes/{inbox_id}/messages/{message_id}
{"labels": ["read", "important"]}

# Delete message
DEL  /v0/inboxes/{inbox_id}/messages/{message_id}

# Send a new message
POST /v0/inboxes/{inbox_id}/messages/send
{
  "to": ["recipient@example.com"],
  "cc": ["cc@example.com"],          # optional
  "bcc": ["bcc@example.com"],        # optional
  "subject": "Subject Line",
  "text": "Plain text body",
  "html": "<p>HTML body</p>"         # optional
}

# Reply to a message
POST /v0/inboxes/{inbox_id}/messages/reply
{
  "message_id": "<original-message-id>",
  "text": "Reply text",
  "html": "<p>Reply HTML</p>"        # optional
}

# Reply all
POST /v0/inboxes/{inbox_id}/messages/reply-all

# Forward
POST /v0/inboxes/{inbox_id}/messages/forward
```

## Threads
```bash
# List threads
GET /v0/inboxes/{inbox_id}/threads

# Get single thread
GET /v0/inboxes/{inbox_id}/threads/{thread_id}
```

## Attachments
- Messages have a `size` field (bytes)
- Attachment retrieval: `GET /v0/inboxes/{inbox_id}/messages/attachments/{attachment_id}`
- Standard email attachment limits apply (~25MB max per message)

## Message Model
```json
{
  "organization_id": "uuid",
  "pod_id": "uuid",
  "inbox_id": "xiao-mo-keke@agentmail.to",
  "thread_id": "uuid",
  "message_id": "<id@domain>",
  "labels": ["received", "unread"],
  "timestamp": "ISO8601",
  "from": "Sender Name <sender@example.com>",
  "to": ["recipient@example.com"],
  "subject": "Subject",
  "preview": "Short preview text",
  "text": "Plain text body",
  "html": "HTML body",
  "extracted_text": "Cleaned text",
  "headers": { /* full email headers */ },
  "size": 5911,
  "smtp_id": "provider-id"
}
```

## Important Notes
- **inbox_id** is the full email address (e.g., `xiao-mo-keke@agentmail.to`)
- **message_id** contains `<` and `>` and `@` characters — must be URL-encoded for API paths
- URL encoding: `@` → `%40`, `<` → `%3C`, `>` → `%3E`, `+` → `%2B`
- Python example: `urllib.parse.quote(message_id, safe='')`
- The `send` endpoint returns `{"message_id": "...", "thread_id": "..."}`
- Free plan likely has send limits; check dashboard for current plan details
