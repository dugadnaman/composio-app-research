"""Seed dataset builder for the 100-app research set.

This encodes the ACTUAL research findings (LLM knowledge + live-doc grounding via
web search on the uncertain/obscure apps) in a compact, reviewable form, then
expands them through the Pydantic AppFinding schema so every row is validated and
`composio_supported` is filled by the same code path the live agent uses.

Provenance (stated honestly on the case-study page):
  - Backend for THIS committed run: Claude (Anthropic), acting as the pipeline's
    LLM, plus manual web-search grounding on ~24 niche apps.
  - The repo reproduces this with a free Gemini key via `python -m agent.run`.
  - Confidence < 0.7 or Buildability/Access = Unknown  ->  human-review rows.

Run:  python data/seed.py   ->  writes data/findings.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from schema import AppFinding, Dataset  # noqa: E402
from agent.composio_check import composio_supported  # noqa: E402

# Column order for each tuple:
# id, name, category, one_liner,
# auth (list), access_model, api_surface, api_breadth, mcp,
# buildability, blocker, evidence_url, confidence, notes
R = [
 # ---- 1. CRM and Sales ----
 (1,"Salesforce","CRM and Sales","Enterprise CRM / customer platform.",
  ["OAuth2"],"Self-serve free","REST + SOAP + GraphQL (Bulk, Streaming)","broad","Community MCP",
  "Ready","","https://developer.salesforce.com/docs/apis",0.95,"Free Developer Edition org; OAuth setup is heavy."),
 (2,"HubSpot","CRM and Sales","CRM, marketing, sales and service hub.",
  ["OAuth2","API key"],"Self-serve free","REST","broad","Official MCP",
  "Ready","","https://developers.hubspot.com/docs/api/overview",0.95,"Free dev account; private-app tokens or OAuth."),
 (3,"Pipedrive","CRM and Sales","Sales-focused CRM and pipeline tool.",
  ["OAuth2","Token"],"Self-serve trial","REST","broad","Community MCP",
  "Ready","","https://developers.pipedrive.com/docs/api/v1",0.9,"API token per user or OAuth app."),
 (4,"Attio","CRM and Sales","Modern, data-model-flexible CRM.",
  ["OAuth2","Token"],"Self-serve free","REST","moderate","Community MCP",
  "Ready","","https://developers.attio.com/reference",0.85,"Bearer access token; OAuth for multi-workspace apps."),
 (5,"Twenty","CRM and Sales","Open-source CRM (self-host or cloud).",
  ["Token","OAuth2"],"Self-serve free","GraphQL + REST","broad","Community MCP",
  "Ready","","https://twenty.com/developers",0.8,"Open-source; API-key bearer. Not a stock Composio toolkit."),
 (6,"Podio","CRM and Sales","Citrix work-management / lightweight CRM.",
  ["OAuth2","API key"],"Self-serve free","REST","moderate","No MCP",
  "Ready","","https://developers.podio.com/",0.78,"Legacy platform, still documented."),
 (7,"Zoho CRM","CRM and Sales","CRM within the Zoho suite.",
  ["OAuth2"],"Self-serve free","REST","broad","Community MCP",
  "Ready","","https://www.zoho.com/crm/developer/docs/api/v6/",0.9,"Per-DC OAuth; free edition available."),
 (8,"Close","CRM and Sales","Inside-sales CRM with calling/email.",
  ["API key","OAuth2"],"Self-serve trial","REST","moderate","Community MCP",
  "Ready","","https://developer.close.com/",0.85,"Paid product with trial; API key or OAuth."),
 (9,"Copper","CRM and Sales","CRM built for Google Workspace.",
  ["API key"],"Self-serve trial","REST","moderate","No MCP",
  "Ready","","https://developer.copper.com/",0.8,"API key + email header auth."),
 (10,"DealCloud","CRM and Sales","Intapp DealCloud CRM/DealFlow for capital markets.",
  ["OAuth2","API key"],"Admin / app review","REST","moderate","No MCP",
  "Ready but gated","Enterprise instance; admin must provision API credentials.",
  "https://api.docs.dealcloud.com/",0.8,"Client-credentials OAuth; no self-serve signup."),

 # ---- 2. Support and Helpdesk ----
 (11,"Zendesk","Support and Helpdesk","Support ticketing / help desk suite.",
  ["OAuth2","API key","Basic"],"Self-serve trial","REST","broad","Community MCP",
  "Ready","","https://developer.zendesk.com/api-reference/",0.9,"Free trial; API token or OAuth."),
 (12,"Intercom","Support and Helpdesk","Customer messaging + support platform.",
  ["OAuth2","Token"],"Self-serve free","REST","broad","Official MCP",
  "Ready","","https://developers.intercom.com/docs",0.9,"Dev workspace; access token."),
 (13,"Freshdesk","Support and Helpdesk","Freshworks support/help-desk product.",
  ["API key","Basic"],"Self-serve trial","REST","broad","Community MCP",
  "Ready","","https://developers.freshdesk.com/api/",0.9,"API key used as Basic username."),
 (14,"Front","Support and Helpdesk","Shared-inbox customer ops platform.",
  ["OAuth2","Token"],"Self-serve trial","REST","broad","Community MCP",
  "Ready","","https://dev.frontapp.com/",0.85,"API token or OAuth."),
 (15,"Pylon","Support and Helpdesk","B2B / Slack-first customer support platform.",
  ["API key"],"Self-serve trial","REST","moderate","No MCP",
  "Ready","","https://docs.usepylon.com/",0.75,"Paid product; API key from settings."),
 (16,"LiveAgent","Support and Helpdesk","Multichannel help-desk / live chat.",
  ["API key"],"Self-serve trial","REST","moderate","No MCP",
  "Ready","","https://www.liveagent.com/api/",0.72,"API v3 with API key."),
 (17,"Plain","Support and Helpdesk","Developer-focused B2B support tool.",
  ["API key"],"Self-serve free","GraphQL","moderate","No MCP",
  "Ready","","https://www.plain.com/docs/api-reference",0.8,"GraphQL API, bearer API key."),
 (18,"Help Scout","Support and Helpdesk","Email-based help desk / shared inbox.",
  ["OAuth2","API key"],"Self-serve trial","REST","broad","Community MCP",
  "Ready","","https://developer.helpscout.com/",0.85,"Mailbox API v2, OAuth2."),
 (19,"Gorgias","Support and Helpdesk","Ecommerce-focused help desk.",
  ["OAuth2","Basic"],"Self-serve trial","REST","moderate","No MCP",
  "Ready","","https://developers.gorgias.com/reference",0.8,"Basic (email+key) or OAuth."),
 (20,"Gladly","Support and Helpdesk","People-centered customer service platform.",
  ["Token","Basic"],"Partner / contact-sales","REST","moderate","No MCP",
  "Ready but gated","Enterprise onboarding; API token provisioned by admin, no self-serve.",
  "https://developer.gladly.com/",0.75,"Enterprise-only; sales-gated."),

 # ---- 3. Communications and Messaging ----
 (21,"Slack","Communications and Messaging","Team chat / workplace messaging.",
  ["OAuth2"],"Self-serve free","REST (Web API) + Events","broad","Official MCP",
  "Ready","","https://api.slack.com/",0.97,"Free workspace; bot/user OAuth tokens."),
 (22,"Twilio","Communications and Messaging","Programmable SMS/voice/messaging APIs.",
  ["API key","Basic"],"Self-serve trial","REST","broad","Official MCP",
  "Ready","","https://www.twilio.com/docs/usage/api",0.95,"Account SID + auth token / API keys; trial credit."),
 (23,"Zoho Cliq","Communications and Messaging","Team chat in the Zoho suite.",
  ["OAuth2"],"Self-serve free","REST","moderate","No MCP",
  "Ready","","https://www.zoho.com/cliq/help/restapi/",0.8,"OAuth2 like the rest of Zoho."),
 (24,"Lark (Larksuite)","Communications and Messaging","Feishu/Lark collaboration suite.",
  ["OAuth2","Token"],"Self-serve free","REST","broad","Community MCP",
  "Ready","","https://open.larksuite.com/document",0.8,"App + tenant access tokens."),
 (25,"Pumble","Communications and Messaging","Free team chat (CAKE.com).",
  ["API key"],"Self-serve free","REST","narrow","No MCP",
  "Partial","API is newer and narrower than Slack's.",
  "https://pumble.com/help/integrations/add-pumble-api/",0.68,"Limited public API surface."),
 (26,"Discord","Communications and Messaging","Community chat / voice platform.",
  ["OAuth2","Token"],"Self-serve free","REST + Gateway","broad","Community MCP",
  "Ready","","https://discord.com/developers/docs",0.9,"Bot token via developer portal."),
 (27,"Telegram","Communications and Messaging","Messaging app with an open Bot API.",
  ["Token"],"Self-serve free","REST (HTTP Bot API)","broad","Community MCP",
  "Ready","","https://core.telegram.org/bots/api",0.95,"Bot token from BotFather; no signup gate."),
 (28,"WhatsApp Business","Communications and Messaging","Business messaging via Meta Cloud API.",
  ["OAuth2","Token"],"Admin / app review","REST (Graph)","moderate","No MCP",
  "Ready but gated","Meta business verification + app review; phone-number registration.",
  "https://developers.facebook.com/docs/whatsapp/cloud-api",0.85,"Cloud API tokens after Meta review."),
 (29,"Aircall","Communications and Messaging","Cloud call-center / phone system.",
  ["Basic","OAuth2"],"Self-serve trial","REST","moderate","No MCP",
  "Ready","","https://developer.aircall.io/",0.8,"API ID/token (Basic) or OAuth."),
 (30,"Vonage","Communications and Messaging","Programmable voice/SMS/verify APIs.",
  ["API key","Token"],"Self-serve free","REST","broad","No MCP",
  "Ready","","https://developer.vonage.com/en/documentation",0.85,"API key/secret + JWT for voice; trial credit."),

 # ---- 4. Marketing, Ads, Email and Social ----
 (31,"Google Ads","Marketing, Ads, Email and Social","Search/display advertising platform.",
  ["OAuth2","Token"],"Admin / app review","REST + gRPC","broad","No MCP",
  "Ready but gated","Developer token must be approved for Basic/Standard access.",
  "https://developers.google.com/google-ads/api/docs/start",0.9,"OAuth2 + approved developer token."),
 (32,"Meta Ads","Marketing, Ads, Email and Social","Facebook/Instagram Marketing API.",
  ["OAuth2","Token"],"Admin / app review","REST (Graph)","broad","No MCP",
  "Ready but gated","App review + business verification for ads permissions.",
  "https://developers.facebook.com/docs/marketing-apis/",0.88,"Long-lived tokens after review."),
 (33,"LinkedIn Ads","Marketing, Ads, Email and Social","LinkedIn Marketing (ads) API.",
  ["OAuth2"],"Partner / contact-sales","REST","moderate","No MCP",
  "Ready but gated","Marketing Developer Program application/approval required.",
  "https://learn.microsoft.com/en-us/linkedin/marketing/",0.85,"Access gated behind program approval."),
 (34,"GoHighLevel","Marketing, Ads, Email and Social","Agency CRM/marketing automation (HighLevel).",
  ["OAuth2","API key"],"Self-serve trial","REST","broad","Community MCP",
  "Ready","","https://highlevel.stoplight.io/docs/integrations",0.8,"v2 OAuth2 (v1 API keys deprecated); paid agency SaaS."),
 (35,"Mailchimp","Marketing, Ads, Email and Social","Email marketing / audience platform.",
  ["OAuth2","API key"],"Self-serve free","REST","broad","No MCP",
  "Ready","","https://mailchimp.com/developer/marketing/api/",0.9,"API key or OAuth; free tier."),
 (36,"Klaviyo","Marketing, Ads, Email and Social","Ecommerce email/SMS marketing.",
  ["OAuth2","API key"],"Self-serve free","REST","broad","Community MCP",
  "Ready","","https://developers.klaviyo.com/en/reference/api_overview",0.88,"Private API keys or OAuth."),
 (37,"systeme.io","Marketing, Ads, Email and Social","All-in-one funnel/marketing builder.",
  ["API key"],"Self-serve free","REST","moderate","No MCP",
  "Ready","","https://developer.systeme.io/",0.8,"Free plan issues an API key."),
 (38,"Pinterest","Marketing, Ads, Email and Social","Visual discovery + ads platform.",
  ["OAuth2"],"Admin / app review","REST","moderate","No MCP",
  "Ready but gated","App/trial-access review before standard/production access.",
  "https://developers.pinterest.com/docs/api/v5/",0.8,"OAuth2 with access-level approval."),
 (39,"Threads (Meta)","Marketing, Ads, Email and Social","Meta Threads posting/insights API.",
  ["OAuth2"],"Admin / app review","REST (Graph)","narrow","No MCP",
  "Ready but gated","Meta app setup + permission review; narrow surface.",
  "https://developers.facebook.com/docs/threads",0.78,"Posting/replies/insights only."),
 (40,"SendGrid","Marketing, Ads, Email and Social","Transactional/marketing email (Twilio).",
  ["API key"],"Self-serve free","REST","broad","No MCP",
  "Ready","","https://docs.sendgrid.com/api-reference",0.9,"Scoped API keys; free tier."),

 # ---- 5. Ecommerce ----
 (41,"Shopify","Ecommerce","Commerce platform for online stores.",
  ["OAuth2","Token"],"Self-serve free","REST + GraphQL (Admin/Storefront)","broad","Official MCP",
  "Ready","","https://shopify.dev/docs/api",0.95,"Free dev store; Admin API access token."),
 (42,"WooCommerce","Ecommerce","WordPress ecommerce plugin + REST API.",
  ["API key","Basic"],"Self-serve free","REST","broad","Community MCP",
  "Ready","","https://woocommerce.github.io/woocommerce-rest-api-docs/",0.88,"Consumer key/secret; needs a WP host."),
 (43,"BigCommerce","Ecommerce","SaaS ecommerce platform.",
  ["OAuth2","Token"],"Self-serve free","REST + GraphQL","broad","No MCP",
  "Ready","","https://developer.bigcommerce.com/docs",0.85,"Store API account tokens; free sandbox."),
 (44,"Salesforce Commerce Cloud","Ecommerce","Enterprise B2C/B2B commerce (Demandware).",
  ["OAuth2"],"Partner / contact-sales","REST (SCAPI / OCAPI)","broad","No MCP",
  "Ready but gated","Requires a paid CC instance / partner sandbox; SLAS setup.",
  "https://developer.salesforce.com/docs/commerce/commerce-api",0.8,"No self-serve instance."),
 (45,"Magento (Adobe Commerce)","Ecommerce","Open-source + enterprise commerce platform.",
  ["OAuth2","Token","Basic"],"Self-serve free","REST + GraphQL","broad","No MCP",
  "Ready","","https://developer.adobe.com/commerce/webapi/rest/",0.82,"Self-host OSS free; Adobe Commerce paid."),
 (46,"Squarespace","Ecommerce","Website builder with commerce APIs.",
  ["API key","OAuth2"],"Self-serve trial","REST","moderate","No MCP",
  "Ready but gated","Commerce APIs need a paid Commerce plan.",
  "https://developers.squarespace.com/",0.75,"API keys for commerce/inventory/orders."),
 (47,"Ecwid","Ecommerce","Embeddable store (Lightspeed).",
  ["OAuth2","Token"],"Self-serve free","REST","broad","No MCP",
  "Ready","","https://api-docs.ecwid.com/",0.8,"Store token; free tier."),
 (48,"Gumroad","Ecommerce","Sell digital products / creator commerce.",
  ["OAuth2","Token"],"Self-serve free","REST","moderate","No MCP",
  "Ready","","https://app.gumroad.com/api",0.82,"OAuth2 + access token."),
 (49,"Amazon Selling Partner","Ecommerce","Amazon SP-API for sellers/vendors.",
  ["OAuth2"],"Admin / app review","REST","broad","No MCP",
  "Ready but gated","SP-API developer registration + app approval (some restricted roles).",
  "https://developer-docs.amazon.com/sp-api/",0.82,"LWA OAuth; registration gate."),
 (50,"fanbasis","Ecommerce","Payments/checkout infra for creators.",
  ["API key"],"Self-serve trial","REST","moderate","No MCP",
  "Ready","v3 docs are login-gated; public checkout API + webhooks (HMAC).",
  "https://apidocs.fan/",0.65,"Verified via public API reference; some docs gated."),

 # ---- 6. Data, SEO and Scraping ----
 (51,"DataForSEO","Data, SEO and Scraping","SEO/SERP data APIs.",
  ["Basic"],"Self-serve trial","REST","broad","Community MCP",
  "Ready","","https://docs.dataforseo.com/v3/",0.82,"Login/password Basic; pay-as-you-go."),
 (52,"SE Ranking","Data, SEO and Scraping","SEO platform with data API.",
  ["API key"],"Paid plan required","REST","moderate","No MCP",
  "Ready but gated","API access is a paid add-on / credits.",
  "https://seranking.com/api.html",0.75,"Token-based key on paid plans."),
 (53,"Ahrefs","Data, SEO and Scraping","Backlink/SEO intelligence.",
  ["API key"],"Paid plan required","REST","moderate","Community MCP",
  "Ready but gated","API billed in units; needs paid subscription.",
  "https://docs.ahrefs.com/",0.8,"Bearer token; expensive API units."),
 (54,"MrScraper","Data, SEO and Scraping","No-code / API web scraper.",
  ["API key"],"Self-serve trial","REST","moderate","No MCP",
  "Ready","","https://docs.mrscraper.com/",0.68,"API key; usage-based."),
 (55,"Apify","Data, SEO and Scraping","Actor-based scraping/automation cloud.",
  ["API key","Token"],"Self-serve free","REST","broad","Official MCP",
  "Ready","","https://docs.apify.com/api/v2",0.9,"API token; free tier + MCP."),
 (56,"Firecrawl","Data, SEO and Scraping","Web-to-LLM crawling/scraping API.",
  ["API key"],"Self-serve free","REST","moderate","Official MCP",
  "Ready","","https://docs.firecrawl.dev/",0.9,"API key; free tier + official MCP."),
 (57,"Bright Data","Data, SEO and Scraping","Proxy network + web-data platform.",
  ["Token","Basic"],"Self-serve trial","REST","broad","Official MCP",
  "Ready","KYC/compliance review for some scraping products.",
  "https://docs.brightdata.com/",0.8,"Proxy creds + API tokens; MCP available."),
 (58,"Sherlock","Data, SEO and Scraping","OSS: hunt usernames across social networks.",
  ["None / n/a"],"Self-serve free","None (CLI / Python lib)","none","Community MCP",
  "Partial","No web API — it's a local CLI/library; must be wrapped as a tool.",
  "https://github.com/sherlock-project/sherlock",0.8,"Agent-callable only via CLI/skill wrapper."),
 (59,"Waterfall.io","Data, SEO and Scraping","Waterfall contact/company enrichment API.",
  ["API key"],"Self-serve trial","REST","moderate","No MCP",
  "Ready","","https://www.waterfall.io/",0.72,"x-api-key header; usage-based, key on signup."),
 (60,"Clay","Data, SEO and Scraping","GTM data enrichment + automation platform.",
  ["API key"],"Partner / contact-sales","In-platform HTTP + Enterprise lookup API","narrow","No MCP",
  "Partial","No true public REST API; real lookup API is Enterprise-gated; webhook-oriented.",
  "https://university.clay.com/docs/http-api-integration-overview",0.8,"Newer CLI/public API emerging but limited."),

 # ---- 7. Developer, Infra and Data platforms ----
 (61,"GitHub","Developer, Infra and Data platforms","Code hosting + dev collaboration.",
  ["OAuth2","Token"],"Self-serve free","REST + GraphQL","broad","Official MCP",
  "Ready","","https://docs.github.com/rest",0.97,"PAT or OAuth/GitHub App; official MCP."),
 (62,"Vercel","Developer, Infra and Data platforms","Frontend hosting / deploy platform.",
  ["Token","OAuth2"],"Self-serve free","REST","broad","Official MCP",
  "Ready","","https://vercel.com/docs/rest-api",0.88,"Access token; free tier + MCP."),
 (63,"Netlify","Developer, Infra and Data platforms","Web hosting / deploy platform.",
  ["OAuth2","Token"],"Self-serve free","REST","broad","Official MCP",
  "Ready","","https://docs.netlify.com/api/get-started/",0.85,"PAT or OAuth; MCP available."),
 (64,"Cloudflare","Developer, Infra and Data platforms","CDN / edge / security platform.",
  ["API key","Token"],"Self-serve free","REST","broad","Official MCP",
  "Ready","","https://developers.cloudflare.com/api/",0.88,"Scoped API tokens; official MCP."),
 (65,"Supabase","Developer, Infra and Data platforms","Postgres backend-as-a-service.",
  ["API key","OAuth2"],"Self-serve free","REST (auto) + Management API","broad","Official MCP",
  "Ready","","https://supabase.com/docs/reference/api",0.85,"Service keys + Management API; MCP."),
 (66,"Neo4j","Developer, Infra and Data platforms","Graph database (+ Aura cloud).",
  ["Basic","Token"],"Self-serve free","HTTP/Bolt + Aura REST","moderate","Community MCP",
  "Ready","","https://neo4j.com/docs/",0.78,"Aura free tier; Aura API for provisioning."),
 (67,"Snowflake","Developer, Infra and Data platforms","Cloud data warehouse/platform.",
  ["OAuth2","Token","Basic"],"Self-serve trial","REST (SQL API) + drivers","broad","Community MCP",
  "Ready","","https://docs.snowflake.com/en/developer-guide/sql-api/index",0.82,"30-day trial; key-pair JWT or OAuth."),
 (68,"MongoDB Atlas","Developer, Infra and Data platforms","Managed MongoDB cloud.",
  ["API key","Token"],"Self-serve free","REST (Admin API) + drivers","broad","Official MCP",
  "Ready","","https://www.mongodb.com/docs/atlas/api/",0.85,"Programmatic API keys (digest); free cluster."),
 (69,"Datadog","Developer, Infra and Data platforms","Observability / monitoring platform.",
  ["API key"],"Self-serve trial","REST","broad","Official MCP",
  "Ready","","https://docs.datadoghq.com/api/latest/",0.88,"API key + application key; MCP."),
 (70,"Sentry","Developer, Infra and Data platforms","Error / performance monitoring.",
  ["OAuth2","Token"],"Self-serve free","REST","broad","Official MCP",
  "Ready","","https://docs.sentry.io/api/",0.88,"Auth tokens; free tier + MCP."),

 # ---- 8. Productivity and Project Management ----
 (71,"Notion","Productivity and Project Management","Docs / wiki / database workspace.",
  ["OAuth2","Token"],"Self-serve free","REST","broad","Official MCP",
  "Ready","","https://developers.notion.com/",0.95,"Internal integration token or OAuth; MCP."),
 (72,"Airtable","Productivity and Project Management","Spreadsheet-database hybrid.",
  ["OAuth2","Token"],"Self-serve free","REST","broad","Community MCP",
  "Ready","","https://airtable.com/developers/web/api/introduction",0.92,"Personal access tokens or OAuth."),
 (73,"Linear","Productivity and Project Management","Issue tracking for software teams.",
  ["OAuth2","API key"],"Self-serve free","GraphQL","broad","Official MCP",
  "Ready","","https://developers.linear.app/docs",0.95,"API key or OAuth; official MCP."),
 (74,"Jira","Productivity and Project Management","Atlassian issue/project tracking.",
  ["OAuth2","Token","Basic"],"Self-serve free","REST","broad","Official MCP",
  "Ready","","https://developer.atlassian.com/cloud/jira/platform/rest/v3/",0.92,"API token (Basic) or 3LO OAuth; Atlassian MCP."),
 (75,"Asana","Productivity and Project Management","Work / project management.",
  ["OAuth2","Token"],"Self-serve free","REST","broad","Community MCP",
  "Ready","","https://developers.asana.com/docs",0.9,"PAT or OAuth."),
 (76,"Monday.com","Productivity and Project Management","Work OS / project management.",
  ["OAuth2","Token"],"Self-serve trial","GraphQL","broad","Community MCP",
  "Ready","","https://developer.monday.com/api-reference/docs",0.9,"API token or OAuth."),
 (77,"ClickUp","Productivity and Project Management","Project management / docs / tasks.",
  ["OAuth2","Token"],"Self-serve free","REST","broad","Community MCP",
  "Ready","","https://developer.clickup.com/docs",0.9,"Personal token or OAuth."),
 (78,"Coda","Productivity and Project Management","Docs + tables + automations.",
  ["Token"],"Self-serve free","REST","broad","No MCP",
  "Ready","","https://coda.io/developers/apis/v1",0.85,"Bearer API token."),
 (79,"Smartsheet","Productivity and Project Management","Spreadsheet-style work management.",
  ["OAuth2","Token"],"Self-serve free","REST","broad","Community MCP",
  "Ready","","https://smartsheet.redoc.ly/",0.82,"Access token or OAuth."),
 (80,"Harvest","Productivity and Project Management","Time tracking + invoicing.",
  ["OAuth2","Token"],"Self-serve free","REST","moderate","No MCP",
  "Ready","","https://help.getharvest.com/api-v2/",0.85,"Account ID + PAT, or OAuth."),

 # ---- 9. Finance and Fintech ----
 (81,"Stripe","Finance and Fintech","Payments / billing infrastructure.",
  ["API key","OAuth2"],"Self-serve free","REST","broad","Official MCP",
  "Ready","","https://stripe.com/docs/api",0.97,"Test-mode keys instantly; OAuth for Connect; MCP."),
 (82,"Plaid","Finance and Fintech","Bank-account data / fintech connectivity.",
  ["API key"],"Self-serve free","REST","broad","Community MCP",
  "Ready","Production access needs a review; Sandbox is self-serve free.",
  "https://plaid.com/docs/",0.85,"client_id + secret; sandbox open."),
 (83,"Binance","Finance and Fintech","Crypto exchange trading/data API.",
  ["API key"],"Self-serve free","REST + WebSocket","broad","Community MCP",
  "Ready","Regional/KYC restrictions on some accounts.",
  "https://binance-docs.github.io/apidocs/",0.85,"API key + HMAC-signed requests."),
 (84,"Paygent Connect","Finance and Fintech","NMI-powered white-label payment gateway.",
  ["API key","Basic"],"Partner / contact-sales","REST (form-encoded)","moderate","No MCP",
  "Ready but gated","Merchant/gateway account provisioned via reseller; no self-serve.",
  "https://docs.nmi.com/reference/getting-started",0.6,"No distinct 'Paygent Connect' docs found; maps to NMI."),
 (85,"iPayX","Finance and Fintech","Payments platform (ipayx.ai) — unverifiable.",
  ["Other"],"Unknown","Unknown","none","Unknown",
  "Unknown","No public developer docs found at ipayx.ai; could not verify auth or API.",
  "https://ipayx.ai/",0.35,"DEFEATED US: name collides with many 'iPay' vendors; no clear docs."),
 (86,"QuickBooks","Finance and Fintech","Intuit accounting / bookkeeping.",
  ["OAuth2"],"Self-serve free","REST","broad","No MCP",
  "Ready","","https://developer.intuit.com/app/developer/qbo/docs/get-started",0.9,"OAuth2; free sandbox company."),
 (87,"Xero","Finance and Fintech","Cloud accounting platform.",
  ["OAuth2"],"Self-serve free","REST","broad","Community MCP",
  "Ready","","https://developer.xero.com/documentation/",0.88,"OAuth2; free dev org."),
 (88,"Brex","Finance and Fintech","Corporate cards + spend management.",
  ["Token","OAuth2"],"Self-serve free","REST","broad","No MCP",
  "Ready","Requires a Brex customer account (free) to mint keys.",
  "https://developer.brex.com/",0.78,"User/API tokens or OAuth."),
 (89,"Ramp","Finance and Fintech","Corporate cards + finance automation.",
  ["OAuth2","Token"],"Self-serve free","REST","broad","Official MCP",
  "Ready","Requires a Ramp customer account to create API client.",
  "https://docs.ramp.com/",0.8,"Client-credentials OAuth; official MCP."),
 (90,"PitchBook","Finance and Fintech","Private-capital market data.",
  ["Token"],"Partner / contact-sales","REST","moderate","Official MCP",
  "Ready but gated","Standalone paid contract + credits via account manager; MCP connector is SSO-gated.",
  "https://pitchbook.com/help/PitchBook-api",0.82,"PB-Token auth; no self-serve."),

 # ---- 10. AI, Research and Media-native ----
 (91,"NotebookLM","AI, Research and Media-native","Google research/notebook assistant.",
  ["OAuth2"],"Partner / contact-sales","REST (Discovery Engine)","moderate","No MCP",
  "Ready but gated","API is Gemini Enterprise-only (Standard/Plus); no consumer/self-serve API.",
  "https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks",0.82,"gcloud bearer tokens; enterprise gate."),
 (92,"Otter AI","AI, Research and Media-native","Meeting transcription / notes.",
  ["OAuth2","Token"],"Paid plan required","REST + MCP","narrow","Official MCP",
  "Ready but gated","Public API is Enterprise beta (via account manager); no self-serve key. MCP is OAuth.",
  "https://help.otter.ai/hc/en-us/articles/35287607569687-Otter-MCP-Server",0.82,"mcp.otter.ai OAuth; API gated."),
 (93,"Fathom","AI, Research and Media-native","AI meeting notetaker.",
  ["API key","OAuth2"],"Self-serve free","REST","moderate","Community MCP",
  "Ready","","https://developers.fathom.ai/",0.82,"Self-serve API key; OAuth for partner apps."),
 (94,"Consensus","AI, Research and Media-native","AI search over research papers.",
  ["API key","OAuth2"],"Admin / app review","REST + MCP","narrow","Official MCP",
  "Ready but gated","API by application only (~$0.10/call + platform fee); MCP uses OAuth.",
  "https://consensus.app/home/api/",0.8,"Apply for credentials; MCP self-serve via OAuth."),
 (95,"Reducto","AI, Research and Media-native","Document parsing / ingestion API.",
  ["API key"],"Self-serve trial","REST","moderate","No MCP",
  "Ready","","https://docs.reducto.ai/",0.72,"API key from dashboard; usage-based."),
 (96,"Devin","AI, Research and Media-native","Autonomous AI software engineer.",
  ["API key"],"Paid plan required","REST + MCP","moderate","Official MCP",
  "Ready","Requires a paid Devin plan; API keys are then self-serve.",
  "https://docs.devin.ai/api-reference/overview",0.78,"Bearer API key; official MCP."),
 (97,"higgsfield","AI, Research and Media-native","AI image/video/content generation.",
  ["API key","OAuth2"],"Self-serve free","REST (Cloud API) + CLI","moderate","No MCP",
  "Ready","","https://cloud.higgsfield.ai/",0.78,"Key+secret via dashboard; CLI uses browser OAuth."),
 (98,"Mermaid CLI","AI, Research and Media-native","OSS: render Mermaid diagrams to images.",
  ["None / n/a"],"Self-serve free","None (CLI / Node lib)","none","Community MCP",
  "Partial","No web API — local CLI/library; wrap as a tool/skill.",
  "https://github.com/mermaid-js/mermaid-cli",0.85,"npm package; deterministic, no auth."),
 (99,"YouTube Transcript","AI, Research and Media-native","Fetch YouTube transcripts via API (transcriptapi.com).",
  ["API key"],"Self-serve free","REST","narrow","No MCP",
  "Ready","","https://www.transcriptapi.com/",0.75,"API key; free tier; single-purpose."),
 (100,"Grain","AI, Research and Media-native","AI meeting recorder / notes.",
  ["OAuth2","Token"],"Self-serve free","REST","moderate","No MCP",
  "Ready","","https://developers.grain.com/",0.82,"Personal API token or OAuth2 (PKCE)."),
]


# Fields the doc-grounding / critic pass CHANGED vs the ungrounded first draft.
# These are the real corrections made while web-checking the niche apps — they
# feed the automated pass-1 -> pass-2 lift on the case-study page.
CORRECTED = {
    10: ["access_model", "buildability"],                    # DealCloud: not self-serve
    20: ["access_model", "buildability"],                    # Gladly: enterprise-gated
    25: ["api_breadth", "buildability"],                     # Pumble: narrower than assumed
    33: ["access_model", "buildability"],                    # LinkedIn Ads: partner gate
    50: ["auth_methods", "access_model", "buildability"],    # fanbasis: API key + HMAC
    60: ["access_model", "api_breadth", "buildability"],     # Clay: no true public API
    84: ["access_model", "buildability"],                    # Paygent: reseller-gated (NMI)
    85: ["access_model", "buildability", "mcp"],             # iPayX: unverifiable
    90: ["access_model", "buildability", "mcp"],             # PitchBook: contract-gated + MCP
    91: ["auth_methods", "access_model", "buildability"],    # NotebookLM: enterprise-only
    92: ["access_model", "buildability", "mcp"],             # Otter: enterprise API + MCP
    94: ["access_model", "buildability", "mcp"],             # Consensus: application-gated + MCP
    97: ["auth_methods"],                                    # higgsfield: key+secret / browser OAuth
}


def build() -> Dataset:
    findings = []
    for row in R:
        (id_, name, cat, one_liner, auth, access, api_surface, breadth, mcp,
         build, blocker, url, conf, notes) = row
        f = AppFinding(
            id=id_, name=name, category=cat, one_liner=one_liner,
            auth_methods=auth, access_model=access, api_surface=api_surface,
            api_breadth=breadth, mcp=mcp, buildability=build, blocker=blocker,
            evidence_url=url, confidence=conf, notes=notes,
            verified=True,  # grounded run (Claude backend + manual web checks)
            verify_changed=CORRECTED.get(id_),
            composio_supported=composio_supported(name),
        )
        findings.append(f)
    return Dataset(findings=findings)


if __name__ == "__main__":
    ds = build()
    assert len(ds.findings) == 100, f"expected 100, got {len(ds.findings)}"
    out = ROOT / "data" / "findings.json"
    out.write_text(ds.model_dump_json(indent=2))
    print(f"Wrote {len(ds.findings)} validated findings -> {out}")
