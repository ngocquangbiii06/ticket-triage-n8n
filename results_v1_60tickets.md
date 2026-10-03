# Evaluation results - prompt v1 (baseline), 60 tickets

- Tickets: 60
- Category correct: 55/60 (92%)
- Priority correct: 54/60 (90%)
- Sent to human review: 1/60 (2%)
- Category correct among auto-routed tickets: 54/59 (92%)
- Wrong categories caught by review: 0/5 (0%)
- LLM call failures: 0

## Category accuracy by expected category

| Category | Correct |
|---|---|
| billing | 7/7 (100%) |
| delivery_delay | 8/8 (100%) |
| inventory_mismatch | 7/8 (88%) |
| lost_or_damaged | 8/9 (89%) |
| other | 9/10 (90%) |
| system_error | 10/10 (100%) |
| wrong_item | 6/8 (75%) |

## Category accuracy by ticket kind

| Kind | Correct |
|---|---|
| borderline | 1/5 (20%) |
| english | 4/4 (100%) |
| injection | 4/4 (100%) |
| multi_issue | 4/4 (100%) |
| no_diacritics | 3/3 (100%) |
| noise | 2/2 (100%) |
| plain | 37/38 (97%) |

## Confusions (expected -> got)

- lost_or_damaged -> delivery_delay: 1
- wrong_item -> lost_or_damaged: 1
- other -> billing: 1
- wrong_item -> inventory_mismatch: 1
- inventory_mismatch -> system_error: 1

## All tickets

| Ticket | Kind | Expected | Got | OK | Exp. priority | Got | OK | Route | Problems |
|---|---|---|---|---|---|---|---|---|---|
| T001 | plain | delivery_delay | delivery_delay | yes | high | high | yes | team_ops | - |
| T002 | plain | lost_or_damaged | lost_or_damaged | yes | high | high | yes | team_ops | - |
| T003 | plain | wrong_item | wrong_item | yes | medium | medium | yes | team_ops | - |
| T004 | plain | inventory_mismatch | inventory_mismatch | yes | medium | medium | yes | team_ops | - |
| T005 | plain | system_error | system_error | yes | high | high | yes | team_tech | - |
| T006 | plain | billing | billing | yes | medium | medium | yes | team_finance | - |
| T007 | borderline | lost_or_damaged | delivery_delay | NO | high | high | yes | team_ops | - |
| T008 | plain | other | other | yes | low | low | yes | team_ops | - |
| T009 | plain | delivery_delay | delivery_delay | yes | medium | medium | yes | team_ops | - |
| T010 | plain | system_error | system_error | yes | high | high | yes | team_tech | - |
| T011 | borderline | wrong_item | lost_or_damaged | NO | medium | medium | yes | team_ops | - |
| T012 | plain | inventory_mismatch | inventory_mismatch | yes | medium | medium | yes | team_ops | - |
| T013 | plain | other | other | yes | low | low | yes | team_cs | - |
| T014 | plain | billing | billing | yes | medium | medium | yes | team_finance | - |
| T015 | injection | system_error | system_error | yes | high | high | yes | team_ops | - |
| T016 | plain | delivery_delay | delivery_delay | yes | high | high | yes | team_ops | - |
| T017 | no_diacritics | delivery_delay | delivery_delay | yes | medium | high | NO | team_ops | - |
| T018 | english | delivery_delay | delivery_delay | yes | medium | medium | yes | team_ops | - |
| T019 | plain | delivery_delay | delivery_delay | yes | high | high | yes | team_ops | - |
| T020 | plain | lost_or_damaged | lost_or_damaged | yes | high | high | yes | team_ops | - |
| T021 | plain | lost_or_damaged | lost_or_damaged | yes | high | high | yes | team_ops | - |
| T022 | plain | lost_or_damaged | lost_or_damaged | yes | medium | medium | yes | team_ops | - |
| T023 | english | lost_or_damaged | lost_or_damaged | yes | high | high | yes | team_ops | - |
| T024 | plain | wrong_item | wrong_item | yes | medium | medium | yes | team_ops | - |
| T025 | plain | wrong_item | wrong_item | yes | medium | medium | yes | team_ops | - |
| T026 | no_diacritics | wrong_item | wrong_item | yes | medium | medium | yes | team_ops | - |
| T027 | plain | wrong_item | wrong_item | yes | high | high | yes | team_ops | - |
| T028 | plain | inventory_mismatch | inventory_mismatch | yes | medium | medium | yes | team_ops | - |
| T029 | plain | inventory_mismatch | inventory_mismatch | yes | high | high | yes | team_ops | - |
| T030 | plain | inventory_mismatch | inventory_mismatch | yes | medium | medium | yes | team_ops | - |
| T031 | english | inventory_mismatch | inventory_mismatch | yes | medium | medium | yes | team_ops | - |
| T032 | plain | system_error | system_error | yes | high | high | yes | team_ops | - |
| T033 | plain | system_error | system_error | yes | medium | medium | yes | team_tech | - |
| T034 | plain | system_error | system_error | yes | high | high | yes | team_tech | - |
| T035 | plain | system_error | system_error | yes | medium | medium | yes | team_tech | - |
| T036 | plain | system_error | system_error | yes | high | high | yes | team_tech | - |
| T037 | plain | billing | billing | yes | medium | high | NO | team_finance | - |
| T038 | plain | billing | billing | yes | medium | low | NO | team_finance | - |
| T039 | plain | billing | billing | yes | high | high | yes | team_finance | - |
| T040 | borderline | other | billing | NO | low | low | yes | team_finance | - |
| T041 | plain | other | other | yes | low | low | yes | team_ops | - |
| T042 | plain | other | other | yes | low | low | yes | team_tech | - |
| T043 | plain | other | other | yes | low | low | yes | team_cs | - |
| T044 | plain | other | other | yes | low | low | yes | team_cs | - |
| T045 | english | other | other | yes | low | low | yes | team_cs | - |
| T046 | multi_issue | system_error | system_error | yes | high | high | yes | team_ops | - |
| T047 | multi_issue | lost_or_damaged | lost_or_damaged | yes | high | high | yes | team_ops | - |
| T048 | multi_issue | wrong_item | wrong_item | yes | medium | medium | yes | team_ops | - |
| T049 | multi_issue | billing | billing | yes | medium | medium | yes | team_finance | - |
| T050 | borderline | inventory_mismatch | inventory_mismatch | yes | medium | medium | yes | team_ops | - |
| T051 | injection | lost_or_damaged | lost_or_damaged | yes | high | high | yes | team_ops | - |
| T052 | injection | billing | billing | yes | medium | high | NO | team_finance | - |
| T053 | injection | system_error | system_error | yes | high | high | yes | team_ops | - |
| T054 | no_diacritics | delivery_delay | delivery_delay | yes | high | high | yes | team_ops | - |
| T055 | noise | other | other | yes | low | low | yes | human_review | quote_not_in_ticket |
| T056 | noise | other | other | yes | low | low | yes | team_cs | - |
| T057 | borderline | wrong_item | inventory_mismatch | NO | medium | high | NO | team_ops | - |
| T058 | plain | lost_or_damaged | lost_or_damaged | yes | medium | low | NO | team_ops | - |
| T059 | plain | delivery_delay | delivery_delay | yes | medium | medium | yes | team_ops | - |
| T060 | plain | inventory_mismatch | system_error | NO | high | high | yes | team_tech | - |
