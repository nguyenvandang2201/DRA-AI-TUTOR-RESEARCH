"""Kiểm thử tính toàn vẹn dữ liệu và tính tái lập của công cụ.

Chạy bằng thư viện chuẩn:  `python -m unittest discover -s tests -v`
Hoặc bằng pytest nếu có:   `pytest tests`
"""

from __future__ import annotations

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from dra_utils import (  # noqa: E402
    DOMAIN_BY_SLUG,
    REQUIRED_FIELDS,
    SPLITS_DIR,
    VALID_LABELS,
    dataset_paths,
    load_all,
    load_dataset,
    normalize_query,
    record_id,
    slug_of,
    tokenize,
)


class TestDatasetIntegrity(unittest.TestCase):
    """Bất biến mà mọi file trong `datasets/` phải thoả."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.paths = dataset_paths()
        cls.records = load_all()

    def test_dataset_files_exist(self) -> None:
        self.assertGreaterEqual(len(self.paths), 3,
                                "phải có ít nhất 3 file dataset (một cho mỗi miền)")

    def test_schema_is_exact(self) -> None:
        for path in self.paths:
            for index, record in enumerate(load_dataset(path)):
                with self.subTest(file=path.name, index=index):
                    self.assertIsInstance(record, dict)
                    self.assertEqual(set(record), set(REQUIRED_FIELDS))

    def test_field_types_and_values(self) -> None:
        for record in self.records:
            with self.subTest(id=record["id"]):
                self.assertIsInstance(record["query"], str)
                self.assertTrue(record["query"].strip())
                self.assertIsInstance(record["domain"], str)
                self.assertNotIsInstance(record["label"], bool)
                self.assertIn(record["label"], VALID_LABELS)

    def test_domain_matches_filename(self) -> None:
        for path in self.paths:
            expected = DOMAIN_BY_SLUG.get(slug_of(path))
            if expected is None:
                continue
            domains = {record["domain"] for record in load_dataset(path)}
            with self.subTest(file=path.name):
                self.assertEqual(domains, {expected})

    def test_no_duplicate_queries(self) -> None:
        counts = Counter(normalize_query(str(record["query"])) for record in self.records)
        duplicates = [query for query, count in counts.items() if count > 1]
        self.assertEqual(duplicates, [], f"có {len(duplicates)} truy vấn trùng lặp")

    def test_labels_are_balanced_per_file(self) -> None:
        for path in self.paths:
            labels = Counter(record["label"] for record in load_dataset(path))
            with self.subTest(file=path.name):
                total = sum(labels.values())
                skew = abs(labels[0] - labels[1]) / total
                self.assertLessEqual(skew, 0.10, f"nhãn lệch quá 10%: {dict(labels)}")

    def test_queries_have_no_encoding_damage(self) -> None:
        for record in self.records:
            with self.subTest(id=record["id"]):
                self.assertNotIn("�", str(record["query"]))

    def test_json_files_are_utf8_and_parse(self) -> None:
        for path in self.paths:
            with self.subTest(file=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(data, list)
                self.assertTrue(data)


class TestUtils(unittest.TestCase):
    """Hàm dùng chung phải ổn định vì `id` bản ghi phụ thuộc vào chúng."""

    def test_tokenize_lowercases_and_drops_punctuation(self) -> None:
        self.assertEqual(tokenize("How does X, Y and Z_1 compare?"),
                         ["how", "does", "x", "y", "and", "z", "1", "compare"])

    def test_tokenize_keeps_contractions(self) -> None:
        self.assertIn("doesn't", tokenize("Why doesn't demand fall?"))

    def test_normalize_query_collapses_whitespace_and_case(self) -> None:
        self.assertEqual(normalize_query("  What   IS\tthis? "), "what is this?")

    def test_record_id_is_stable_and_insensitive_to_formatting(self) -> None:
        self.assertEqual(record_id("What is a p-value?"), record_id("what is   a p-value? "))
        self.assertNotEqual(record_id("What is a p-value?"), record_id("What is a z-score?"))
        self.assertEqual(len(record_id("anything")), 12)


class TestSplits(unittest.TestCase):
    """`datasets/splits/` phải khớp với dữ liệu nguồn và với manifest."""

    @classmethod
    def setUpClass(cls) -> None:
        if not (SPLITS_DIR / "manifest.json").exists():
            raise unittest.SkipTest("chưa sinh split; chạy python tools/make_splits.py")
        cls.manifest = json.loads((SPLITS_DIR / "manifest.json").read_text(encoding="utf-8"))
        cls.splits = {
            name: json.loads((SPLITS_DIR / f"{name}.json").read_text(encoding="utf-8"))
            for name in ("train", "dev", "test")
        }
        cls.records = load_all()

    def test_splits_partition_the_dataset(self) -> None:
        ids = [record["id"] for bucket in self.splits.values() for record in bucket]
        self.assertEqual(len(ids), len(self.records))
        self.assertEqual(set(ids), {record["id"] for record in self.records})

    def test_splits_do_not_overlap(self) -> None:
        train, dev, test = (set(record["id"] for record in self.splits[name])
                            for name in ("train", "dev", "test"))
        self.assertFalse(train & dev)
        self.assertFalse(train & test)
        self.assertFalse(dev & test)

    def test_manifest_counts_match_files(self) -> None:
        for name, bucket in self.splits.items():
            with self.subTest(split=name):
                self.assertEqual(self.manifest["splits"][name]["count"], len(bucket))

    def test_each_split_keeps_label_balance(self) -> None:
        for name, bucket in self.splits.items():
            labels = Counter(record["label"] for record in bucket)
            with self.subTest(split=name):
                skew = abs(labels[0] - labels[1]) / len(bucket)
                self.assertLessEqual(skew, 0.05)

    def test_each_split_covers_every_domain(self) -> None:
        all_domains = {record["domain"] for record in self.records}
        for name, bucket in self.splits.items():
            with self.subTest(split=name):
                self.assertEqual({record["domain"] for record in bucket}, all_domains)

    def test_splits_are_reproducible(self) -> None:
        from make_splits import build  # import trễ để test khác chạy được khi thiếu split

        rebuilt, manifest = build(self.manifest["seed"],
                                  tuple(self.manifest["ratios"][name]
                                        for name in ("train", "dev", "test")))
        for name, bucket in rebuilt.items():
            with self.subTest(split=name):
                self.assertEqual([record["id"] for record in bucket],
                                 [record["id"] for record in self.splits[name]])
        self.assertEqual(manifest["seed"], self.manifest["seed"])


class TestBaselineRouter(unittest.TestCase):
    """Baseline phải học được tín hiệu, không chỉ đoán bừa."""

    def test_vectorizer_produces_unit_norm_vectors(self) -> None:
        from baseline_router import TfidfVectorizer

        texts = ["how does supply compare to demand", "what is the marginal cost",
                 "how does price compare to cost"]
        vectorizer = TfidfVectorizer(min_df=1).fit(texts)
        vector = vectorizer.transform(texts[0])
        norm = sum(value * value for value in vector.values()) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=9)

    def test_unseen_lexical_terms_are_ignored(self) -> None:
        """Từ ngoài từ vựng bị bỏ qua; chỉ còn đặc trưng cấu trúc `__len_bucket`/`__q_marks`."""

        from baseline_router import TfidfVectorizer

        vectorizer = TfidfVectorizer(min_df=1).fit(["what is the marginal cost"])
        index_to_term = {index: term for term, index in vectorizer.vocabulary.items()}
        terms = {index_to_term[index] for index in vectorizer.transform("zzzz qqqq")}
        self.assertTrue(all(term.startswith("__") for term in terms), terms)

    def test_metrics_on_perfect_prediction(self) -> None:
        from baseline_router import metrics

        result = metrics([0, 1, 0, 1], [0, 1, 0, 1])
        self.assertEqual(result["accuracy"], 1.0)
        self.assertEqual(result["f1"], 1.0)
        self.assertEqual(result["macro_f1"], 1.0)

    def test_metrics_on_all_wrong_prediction(self) -> None:
        from baseline_router import metrics

        result = metrics([0, 1, 0, 1], [1, 0, 1, 0])
        self.assertEqual(result["accuracy"], 0.0)
        self.assertEqual(result["f1"], 0.0)

    def test_model_beats_majority_baseline_on_holdout(self) -> None:
        if not (SPLITS_DIR / "train.json").exists():
            self.skipTest("chưa sinh split; chạy python tools/make_splits.py")
        from baseline_router import load_split, train_linear

        train, dev = load_split("train"), load_split("dev")
        result, _, _ = train_linear(train, dev, epochs=150)
        self.assertGreater(result["accuracy"], 0.80,
                           "baseline tuyến tính phải vượt xa mức đoán bừa 0.50")


if __name__ == "__main__":
    unittest.main()
