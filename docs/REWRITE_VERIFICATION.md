> Historical checks for an earlier implementation. See PRODUCTION_VERIFICATION.md for current delivery checks.

# Single-page / Gemini / Chroma rewrite — 2 October 2026

Verified in this workspace:

- 42 Python tests passed, including the nine new research-pipeline integration tests.
- Python lint passed.
- Frontend TypeScript and ESLint passed.
- Next.js 15.5.27 production build passed.
- Chroma ingestion: seven documents, 47 passages. Incremental updates and removal of obsolete chunks were tested in isolated temporary databases.
- Gemini API authentication/header and content request contracts tested with mocked responses. Grounded citations are passed to the provider, invented monetary claims are rejected, and provider failures retain calculated explanations.
- Tavily allowed-domain filtering, timeout fallback and combined PDF/web context tested with mocked responses.
- PDF upload validation, filename sanitization and indexing tested in temporary directories.
- Server-sent analysis stages and saved results verified.
- Signed-rate chat parsing, ambiguous percentages and reuse of saved tariffs verified.
- Browser sample flow: all three form steps → streamed analysis → inline financial results, with missing-provider status clearly shown.
- Desktop and 390px mobile layouts inspected. The Three.js scene rendered; neither viewport had horizontal document overflow.
- Browser follow-up question at a selected 30-year horizon recalculated at that horizon.
- Report and CSV exports passed for 30, 40 and 50 years; final CSV present values matched saved LCC totals. Reports include two charts and labelled evidence excerpts.
- Final production build passed after UI readability and fallback-status refinements. Dependency consistency check passed.

No Gemini or Tavily credentials were supplied; live provider requests were not made. Cached tariff values were retained rather than independently reverified online during this rewrite.

Earlier verification in VERIFICATION.md describes the previous seven-step UI and FAISS implementation.
