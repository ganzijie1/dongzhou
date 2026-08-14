"""Run the domain-shift audit with character labels for grouped splitting."""

import evaluate_terrain_domain_shift as audit


def choose_c(features, labels, groups):
    train, validation = audit.data.choose_group_split(
        audit.data.CLASSES[labels], groups
    )
    best = None
    for c in (0.003, 0.01, 0.03, 0.1, 0.3):
        prediction = audit.fit_predict(
            features[train], labels[train], features[validation], c
        )
        score = audit.f1_score(
            labels[validation], prediction,
            labels=audit.np.arange(len(audit.data.CLASSES)),
            average="macro", zero_division=0,
        )
        candidate = (score, -c, c)
        if best is None or candidate > best:
            best = candidate
    return float(best[2])


audit.choose_c = choose_c
audit.main()
