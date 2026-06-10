# Integration Blueprints

These files show how the CRM routing app can connect to lightweight automation tools without changing the core product into a company-specific demo.

## What This Demonstrates

- **n8n / Make / Zapier workflow design:** webhook intake, normalization, Claude enrichment, database update, and team notification.
- **Airtable / Supabase readiness:** the app already models structured tables for tickets, managers, business units, and routing results.
- **Retool-style internal tools:** the database schema and final routing table can be used directly for operations dashboards.
- **Document workflow thinking:** attachments are resolved locally and passed into AI analysis, which is the same pattern used for bills, screenshots, contracts, and statements.

## Included Artifacts

- `n8n/ticket-routing-workflow.example.json`: example n8n workflow export showing a webhook-driven ticket automation.
- `../docs/model_n8n_supabase_guide.md`: model choice, n8n workflow plan, and Supabase setup notes.

## Suggested Demo Story

1. Show the Streamlit app as the internal operations dashboard.
2. Show `router.py` as the business-rules automation layer.
3. Show `main.py` as the structured Anthropic Claude enrichment layer.
4. Show the n8n example as the integration layer that could trigger this workflow from a form, CRM, inbox, or document upload.
5. Explain that Airtable, Retool, Supabase, or Zapier can sit around the same database-backed workflow depending on team maturity.
