from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "AGENTS.md").is_file())
PHASE = ROOT / "phases" / "phase2_cohort_definition"
TASK = PHASE / "tasks" / "task01_cohort_spec"


def main() -> None:
    spec_text = (PHASE / "COHORT_SPEC.md").read_text(encoding="utf-8")
    decision_text = (PHASE / "DECISION_LOG.md").read_text(encoding="utf-8")
    report_text = (TASK / "report" / "REPORT_phase2_task01.md").read_text(encoding="utf-8")

    with (TASK / "outputs" / "rule_register_phase2_task01.csv").open(encoding="utf-8-sig", newline="") as handle:
        rules = list(csv.DictReader(handle))
    with (TASK / "outputs" / "decision_questions_phase2_task01.csv").open(encoding="utf-8-sig", newline="") as handle:
        questions = list(csv.DictReader(handle))

    required_rule_columns = {
        "rule_order", "rule_id", "component", "source_table", "logic",
        "rationale", "audit_unit", "decision_id", "status",
    }
    assert rules and required_rule_columns == set(rules[0]), "Rule register schema is not complete"
    rule_ids = [row["rule_id"] for row in rules]
    assert len(rule_ids) == len(set(rule_ids)), "Duplicate rule_id"
    assert [int(row["rule_order"]) for row in rules] == list(range(1, len(rules) + 1)), "rule_order is not contiguous"
    for rule_id in rule_ids:
        assert re.search(rf"\b{re.escape(rule_id)}\b", spec_text), f"Rule missing from spec: {rule_id}"

    expected_pending = {f"P2-D{number:02d}" for number in range(8, 15)}
    question_ids = {row["decision_id"] for row in questions}
    assert question_ids == expected_pending, "Decision question register must contain P2-D08 through P2-D14"
    for decision_id in expected_pending:
        assert decision_id in spec_text, f"Decision missing from spec: {decision_id}"
        assert decision_id in decision_text, f"Decision missing from decision log: {decision_id}"
        assert decision_id in report_text, f"Decision missing from report: {decision_id}"

    assert "CHƯA DUYỆT" in spec_text
    assert "CHỜ QUYẾT ĐỊNH P2-D08" in spec_text
    assert "selected_window_hours =" not in spec_text
    assert "Task 1 không tạo cohort" in spec_text
    print(f"PASS phase2 task01: {len(rules)} rules, {len(questions)} pending decisions")


if __name__ == "__main__":
    main()
