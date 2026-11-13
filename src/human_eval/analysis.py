"""
analysis.py - turn the ratings into answers.

    script_means(raters)            mean human score per script and criterion
    group_means(...)                ... averaged per audience / per search mode (like Day 9's tables)
    claim_labels(raters)            one label per sentence (majority of the raters)
    labels_by_verdict(...)          for each checker verdict: how many sentences humans called true / hype / wrong
    human_truth(...)                share of claims that are really true, per audience - vs "supported" / "grounded"
    agreement(raters)               do the raters agree with each other? (needs 2+ raters)
    correlations(...)               do the automatic metrics go up when the human scores go up?

With 1 rater and 15 scripts these are first indications, not statistics.
"""

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from itertools import combinations
from statistics import mean

from scipy.stats import spearmanr

from src.human_eval.items import ClaimItem, Items, ScriptItem
from src.human_eval.ratings import RaterFile
from src.human_eval.rubric import CLAIM_LABELS, CRITERIA, SKIP

CRITERION_NAMES = [c.name for c in CRITERIA]
LABELS = list(CLAIM_LABELS.values())  # true, hype, wrong, no_claim
STRICTNESS = ["no_claim", "true", "hype", "wrong"]  # a tie between raters goes to the label further right
VERDICT_ORDER = ("supported", "weak", "unsupported", "uncited")

# (human criterion, automatic metric in eval/results.json): does the metric measure what humans see?
METRIC_PAIRS = [
    ("factuality", "supported_share"),
    ("factuality", "grounded_share"),
    ("audience_fit", "reading_ease"),
    ("helpfulness", "bertscore"),
    ("helpfulness", "rougeL"),
]

Means = dict[str, dict[str, float]]  # case_id -> criterion -> mean score


def script_means(raters: list[RaterFile]) -> Means:
    scores: dict[str, dict[str, list[int]]] = {}
    for rater in raters:
        for case_id, rating in rater.scripts.items():
            for name in CRITERION_NAMES:
                scores.setdefault(case_id, {}).setdefault(name, []).append(rating[name])
    return {case_id: {name: mean(values) for name, values in by.items()} for case_id, by in scores.items()}


def group_means(scripts: list[ScriptItem], means: Means, key: Callable[[ScriptItem], str],
                keep: Callable[[ScriptItem], bool] = lambda _: True) -> list[tuple[str, int, dict[str, float]]]:
    groups: dict[str, list[str]] = {}
    for s in scripts:
        if keep(s) and s.case_id in means:
            groups.setdefault(key(s), []).append(s.case_id)
    return [(group, len(ids), {name: mean(means[i][name] for i in ids) for name in CRITERION_NAMES})
            for group, ids in groups.items()]


def claim_labels(raters: list[RaterFile]) -> dict[str, str]:
    """Majority label per sentence. A tie goes to the WORSE label (wrong > hype > true): be strict.
    Skipped sentences ("unsure") are not votes."""
    votes: dict[str, list[str]] = {}
    for rater in raters:
        for key, answer in rater.claims.items():
            if answer["label"] != SKIP:
                votes.setdefault(key, []).append(answer["label"])
    return {key: max(Counter(v).items(), key=lambda kv: (kv[1], STRICTNESS.index(kv[0])))[0]
            for key, v in votes.items()}


def labels_by_verdict(claims: list[ClaimItem], labels: dict[str, str]) -> list[tuple[str, int, dict[str, float]]]:
    table = []
    for verdict in VERDICT_ORDER:
        rated = [labels[c.key] for c in claims if c.verdict == verdict and c.key in labels]
        if rated:
            table.append((verdict, len(rated), {label: rated.count(label) / len(rated) for label in LABELS}))
    return table


@dataclass
class Truth:
    audience: str
    n_scripts: int
    supported: float  # the checker, strict
    grounded: float  # the checker, lenient
    human: float  # estimated share of claims a human calls TRUE


def human_truth(items: Items, labels: dict[str, str], metrics: dict[str, dict]) -> list[Truth]:
    """
    Every doubtful claim was rated, but only ONE supported claim per script (the control).
    So: really-true claims = supported claims x (share of controls rated true) + doubtful claims rated true.
    Sentences rated no_claim ("The sources do not mention costs.") are not counted at all.
    Scripts with unrated doubtful claims are left out.
    """
    controls = [labels[c.key] for c in items.claims if c.verdict == "supported" and c.key in labels]
    if not controls:
        return []
    control_true = controls.count("true") / len(controls)

    per_audience: dict[str, list[tuple[float, float, float]]] = {}
    for script in items.scripts:
        doubtful = [c for c in items.claims if c.case_id == script.case_id and c.verdict != "supported"]
        row = metrics.get(script.case_id)
        if row is None or any(c.key not in labels for c in doubtful):
            continue
        n = row["n_claims"] - sum(labels[c.key] == "no_claim" for c in doubtful)
        if n == 0:
            continue
        n_supported = round(row["supported_share"] * row["n_claims"])
        really_true = n_supported * control_true + sum(labels[c.key] == "true" for c in doubtful)
        per_audience.setdefault(script.audience, []).append(
            (row["supported_share"], row["grounded_share"], really_true / n))
    return [Truth(audience, len(v), mean(x[0] for x in v), mean(x[1] for x in v), mean(x[2] for x in v))
            for audience, v in per_audience.items()]


@dataclass
class Agreement:
    n_pairs: int  # (rater pair, item) comparisons
    exact: float  # same score / label
    within_one: float | None  # scores at most 1 apart (scripts only)


def agreement(raters: list[RaterFile]) -> dict[str, Agreement]:
    """Per criterion (and for the sentence labels): how often do two raters give the same answer?"""
    result = {}
    for name in CRITERION_NAMES:
        diffs = [abs(a.scripts[k][name] - b.scripts[k][name])
                 for a, b in combinations(raters, 2) for k in a.scripts.keys() & b.scripts.keys()]
        if diffs:
            result[name] = Agreement(len(diffs), diffs.count(0) / len(diffs), sum(d <= 1 for d in diffs) / len(diffs))
    same = [a.claims[k]["label"] == b.claims[k]["label"]
            for a, b in combinations(raters, 2) for k in a.claims.keys() & b.claims.keys()
            if SKIP not in (a.claims[k]["label"], b.claims[k]["label"])]
    if same:
        result["sentence labels"] = Agreement(len(same), sum(same) / len(same), None)
    return result


@dataclass
class Correlation:
    criterion: str
    metric: str
    n: int
    rho: float | None  # Spearman: +1 = same ranking, 0 = unrelated, -1 = opposite
    p: float | None


def correlations(means: Means, metrics: dict[str, dict]) -> list[Correlation]:
    result = []
    for criterion, metric in METRIC_PAIRS:
        pairs = [(m[criterion], metrics[c][metric]) for c, m in means.items()
                 if c in metrics and metrics[c].get(metric) is not None]
        rho = p = None
        if len(pairs) >= 4 and len({h for h, _ in pairs}) > 1 and len({a for _, a in pairs}) > 1:
            rho, p = (float(x) for x in spearmanr([h for h, _ in pairs], [a for _, a in pairs]))
        result.append(Correlation(criterion, metric, len(pairs), rho, p))
    return result
