# Evaluation Report

## Summary

- Total examples: 12
- Top-1 retrieval accuracy: 83.33%
- Evidence recall@3: 100.00%
- Escalation accuracy: 75.00%
- Average gold coverage: 37.50%
- Average confidence: 0.764
- Unsupported answer count: 2

## Per-example results

| ID | Expected Source | Predicted Source | Expected Escalation | Predicted Escalation | Coverage | Confidence |
|---|---|---|---:|---:|---:|---:|
| ex_001 | cashout_failures.md | cashout_failures.md | False | False | 0.333 | 0.747 |
| ex_002 | cashout_failures.md | cashout_failures.md | False | False | 1.000 | 0.742 |
| ex_003 | cashout_failures.md | cashout_failures.md | False | False | 0.500 | 0.755 |
| ex_004 | wrong_recipient.md | wrong_recipient.md | True | True | 0.667 | 0.770 |
| ex_005 | wrong_recipient.md | wrong_recipient.md | True | True | 0.500 | 0.770 |
| ex_006 | account_locked.md | account_locked.md | True | False | 0.000 | 0.770 |
| ex_007 | account_locked.md | account_locked.md | True | False | 0.500 | 0.770 |
| ex_008 | account_locked.md | account_locked.md | True | True | 0.500 | 0.770 |
| ex_009 | kyc_help.md | kyc_help.md | False | False | 0.500 | 0.770 |
| ex_010 | kyc_help.md | kyc_help.md | False | True | 0.000 | 0.770 |
| ex_011 | kyc_help.md | account_locked.md | True | True | 0.000 | 0.770 |
| ex_012 | faq.md | kyc_help.md | True | True | 0.000 | 0.766 |
