### Team Information:
Team 4
Ren Xiaoyao (AI Jobs Dataset, AI Jobs Predictor Model, Testing App, Hydra)<br>
Damien Leong (Healthcare Disease Dataset, Health Predictor Model, App Deployment, DVC, Poetry)<br>

### Project / Folder Structure
Machine-Learning-Operations/<br>
├── app/                              # Streamlit web application<br>
│   ├── Home.py                       # Main entry point for Streamlit navigation<br>
│   └── pages/                        # Individual prediction pages<br>
│       ├── XiaoYao_Jobs_Predictor.py # AI Jobs Salary Predictor UI & Logic<br>
│       └── Damien_Health_Predictor.py# Health Disease Predictor UI & Logic<br>
├── conf/                             # Hydra configuration files<br>
│   ├── AI_Jobs_config.yaml           # Config for paths (data/model) for AI Jobs<br>
│   └── Health_config.yaml            # Config for paths for Health dataset<br>
├── data/                             # Datasets (tracked by DVC)<br>
│   ├── global_ai_jobs.csv<br>
│   └── bronze_healthcare_disease_prediction_dataset.csv<br>
├── dvc-storage/                      # Local DVC remote storage for data versioning<br>
├── models/                           # Saved PyCaret pipelines (.pkl)<br>
│   ├── AI_Jobs_model.pkl<br>
│   └── Health_model.pkl<br>
├── notebooks/                        # Jupyter notebooks for EDA and Model Training<br>
│   ├── XiaoYao_AI_Jobs_EDA_and_Training.ipynb<br>
│   └── Damien_Health_EDA_and_Training.ipynb<br>
├── .gitattributes                    # Git LFS / binary file tracking rules<br>
├── .gitignore                        # Files ignored by Git (venv, cache, etc.)<br>
├── pyproject.toml                    # Poetry dependency management file<br>
├── poetry.lock                       # Locked dependencies for reproducibility<br>
├── setup.sh                          # Streamlit Cloud setup script (runs dvc pull)<br>
└── README.md                         # This file<br>

### Deployment Guide
1. `git clone https://github.com/Dam314159/Machine-Learning-Operations`
   - This will create a new folder in the current location
2. Create or reuse a Python virtual environment (Python 3.10) and activate it
3. With the virtual environment active, use the command `poetry install` in a terminal to install all the neceessary libraries
4. Run `dvc remote list` and check to see if it points to the correct `dvc-storage` folder inside the cloned repository
   - If it's incorrect, then run `dvc remote modify storage ./dvc-storage` or go into the file `.\.dvc\config` and change `url` to `../dvc-storage`
5. Run `dvc pull` to get the actual csv files into the `data` folder
6. Use hydra for data paths and model paths
8. Select your choice of cloud or any platform as a service (PaaS) that enables the deployment of web apps based on a managed container system, with integrated data services and a powerful ecosystem e.g. Heroku, Streamlit or Render.
9. Set up the environment to either `dvc pull` the data automatically or manually pull it before each deploy.
10. Run the app from `app/Home.py` making sure the neceessary libraries in `pyproject.toml` are installed, if not create a `requirements.txt` manually if poetry is for some reason not working.

### User Guide
Navigation: Use the sidebar on the left to select which predictor you want to use (e.g., "Job Prediction" or "Health Prediction").
Input Modes: Each page has two tabs at the top:
Single Input: For real-time prediction of a single record.
Batch Upload (CSV): For generating bulk predictions.

Single Input Prediction:
Fill in the form fields (Country, BMI, sliders for numerical values, etc.).
Click the "Predict" button.

Batch Prediction:
Upload a CSV file containing the required columns.
Click "Generate Batch Predictions".

### URLS
The link to our repository 
<https://github.com/Dam314159/Machine-Learning-Operations>
The link to our deployed app
<https://machine-learning-operations-wingding.streamlit.app/>
