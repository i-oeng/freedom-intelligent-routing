# Portfolio Talking Points

Use this project as a technical proof of how you build practical internal systems quickly.

## What To Emphasize

- Built a working Streamlit operations dashboard, not just a notebook or script.
- Used structured AI output with Pydantic validation.
- Added multimodal attachment handling for screenshots/documents.
- Designed a database-backed workflow with tickets, managers, business units, and routing results.
- Encoded business rules for skill matching, language routing, VIP handling, geography, and workload balancing.
- Added exportable results and an analyst Q&A flow.
- Added tests around routing behavior and attachment resolution.
- Added an n8n workflow blueprint showing how webhook automation could connect forms, CRMs, Claude enrichment, and PostgreSQL.

## How To Connect It To Automation Tools

- **n8n:** webhook intake, Anthropic Claude enrichment, Postgres insert, notification, and downstream routing trigger.
- **Make/Zapier:** same workflow as form submission -> AI enrichment -> database/CRM update -> Slack or email alert.
- **Airtable:** lightweight CRM table for tickets, managers, routing status, and document review queues.
- **Retool:** internal admin UI on top of the same database for operations teams.
- **Supabase:** hosted Postgres, auth, storage for attachments, and client-facing views.

## How To Say It

> I built a CRM routing system that turns messy customer intake into structured AI-enriched records, assigns work by rules and workload, and gives operators a dashboard and exportable results. I also included an n8n integration blueprint to show how the same workflow can be triggered from forms, CRMs, inboxes, or document uploads.

## What Not To Say

Do not present it as if it was built for one specific employer. Present it as a general internal-tools and workflow-automation project with patterns that transfer to CRM, operations, document processing, proposal workflows, and client dashboards.
