# Author: Alexandre Gramfort <alexandre.gramfort@inria.fr>
#         Albert Thomas <albert.thomas@telecom-paristech.fr>
# License: BSD 3 clause

import time
import datetime
from csv import reader

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from pendulum import date

from sklearn import svm
from sklearn.datasets import make_moons, make_blobs
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.linear_model import SGDOneClassSVM
from sklearn.kernel_approximation import Nystroem
from sklearn.pipeline import make_pipeline

matplotlib.rcParams["contour.negative_linestyle"] = "solid"

ANSWER_TO_EVERYTHING = 42

# plt.xlim(-1500, 1500)

PLOT_EXPECTED_MIN_X = 1
PLOT_EXPECTED_MAX_X = 366

# plt.ylim(-50, 50)

PLOT_EXPECTED_MIN_Y = -100
PLOT_EXPECTED_MAX_Y = 650

# Example settings
n_samples = 300
outliers_fraction = 0.06
n_outliers = int(outliers_fraction * n_samples)
n_inliers = n_samples - n_outliers


def print_datasets():
    print(type(datasets))
    print(f"Rows in dataset list: {len(datasets)}")

    for idx, ds in enumerate(datasets):
        print(f"Dataset type: {type(ds)}")
        print(
            f"# INI # DS # {idx} --> Rows in DS # {len(ds)} --> {ds.shape} --> {ds[0]},{ds[1]}"
        )
        for jdx, elem in enumerate(ds):
            print(f"    Elem within dataset type: {type(elem)}")
            print(
                f"    Rows in Elem within dataset: {len(elem)} --> {elem.shape} --> {elem[0]},{elem[1]}"
            )
            print(f"    ## INI ## ELEM # {jdx} --> {elem}")

            for kdx, sube in enumerate(elem):
                print(f"          Subelem inside elem type: {type(sube)}")
                print(f"          ### INI ### SUBELEM # {kdx} --> {sube}")
            print(f"    ## END ## ELEM # {jdx}")
        print(f"# END # DS # {idx}")


def load_dataset(file_name):
    """
    Carga el archivo file_name y lo itera linea por linea sin cargarlo todo a memoria
    Genera una lista que tiene un array con los datos para luego alimentar a los algoritmos de
    deteccion de anomalias
    """
    outlier_list = []
    outlier_sub_list = []
    outlier_list.append(outlier_sub_list)

    # open file in read mode
    with open(file_name, "r", encoding="UTF-8") as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)
        header = next(csv_reader)
        # Iterate over each row in the csv using reader object

        if header is not None:
            print(f"Header was: {header}")
            # header = "AEP_CODE,FL_DATE,AVG_DELAY\n"
            AEP_CODE_IDX = 0
            FL_DATE_IDX = 1
            AVG_DELAY_IDX = 2

            for idx, row in enumerate(csv_reader):
                origin = row[AEP_CODE_IDX]
                fl_date_str = row[FL_DATE_IDX]
                dep_delay_str = row[AVG_DELAY_IDX]

                if dep_delay_str == "":
                    dep_delay = 0.0
                else:
                    dep_delay = float(row[AVG_DELAY_IDX])

                fl_date = datetime.datetime.strptime(fl_date_str, "%Y-%m-%d")
                day_of_year = (fl_date - datetime.datetime(fl_date.year, 1, 1)).days + 1

                # parse_fl_date = float(fl_date.replace("-", "")[4:])
                parse_fl_date = day_of_year
                parse_dep_delay = dep_delay

                parse_row = [parse_fl_date, parse_dep_delay]
                # row variable is a list that represents a row in csv

                nprow = np.array([parse_fl_date, parse_dep_delay])

                print(f"{row} --> {parse_row} --> {nprow}")

                out_sublist = outlier_list[0]
                out_sublist.append(nprow)

    result_list = []
    result_sub_array = np.array(out_sublist)
    result_list.append(result_sub_array)

    return result_list


print(">>> - Create anomaly algorithms")

# define outlier/anomaly detection methods to be compared.
# the SGDOneClassSVM must be used in a pipeline with a kernel approximation
# to give similar results to the OneClassSVM
anomaly_algorithms = [
    ("Robust covariance", EllipticEnvelope(contamination=outliers_fraction)),
    ("One-Class SVM", svm.OneClassSVM(nu=outliers_fraction, kernel="rbf", gamma=0.1)),
    (
        "One-Class SVM (SGD)",
        make_pipeline(
            Nystroem(gamma=0.1, random_state=ANSWER_TO_EVERYTHING, n_components=150),
            SGDOneClassSVM(
                nu=outliers_fraction,
                shuffle=True,
                fit_intercept=True,
                random_state=ANSWER_TO_EVERYTHING,
                tol=1e-6,
            ),
        ),
    ),
    (
        "Isolation Forest",
        IsolationForest(
            contamination=outliers_fraction, random_state=ANSWER_TO_EVERYTHING
        ),
    ),
    (
        "Local Outlier Factor",
        LocalOutlierFactor(n_neighbors=35, contamination=outliers_fraction),
    ),
]

print("END - Create anomaly algorithms")

print(">>> - Create datasets")

# Define datasets
blobs_params = dict(random_state=0, n_samples=n_inliers, n_features=2)
datasets = [
    make_blobs(centers=[[0, 0], [0, 0]], cluster_std=0.5, **blobs_params)[0],
    make_blobs(centers=[[2, 2], [-2, -2]], cluster_std=[0.5, 0.5], **blobs_params)[0],
    make_blobs(centers=[[2, 2], [-2, -2]], cluster_std=[1.5, 0.3], **blobs_params)[0],
    4.0
    * (
        make_moons(n_samples=n_samples, noise=0.05, random_state=0)[0]
        - np.array([0.5, 0.25])
    ),
    14.0 * (np.random.RandomState(ANSWER_TO_EVERYTHING).rand(n_samples, 2) - 0.5),
]

datasets = load_dataset("./data/avg_2007.csv")

print("END - Create datasets")

print("START - Print datasets")
print_datasets()
print("END - Print datasets")

print(">>> - Compare algorithms")

# Compare given classifiers under given settings
xx1, yy1 = np.meshgrid(np.linspace(-7, 7, 150), np.linspace(-7, 7, 150))
# xx1, yy1 = np.meshgrid(np.linspace(-1500, 1500, 150), np.linspace(-50, 50, 150))

print("END - Compare algorithms")

print(">>> - Create plot structure")

plt.figure(figsize=(len(anomaly_algorithms) * 2 + 4, 12.5))
plt.subplots_adjust(
    left=0.02, right=0.98, bottom=0.001, top=0.96, wspace=0.05, hspace=0.01
)

plot_num = 1
rng = np.random.RandomState(ANSWER_TO_EVERYTHING)

print("END - Create plot structure")


def main(n_outliers, anomaly_algorithms, datasets, xx_param, yy_param, plot_num, rng):
    print(">>> - Run each algorithm in each dataset")

    for i_dataset, X in enumerate(datasets):
        # Add outliers
        print(f"    >>> - Start Running Dataset # {i_dataset} with size: {len(X)}")

        # X = np.concatenate(
        #    [X, rng.uniform(low=-6, high=6, size=(n_outliers, 2))], axis=0
        # )

        # X = np.concatenate(
        #    [X, rng.uniform(low=-6, high=6, size=(n_outliers, 2))], axis=0
        # )
        print(f"    >>> - Dataset size incluiding outliers: {len(X)}")

        for name, algorithm in anomaly_algorithms:
            t0 = time.time()
            algorithm.fit(X)
            t1 = time.time()
            plt.subplot(len(datasets), len(anomaly_algorithms), plot_num)
            if i_dataset == 0:
                plt.title(name, size=18)

            print(f"        >>> - Run algorithm {name}")

            # fit the data and tag outliers
            if name == "Local Outlier Factor":
                y_pred = algorithm.fit_predict(X)
                print(f"INPUT : {X}")
                print(f"OUTPUT: {y_pred}")
            else:
                y_pred = algorithm.fit(X).predict(X)
                print(f"INPUT : {X}")
                print(f"OUTPUT: {y_pred}")

            print(f"        >>> - Plot algorithm {name}")

            # plot the levels lines and the points
            if name != "Local Outlier Factor":  # LOF does not implement predict
                print(f"        >>> - Draw contour")
                ravel_xx = xx_param.ravel()
                ravel_yy = yy_param.ravel()
                point_xy = np.c_[ravel_xx, ravel_yy]
                print(f"CTR PARAM X # : {len(xx_param)} --> {xx_param.shape}")
                print(f"CTR PARAM X: {xx_param}")
                print(f"CTR PARAM Y # : {len(yy_param)} --> {yy_param.shape}")
                print(f"CTR PARAM Y: {yy_param}")
                print(f"CTR RAVEL X #: {len(ravel_xx)} --> {ravel_xx.shape}")
                print(f"CTR RAVEL X: {ravel_xx}")
                print(f"CTR RAVEL Y #: {len(ravel_yy)} --> {ravel_yy.shape}")
                print(f"CTR RAVEL Y: {ravel_yy}")
                print(f"CTR INPUT XY #: {len(point_xy)} --> {point_xy.shape}")
                print(f"CTR INPUT XY: {point_xy}")

                Z = algorithm.predict(point_xy)
                print(f"RAW PREDICTION Z # {len(Z)} --> {Z.shape}")
                print(f"RAW OUTPUT Z: {Z}")
                Z = Z.reshape(xx_param.shape)
                print(f"RESHAPE PREDICTION Z # {len(Z)} --> {Z.shape}")
                print(f"CTR FINAL OUTPUT Z: {Z}")
                plt.contour(
                    xx_param, yy_param, Z, levels=[0], linewidths=2, colors="black"
                )

            cerulean = "#377eb8"  # outliers
            orange = "#ff7f00"  # inliers

            colors = np.array([cerulean, orange])
            scatter_x0_in = X[:, 0]
            scatter_x1_in = X[:, 1]

            print(f"INPUT SCATTER X0: {scatter_x0_in}")
            print(f"INPUT SCATTER X1: {scatter_x1_in}")

            plt.scatter(
                scatter_x0_in, scatter_x1_in, s=10, color=colors[(y_pred + 1) // 2]
            )

            plt.xlim(PLOT_EXPECTED_MIN_X, PLOT_EXPECTED_MAX_X)
            plt.ylim(PLOT_EXPECTED_MIN_Y, PLOT_EXPECTED_MAX_Y)

            # plt.xticks(())
            # plt.yticks(())

            # plt.xticks(())
            # plt.yticks(())

            plt.text(
                0.99,
                0.01,
                ("%.2fs" % (t1 - t0)).lstrip("0"),
                transform=plt.gca().transAxes,
                size=15,
                horizontalalignment="right",
            )
            print(f"        END - Plot algorithm {name}")
            print(f"        END - Run algorithm {name}")
            print(f"    END - Run dataset # {i_dataset}")
            plot_num += 1

    print("END - Run each algorithm in each dataset")

    print(">>> - Save plot to PNG")

    # plt.show()
    plt.savefig("./data/example.png")

    print("END - Save plot to PNG")


main(n_outliers, anomaly_algorithms, datasets, xx1, yy1, plot_num, rng)


# generate_outlier_dataset("./data/avg_2007.csv")
