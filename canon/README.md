# Canon Reference

This directory is a reference pointer to the GAIA constitutional canon.

The canonical documents are maintained in the GAIA OS repository:
**[https://github.com/R0GV3TheAlchemist/GAIA](https://github.com/R0GV3TheAlchemist/GAIA)**

## What the Canon Is

The GAIA canon is the constitutional foundation of the entire system — 35+ documents defining:

- The legal hierarchy (9 tiers, from international law to platform policy)
- The axiological hierarchy (values, sovereignty, rights)
- The constitutional hierarchy (what no lower layer may override)
- The ontological hierarchy (what GAIA is and is not)
- The epistemic framework (how GAIA knows and claims)
- The social hierarchy, temporal hierarchy, scale hierarchy
- Identity, memory, security, and runtime specifications

## Relationship to This Repo

GAIA-APP does not rewrite or override the canon. It *enforces* it.

The `core/` Python modules in this repo are the runtime implementation of canon principles:

| Canon Document | Runtime Implementation |
|---|---|
| Doc 21 — Axiological (Sovereignty) | `core/action_gate.py`, `core/consent_ledger.py` |
| Doc 34 — Identity | `core/memory_store.py` |
| Doc 35 — Security | `core/action_gate.py` |
| Doc 29 — Legal Hierarchy (T8) | Platform policy compliance layer (planned) |

## Integration (Future)

In a future version, this directory will include a `git submodule` reference to the GAIA OS repo,
allowing canon documents to be loaded directly by `core/canon_loader.py` for runtime validation.

```bash
# Future setup:
git submodule add https://github.com/R0GV3TheAlchemist/GAIA canon/gaia-os
```
