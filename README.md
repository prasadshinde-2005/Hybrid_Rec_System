# 🎵 Spotify Hybrid Recommendation System

An end-to-end music recommendation system that combines **Content-Based Filtering** and **Collaborative Filtering** using a weighted hybrid approach to deliver personalised song recommendations.

The project uses song metadata and user listening history to recommend tracks based on both song similarity and user listening behaviour. It also follows MLOps practices to make the workflow reproducible, track experiments, and support automated testing and containerisation.

## 🚀 Project Overview

Music recommendation systems often rely on either song characteristics or user behaviour. This project combines both approaches to provide more relevant recommendations.

It uses two datasets:

- **Songs Dataset (`songs_data`)** – Contains song-related information and metadata.
- **User Listening History Dataset (`user_listening_history_data`)** – Contains user-song interaction and listening history.

The recommendations from both models are combined using a weighted approach.

## 🧠 Recommendation Approaches

### 1. Content-Based Filtering

Recommends songs similar to a selected track based on its available features and metadata.

- Processes song features.
- Uses feature representation and similarity calculations.
- Recommends tracks with similar characteristics.

### 2. Collaborative Filtering

Recommends songs based on user listening patterns and interactions.

- Builds a user-item interaction matrix.
- Identifies similarities between listening patterns.
- Recommends songs based on collaborative behaviour.

### 3. Hybrid Recommendation System

Combines the scores from both recommendation approaches using a weighted strategy.

**Hybrid Score = (α × Content-Based Score) + (β × Collaborative Score)**

Here, α and β represent the weights assigned to each recommendation approach.

This helps balance song similarity with user listening behaviour.

## ⚙️ MLOps Implementation

This project follows an end-to-end MLOps workflow using:

| Tool | Purpose |
|---|---|
| Python | Core development |
| Pandas, NumPy | Data processing |
| Scikit-learn | Feature processing and similarity calculations |
| DVC | Data and pipeline versioning |
| MLflow | Experiment tracking and model management |
| Git & GitHub | Version control and collaboration |
| GitHub Actions | CI automation |
| Docker | Application containerisation |

## 🔄 Project Workflow

1. Load song metadata and user listening history.
2. Perform data cleaning and preprocessing.
3. Build the content-based recommendation component.
4. Build the collaborative filtering component.
5. Combine both recommendation scores using a weighted approach.
6. Generate personalised song recommendations.
7. Track experiments using MLflow.
8. Manage data and pipeline stages using DVC.
9. Automate checks using GitHub Actions.
10. Containerise the application using Docker.

## 📁 Project Structure

```text
Hybrid-Rec-System/
│
├── data/
│   ├── Songs_data.csv
│   ├── User_Listening_History.csv
│   └── processed_data/
│
├── notebooks/
│
├── src/
│   ├── data_cleaning.py
│   ├── content_based_filtering.py
│   ├── collaborative_filtering.py
│   └── hybrid_recommender.py
│
├── models/
│
├── tests/
│
├── .github/
│   └── workflows/
│
├── dvc.yaml
├── dvc.lock
├── Dockerfile
├── requirements.txt
└── README.md
```

*Note: Adjust the folder and file names above to match your actual repository.*

## 🛠️ Installation and Setup

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Hybrid-Rec-System
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the DVC Pipeline

```bash
dvc repro
```

### 5. Run the Application

Add your actual application entry-point command here once finalised.

## 🐳 Docker

The project uses Docker to package the application and its dependencies into a container, helping maintain a consistent execution environment.

Build the Docker image:

```bash
docker build -t hybrid-recommender .
```

Run the container:

```bash
docker run hybrid-recommender
```

## 🔮 Future Improvements

- Add real-time user feedback to improve recommendations.
- Experiment with different hybrid weighting strategies.
- Improve recommendation diversity and personalisation.
- Deploy the application using a cloud platform.
- Add monitoring for recommendation quality and system performance.

## 👨‍💻 Author

**Prasad Shinde**

Engineering Student | Aspiring Data Scientist & ML Engineer

[GitHub](https://github.com/) | [LinkedIn](https://www.linkedin.com/)

---

⭐ If you find this project interesting, feel free to explore the repository and share your feedback!


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
