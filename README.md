# Music Recommendation System for Running

**Machine Learning-Based Music Recommendation Using Listening Preferences and Exercise Intensity**

## Project Overview

This project is an undergraduate Computer Science thesis developed at Naresuan University.

The system aims to recommend music for running by combining user listening preferences with predefined exercise intensity zones and workout plans.

The project was developed collaboratively. My primary responsibility was the **machine learning models, dataset preparation, recommendation logic, and evaluation**, while my teammate developed the Flutter mobile application.

## Key Features

- Personalized music genre recommendations based on user listening preferences
- Machine learning model comparison and evaluation
- Music BPM matching with predefined running intensity zones
- Workout plan-based playlist generation
- Research-informed BPM and exercise intensity matching
- Integration-oriented recommendation logic for a Flutter mobile application

## System Workflow

1. Users select their music preferences and workout plans in the Flutter application.
2. Model 1 recommends music genres based on user preferences.
3. The selected workout plan determines predefined exercise intensity zones.
4. Model 2 matches recommended genres and target BPM ranges with songs in the music dataset.
5. The system generates a playlist aligned with the planned workout.

Heart rate target ranges are associated with exercise zones to guide users during running. The system does not dynamically change music recommendations based on real-time heart rate measurements.

## Machine Learning Models

### Model 1 — Music Genre Preference Recommendation

**Objective:** Recommend music genres based on users' listening preferences.

Dataset: Music & Mental Health Survey (MxMH)

Approaches evaluated:

- Self-Frequency Baseline
- Logistic Regression
- k-Nearest Neighbors Collaborative Filtering

Evaluation metrics:

| Model | Accuracy@1 | Recall@3 | MAP@3 |
|---|---:|---:|---:|
| Self-Frequency Baseline | 0.520 | 0.858 | 0.668 |
| Logistic Regression | 0.514 | 0.845 | 0.667 |
| kNN Collaborative Filtering | 0.189 | 0.541 | 0.340 |

The baseline and Logistic Regression approaches were shortlisted based on their evaluation results.

### Model 2 — BPM and Exercise Intensity Matching

**Objective:** Match music tempo with predefined exercise intensity zones and workout plans.

The recommendation approach considers:

- Recommended music genres from Model 1
- Target BPM ranges for each running zone
- Music metadata and BPM information
- Workout block durations
- Preference and BPM matching scores

The system uses predefined exercise zones rather than real-time heart rate adaptive music selection.

## Datasets

**MxMH Survey Dataset**

Used to analyze music listening preferences and evaluate genre recommendation approaches.

**Jamendo Music Dataset**

Used for music metadata preparation, BPM analysis, and playlist generation.

## Technologies

- Python
- Pandas and NumPy
- Scikit-learn
- Jupyter Notebook
- Music metadata and BPM processing
- Machine Learning and Recommendation Algorithms

## Repository Structure

```text
thesis_model/
├── model/
│   ├── model1.ipynb
│   ├── model2.ipynb
│   └── ...
├── thesis_jamendo_dataset/
│   └── ...
└── README.md
```

## My Contributions

- Designed and evaluated music genre recommendation approaches
- Prepared and analyzed datasets
- Developed BPM and exercise intensity matching logic
- Implemented workout-based playlist generation
- Conducted model comparisons and evaluation
- Studied relevant research to support recommendation design
- Collaborated with the Flutter application developer on system integration

## Project Scope

This repository focuses on the machine learning models, dataset preparation, and recommendation algorithms.

The Flutter mobile application was developed by my teammate and is not included in this repository.

## Future Improvements

- Evaluate recommendation quality with additional users
- Explore adaptive recommendations using real-time exercise data
- Expand the music dataset and available genres
- Improve personalization using user feedback
