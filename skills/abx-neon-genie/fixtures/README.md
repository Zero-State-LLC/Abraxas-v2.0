# abx-neon-genie fixtures

SHADOW residual corpus for `neon_genie_ideation` skill package tests.

| File | Use |
|------|-----|
| `venture_request_prompt_led.v0.json` | PROMPT_LED cycle (no evidence required) |
| `venture_request_market_led_no_pack.v0.json` | MARKET_LED without pack → commercial gate |
| `venture_request_trend_led_with_stub_pack.v0.json` | TREND_LED with stub EvidencePack payload |

Authority: advisory only. No packaging runtime, promotion, or Hermes Hub mutation.

```bash
python scripts/codegen/run_abx_neon_genie.py --input skills/abx-neon-genie/fixtures/venture_request_prompt_led.v0.json
```
