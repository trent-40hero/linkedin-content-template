# Setup Guide

Get your LinkedIn content system running in under an hour. This guide walks you through personalizing the template and creating your first week of posts.

---

## Prerequisites

- [Claude Code](https://claude.ai/code) installed
- A LinkedIn account with posting access
- (Optional) n8n instance + Make.com account for automated scheduling

---

## Step 1: Clone and Open

```bash
git clone <this-repo-url>
cd linkedin-content-template
claude
```

Claude Code will automatically read `CLAUDE.md` and understand your content system.

**Quick start prompt:**
```
Help me set up this LinkedIn content workflow. I'm [your name], [your title]
at [company]. I have [X years] experience in [field]. My target audience is
[who you want to reach].
```

Claude will walk you through the remaining steps interactively.

---

## Step 2: Define Your Identity

Open `CLAUDE.md` and fill in the **Who I Am** section:

```markdown
**Name**: Jane Smith
**Company**: Acme Consulting
**Title**: Revenue Operations Leader
**Experience**: 12 years in B2B SaaS revenue operations
**Target Audience**: VP of Sales and RevOps leaders at Series B-D SaaS companies
```

This is the foundation. Everything else builds on who you are and who you serve.

---

## Step 3: Map Your Expertise

Fill in the **Monetizable Expertise** section. Ask yourself:

1. **What do you know that changes outcomes?** Not general knowledge — specific skills that people would pay to learn or hire you for.
2. **What makes you credible?** Years of experience, results you've achieved, certifications, notable clients.
3. **What business value do you deliver?** Translate your skills into outcomes your ICP cares about (revenue, time saved, risk reduced).

**Example:**
```markdown
### Revenue Operations for B2B SaaS
- Building pipeline forecasting models that actually predict revenue
- CRM architecture that scales from Series A to IPO
- Sales/marketing alignment frameworks that reduce lead waste by 40%
- Tech stack evaluation and consolidation (Salesforce, HubSpot, Outreach)

### The Credibility Beneath It
- 12 years building RevOps functions at 4 SaaS companies ($5M-$200M ARR)
- Took one company from $8M to $45M ARR as first RevOps hire
- Certified Salesforce Admin + HubSpot Revenue Operations
- Speaker at SaaStr and RevOps Summit
```

---

## Step 4: Find Your Strategic Arbitrage

This is the most important section. Your **strategic arbitrage** is the rare intersection of skills or experiences that makes your perspective unique.

Ask yourself:
- What two worlds do I bridge that most people don't?
- What's my "I've seen both sides" advantage?
- What do I believe that most people in my field disagree with?

**Example:**
```markdown
### Unique Positioning
- **RevOps leader who actually built the systems** — not just strategic, hands-on technical
- Not a Salesforce admin who only knows one tool
- Not a strategy consultant who's never touched a CRM
- Practitioner perspective: I implement what I recommend
```

---

## Step 5: Set Your Voice

Update the **Signature Phrases/Patterns** section with phrases that sound like you. Think about how you actually talk to peers:

```markdown
### Signature Phrases/Patterns
- "After building RevOps at 4 companies, here's what actually moves the needle..."
- "Most SaaS companies are over-tooled and under-processed..."
- "I've seen this CRM mistake at every company I've joined..."
- "Here's what your sales team won't tell leadership about the pipeline..."
- "This is the exact dashboard I build first at every new company..."
```

---

## Step 6: Choose Your Pillars

The three pillars are already defined in `CLAUDE.md`:

1. **Educational** — teach your process, give away the "how"
2. **Storytelling** — personal/client narratives with business lessons
3. **Authority Jacking** — ride trending topics with your unique lens

Fill in the topic examples under each pillar. These become your content idea starters.

---

## Step 7: Customize Hashtags

**Key principle: target your ICP, not your topic.**

Your content is about your expertise, but your audience isn't searching for topic hashtags. They browse industry and role hashtags.

Replace the placeholder hashtags in `CLAUDE.md` with ones your ICP actually follows:

```markdown
**Use industry-focused hashtags for discovery:**
- #RevOps
- #SaaS
- #B2BSales
- #RevenueOperations

**Avoid:**
- #CRM, #Salesforce, #TechStack — these attract vendors, not buyers
```

---

## Step 8: Seed Your Topics

Open `topics/ideas.md` and brainstorm your first batch of topic ideas. Aim for at least 3-5 per section:

- **Educational**: What can you teach? Processes, frameworks, tools, mistakes to avoid
- **Storytelling**: What stories do you have? Career pivots, client wins, failures, surprises
- **Authority Jacking**: What trends affect your audience? News, announcements, shifts
- **Questions**: What do you genuinely want to know from your audience?

Use the format: `- [ ] Topic | Hook: "..." | Pillar: X | Format: Y`

---

## Step 9: Connect Automation (Optional)

If you want automated scheduling and posting:

### n8n Setup
1. Import `workflows/n8n/linkedin-scheduler-v2-workflow.json` into your n8n instance
2. Import `workflows/n8n/linkedin-post-worker-workflow.json`
3. Update the webhook URL in the scheduler workflow
4. Connect a Slack credential if you want posting notifications

### Make.com Setup
1. Import `workflows/make/Integration Webhooks.blueprint.json`
2. Connect your LinkedIn account
3. Update the webhook URL in `tool/export.py` (or set `N8N_LINKEDIN_WEBHOOK` env var)

### Author Info for Exports
Set environment variables or update `tool/export.py`:
```bash
export LINKEDIN_AUTHOR_NAME="Jane Smith"
export LINKEDIN_AUTHOR_COMPANY="Acme Consulting"
```

---

## Step 10: Content Intelligence (Optional)

The most powerful part of this system is the content intelligence pipeline. The concept is simple: pull data from multiple sources weekly to fuel your topic bank with real-world signals.

### The Methodology

1. **Pick 2-3 data sources** that give you insight into what your audience cares about. Examples:
   - Comments on your LinkedIn posts (scrape with Apify, PhantomBuster, etc.)
   - Meeting notes or call recordings (Fireflies, Otter, Fathom, etc.)
   - Daily journal or activity log (Notion, Obsidian, Apple Notes, etc.)
   - CRM notes from client conversations
   - Customer support tickets or FAQ patterns
   - Industry communities (Slack, Discord, Reddit, forums)

2. **Weekly analysis**: Create `topics/[source-name]/analysis-YYYY-wXX.md` for each source:
   - What themes keep coming up?
   - What questions are people asking?
   - What language does your audience use? (Mirror it in your posts)

3. **Cross-reference**: Themes appearing in 2+ sources get priority. Themes in 3+ sources are high-confidence content bets.

4. **Track trends**: Create `topics/TRENDS.md` to track which themes are rising, steady, or fading week-over-week.

5. **Feed the bank**: Add the best ideas to `topics/ideas.md` with source attribution.

### Why This Works
- You're writing about what people actually care about, not what you assume they care about
- Cross-referencing eliminates noise — if something shows up in comments AND meetings, it's real
- Historical trend data lets you spot persistent themes vs. one-off spikes
- Your content becomes a conversation with your audience, not a broadcast at them

---

## Step 11: Create Your First Week

Once your `CLAUDE.md` is personalized and `topics/ideas.md` has some entries:

```
Let's create my first week of LinkedIn posts. Pick 4 topics from
topics/ideas.md that balance pillars and formats. Draft each post
using the SLAY or PAS framework, validate against the checklist,
generate schedule times, and save to posts/.
```

Claude will:
1. Select 4 balanced topics
2. Draft each post using your voice and the frameworks
3. Validate against `frameworks/post-checklist.md`
4. Generate compliant schedule times with `tool/schedule.py`
5. Save to `posts/YYYY-WXX/post-N.md`
6. Export to JSON if you have automation set up

### Check the example post
See `posts/example/post-1.md` for the expected frontmatter format. Delete it once you've created your first real posts.

---

## Checklist

Before your first post, verify:

- [ ] `CLAUDE.md` — Who I Am section filled in
- [ ] `CLAUDE.md` — Monetizable Expertise section filled in
- [ ] `CLAUDE.md` — Strategic Arbitrage section filled in
- [ ] `CLAUDE.md` — Voice section customized with your phrases
- [ ] `CLAUDE.md` — Three Pillars have your topic examples
- [ ] `CLAUDE.md` — Hashtags replaced with your ICP hashtags
- [ ] `topics/ideas.md` — At least 10 topic ideas seeded
- [ ] No `[PLACEHOLDER]` or `[YOUR_` text remaining in `CLAUDE.md`
- [ ] (Optional) n8n + Make.com workflows imported and connected
- [ ] (Optional) `LINKEDIN_AUTHOR_NAME` and `LINKEDIN_AUTHOR_COMPANY` env vars set

**Quick check:**
```bash
grep -rn "\[YOUR_\|\[PLACEHOLDER\]" CLAUDE.md
```
If this returns results, you still have sections to fill in.

---

## Need Help?

Open Claude Code in this directory and ask:
```
Help me finish setting up my LinkedIn content system.
Show me what's still incomplete in CLAUDE.md.
```

Claude will scan for remaining placeholders and walk you through them.
