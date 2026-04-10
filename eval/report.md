# Evaluation Report

## Summary

- Total examples: 12
- Top-1 retrieval accuracy: 83.33%
- Evidence recall@3: 100.00%
- Escalation accuracy: 75.00%
- Average gold coverage: 84.72%
- Average confidence: 0.771
- Unsupported answer count: 0

## Per-example results

| ID | Expected Source | Predicted Source | Expected Escalation | Predicted Escalation | Coverage | Confidence |
|---|---|---|---:|---:|---:|---:|
| ex_001 | cashout_failures.md | cashout_failures.md | False | False | 0.667 | 0.746 |
| ex_002 | cashout_failures.md | cashout_failures.md | False | False | 0.500 | 0.737 |
| ex_003 | cashout_failures.md | cashout_failures.md | False | False | 0.500 | 0.758 |
| ex_004 | wrong_recipient.md | wrong_recipient.md | True | True | 1.000 | 0.780 |
| ex_005 | wrong_recipient.md | wrong_recipient.md | True | True | 1.000 | 0.780 |
| ex_006 | account_locked.md | account_locked.md | True | False | 0.500 | 0.780 |
| ex_007 | account_locked.md | account_locked.md | True | False | 1.000 | 0.780 |
| ex_008 | account_locked.md | account_locked.md | True | True | 1.000 | 0.780 |
| ex_009 | kyc_help.md | kyc_help.md | False | False | 1.000 | 0.780 |
| ex_010 | kyc_help.md | kyc_help.md | False | True | 1.000 | 0.780 |
| ex_011 | kyc_help.md | account_locked.md | True | True | 1.000 | 0.780 |
| ex_012 | faq.md | kyc_help.md | True | True | 1.000 | 0.774 |
