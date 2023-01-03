# This script is based on scikit-learn's tutorial: Clustering text documents using k-means
# Ref: https://scikit-learn.org/stable/auto_examples/text/plot_document_clustering.html
import argparse
import os
import pickle
import sys
from collections import defaultdict
from pathlib import Path
from time import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import HashingVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.utils import Bunch

# import ipdb

evaluations = []
evaluations_std = []


class RandomModel:

    def __init__(self, n_clusters):
        self.random_state = 12345
        self.labels_ = None
        self.n_clusters = n_clusters

    def fit(self, X):
        self.labels_ = np.random.randint(0, self.n_clusters, X.shape[0])

    def set_params(self, random_state):
        self.random_state = random_state


# Ref: https://scikit-learn.org/stable/auto_examples/text/plot_document_clustering.html
def fit_and_evaluate(km, X, name=None, n_runs=5):
    name = km.__class__.__name__ if name is None else name

    train_times = []
    scores = defaultdict(list)
    for seed in range(n_runs):
        km.set_params(random_state=seed)
        t0 = time()
        km.fit(X)
        train_times.append(time() - t0)
        scores["Homogeneity"].append(metrics.homogeneity_score(labels, km.labels_))
        scores["Completeness"].append(metrics.completeness_score(labels, km.labels_))
        scores["V-measure"].append(metrics.v_measure_score(labels, km.labels_))
        scores["Adjusted Rand-Index"].append(
            metrics.adjusted_rand_score(labels, km.labels_)
        )
        scores["Silhouette Coefficient"].append(
            metrics.silhouette_score(X, km.labels_, sample_size=2000)
        )
    train_times = np.asarray(train_times)

    print(f"clustering done in {train_times.mean():.2f} ± {train_times.std():.2f} s ")
    evaluation = {
        "estimator": name,
        "train_time": train_times.mean(),
    }
    evaluation_std = {
        "estimator": name,
        "train_time": train_times.std(),
    }
    for score_name, score_values in scores.items():
        mean_score, std_score = np.mean(score_values), np.std(score_values)
        print(f"{score_name}: {mean_score:.3f} ± {std_score:.3f}")
        evaluation[score_name] = mean_score
        evaluation_std[score_name] = std_score
    evaluations.append(evaluation)
    evaluations_std.append(evaluation_std)


def dump_pickle(filepath, data):
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)


def load_pickle(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except OSError as e:
        raise


def shuffle_dataset(dataset):
    idx = np.random.permutation(range(len(dataset.target)))
    for k, v in dataset.items():
        if isinstance(v, list):
            dataset[k] = list(np.array(v)[idx])
        elif isinstance(v, np.ndarray):
            dataset[k] = v[idx]


def generate_dataset(input_directory, dataset_type):
    dataset = Bunch(
        data=[],
        filenames=[],
        target_names=[],
        target=[],
        DESCR=''
    )

    labels = sorted([item.name for item in input_directory.iterdir() if item.is_dir()])
    target_name_to_value = dict(zip(labels, [i for i in range(len(labels))]))

    for i, filepath in enumerate(input_directory.rglob('*.html'), start=1):
        print(f'Processing document {i}: {filepath.name}\n')
        raw_text = read_file(filepath)
        text = BeautifulSoup(raw_text, 'html.parser').get_text().replace('\xa0', ' ')
        dataset.data.append(text)
        dataset.filenames.append(filepath)
        target_name = filepath.parent.name
        dataset.target_names.append(target_name)
        dataset.target.append(target_name_to_value[target_name])
    dataset.target = np.asarray(dataset.target)
    return dataset


def setup_argparser():
    msg = 'Cluster text documents (HTML pages or ebooks).'
    parser = argparse.ArgumentParser(
        description='',
        usage=f"python %(prog)s [OPTIONS]\n\n{msg}",
        # ArgumentDefaultsHelpFormatter
        # HelpFormatter
        # RawDescriptionHelpFormatter
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'input_directory', default=None, nargs=1,
        help="Path to the main directory containing the documents to cluster.")
    parser.add_argument(
        '-e', '--ebooks', action='store_true',
        help='Whether to cluster ebooks (pdf, djvu, epub).')
    return parser


if __name__ == '__main__':
    parser = setup_argparser()
    args = parser.parse_args()
    input_directory = Path(args.input_directory[0])
    SEED = 12345
    np.random.seed(SEED)
    dataset_path = input_directory.joinpath('dataset.pkl')

    try:
        print("Loading text dataset ...")
        dataset = load_pickle(dataset_path)
    except OSError:
        print(f"[ERROR] Dataset not found: {dataset_path}")
        print("Generating dataset ...")
        dataset = generate_dataset(input_directory, dataset_type=args.ebooks)
        print(f"Saving dataset: {dataset_path}")
        dump_pickle(input_directory.joinpath('dataset.pkl'), dataset)

    """
    for filename in dataset.filenames:
        title = filename.name.split(' - ')[0]
        title_url = title.replace(' ', '_').replace("'", '%27')
        print(f"- `{title} <https://en.wikipedia.org/wiki/{title_url}>`_")
    """

    shuffle_dataset(dataset)
    labels = dataset.target
    unique_labels, category_sizes = np.unique(labels, return_counts=True)
    true_k = unique_labels.shape[0]
    print(f"{len(dataset.data)} documents - {true_k} categories")

    # Feature Extraction using TfidfVectorizer
    print("\nFeature Extraction using TfidfVectorizer")
    vectorizer = TfidfVectorizer(
        max_df=0.5,
        min_df=5,
        stop_words="english",
    )
    t0 = time()
    X_tfidf = vectorizer.fit_transform(dataset.data)

    print(f"vectorization done in {time() - t0:.3f} s")
    print(f"n_samples: {X_tfidf.shape[0]}, n_features: {X_tfidf.shape[1]}")
    print(f"Sparsity: {X_tfidf.nnz / np.prod(X_tfidf.shape):.3f}")

    # Clustering sparse data with random model
    print("\nClustering sparse data with RandomModel")
    random_model = RandomModel(true_k)
    fit_and_evaluate(random_model, X_tfidf, name="RandomModel\non tf-idf vectors")

    # Clustering sparse data with k-means
    print("\nClustering sparse data with k-means")
    kmeans = KMeans(
        n_clusters=true_k,
        max_iter=100,
        n_init=5,
    )
    fit_and_evaluate(kmeans, X_tfidf, name="KMeans\non tf-idf vectors")

    # Performing dimensionality reduction using LSA
    print("\nPerforming dimensionality reduction using LSA")
    lsa = make_pipeline(TruncatedSVD(n_components=100), Normalizer(copy=False))
    t0 = time()
    X_lsa = lsa.fit_transform(X_tfidf)
    explained_variance = lsa[0].explained_variance_ratio_.sum()

    print(f"LSA done in {time() - t0:.3f} s")
    print(f"Explained variance of the SVD step: {explained_variance * 100:.1f}%")

    print("\nRandomModel with LSA on tf-idf vectors")
    fit_and_evaluate(random_model, X_lsa, name="RandomModel\nwith LSA on tf-idf vectors")

    print("\nKMeans with LSA on tf-idf vectors")
    kmeans = KMeans(
        n_clusters=true_k,
        max_iter=100,
        n_init=1,
    )
    fit_and_evaluate(kmeans, X_lsa, name="KMeans\nwith LSA on tf-idf vectors")

    print("\nMiniBatchKMeans with LSA on tf-idf vectors")
    minibatch_kmeans = MiniBatchKMeans(
        n_clusters=true_k,
        n_init=1,
        init_size=1000,
        batch_size=1000,
    )
    fit_and_evaluate(
        minibatch_kmeans,
        X_lsa,
        name="MiniBatchKMeans\nwith LSA on tf-idf vectors",
    )

    print("\nTop terms per cluster")
    original_space_centroids = lsa[0].inverse_transform(kmeans.cluster_centers_)
    order_centroids = original_space_centroids.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()

    for i in range(true_k):
        print(f"Cluster {i}: ", end="")
        for ind in order_centroids[i, :10]:
            print(f"{terms[ind]} ", end="")
        print()

    # HashingVectorizer
    print("\nHashingVectorizer")
    lsa_vectorizer = make_pipeline(
        HashingVectorizer(stop_words="english", n_features=50_000),
        TfidfTransformer(),
        TruncatedSVD(n_components=100, random_state=0),
        Normalizer(copy=False),
    )

    t0 = time()
    X_hashed_lsa = lsa_vectorizer.fit_transform(dataset.data)
    print(f"vectorization done in {time() - t0:.3f} s")

    print("\nRandomModel with LSA on hashed vectors")
    fit_and_evaluate(random_model, X_hashed_lsa, name="RandomModel\nwith LSA on hashed vectors")

    print("\nKMeans with LSA on hashed vectors")
    fit_and_evaluate(kmeans, X_hashed_lsa, name="KMeans\nwith LSA on hashed vectors")

    print("\nMiniBatchKMeans with LSA on hashed vectors")
    fit_and_evaluate(
        minibatch_kmeans,
        X_hashed_lsa,
        name="MiniBatchKMeans\nwith LSA on hashed vectors",
    )

    # Clustering evaluation summary
    print("\nClustering evaluation summary")
    fig, (ax0, ax1) = plt.subplots(ncols=2, figsize=(16, 6), sharey=True)

    df = pd.DataFrame(evaluations[::-1]).set_index("estimator")
    df_std = pd.DataFrame(evaluations_std[::-1]).set_index("estimator")

    df.drop(
        ["train_time"],
        axis="columns",
    ).plot.barh(ax=ax0, xerr=df_std)
    ax0.set_xlabel("Clustering scores")
    ax0.set_ylabel("")

    df["train_time"].plot.barh(ax=ax1, xerr=df_std["train_time"])
    ax1.set_xlabel("Clustering time (s)")
    plt.tight_layout()

    plt.show()

# ipdb.set_trace()
