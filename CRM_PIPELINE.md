# AETHER AI — CRM Pipeline Setup Guide

**Version:** 1.0
**Date:** May 22, 2026
**Author:** AETHER AI Sales Operations
**Related Documents:** PROSPECT_LIST.md (220 prospects)

---

## Table of Contents

1. [Sales Pipeline Stages](#1-sales-pipeline-stages)
2. [Lead Scoring Model](#2-lead-scoring-model)
3. [Outreach Sequence Automation](#3-outreach-sequence-automation)
4. [CRM Platform Setup (Airtable)](#4-crm-platform-setup-airtable)
5. [Reporting Dashboard](#5-reporting-dashboard)
6. [Data Import Procedure](#6-data-import-procedure)

---

## 1. Sales Pipeline Stages

AETHER AI uses an 8-stage pipeline from first touch to closed deal. Every lead moves through these stages sequentially — no skipping allowed.

### Pipeline Overview

| Stage | Definition | Entry Criteria | Exit Criteria | Expected Duration |
|-------|-----------|---------------|---------------|------------------|
| **Lead** | Prospect identified and added to CRM, no outreach yet | Prospect data imported (company, website, contact, priority) from PROSPECT_LIST.md or other source | Lead scored and assigned to SDR | 0–2 days |
| **Contacted** | First outreach sent (email or LinkedIn) | Lead is scored + assigned to a rep | Prospect replies OR 3 follow-ups sent with no reply | 3–14 days |
| **Qualified** | Prospect confirmed as good fit via reply or LinkedIn acceptance | Prospect responded to outreach | Demo booked on calendar (mutually agreed time) | 3–14 days |
| **Demo Booked** | A confirmed demo/presentation on the calendar | Prospect confirmed time slot; calendar invite sent | Demo completed (prospect attended) | 1–7 days |
| **Demo Completed** | Product demo has been delivered | Demo meeting held (attended or no-show with follow-up) | Proposal sent to prospect | 1–3 days |
| **Proposal Sent** | Formal proposal/quote delivered to prospect | Demo completed + SDR/AE drafted proposal | Prospect responds with questions, requests revision, or indicates buying intent | 3–14 days |
| **Negotiation** | Active negotiation on pricing, scope, or terms | Prospect gave positive signal or asked for pricing discussion | Verbal agreement OR deal lost | 3–30 days |
| **Closed Won** | Contract signed, payment received | Negotiation concluded with agreement from both sides | — (terminal stage) | — |
| **Closed Lost** | Opportunity declined or dead | Prospect explicitly declined, ghosted >60 days, or disqualified | — (terminal stage) | — |

### Stage Rules

- **No backsliding:** A lead never moves backward. If a lead at "Demo Booked" doesn't show, move to "Demo Completed" (no-show) and send a rebooking link — don't go back to "Qualified."
- **Ghosting timeout:** If a prospect stops responding at any stage for **14 consecutive days**, move to "Closed Lost" with reason: "Ghosted."
- **Re-entry:** A Closed Lost lead can re-enter as "Lead" if a new trigger event occurs (new funding, new leadership, platform migration) — only after a 90-day cooldown.
- **Auto-promotions:** Stage changes that should happen automatically via Airtable automation:
  - Lead → Contacted: when first outreach is logged
  - Contacted → Qualified: when reply is detected (via Zapier/email integration)
  - Demo Booked → Demo Completed: after the scheduled meeting time passes

### Stage Buckets (for Reporting)

| Bucket | Stages Included |
|--------|----------------|
| **Top of Funnel** | Lead, Contacted |
| **Middle of Funnel** | Qualified, Demo Booked |
| **Bottom of Funnel** | Demo Completed, Proposal Sent, Negotiation |
| **Closed** | Closed Won, Closed Lost |

---

## 2. Lead Scoring Model

Leads are scored automatically on import using a weighted formula. The score determines assignment priority and outreach sequence velocity.

### Scoring Formula

```
score = (catalog_size × 0.30)
      + (revenue_tier × 0.25)
      + (platform_match × 0.20)
      + (industry_fit × 0.15)
      + (engagement × 0.10)

Maximum possible score: 100
```

### Dimension Scoring Tables

#### Catalog Size (weight: 0.30)
| Est. SKU Count | Points |
|----------------|--------|
| 500+ | 100 |
| 200–499 | 80 |
| 100–199 | 60 |
| 50–99 | 40 |
| < 50 | 20 |

#### Revenue Tier (weight: 0.25)
| Est. Revenue | Points |
|-------------|--------|
| $100M+ | 100 |
| $50M–$100M | 90 |
| $20M–$50M | 75 |
| $5M–$20M | 55 |
| < $5M | 30 |

#### Platform Match (weight: 0.20)
| Platform | Points |
|----------|--------|
| Shopify Plus | 100 |
| Shopify | 85 |
| WooCommerce | 70 |
| Magento / Custom | 50 |
| Other / Unknown | 20 |

#### Industry Fit (weight: 0.15)
| Industry | Points | Rationale |
|----------|--------|-----------|
| Fashion & Apparel | 100 | Highest product photography volume, seasonal collections |
| Beauty & Personal Care | 90 | Editorial-grade imagery, high SKU rotation |
| Home Goods & Decor | 95 | Room-scene photography at scale |
| Jewelry & Accessories | 85 | Macro photography, high SKU density |
| Automotive Parts | 95 | Massive catalogs, installation photos needed |
| Sporting Goods | 80 | Action/lifestyle + product shots |
| Electronics | 75 | Product hero shots + lifestyle |
| Food & Beverage | 60 | Lower SKU counts, specialized photography |
| Pet & Other | 50 | Lower volume, broader need |

#### Engagement (weight: 0.10)
| Signal | Points |
|--------|--------|
| Inbound lead / Referral | 100 |
| LinkedIn accepted + replied to email | 80 |
| Opened email + clicked link | 70 |
| Opened email only | 50 |
| No engagement | 20 |
| Bounced / Invalid contact | 0 |

*Note: Engagement score starts at 20 for new imports and updates dynamically as the prospect interacts with outreach.*

### Score Ranges

| Grade | Score Range | Priority Label | Auto-Assignment | Action |
|-------|------------|----------------|-----------------|--------|
| **A** | 80–100 | Hot | SDR assigned within 24 hours, highest outreach velocity | Priority outreach sequence (Day 0, 3, 7, 14), AE looped in |
| **B** | 60–79 | Warm | SDR assigned within 48 hours, standard sequence | Standard outreach sequence, qualification needed |
| **C** | 40–59 | Cool | Added to nurture queue, SDR assigned weekly batch | Educational drip, monthly check-in |
| **D** | < 40 | Cold | No SDR assigned; added to long-term nurture | Monthly newsletter only, reviewed quarterly |

### Auto-Assignment Rules

1. **A-grade leads:** Auto-assigned to the SDR with the fewest active A-grade leads (round-robin load balancing). CC the AE for the territory.
2. **B-grade leads:** Auto-assigned to the next available SDR (round-robin across all SDRs).
3. **C-grade leads:** Batched weekly and assigned in bulk to the most junior SDR for nurture.
4. **D-grade leads:** No SDR assigned. Added to automated monthly newsletter list only.
5. **Territory override:** If a lead's Location matches an AE's named territory, assign to that AE's paired SDR regardless of load balance.
6. **Re-assignment:** If an SDR hasn't made first contact within 48 hours, the lead is auto-reassigned.

### Score Examples (from PROSPECT_LIST.md)

| Company | Catalog | Revenue | Platform | Industry | Base Score | Grade |
|---------|---------|---------|----------|----------|-----------|-------|
| Everlane | 500+ (100) | $100M–$200M (100) | Shopify Plus (100) | Fashion (100) | (100×0.30)+(100×0.25)+(100×0.20)+(100×0.15)+(20×0.10) = **92** | **A** |
| Allbirds | 200+ (80) | $270M (100) | Shopify Plus (100) | Fashion (100) | (80×0.30)+(100×0.25)+(100×0.20)+(100×0.15)+(20×0.10) = **89** | **A** |
| Blueland | 80+ (40) | $15M–$30M (55) | Shopify (85) | Home (95) | (40×0.30)+(55×0.25)+(85×0.20)+(95×0.15)+(20×0.10) = **56** | **C** |
| Vetta Capsule | 100+ (60) | $5M–$10M (55) | Shopify (85) | Fashion (100) | (60×0.30)+(55×0.25)+(85×0.20)+(100×0.15)+(20×0.10) = **63** | **B** |

---

## 3. Outreach Sequence Automation

AETHER AI uses a structured multi-channel outreach sequence. The sequence adapts based on lead grade and stops automatically on any reply.

### Base Sequence (A & B Grade)

| Day | Channel | Content | Action by |
|-----|---------|---------|-----------|
| **0** | Email (Cold) | **Intro email:** Brief, personalized, value-prop focused. Subject line references the brand's catalog size or recent launch. Include social proof: "We help [similar brand] produce product photography 4x faster." | Automated (template) |
| **3** | Email (Follow-up) | **Value-add:** Share a relevant industry insight, case study, or ROI calculator link. New subject line. No hard sell. | Automated (template) |
| **7** | LinkedIn | **Connection request:** Personalized note referencing their role and AETHER AI's relevance. "Love what [Company] is doing with [specific product line]. Would love to connect." | SDR manual (with template) |
| **14** | Email (Breakup) | **Final outreach:** "Last email — if the timing isn't right, no problem. Here's a link to a 2-minute explainer video if you're ever curious." Soft close, clear opt-out. | Automated (template) |
| **30** | Email (Re-engagement) | **Trigger-based:** Only sent if the prospect opened any prior email but didn't reply. "Noticed you checked out our case study — thought you might find this new data on e-commerce photography ROI interesting." | Automated (conditional) |

### C-Grade Sequence (Slower Cadence)

| Day | Channel | Content |
|-----|---------|---------|
| **0** | Email | Same intro email (light on case studies, heavier on education) |
| **14** | Email | Industry whitepaper link: "The Cost of Product Photography at Scale" |
| **30** | Email | Invitation to upcoming webinar / product demo |
| **60** | Email | Case study from similar brand (if available) |
| **90** | Email | Re-engagement / "Are you still there?" |

### Automation Rules

1. **Auto-stop on reply:** Any email reply (even "not interested") immediately stops ALL future automated outreach. The lead status is updated to "Qualified" (or "Closed Lost" if the reply indicates disinterest).
2. **Open tracking:** If a prospect opens 3+ emails without replying, flag for SDR manual LinkedIn outreach (bypass Day 7 auto-LinkedIn).
3. **Bounce handling:** Email bounces are auto-detected. After 2 bounces, the lead moves to "Closed Lost" with reason "Invalid contact."
4. **Unsubscribe:** One-click unsubscribe in every email footer. Unsubscribed leads auto-move to "Closed Lost."
5. **LinkedIn rate limits:** SDRs should send no more than 30 LinkedIn connection requests per day to avoid soft bans. The CRM tracks daily LinkedIn activity.

### Template Library

All email templates are stored in Airtable's "Email Templates" table with variables:
- `{{company_name}}`
- `{{contact_first_name}}`
- `{{contact_role}}`
- `{{similar_brand_vertical}}` (e.g., "home goods brand")
- `{{sku_count_range}}`
- `{{platform_name}}`
- `{{sdr_name}}`
- `{{meeting_link}}`
- `{{case_study_link}}`

---

## 4. CRM Platform Setup (Airtable)

**Platform:** Airtable (Free tier to start, Team tier if >50K records or automation needs grow)

### Table Schema

#### Primary Table: `Leads`

| Field Name | Field Type | Description | Required |
|------------|-----------|-------------|----------|
| `Prospect #` | Number | Sequential ID from PROSPECT_LIST.md | Yes |
| `Company` | Single line text | Legal business name | Yes |
| `Website` | URL | Primary e-commerce domain | Yes |
| `Est. Revenue` | Single select | $100M+, $50M–$100M, $20M–$50M, $5M–$20M, <$5M | Yes |
| `Est. SKU Count` | Single select | 500+, 200–499, 100–199, 50–99, <50 | Yes |
| `Platform` | Single select | Shopify Plus, Shopify, WooCommerce, Magento/Custom, Other | Yes |
| `Location` | Single line text | City, State | Yes |
| `Industry` | Single select | Fashion, Beauty, Home, Electronics, Sporting, Auto, Jewelry, Food, Pet | Yes |
| `Contact Role` | Single line text | Decision-maker title | No |
| `Contact Source` | Single line text | LinkedIn, Crunchbase, etc. | No |
| `Priority (Legacy)` | Single select | A, B, C (from original prospect list) | Yes |
| `Lead Score` | Formula | `(catalog_points × 0.30) + (revenue_points × 0.25) + (platform_points × 0.20) + (industry_points × 0.15) + (engagement_points × 0.10)` | Auto |
| `Score Grade` | Formula | `IF(score>=80,"A",IF(score>=60,"B",IF(score>=40,"C","D")))` | Auto |
| `Pipeline Stage` | Single select | Lead, Contacted, Qualified, Demo Booked, Demo Completed, Proposal Sent, Negotiation, Closed Won, Closed Lost | Yes (default: Lead) |
| `Assigned To` | Collaborator | SDR or AE responsible | No |
| `AE (Account Exec)` | Collaborator | AE overseeing the deal (for A-grade and later stages) | No |
| `Email (Primary)` | Email | Primary contact email | No |
| `Email (Secondary)` | Email | Backup contact email | No |
| `Phone` | Phone | Direct line | No |
| `LinkedIn URL` | URL | LinkedIn profile of contact | No |
| `Company LinkedIn` | URL | Company LinkedIn page | No |
| `Notes` | Long text | Internal notes, call summaries, objections | No |
| `First Contacted Date` | Date | Date first outreach was sent | No |
| `Last Contacted Date` | Date | Date of last communication | No |
| `Demo Date` | Date | Scheduled demo date/time | No |
| `Proposal Sent Date` | Date | Date proposal was delivered | No |
| `Closed Date` | Date | Date deal was won/lost | No |
| `Deal Value` | Currency | Estimated annual contract value | No |
| `Closed Reason` | Single select | Ghosted, Budget, Not a fit, Competitor, Timing, No decision, Other | No |
| `Days in Current Stage` | Formula | `DATETIME_DIFF(TODAY(), stage_entry_date, "days")` | Auto |
| `Stage Entry Date` | Date | When the lead entered the current stage (auto-set by automation) | Auto |
| `Engagement Score` | Number (0–100) | Updated dynamically by email tracking | Default: 20 |
| `Email Status` | Single select | Valid, Bounced, Unsubscribed, Unknown | No |
| `Outreach Sequence Day` | Number | Current day in the outreach sequence (0, 3, 7, 14, 30, or null) | Auto |
| `Sequence Paused` | Checkbox | True if prospect replied (auto-stop) | Auto |
| `Tags` | Multiple select | High priority, Inbound, Referral, Need research, Warm intro, etc. | No |
| `Last Activity Date` | Date | Most recent activity (email open, reply, call, note added) | No |

#### Secondary Table: `Email Templates`

| Field Name | Field Type | Description |
|------------|-----------|-------------|
| `Template Name` | Single line text | Human-readable name |
| `Sequence Day` | Number | Which day in sequence (0, 3, 14, 30) |
| `Subject Line` | Single line text | Subject with variables |
| `Body` | Long text | Email body with variables |
| `Grade Target` | Multiple select | Which grades use this (A, B, C) |
| `Active` | Checkbox | Whether template is currently in rotation |

#### Secondary Table: `Activities`

| Field Name | Field Type | Description |
|------------|-----------|-------------|
| `Lead` | Link to Leads | Which lead this activity relates to |
| `Activity Type` | Single select | Email sent, Email opened, Email replied, LinkedIn request, LinkedIn accepted, Call, Note, Stage change |
| `Activity Date` | Date/Time | When the activity occurred |
| `Description` | Long text | Notes about the activity |
| `Created By` | Collaborator | Who logged the activity |

### Views

Create these views for the `Leads` table:

#### 1. Pipeline Kanban (main view)
- **View type:** Kanban
- **Group by:** Pipeline Stage (ordered: Lead → Contacted → Qualified → Demo Booked → Demo Completed → Proposal Sent → Negotiation → Closed Won, Closed Lost)
- **Sort by:** Score Grade (descending), then Last Activity Date (ascending)
- **Visible fields:** Company, Score Grade, Assigned To, Deal Value, Days in Current Stage
- **Colors:** Stage-based color coding
  - Lead/Contacted: Gray
  - Qualified/Demo Booked: Blue
  - Demo Completed/Proposal Sent: Yellow
  - Negotiation: Orange
  - Closed Won: Green
  - Closed Lost: Red

#### 2. All Leads (table view)
- **View type:** Grid
- **Filters:** None (all leads)
- **Sort by:** Company (A-Z)
- **Visible fields:** All fields
- **Group by:** None
- **Purpose:** Data management and bulk editing

#### 3. Priority A Only
- **View type:** Grid
- **Filters:** Score Grade = A, Pipeline Stage ≠ Closed Won, Pipeline Stage ≠ Closed Lost
- **Sort by:** Lead Score (descending)
- **Visible fields:** Company, Website, Industry, Lead Score, Pipeline Stage, Assigned To, Days in Current Stage, Contact Role, Email
- **Group by:** Pipeline Stage
- **Purpose:** Daily focus for AEs and SDRs on highest-value opportunities

#### 4. My Outreach This Week
- **View type:** Grid
- **Filters:** Assigned To = Me, Pipeline Stage = Lead OR Contacted OR Qualified, Last Contacted Date ≤ 7 days ago
- **Sort by:** Last Contacted Date (ascending) — oldest first
- **Visible fields:** Company, Pipeline Stage, Days in Current Stage, Lead Score, Outreach Sequence Day, Last Contacted Date
- **Purpose:** SDR daily task list — shows who needs to be contacted today
- **Conditional formatting:** Highlight rows where Days in Current Stage > 14 (red)

### Automations

#### Automation 1: Demo Booked → Calendar Link
- **Trigger:** When Pipeline Stage changes to "Demo Booked"
- **Condition:** Demo Date is not empty
- **Action:** Send email to lead contact with:
  - Calendar invite (.ics attachment)
  - Meeting link (Zoom/Google Meet)
  - Pre-demo checklist (what to prepare)
  - Auto-add to AETHER AI's CRM calendar
- **CC:** Assigned AE

#### Automation 2: Reply Detected → Stage Change
- **Trigger:** When Activity Type = "Email replied" for a lead
- **Condition:** Pipeline Stage is Lead or Contacted
- **Action:** Update Pipeline Stage to "Qualified", pause outreach sequence (Sequence Paused = True)

#### Automation 3: Stage Entry Date Setter
- **Trigger:** When Pipeline Stage changes
- **Action:** Update Stage Entry Date to TODAY()

#### Automation 4: Days-in-Stage Warning
- **Trigger:** Daily schedule (every morning)
- **Condition:** Days in Current Stage > expected duration for stage (see pipeline table)
- **Action:** Send notification to Assigned To (Airtable reminder or Slack via Zapier)

#### Automation 5: Lead Score Recalculation
- **Trigger:** When any score-related field changes (Est. SKU Count, Est. Revenue, etc.)
- **Action:** Recalculate Lead Score and Score Grade formulas

### Integration: Webhook Notifications

Use Airtable's webhook feature (via Zapier or Make.com) to send notifications:

| Trigger Event | Destination | Payload |
|-------------|------------|---------|
| Lead imported | #leads Slack channel | `New lead: {{Company}} ({{Score Grade}}) — {{Industry}}` |
| Stage → Demo Booked | AE + SDR Slack DM | `🎯 Demo booked: {{Company}} on {{Demo Date}}` |
| Stage → Closed Won | #wins Slack channel | `🎉 Deal won: {{Company}} — ${{Deal Value}}` |
| Stage → Closed Lost | AE + SDR Slack DM | `❌ Lost: {{Company}} — Reason: {{Closed Reason}}` |
| Days in Stage > 14 | SDR Slack DM | `⏰ Stale lead: {{Company}} at {{Pipeline Stage}} for {{Days in Current Stage}} days` |

### Airtable Base Structure

```
AETHER AI CRM (Base)
├── Leads (Table)          ← Primary
│   ├── Pipeline Kanban    (Kanban view)
│   ├── All Leads          (Grid view)
│   ├── Priority A Only    (Grid view)
│   └── My Outreach This Week (Grid view)
├── Email Templates (Table)
│   └── All Templates      (Grid view)
├── Activities (Table)
│   └── All Activities     (Grid view)
└── Pipeline Settings (Table)  [Optional: stores stage durations, thresholds]
```

---

## 5. Reporting Dashboard

Create a dedicated Airtable Interface (or connect to Google Sheets / Metabase for richer visualization).

### Monthly Metrics Table

Track these metrics **monthly** at the top of the dashboard:

| Metric | Definition | Target (Month 1) | Target (Month 3) |
|--------|-----------|------------------|------------------|
| Leads Generated | New leads added to CRM | 220 (from import) | 30 new |
| Outreach Sent | First emails sent (Contacted stage) | 50 | 100 |
| Replies Received | Any email reply received | 10 | 25 |
| Demos Booked | Leads moved to Demo Booked | 5 | 15 |
| Demos Completed | Demos actually attended | 4 | 12 |
| Proposals Sent | Leads moved to Proposal Sent | 3 | 8 |
| Closed Won | Deals won | 1 | 3 |
| Total Pipeline Value | Sum of Deal Value for all active deals | — | $150K+ |

### Conversion Rate Funnel

Calculate the conversion rate between each adjacent stage:

```
Lead → Contacted:       outreach_sent / total_leads × 100
Contacted → Qualified:  replies / outreach_sent × 100
Qualified → Demo Booked: demos_booked / qualified × 100
Demo Booked → Completed: demos_completed / demos_booked × 100
Completed → Proposal:   proposals_sent / demos_completed × 100
Proposal → Negotiation: negotiation / proposals_sent × 100
Negotiation → Closed Won: closed_won / negotiation × 100
Overall (Lead → Won):   closed_won / total_leads × 100
```

**Benchmark targets for B2B SaaS (AI/e-commerce):**

| Stage Transition | Industry Benchmark | AETHER Target |
|-----------------|-------------------|---------------|
| Lead → Contacted | 80%+ | 90% |
| Contacted → Qualified | 15–25% | 20% |
| Qualified → Demo Booked | 40–60% | 50% |
| Demo Booked → Completed | 75–85% | 80% |
| Completed → Proposal | 60–80% | 70% |
| Proposal → Negotiation | 50–70% | 60% |
| Negotiation → Closed Won | 40–60% | 50% |
| **Lead → Won (overall)** | **1–3%** | **5%** |

### Time-in-Stage Averages

Track average (mean) and maximum days in each stage, refreshed weekly:

| Stage | Week 1 Avg | Target |
|-------|-----------|--------|
| Lead | — | ≤ 2 days |
| Contacted | — | ≤ 10 days |
| Qualified | — | ≤ 7 days |
| Demo Booked | — | ≤ 3 days |
| Demo Completed | — | ≤ 2 days |
| Proposal Sent | — | ≤ 7 days |
| Negotiation | — | ≤ 14 days |
| **Total cycle** | — | **≤ 45 days** |

**Warning flags:**
- Any stage exceeding 2× the target avg → auto-flag in Slack
- Total cycle > 60 days → weekly executive review

### Pipeline Value (Weighted)

Calculate weighted pipeline value using stage-based probability:

| Stage | Probability Weight | Formula |
|-------|-------------------|---------|
| Lead | 5% | sum(deal_value × 0.05) |
| Contacted | 10% | sum(deal_value × 0.10) |
| Qualified | 20% | sum(deal_value × 0.20) |
| Demo Booked | 35% | sum(deal_value × 0.35) |
| Demo Completed | 50% | sum(deal_value × 0.50) |
| Proposal Sent | 65% | sum(deal_value × 0.65) |
| Negotiation | 80% | sum(deal_value × 0.80) |
| **Weighted Pipeline** | — | **Sum of all weighted values** |

**Display at top of dashboard:**
```
Total Pipeline (raw):      $XXX,XXX
Weighted Pipeline:         $XXX,XXX
Closed Won (this month):   $XX,XXX
Closed Won (all time):     $XXX,XXX
```

### Dashboard Widgets (Suggested Layout)

```
┌─────────────────────────────────────────────────────┐
│  PIPELINE OVERVIEW                                   │
│  Total Leads: 220  |  Active: 215  |  Won: 0  |  Lost: 5  │
│  Weighted Pipeline: $XXX  |  Raw Pipeline: $XXX         │
├─────────────────────────────────────────────────────┤
│  FUNNEL (Bar Chart)        │  MONTHLY TREND (Line)    │
│  Lead         ██████  220  │  ┌─┐                      │
│  Contacted    ████    180  │  │ │  Demos: 5           │
│  Qualified    ██       40  │  │ │  Won: 1             │
│  Demo Booked  █        15  │  └─┘                     │
│  Demo Done    █        12  │  May Jun Jul             │
│  Proposal     █        8   │                          │
│  Closed Won   ▏        1   │                          │
├────────────────────────────┼─────────────────────────┤
│  STAGE VELOCITY            │  TOP PERFORMERS          │
│  Stage          Avg  Max   │  SDR Name    | Demos    │
│  Lead          2d   5d     │  Alice        | 4        │
│  Contacted     7d   14d    │  Bob          | 3        │
│  ...                      │  Carol        | 2        │
└─────────────────────────────────────────────────────┘
```

### Dashboard Refresh Cadence

| Update Type | Frequency | Owner |
|------------|-----------|-------|
| Automated data pull | Real-time (live from Airtable) | System |
| Manual data review | Weekly (Monday AM) | SDR Lead |
| Pipeline forecast | Weekly (Monday) | Sales Manager |
| Executive report | Monthly (1st) | Sales Ops |
| Quarter review | Quarterly | VP Sales |

---

## 6. Data Import Procedure

### Importing the 220-Prospect List

The complete prospect list is documented in `PROSPECT_LIST.md`. Below is the step-by-step import procedure.

#### Step 1: Prepare the CSV

Convert PROSPECT_LIST.md to a structured CSV with these columns:

| CSV Column Header | Source in PROSPECT_LIST.md | Airtable Field Mapping | Data Type Notes |
|-------------------|---------------------------|----------------------|-----------------|
| `prospect_number` | Column `#` | Prospect # | Integer |
| `company` | Column `Company` | Company | Text |
| `website` | Column `Website` | Website | URL (prepend `https://` if missing) |
| `revenue` | Column `Est. Revenue` | Est. Revenue | Map to single-select values: `$100M+`, `$50M–$100M`, `$20M–$50M`, `$5M–$20M`, `<$5M` |
| `sku_count` | Column `Est. SKU Count` | Est. SKU Count | Map to single-select: `500+`, `200–499`, `100–199`, `50–99`, `<50` |
| `platform` | Column `Platform` | Platform | Map to single-select: `Shopify Plus`, `Shopify`, `WooCommerce`, `Magento/Custom`, `Other` |
| `location` | Column `Location` | Location | Text |
| `contact_role` | Column `Contact Role` | Contact Role | Text |
| `contact_source` | Column `Contact Source` | Contact Source | Text |
| `priority_legacy` | Column `Priority` | Priority (Legacy) | Single select: A, B, C |
| `industry` | Column `Notes` (inferred from section header) | Industry | Map based on section header (see Industry Mapping below) |
| `notes` | Column `Notes` | Notes | Text |

#### Industry Mapping (from Section Headers)

| PROSPECT_LIST.md Section | Industry Value |
|--------------------------|---------------|
| FASHION & APPAREL | Fashion |
| BEAUTY & PERSONAL CARE | Beauty |
| HOME GOODS & DECOR | Home |
| ELECTRONICS & ACCESSORIES | Electronics |
| SPORTING GOODS & OUTDOOR | Sporting |
| AUTOMOTIVE PARTS & ACCESSORIES | Auto |
| JEWELRY, WATCHES & ACCESSORIES | Jewelry |
| FOOD, BEVERAGE & NUTRITION | Food |
| PET & MISCELLANEOUS | Pet |

#### Step 2: Import into Airtable

1. Go to Airtable base → "All Leads" view → File → Import → CSV
2. Upload the prepared CSV file
3. **Field mapping review:** Check each Airtable field is correctly mapped from the CSV column
4. **Auto-fields:** Verify that `Lead Score`, `Score Grade`, `Pipeline Stage` (default: Lead), `Stage Entry Date` (default: TODAY()), and `Engagement Score` (default: 20) are auto-populated
5. **Import mode:** "Append records" (do not overwrite existing data)
6. **Run validation:** After import, check that the record count matches (220) and that no fields are empty for required columns

#### Step 3: Post-Import Validation

Run these checks:

| Check | Expected | If Failed |
|-------|----------|-----------|
| Record count | 220 | Re-import missing records |
| Score grades populated | All 220 have A/B/C/D | Check Lead Score formula |
| Pipeline Stage = "Lead" | All 220 | Bulk update to "Lead" |
| No null companies | 220/220 | Manually fill from source |
| Priority breakdown | A: 145, B: 50, C: 25 | Verify against PROSPECT_LIST.md appendix |
| Industry distribution | Fashion: 55, Beauty: 25, Home: 30, etc. | Verify against PROSPECT_LIST.md appendix |

#### Step 4: Deduplication Rules

Airtable has no native dedup on import. Apply these rules **manually after import**:

1. **Primary dedup key:** `Company` (exact match, case-insensitive). Sort by Company alphabetically, scan for duplicates.
2. **Secondary dedup key:** `Website` (normalized: strip `www.` and trailing `/`). Two records with the same normalized website are duplicates.
3. **Defined duplicates from PROSPECT_LIST.md:**
   - Mizzen+Main appears twice (prospects #17 and #42) — **merge into one record** keeping the earliest prospect number, combine notes
   - Marine Layer appears twice (prospects #4 and #153) — **merge into one record**
   - Outerknown appears twice (prospects #9 and #155) — **merge into one record**
   - Mejuri appears twice (prospects #176 and #196) — **merge into one record**, keeping CA office location and Canadian operations noted
   - Outdoor Voices appears as Fashion (prospect #14) and Sporting Goods (prospect #132) — **merge into one record**, Industry = Fashion
4. **Merge behavior:**
   - Keep the lower prospect number
   - Concatenate Notes fields
   - Keep the earliest-estimated revenue value
   - Combine Contact Roles if different
   - Keep the higher Priority (Legacy) rating
5. **After dedup:** Expected total = **215 unique companies** (220 - 5 known duplicates)

#### CSV Generation Script

For reference, a script to convert PROSPECT_LIST.md to CSV:

```bash
# Bash: Parse the markdown table rows into CSV
# Uses sed/awk to extract rows from each section
# Output: airtable_import.csv with all columns mapped
# Run from the directory containing PROSPECT_LIST.md

echo "prospect_number,company,website,revenue,sku_count,platform,location,contact_role,contact_source,priority_legacy,industry,notes" > airtable_import.csv

# Parse Fashion section (prospects 1-55)
# Parse Beauty section (prospects 56-80)
# ... etc for each section
# Manual verification recommended
```

---

## Appendix A: Prospect Counts by Industry & Priority

| Industry | A | B | C | Total |
|----------|---|---|---|-------|
| Fashion & Apparel | 40 | 10 | 5 | 55 |
| Beauty & Personal Care | 15 | 7 | 3 | 25 |
| Home Goods & Decor | 22 | 6 | 2 | 30 |
| Electronics & Accessories | 14 | 5 | 1 | 20 |
| Sporting Goods & Outdoor | 18 | 5 | 2 | 25 |
| Automotive Parts & Accessories | 17 | 3 | 0 | 20 |
| Jewelry, Watches & Accessories | 10 | 3 | 2 | 15 |
| Food, Beverage & Nutrition | 3 | 5 | 2 | 10 |
| Pet & Miscellaneous | 2 | 1 | 2 | 5 |
| **Canadian Brands** (included above) | (10) | (3) | (2) | (15) |
| **Totals** | **141** | **45** | **19** | **205** |

*Note: Post-dedup totals. Pre-dedup (source): A=145, B=50, C=25 = 220.*

## Appendix B: Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│                AETHER AI CRM QUICK REFERENCE              │
├──────────────────────────────────────────────────────────┤
│  LEAD SCORE FORMULA                                       │
│  score = (catalog×0.30) + (revenue×0.25) +               │
│          (platform×0.20) + (industry×0.15) +              │
│          (engagement×0.10)                                │
│                                                          │
│  GRADES:  A(80-100) → Priority, immediate outreach       │
│           B(60-79)  → Standard outreach                   │
│           C(40-59)  → Nurture queue                       │
│           D(<40)    → Long-term nurture                    │
│                                                          │
│  PIPELINE: Lead →Contacted →Qualified →Demo Booked       │
│            →Demo Completed →Proposal Sent →Negotiation    │
│            →Closed Won / Closed Lost                      │
│                                                          │
│  OUTREACH: Day 0 (Email) → Day 3 (Email) → Day 7 (LI)   │
│            → Day 14 (Email) → Day 30 (Re-engage)          │
│            ⚡ Auto-stop on any reply                      │
│                                                          │
│  TARGET CYCLE: ≤45 days from Lead to Closed Won          │
│                                                          │
│  PLATFORM: Airtable Free (upgraded as needed)            │
│  INTEGRATION: Zapier/Make → Slack notifications           │
└──────────────────────────────────────────────────────────┘
```

---

*End of CRM Pipeline Setup Guide. For questions or updates, contact AETHER AI Sales Operations.*
