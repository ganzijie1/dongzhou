"""Evaluate content-preserving raw + per-domain-normalized terrain features."""

import json

import numpy as np

import run_terrain_domain_shift as fixed


audit = fixed.audit
original_main = audit.main


def main():
    map_x, map_labels, map_groups, map_names, _ = audit.data.trusted_map_cells()
    texture_x, texture_labels, texture_groups, _ = audit.data.texture_cells()
    texture_domain = audit.texture_domains(texture_groups)
    folds, truths, predictions = [], [], []
    for held_out in sorted(set(map_names.tolist())):
        source_mask, target_mask = map_names != held_out, map_names == held_out
        train_x = np.concatenate((map_x[source_mask], texture_x)).astype(np.float32)
        train_labels = np.concatenate((map_labels[source_mask], texture_labels))
        train_y = audit.data.class_index(train_labels)
        train_groups = np.concatenate((map_groups[source_mask], texture_groups))
        train_domains = np.concatenate((map_names[source_mask], texture_domain))
        test_x = map_x[target_mask].astype(np.float32)
        test_y = audit.data.class_index(map_labels[target_mask])
        test_domains = map_names[target_mask]
        transformed_train = np.concatenate((
            train_x, audit.domain_standardize(train_x, train_domains)
        ), axis=1).astype(np.float32)
        transformed_test = np.concatenate((
            test_x, audit.domain_standardize(test_x, test_domains)
        ), axis=1).astype(np.float32)
        c = fixed.choose_c(transformed_train, train_y, train_groups)
        prediction = audit.fit_predict(
            transformed_train, train_y, transformed_test, c
        )
        folds.append({"held_out_map": held_out, "selected_c": c,
                      **audit.metrics(test_y, prediction)})
        truths.append(test_y); predictions.append(prediction)
    payload = {
        "evaluation": "leave-one-fully-reviewed-map-out",
        "method": "raw-plus-unsupervised-per-domain-robust-features",
        "target_label_access": "metrics-only after prediction",
        "folds": folds,
        "pooled": audit.metrics(np.concatenate(truths), np.concatenate(predictions)),
        "production_promotion": False, "auto_apply": False,
    }
    path = audit.ROOT / "output/terrain_model/terrain_dual_branch_report.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["pooled"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
