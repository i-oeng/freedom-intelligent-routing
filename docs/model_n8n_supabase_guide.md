# Model, n8n, and Supabase Guide

## Model Choice

Use `claude-haiku-4-5` as the default model for this project.

Why:

- Fast and cost-aware for repeated CRM ticket triage.
- Strong enough for first-pass classification, summarization, priority scoring, and routing support.
- Better fit for high-volume automation workflows than using a larger model for every ticket.

Recommended setup:

```bash
ANTHROPIC_MODEL="claude-haiku-4-5"
```

Use these alternatives when needed:

- `claude-sonnet-4-6`: harder screenshots, messier documents, analyst Q&A, and deeper reasoning.
- `claude-opus-4-8`: complex document review, messy contracts, or high-stakes reasoning.
- `claude-fable-5`: only for the most demanding reasoning or long-horizon agentic work; likely overkill for normal CRM routing.

For this app, the practical split is:

- Batch ticket classification: `claude-haiku-4-5`
- Screenshot/document-aware classification: start with `claude-haiku-4-5`, switch to `claude-sonnet-4-6` if quality is weak
- Analyst Q&A over final results: `claude-haiku-4-5` for simple questions, `claude-sonnet-4-6` for deeper analysis
- Complex underwriting/proposal review later: `claude-opus-4-8`

## How n8n Fits

n8n should sit around the app as an automation layer, not replace the core Python logic.

Useful workflows:

1. **Webhook intake**
   - Trigger from Typeform, Tally, website form, CRM form, inbox parser, or internal tool.
   - Normalize fields into `client_guid`, `description`, `segment`, `city`, and `attachment`.

2. **AI enrichment**
   - Call Anthropic from n8n for quick classification, or send the record to the Python app/database and let `main.py` classify it.
   - Keep the Python analyzer as the canonical logic if you want tested behavior.

3. **Database write**
   - Insert normalized tickets into Supabase/Postgres.
   - Optionally insert an automation log row for debugging.

4. **Notification**
   - Send Slack, Telegram, email, or CRM notification when a VIP/high-priority ticket arrives.

5. **Follow-up automation**
   - If priority is high, create a task.
   - If attachment is missing, request the document.
   - If language is KZ/ENG, route to the right queue.

Included example:

```text
integrations/n8n/ticket-routing-workflow.example.json
```

Recommended n8n workflow:

```text
Webhook -> Normalize Payload -> Anthropic Classification -> Supabase/Postgres Insert -> Respond -> Notify Team
```

## How Supabase Fits

Use Supabase as the hosted Postgres backend for this project.

What to put in Supabase:

- `tickets`
- `managers`
- `business_units`
- `routing_results`
- optional future table: `automation_logs`
- optional future table: `documents`

Basic setup:

1. Create a Supabase project.
2. Copy the Postgres connection string.
3. Put it in `.env.local` as `DATABASE_URL`.
4. Run:

```bash
python database.py
python load.py
```

For local Streamlit or a long-running server, use Supabase's direct or session-style connection string when available.

For serverless jobs, edge functions, or many short n8n executions, use Supabase's transaction pooler connection string. Be aware that transaction pooling does not support prepared statements, so avoid client settings that force prepared statements.

Future Supabase upgrades:

- Use Supabase Storage for uploaded screenshots/documents.
- Use Supabase Auth for manager/client login.
- Use Row Level Security for client-facing views.
- Use database views for dashboards:
  - manager workload
  - high-priority tickets
  - SLA queue
  - processed vs pending tickets

## Best Portfolio Story

Present the system as three layers:

1. **Python app:** internal dashboard, AI enrichment, routing logic.
2. **n8n:** workflow automation and integrations.
3. **Supabase:** hosted Postgres, auth/storage path, and operational data layer.

That shows you can build the core system and also connect it to practical low-code/internal-tool stacks.
