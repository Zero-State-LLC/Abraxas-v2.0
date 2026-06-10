# IntelligenceSystem Quickstart

## Installation / Import

```python
from core.intelligence.intelligence_system import IntelligenceSystem
from workflows.la_ca_adaptive_pipeline import LACAAdaptivePipeline
```

## Basic Usage

```python
system = IntelligenceSystem(config={
    "calibration_method": "beta"   # or 'isotonic', 'platt', 'dirichlet'
})

# Simple processing
result = system.process(data, target=0.3)

# Rich diagnostic report (recommended)
report = system.analyze(data, target=0.3)
print(report.get("brier_summary_text"))
```

## LA/CA Pipeline

```python
pipeline = LACAAdaptivePipeline()

result = pipeline.process_by_type("fire", {
    "value": 95,
    "severity": 0.8,
    "velocity": 0.5
})

print(pipeline.get_status())
```

## Available Calibration Methods

```python
print(IntelligenceSystem.available_calibration_methods())
# ['isotonic', 'platt', 'beta', 'dirichlet']
```

## Brier & Proper Scoring

The system automatically tracks:
- Brier Score + Skill Score
- Log Score + Spherical Score
- Full decomposition (Reliability / Resolution / Uncertainty)

Access via `result["brier_variants"]` or `system.get_brier_variants()`.
