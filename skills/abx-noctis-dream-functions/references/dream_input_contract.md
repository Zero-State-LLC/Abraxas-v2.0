# Dream Input Contract (v1)

```yaml
schema_version: "DreamInput.v1"
dream_id: string
source: USER | EXTERNAL | SYSTEM
captured_at: string  # ISO-8601

subject_ref: string | null
privacy_tier: PRIVATE | RESEARCH | PUBLIC_SYNTHETIC

narrative_raw: string
narrative_normalized: string

context:
  tags: []
  mood_self_report: string | null
  ...
emotional_vector: {...}
sensory_tags: []
lucidity_score: number | null
recall_confidence: number | null

seed: string
provenance:
  intake_method: text | voice | imported | generated
  operator: human | system
  input_refs: []
  content_sha256: string

authority:
  lane: SHADOW_SYMBOLIC
  medical_claims_allowed: false
  therapy_claims_allowed: false
  diagnostic_claims_allowed: false
  prediction_authority_allowed: false
  runtime_mutation_allowed: false
  promotion_allowed: false
```

Empty `narrative_raw` or equivalent → `NOT_COMPUTABLE`.

Use Abraxas Ingest for voice/file/legacy sources before this contract.