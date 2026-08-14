"""Fixed raw/normalized ensemble with Freeciv full-map weak supervision."""

import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

import evaluate_terrain_domain_shift as audit
import evaluate_terrain_freeciv_maps as freeciv


REPORT = audit.ROOT / "output/terrain_model/terrain_freeciv_ensemble_report.json"


def probabilities(train_x, train_y, test_x, c):
    scaler = StandardScaler().fit(train_x)
    model = LogisticRegression(
        C=c, class_weight="balanced", max_iter=2500, solver="lbfgs",
        random_state=audit.SEED,
    ).fit(scaler.transform(train_x), train_y)
    return model.predict_proba(scaler.transform(test_x))


def main():
    map_x, map_labels, map_groups, map_names, _ = audit.data.trusted_map_cells()
    texture_x, texture_labels, texture_groups, _ = audit.data.texture_cells()
    ext_x, ext_labels, ext_groups, _ = freeciv.freeciv_cells()
    folds, truths, predictions = [], [], []
    raw_weight = 0.65
    for held_out in sorted(set(map_names.tolist())):
        source, target = map_names != held_out, map_names == held_out
        train_x = np.concatenate((map_x[source], texture_x, ext_x)).astype(np.float32)
        train_labels = np.concatenate((map_labels[source], texture_labels, ext_labels))
        train_y = audit.data.class_index(train_labels)
        train_groups = np.concatenate((map_groups[source], texture_groups, ext_groups))
        train_domains = np.asarray([
            group.split("-block-")[0] if "-block-" in group else
            group.rsplit("-", 2)[0] for group in train_groups
        ])
        test_x = map_x[target].astype(np.float32)
        test_y = audit.data.class_index(map_labels[target])
        norm_train = audit.domain_standardize(train_x, train_domains)
        norm_test = audit.domain_standardize(test_x, map_names[target])
        raw_c = freeciv.choose_c(train_x, train_y, train_groups)
        norm_c = freeciv.choose_c(norm_train, train_y, train_groups)
        score = raw_weight * probabilities(train_x, train_y, test_x, raw_c)
        score += (1.0 - raw_weight) * probabilities(
            norm_train, train_y, norm_test, norm_c
        )
        prediction = score.argmax(1)
        folds.append({"held_out_map": held_out, "raw_c": raw_c,
                      "normalized_c": norm_c,
                      **audit.metrics(test_y, prediction)})
        truths.append(test_y); predictions.append(prediction)
    payload = {
        "evaluation": "leave-one-fully-reviewed-map-out",
        "method": "Freeciv full-map supervision + fixed 0.65 raw/0.35 normalized ensemble",
        "target_label_access": "metrics-only after prediction",
        "folds": folds,
        "pooled": audit.metrics(np.concatenate(truths), np.concatenate(predictions)),
        "production_promotion": False, "auto_apply": False,
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["pooled"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
