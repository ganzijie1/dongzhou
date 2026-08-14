"""Evaluate a fixed raw/normalized probability ensemble under map LOMO."""

import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import evaluate_terrain_domain_shift as audit


def probabilities(train_x, train_y, test_x, c):
    scaler = StandardScaler().fit(train_x)
    model = LogisticRegression(
        C=c, class_weight="balanced", max_iter=2500, solver="lbfgs",
        random_state=audit.SEED,
    ).fit(scaler.transform(train_x), train_y)
    return model.predict_proba(scaler.transform(test_x))


def choose_c(x, y, groups):
    train, validation = audit.data.choose_group_split(audit.data.CLASSES[y], groups)
    best = None
    for c in (0.003, 0.01, 0.03, 0.1, 0.3):
        prediction = audit.fit_predict(x[train], y[train], x[validation], c)
        score = audit.f1_score(
            y[validation], prediction, labels=np.arange(len(audit.data.CLASSES)),
            average="macro", zero_division=0,
        )
        candidate = (score, -c, c)
        if best is None or candidate > best:
            best = candidate
    return float(best[2])


def main():
    map_x, map_labels, map_groups, map_names, _ = audit.data.trusted_map_cells()
    texture_x, texture_labels, texture_groups, _ = audit.data.texture_cells()
    texture_domain = audit.texture_domains(texture_groups)
    folds, truths, predictions = [], [], []
    raw_weight = 0.70
    for held_out in sorted(set(map_names.tolist())):
        source, target = map_names != held_out, map_names == held_out
        train_x = np.concatenate((map_x[source], texture_x)).astype(np.float32)
        train_labels = np.concatenate((map_labels[source], texture_labels))
        train_y = audit.data.class_index(train_labels)
        train_groups = np.concatenate((map_groups[source], texture_groups))
        domains = np.concatenate((map_names[source], texture_domain))
        test_x = map_x[target].astype(np.float32)
        test_y = audit.data.class_index(map_labels[target])
        normalized_train = audit.domain_standardize(train_x, domains)
        normalized_test = audit.domain_standardize(test_x, map_names[target])
        raw_c = choose_c(train_x, train_y, train_groups)
        normalized_c = choose_c(normalized_train, train_y, train_groups)
        score = raw_weight * probabilities(train_x, train_y, test_x, raw_c)
        score += (1.0 - raw_weight) * probabilities(
            normalized_train, train_y, normalized_test, normalized_c
        )
        prediction = score.argmax(axis=1)
        folds.append({"held_out_map": held_out, "raw_c": raw_c,
                      "normalized_c": normalized_c,
                      **audit.metrics(test_y, prediction)})
        truths.append(test_y); predictions.append(prediction)
    payload = {
        "evaluation": "leave-one-fully-reviewed-map-out",
        "method": "fixed-0.70-raw-0.30-per-domain-normalized-probability-ensemble",
        "target_label_access": "metrics-only after prediction",
        "folds": folds,
        "pooled": audit.metrics(np.concatenate(truths), np.concatenate(predictions)),
        "production_promotion": False, "auto_apply": False,
    }
    path = audit.ROOT / "output/terrain_model/terrain_probability_ensemble_report.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["pooled"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
