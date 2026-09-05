#!/usr/bin/env python3
"""Validate exact local artifacts and advisory authority locks; never source truth."""
import argparse
import json
from pathlib import Path

from jsonschema import validators

LOCKS = {'execution_authority', 'forecast_authority', 'medical_authority',
         'runtime_mutation_allowed', 'promotion_authorized', 'canon_mutation_allowed',
         'production_activation_allowed', 'active_skill_replacement_allowed',
         'automatic_transition_allowed', 'memory_write_authority'}


def check_locks(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in LOCKS and child is not False:
                raise ValueError('authority lock is not false: ' + key)
            check_locks(child)
    elif isinstance(value, list):
        for child in value:
            check_locks(child)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--schema', required=True, type=Path)
    parser.add_argument('--member', help='Validate this top-level member against schema')
    parser.add_argument('artifacts', type=Path, nargs='+', help='Exact nonempty set; no implicit globs')
    args = parser.parse_args()
    try:
        schema = json.loads(args.schema.read_text())
        validator = validators.validator_for(schema)
        validator.check_schema(schema)
        for path in args.artifacts:
            packet = json.loads(path.read_text())
            member = packet[args.member] if args.member else packet
            validator(schema).validate(member)
            check_locks(packet)
    except Exception as exc:
        # Avoid dumping private payloads in jsonschema exception messages.
        parser.exit(1, 'VALIDATION_FAILED: ' + type(exc).__name__ + '\n')
    print(json.dumps({'status':'SCHEMA_AND_LOCKS_VALID', 'artifacts':[str(p) for p in args.artifacts], 'source_truth_verified':False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
