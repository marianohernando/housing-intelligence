# OPS-001 (line C) · cleaner `.vercel.app` alias candidates (2026-11-11)

No alias was assigned: Mariano decides. The method is an HTTP probe of `https://<name>.vercel.app/`, reading the status and the `x-vercel-error` header.

Calibration:

| Name | Answer | Meaning |
|---|---|---|
| `zq-vf-<random>-libre` | 404 `DEPLOYMENT_NOT_FOUND` | Surely free |
| `vida-facil-eight` (ours) | 200 | Taken, with a deployment |
| `vidafacil` | 200 | Taken by another account |
| `vida-facil` | 404 `NOT_FOUND` | **Taken**: `vercel domains add` returned 403 "already in use" |

Candidates. Every one answered 404 `DEPLOYMENT_NOT_FOUND`, the same as a free name:

`vidafacil-madrid`, `vida-facil-madrid`, `vidafacil-datamad`, `vida-facil-datamad`, `vidafacil-cm`, `vida-facil-cm`, `vidafacilmadrid`, `vida-facil-app`, `vidafacil-app`, `vida-facil-demo`.

Shortlist:
1. **`vidafacil-madrid.vercel.app`**: short, Spanish, and says where. Easy to dictate: "vidafácil guion madrid".
2. **`vida-facil-madrid.vercel.app`**: keeps the project's name exactly.
3. **`vidafacil-datamad.vercel.app`**: ties the demo to the competition.

Outside `.vercel.app`, a subdomain of a domain Mariano already has on Vercel is also possible, for example `vidafacil.<his domain>`. That is his decision because it is his own brand.

The probe is a strong signal, not a guarantee. The only real check is assigning the alias:

```bash
npx vercel@65.12.1 domains add <name>.vercel.app vida-facil
```

It is reversible with `domains rm`.

After choosing one:
- update `NEXT_PUBLIC_API_URL`, `CORS_ORIGINS` and `DEMO_URL` in `infra/deploy/deploy.sh` and `scripts/smoke_demo.sh`;
- run `make deploy-demo`.
