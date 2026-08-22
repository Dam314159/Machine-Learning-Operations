How to set up the environment
1. `git clone https://github.com/Dam314159/Machine-Learning-Operations`
   - This will create a new folder in the current location
2. Create or reuse a Python virtual environment (Python 3.10) and activate it
3. With the virtual environment active, use the command `poetry install` in a terminal to install all the neceessary libraries
4. Run `dvc remote list` and check to see if it points to the correct `dvc-storage` folder inside the cloned repository
   - If it's incorrect, then run `dvc remote modify storage ./dvc-storage` or go into the file `.\.dvc\config` and change `url` to `../dvc-storage`
5. Run `dvc pull` to get the actual csv files into the `data` folder
6. Use hydra to for data paths and model paths

To deploy our app
1. Create a clone or fork of the repository
2. Select your choice of cloud or any platform as a service (PaaS) that enables the deployment of web apps based on a managed container system, with integrated data services and a powerful ecosystem e.g. Heroku, Streamlit or Render.
3. Set up the environment to either `dvc pull` the data automatically or manually pull it before each deploy.
4. Run the app from `app/Home.py` making sure the neceessary libraries in `pyproject.toml` are installed, if not create a `requirements.txt` manually if poetry is for some reason not working.

The link to our deployed app
<https://machine-learning-operations-wingding.streamlit.app/>
