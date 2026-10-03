# Evaluation results - prompt v3, 60 tickets

- Tickets: 60
- Category correct: 58/60 (97%)
- Priority correct: 48/60 (80%)
- Sent to human review: 9/60 (15%)
- Category correct among auto-routed tickets: 50/51 (98%)
- Wrong categories caught by review: 1/2 (50%)
- LLM call failures: 0

## Category accuracy by expected category

| Category | Correct |
|---|---|
| billing | 7/7 (100%) |
| delivery_delay | 7/8 (88%) |
| inventory_mismatch | 7/8 (88%) |
| lost_or_damaged | 9/9 (100%) |
| other | 10/10 (100%) |
| system_error | 10/10 (100%) |
| wrong_item | 8/8 (100%) |

## Category accuracy by ticket kind

| Kind | Correct |
|---|---|
| borderline | 5/5 (100%) |
| english | 4/4 (100%) |
| injection | 4/4 (100%) |
| multi_issue | 4/4 (100%) |
| no_diacritics | 2/3 (67%) |
| noise | 2/2 (100%) |
| plain | 37/38 (97%) |

## Confusions (expected -> got)

- delivery_delay -> billing: 1
- inventory_mismatch -> system_error: 1

## All tickets

| Ticket | Kind | Expected | Got | OK | Exp. priority | Got | OK | Route | Problems |
|---|---|---|---|---|---|---|---|---|---|
| T001 | plain | delivery_delay | delivery_delay | yes | high | high | yes | team_ops | - |
| T002 | plain | lost_or_damaged | lost_or_damaged | yes | high | medium | NO | team_ops | - |
| T003 | plain | wrong_item | wrong_item | yes | medium | medium | yes | human_review | quote_not_in_ticket |
| T004 | plain | inventory_mismatch | inventory_mismatch | yes | medium | low | NO | team_ops | - |
| T005 | plain | system_error | system_error | yes | high | high | yes | team_tech | - |
| T006 | plain | billing | billing | yes | medium | medium | yes | team_finance | - |
| T007 | borderline | lost_or_damaged | lost_or_damaged | yes | high | high | yes | team_ops | - |
| T008 | plain | other | other | yes | low | low | yes | team_cs | - |
| T009 | plain | delivery_delay | delivery_delay | yes | medium | medium | yes | team_ops | - |
| T010 | plain | system_error | system_error | yes | high | high | yes | team_tech | - |
| T011 | borderline | wrong_item | wrong_item | yes | medium | medium | yes | team_ops | - |
| T012 | plain | inventory_mismatch | inventory_mismatch | yes | medium | low | NO | team_ops | - |
| T013 | plain | other | other | yes | low | low | yes | team_cs | - |
| T014 | plain | billing | billing | yes | medium | medium | yes | team_finance | - |
| T015 | injection | system_error | system_error | yes | high | high | yes | team_tech | - |
| T016 | plain | delivery_delay | delivery_delay | yes | high | high | yes | team_ops | - |
| T017 | no_diacritics | delivery_delay | delivery_delay | yes | medium | medium | yes | team_ops | - |
| T018 | english | delivery_delay | delivery_delay | yes | medium | medium | yes | team_ops | - |
| T019 | plain | delivery_delay | delivery_delay | yes | high | high | yes | team_ops | - |
| T020 | plain | lost_or_damaged | lost_or_damaged | yes | high | high | yes | team_ops | - |
| T021 | plain | lost_or_damaged | lost_or_damaged | yes | high | high | yes | team_ops | - |
| T022 | plain | lost_or_damaged | lost_or_damaged | yes | medium | medium | yes | team_ops | - |
| T023 | english | lost_or_damaged | lost_or_damaged | yes | high | high | yes | team_ops | - |
| T024 | plain | wrong_item | wrong_item | yes | medium | medium | yes | team_ops | - |
| T025 | plain | wrong_item | wrong_item | yes | medium | low | NO | team_ops | - |
| T026 | no_diacritics | wrong_item | wrong_item | yes | medium | low | NO | team_ops | - |
| T027 | plain | wrong_item | wrong_item | yes | high | high | yes | team_ops | - |
| T028 | plain | inventory_mismatch | inventory_mismatch | yes | medium | low | NO | team_ops | - |
| T029 | plain | inventory_mismatch | inventory_mismatch | yes | high | medium | NO | team_ops | - |
| T030 | plain | inventory_mismatch | inventory_mismatch | yes | medium | low | NO | team_ops | - |
| T031 | english | inventory_mismatch | inventory_mismatch | yes | medium | low | NO | team_ops | - |
| T032 | plain | system_error | system_error | yes | high | high | yes | human_review | quote_not_in_ticket |
| T033 | plain | system_error | system_error | yes | medium | low | NO | team_tech | - |
| T034 | plain | system_error | system_error | yes | high | high | yes | team_tech | - |
| T035 | plain | system_error | system_error | yes | medium | medium | yes | team_tech | - |
| T036 | plain | system_error | system_error | yes | high | high | yes | team_tech | - |
| T037 | plain | billing | billing | yes | medium | medium | yes | team_finance | - |
| T038 | plain | billing | billing | yes | medium | medium | yes | team_finance | - |
| T039 | plain | billing | billing | yes | high | high | yes | team_finance | - |
| T040 | borderline | other | other | yes | low | low | yes | team_cs | - |
| T041 | plain | other | other | yes | low | low | yes | team_cs | - |
| T042 | plain | other | other | yes | low | low | yes | team_cs | - |
| T043 | plain | other | other | yes | low | low | yes | team_cs | - |
| T044 | plain | other | other | yes | low | low | yes | team_cs | - |
| T045 | english | other | other | yes | low | low | yes | team_cs | - |
| T046 | multi_issue | system_error | system_error | yes | high | high | yes | human_review | ambiguous: also delivery_delay |
| T047 | multi_issue | lost_or_damaged | lost_or_damaged | yes | high | high | yes | human_review | ambiguous: also delivery_delay |
| T048 | multi_issue | wrong_item | wrong_item | yes | medium | medium | yes | team_ops | - |
| T049 | multi_issue | billing | billing | yes | medium | medium | yes | team_finance | - |
| T050 | borderline | inventory_mismatch | inventory_mismatch | yes | medium | low | NO | team_ops | - |
| T051 | injection | lost_or_damaged | lost_or_damaged | yes | high | high | yes | team_ops | - |
| T052 | injection | billing | billing | yes | medium | medium | yes | team_finance | - |
| T053 | injection | system_error | system_error | yes | high | high | yes | human_review | ambiguous: also delivery_delay |
| T054 | no_diacritics | delivery_delay | billing | NO | high | high | yes | team_finance | - |
| T055 | noise | other | other | yes | low | low | yes | human_review | too_short, quote_not_in_ticket |
| T056 | noise | other | other | yes | low | low | yes | human_review | too_short |
| T057 | borderline | wrong_item | wrong_item | yes | medium | medium | yes | team_ops | - |
| T058 | plain | lost_or_damaged | lost_or_damaged | yes | medium | medium | yes | human_review | ambiguous: also other |
| T059 | plain | delivery_delay | delivery_delay | yes | medium | low | NO | team_ops | - |
| T060 | plain | inventory_mismatch | system_error | NO | high | high | yes | human_review | ambiguous: also inventory_mismatch |
