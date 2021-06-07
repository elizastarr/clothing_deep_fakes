resleeve
==============================

Assignment for Resleeve

The Assignment
------------
- Work with data (wrangling, pre-processing)
    - Read some images and display them
    - Have some code for the pre-processing pipeline
- Modeling (Pytorch/Tensorflow)
    - Load a pre-trained network and have some code to make predictions
    - Select a metric and evaluate the pre-trained network on the test dataset
    - Train your own network (from scratch or using the pre-trained network) on the training dataset
    - Evaluate your network on the test dataset
- Bonus: build an API
- Couple of slides explaining
    - What did you do?
    - How you would deploy your model in production?


Execution
------------
- **cp_dataset.py: display()** Read some images and display them
- **src/data/make_dataset.py** Have some code for the pre-processing pipeline

- **models/cp-vton-plus** Load a pre-trained network  
- **src/models/predict_model.py** have some code to make predictions
- **notebooks/reports/0.1/ers/evaluate.ipynb** Select a metric and evaluate the pre-trained network on the test dataset
- Train your own network (from scratch or using the pre-trained network) on the training dataset
- Evaluate your network on the test dataset


Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
