"""Baseline định tuyến truy vấn (factual = 0 / analytical = 1).

Mục tiêu là cung cấp mốc so sánh rẻ và tái lập được cho tầng định tuyến của
kiến trúc DRA: nếu một mô hình tuyến tính trên TF-IDF đã đạt độ chính xác cao,
thì phần định tuyến không cần gọi LLM lớn -- đúng tinh thần của DRA.

Toàn bộ mô hình được cài bằng thư viện chuẩn (không cần numpy/scikit-learn) để
kết quả trong bài báo có thể lặp lại trên máy trống.

Ba chế độ đánh giá:

* `holdout` -- huấn luyện trên `datasets/splits/train.json`, đánh giá trên
  `test.json` (hoặc `dev.json` với `--eval-split dev`).
* `cv`      -- k-fold phân tầng trên toàn bộ dữ liệu.
* `lodo`    -- leave-one-domain-out: huấn luyện trên hai miền, đánh giá trên
  miền còn lại. Đây là phép đo khả năng khái quát hoá liên miền của router.

Chạy: `python tools/baseline_router.py`
      `python tools/baseline_router.py --report`   -> ghi docs/baseline_results.md
      `python tools/baseline_router.py --predict "How does X compare to Y?"`
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dra_utils import (  # noqa: E402
    DOCS_DIR,
    SPLITS_DIR,
    load_all,
    markdown_table,
    setup_stdout,
    tokenize,
    write_text,
)

REPORT_PATH = DOCS_DIR / "baseline_results.md"

Sparse = Dict[int, float]

#: Từ khoá gợi ý truy vấn cần suy luận nhiều bước, dùng cho baseline luật.
ANALYTICAL_CUES = (
    "compare", "contrast", "differ", "difference", "similar", "relate",
    "why", "how", "explain", "analyze", "evaluate", "assess", "discuss",
    "implication", "consequence", "impact", "trade", "versus", "vs",
    "connect", "synthesize", "interact", "influence", "affect", "role",
)


# --------------------------------------------------------------------------
# Đặc trưng
# --------------------------------------------------------------------------

class TfidfVectorizer:
    """TF-IDF n-gram tối giản, chỉ dùng dict và math."""

    def __init__(self, ngram_max: int = 2, min_df: int = 2) -> None:
        self.ngram_max = ngram_max
        self.min_df = min_df
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[int, float] = {}

    def _features(self, text: str) -> Counter:
        tokens = tokenize(text)
        counts: Counter = Counter()
        for n in range(1, self.ngram_max + 1):
            for i in range(len(tokens) - n + 1):
                counts[" ".join(tokens[i:i + n])] += 1
        # Đặc trưng độ dài rời rạc hoá: router dựa nhiều vào độ dài truy vấn.
        counts[f"__len_bucket_{min(len(tokens) // 8, 6)}"] += 1
        counts[f"__q_marks_{min(text.count('?'), 3)}"] += 1
        return counts

    def fit(self, texts: Sequence[str]) -> "TfidfVectorizer":
        document_frequency: Counter = Counter()
        for text in texts:
            document_frequency.update(self._features(text).keys())

        kept = sorted(term for term, df in document_frequency.items() if df >= self.min_df)
        self.vocabulary = {term: index for index, term in enumerate(kept)}

        n_docs = len(texts)
        self.idf = {
            self.vocabulary[term]: math.log((1 + n_docs) / (1 + document_frequency[term])) + 1.0
            for term in kept
        }
        return self

    def transform(self, text: str) -> Sparse:
        vector: Sparse = {}
        for term, count in self._features(text).items():
            index = self.vocabulary.get(term)
            if index is None:
                continue
            vector[index] = (1.0 + math.log(count)) * self.idf[index]

        norm = math.sqrt(sum(value * value for value in vector.values()))
        if norm > 0:
            for index in vector:
                vector[index] /= norm
        return vector

    def transform_all(self, texts: Iterable[str]) -> List[Sparse]:
        return [self.transform(text) for text in texts]


# --------------------------------------------------------------------------
# Mô hình
# --------------------------------------------------------------------------

class LogisticRegression:
    """Hồi quy logistic huấn luyện bằng gradient descent toàn batch + L2.

    Toàn batch (thay vì SGD) để kết quả hoàn toàn tất định, không phụ thuộc thứ
    tự duyệt mẫu.
    """

    def __init__(self, n_features: int, learning_rate: float = 2.0,
                 epochs: int = 400, l2: float = 1e-4) -> None:
        self.weights = [0.0] * n_features
        self.bias = 0.0
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.l2 = l2

    def decision(self, vector: Sparse) -> float:
        return self.bias + sum(value * self.weights[index] for index, value in vector.items())

    def predict_proba(self, vector: Sparse) -> float:
        score = self.decision(vector)
        if score >= 0:
            return 1.0 / (1.0 + math.exp(-score))
        exponent = math.exp(score)
        return exponent / (1.0 + exponent)

    def fit(self, vectors: Sequence[Sparse], labels: Sequence[int]) -> "LogisticRegression":
        n = len(vectors)
        if n == 0:
            return self

        for _ in range(self.epochs):
            gradient: Dict[int, float] = defaultdict(float)
            bias_gradient = 0.0
            for vector, label in zip(vectors, labels):
                error = self.predict_proba(vector) - label
                bias_gradient += error
                for index, value in vector.items():
                    gradient[index] += error * value

            step = self.learning_rate / n
            self.bias -= step * bias_gradient
            for index, value in gradient.items():
                self.weights[index] -= step * value + self.learning_rate * self.l2 * self.weights[index]
        return self

    def predict(self, vector: Sparse, threshold: float = 0.5) -> int:
        return int(self.predict_proba(vector) >= threshold)


class LengthBaseline:
    """Luật một biến: truy vấn dài hơn ngưỡng thì coi là analytical."""

    def __init__(self) -> None:
        self.threshold = 0

    def fit(self, texts: Sequence[str], labels: Sequence[int]) -> "LengthBaseline":
        lengths = [len(tokenize(text)) for text in texts]
        best_accuracy, best_threshold = -1.0, 0
        for threshold in range(min(lengths), max(lengths) + 1):
            correct = sum(1 for length, label in zip(lengths, labels)
                          if int(length >= threshold) == label)
            accuracy = correct / len(labels)
            if accuracy > best_accuracy:
                best_accuracy, best_threshold = accuracy, threshold
        self.threshold = best_threshold
        return self

    def predict(self, text: str) -> int:
        return int(len(tokenize(text)) >= self.threshold)


class KeywordBaseline:
    """Luật từ khoá cố định, không cần huấn luyện."""

    def predict(self, text: str) -> int:
        tokens = set(tokenize(text))
        return int(bool(tokens & set(ANALYTICAL_CUES)))


# --------------------------------------------------------------------------
# Đo lường
# --------------------------------------------------------------------------

def metrics(y_true: Sequence[int], y_pred: Sequence[int]) -> Dict[str, float]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)

    def f1_for(precision: float, recall: float) -> float:
        return 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    precision1 = tp / (tp + fp) if tp + fp else 0.0
    recall1 = tp / (tp + fn) if tp + fn else 0.0
    precision0 = tn / (tn + fn) if tn + fn else 0.0
    recall0 = tn / (tn + fp) if tn + fp else 0.0

    return {
        "accuracy": (tp + tn) / len(y_true) if y_true else 0.0,
        "precision": precision1,
        "recall": recall1,
        "f1": f1_for(precision1, recall1),
        "macro_f1": (f1_for(precision1, recall1) + f1_for(precision0, recall0)) / 2,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
    }


def train_linear(train: Sequence[Dict[str, object]], test: Sequence[Dict[str, object]],
                 epochs: int) -> Tuple[Dict[str, float], TfidfVectorizer, LogisticRegression]:
    vectorizer = TfidfVectorizer().fit([str(record["query"]) for record in train])
    x_train = vectorizer.transform_all(str(record["query"]) for record in train)
    y_train = [int(record["label"]) for record in train]

    model = LogisticRegression(len(vectorizer.vocabulary), epochs=epochs).fit(x_train, y_train)

    y_true = [int(record["label"]) for record in test]
    y_pred = [model.predict(vectorizer.transform(str(record["query"]))) for record in test]
    return metrics(y_true, y_pred), vectorizer, model


def evaluate_rules(train: Sequence[Dict[str, object]],
                   test: Sequence[Dict[str, object]]) -> Dict[str, Dict[str, float]]:
    y_true = [int(record["label"]) for record in test]
    texts = [str(record["query"]) for record in test]

    length = LengthBaseline().fit([str(record["query"]) for record in train],
                                  [int(record["label"]) for record in train])
    keyword = KeywordBaseline()
    majority = Counter(int(record["label"]) for record in train).most_common(1)[0][0]

    return {
        "majority": metrics(y_true, [majority] * len(y_true)),
        "keyword": metrics(y_true, [keyword.predict(text) for text in texts]),
        f"length>={length.threshold}": metrics(y_true, [length.predict(text) for text in texts]),
    }


def stratified_folds(records: Sequence[Dict[str, object]], k: int,
                     seed: int) -> List[List[Dict[str, object]]]:
    folds: List[List[Dict[str, object]]] = [[] for _ in range(k)]
    strata: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for record in records:
        strata[f"{record['domain']}|{record['label']}"].append(record)

    for key in sorted(strata):
        bucket = sorted(strata[key], key=lambda record: str(record["id"]))
        random.Random(f"{seed}:{key}").shuffle(bucket)
        for index, record in enumerate(bucket):
            folds[index % k].append(record)
    return folds


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def stdev(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    average = mean(values)
    return math.sqrt(sum((value - average) ** 2 for value in values) / (len(values) - 1))


# --------------------------------------------------------------------------
# Chế độ chạy
# --------------------------------------------------------------------------

def load_split(name: str) -> List[Dict[str, object]]:
    path = SPLITS_DIR / f"{name}.json"
    if not path.exists():
        raise SystemExit(f"Thiếu {path}. Chạy trước: python tools/make_splits.py")
    return json.loads(path.read_text(encoding="utf-8"))


def run_holdout(eval_split: str, epochs: int) -> Dict[str, Dict[str, float]]:
    train, test = load_split("train"), load_split(eval_split)
    results = evaluate_rules(train, test)
    results["tfidf+logreg"], _, _ = train_linear(train, test, epochs)
    return results


def run_cv(k: int, seed: int, epochs: int) -> Tuple[Dict[str, float], List[Dict[str, float]]]:
    records = load_all()
    folds = stratified_folds(records, k, seed)

    per_fold = []
    for index in range(k):
        test = folds[index]
        train = [record for j, fold in enumerate(folds) if j != index for record in fold]
        fold_metrics, _, _ = train_linear(train, test, epochs)
        per_fold.append(fold_metrics)

    summary = {
        key: mean([fold[key] for fold in per_fold])
        for key in ("accuracy", "precision", "recall", "f1", "macro_f1")
    }
    summary["accuracy_std"] = stdev([fold["accuracy"] for fold in per_fold])
    return summary, per_fold


def run_lodo(epochs: int) -> Dict[str, Dict[str, float]]:
    records = load_all()
    domains = sorted({str(record["domain"]) for record in records})

    results = {}
    for domain in domains:
        test = [record for record in records if record["domain"] == domain]
        train = [record for record in records if record["domain"] != domain]
        results[domain], _, _ = train_linear(train, test, epochs)
    return results


def top_features(vectorizer: TfidfVectorizer, model: LogisticRegression,
                 top_n: int = 10) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]]]:
    pairs = [(term, model.weights[index]) for term, index in vectorizer.vocabulary.items()]
    pairs.sort(key=lambda item: (-item[1], item[0]))
    positives = pairs[:top_n]
    pairs.sort(key=lambda item: (item[1], item[0]))
    return positives, pairs[:top_n]


def format_metrics_table(results: Dict[str, Dict[str, float]], first_column: str) -> str:
    rows = []
    for name in sorted(results, key=lambda key: -results[key]["accuracy"]):
        m = results[name]
        rows.append((name, f"{m['accuracy']:.3f}", f"{m['precision']:.3f}",
                     f"{m['recall']:.3f}", f"{m['f1']:.3f}", f"{m['macro_f1']:.3f}",
                     f"{m['tp']}/{m['fp']}/{m['fn']}/{m['tn']}"))
    return markdown_table(
        [first_column, "Accuracy", "Precision", "Recall", "F1", "Macro-F1", "TP/FP/FN/TN"],
        rows,
        ["left", "right", "right", "right", "right", "right", "center"],
    )


def build_report(epochs: int, folds: int, seed: int) -> str:
    holdout = run_holdout("test", epochs)
    cv_summary, cv_folds = run_cv(folds, seed, epochs)
    lodo = run_lodo(epochs)

    train = load_split("train")
    _, vectorizer, model = train_linear(train, load_split("test"), epochs)
    positives, negatives = top_features(vectorizer, model)

    lines = [
        "# Kết quả baseline định tuyến",
        "",
        "File này được sinh tự động bởi `python tools/baseline_router.py --report`.",
        "Mô hình chỉ dùng thư viện chuẩn Python nên số liệu lặp lại được trên máy trống.",
        "",
        "Nhiệm vụ: dự đoán nhãn định tuyến của truy vấn (0 = factual, 1 = analytical).",
        f"Cấu hình: TF-IDF 1-2 gram, min_df=2, hồi quy logistic (GD toàn batch, {epochs} epoch, L2=1e-4).",
        "",
        "## 1. Hold-out (train -> test)",
        "",
        "Huấn luyện trên `datasets/splits/train.json`, đánh giá trên `datasets/splits/test.json`.",
        "",
        format_metrics_table(holdout, "Mô hình"),
        "",
        f"## 2. Kiểm định chéo {folds}-fold phân tầng (toàn bộ {len(load_all())} truy vấn)",
        "",
        markdown_table(
            ["Chỉ số", "Trung bình"],
            [("Accuracy", f"{cv_summary['accuracy']:.3f} ± {cv_summary['accuracy_std']:.3f}"),
             ("Precision (nhãn 1)", f"{cv_summary['precision']:.3f}"),
             ("Recall (nhãn 1)", f"{cv_summary['recall']:.3f}"),
             ("F1 (nhãn 1)", f"{cv_summary['f1']:.3f}"),
             ("Macro-F1", f"{cv_summary['macro_f1']:.3f}")],
            ["left", "right"],
        ),
        "",
        "Accuracy từng fold: " + ", ".join(f"{fold['accuracy']:.3f}" for fold in cv_folds) + ".",
        "",
        "## 3. Leave-one-domain-out",
        "",
        "Huấn luyện trên hai miền, đánh giá trên miền chưa từng thấy. Đây là phép đo",
        "khả năng khái quát hoá liên miền của tầng định tuyến.",
        "",
        format_metrics_table(lodo, "Miền dùng để test"),
        "",
        "## 4. Đặc trưng có trọng số lớn nhất",
        "",
        "Trọng số dương đẩy truy vấn về nhãn 1 (analytical), trọng số âm về nhãn 0 (factual).",
        "",
        markdown_table(
            ["Đẩy về nhãn 1", "Trọng số", "Đẩy về nhãn 0", "Trọng số"],
            [("`" + positives[i][0] + "`", f"{positives[i][1]:+.3f}",
              "`" + negatives[i][0] + "`", f"{negatives[i][1]:+.3f}")
             for i in range(min(len(positives), len(negatives)))],
            ["left", "right", "left", "right"],
        ),
        "",
        "## Diễn giải",
        "",
        "- Baseline luật (`majority`, `keyword`, `length`) cho biết mức sàn: phần nào của",
        "  nhiệm vụ giải được chỉ bằng heuristic không cần học.",
        "- Khoảng cách giữa hold-out và leave-one-domain-out cho biết router học đặc trưng",
        "  cấu trúc câu hỏi (khái quát được) hay chỉ học từ vựng riêng của từng miền.",
        "- Mọi kết quả cao hơn ở đây đều nên được so với chi phí: baseline này chạy dưới",
        "  một mili-giây cho mỗi truy vấn và không cần gọi API.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    setup_stdout()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=("holdout", "cv", "lodo", "all"), default="all")
    parser.add_argument("--eval-split", choices=("dev", "test"), default="test")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260819)
    parser.add_argument("--epochs", type=int, default=400)
    parser.add_argument("--report", action="store_true", help="ghi docs/baseline_results.md")
    parser.add_argument("--predict", metavar="QUERY",
                        help="huấn luyện trên train.json rồi dự đoán một truy vấn")
    args = parser.parse_args()

    if args.predict:
        train = load_split("train")
        _, vectorizer, model = train_linear(train, train[:1], args.epochs)
        probability = model.predict_proba(vectorizer.transform(args.predict))
        label = int(probability >= 0.5)
        print(f"Truy vấn : {args.predict}")
        print(f"P(nhãn 1): {probability:.3f}")
        print(f"Định tuyến: nhãn {label} "
              f"({'analytical -> nhánh suy luận sâu' if label else 'factual -> nhánh tra cứu nhanh'})")
        return 0

    if args.report:
        write_text(REPORT_PATH, build_report(args.epochs, args.folds, args.seed))
        print(f"Đã ghi {REPORT_PATH}")
        return 0

    if args.mode in ("holdout", "all"):
        print(f"== Hold-out (train -> {args.eval_split}) ==")
        print(format_metrics_table(run_holdout(args.eval_split, args.epochs), "Mô hình"))
        print()

    if args.mode in ("cv", "all"):
        summary, per_fold = run_cv(args.folds, args.seed, args.epochs)
        print(f"== Kiểm định chéo {args.folds}-fold ==")
        print(f"Accuracy {summary['accuracy']:.3f} ± {summary['accuracy_std']:.3f}, "
              f"Macro-F1 {summary['macro_f1']:.3f}")
        print("Từng fold: " + ", ".join(f"{fold['accuracy']:.3f}" for fold in per_fold))
        print()

    if args.mode in ("lodo", "all"):
        print("== Leave-one-domain-out ==")
        print(format_metrics_table(run_lodo(args.epochs), "Miền dùng để test"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
