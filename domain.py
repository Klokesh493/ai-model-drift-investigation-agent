"""Investigate model drift with independent population, label and freshness checks."""
import math

from loop import Probe, integer, name, rows

BRIEF = "Triage model drift by comparing feature distributions, mature label quality and data freshness."
REQUIRED = {"population", "quality", "freshness"}


def build_probes(case):
    def population():
        drifted, assessed, insufficient = [], [], []
        for row in rows(case["features"]):
            feature = name(row["name"])
            if feature in assessed:
                raise ValueError("duplicate feature")
            assessed.append(feature)
            baseline, current = row["baseline_bins"], row["current_bins"]
            if not isinstance(baseline, list) or not isinstance(current, list) or not 2 <= len(baseline) == len(current) <= 30:
                raise ValueError("bins must align and contain 2–30 entries")
            old, new = [integer(x) for x in baseline], [integer(x) for x in current]
            if min(sum(old), sum(new)) < 100:
                insufficient.append(feature)
                continue
            old_total, new_total = sum(old) + len(old), sum(new) + len(new)
            old_ratios = [(count + 1) / old_total for count in old]
            new_ratios = [(count + 1) / new_total for count in new]
            psi = sum((q - p) * math.log(q / p) for p, q in zip(old_ratios, new_ratios))
            if psi >= 0.25:
                drifted.append({"feature": feature, "psi": round(psi, 4)})
        return {"drifted": drifted, "assessed": len(assessed), "insufficient": insufficient}

    def quality():
        values = {}
        for key in ("baseline", "current"):
            row = case["labels"][key]
            total, correct = integer(row["total"]), integer(row["correct"])
            if correct > total:
                raise ValueError("correct labels cannot exceed total")
            values[key] = correct / total if total >= 100 else None
        return values

    def freshness():
        age = integer(case["age_minutes"])
        return {"age_minutes": age, "stale": age > 60}

    return [
        Probe("population", "Compare feature histograms using the population stability index.", population),
        Probe("quality", "Check mature-label sample sizes and baseline versus current accuracy.", quality),
        Probe("freshness", "Check whether the data export is older than 60 minutes.", freshness),
    ]


def decide(evidence):
    population, quality, freshness = (evidence[key] for key in ("population", "quality", "freshness"))
    if freshness["stale"] or not population["assessed"] or population["insufficient"] or None in quality.values():
        decision, reason = "review", "refresh telemetry or gather mature labels before diagnosing drift"
    elif quality["current"] < quality["baseline"] - 0.05:
        decision, reason = ("investigate_drift", "feature shift and measured quality loss coexist") if population["drifted"] else (
            "investigate_quality", "measured quality dropped without a flagged population shift")
    elif population["drifted"]:
        decision, reason = "watch", "population shifted without measured quality loss"
    else:
        decision, reason = "observe", "feature and mature-label thresholds passed"
    return {"decision": decision, "reason": reason, "citations": sorted(REQUIRED)}


def prepare(case):
    return build_probes(case), decide
