# OPS-001 (line C) · Hosting research for the demo (2026-11-11)

The demo has two parts: the web (Next.js 16) and the API (FastAPI with geospatial dependencies, about 280 MB on Linux), reading from Supabase `ilvbivfnqvfqslbbiuts` in eu-west-1. The hosting must be free.

| | A · Vercel Hobby, one project with Services | B · Vercel (web) + Render Free (API) | C · Vercel (web) + Cloud Run (API) |
|---|---|---|---|
| API bundle | Python up to 500 MB unzipped. Containers in beta, same limits as Functions | Docker, no relevant limit | Container, no relevant limit |
| Memory / CPU | 2 GB / 1 vCPU | 512 MB / 0.1 CPU | Configurable |
| Cold start | Not documented in numbers. A container scales to zero after 5 min without traffic in production | Sleeps after 15 min idle; waking up takes about 1 min | Seconds |
| EU region | One region on Hobby: `dub1` Dublin, next to Supabase | Frankfurt | Madrid / Belgium |
| Free allowance | 1M invocations, 4 h active CPU, 360 GB-h, 100 GB transfer per month. Response body up to 4.5 MB | 750 h, 5 GB bandwidth, 500 build min per month. Without a card, going over suspends the free services for the month | 2M requests, 180k vCPU-s, 360k GiB-s. Free egress only 1 GB from North America |
| Accounts | Vercel only | Vercel + Render | Vercel + GCP with a billing account |
| Risks | Services and the container runtime are in beta. Hobby is for non-commercial use: a competition demo with no payments or ads fits | 1 min cold start in front of the jury | Card required, more moving parts |

**Mariano's choice (2026-11-11): A**, with the Vercel account already logged in the CLI.

Sources (official documentation, read on 2026-11-11):
- Vercel: [Python runtime](https://vercel.com/docs/functions/runtimes/python), [Functions limits](https://vercel.com/docs/functions/limitations), [fair use and Hobby allowances](https://vercel.com/docs/limits/fair-use-guidelines), [Services](https://vercel.com/docs/services), [Services routing](https://vercel.com/docs/services/routing), [Service config reference](https://vercel.com/docs/services/config-reference), [Container runtime](https://vercel.com/docs/functions/runtimes/container), [Function regions](https://vercel.com/docs/functions/configuring-functions/region), [.vercelignore](https://vercel.com/docs/deployments/vercel-ignore).
- Render: [free instances](https://render.com/docs/free), [pricing](https://render.com/pricing.md), [compute plans](https://render.com/docs/compute-plans.md), [regions](https://render.com/docs/regions).
- Google Cloud: [Free Tier features](https://docs.cloud.google.com/free/docs/free-cloud-features).
- Supabase: [connecting to Postgres](https://supabase.com/docs/guides/database/connecting-to-postgres). The direct connection is IPv6 only on the free plan; from IPv4 networks use the session pooler; serverless clients should use the transaction pooler, which does not support prepared statements.
