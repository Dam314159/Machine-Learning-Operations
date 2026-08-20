How to set up the environment
1. `git clone https://github.com/Dam314159/Machine-Learning-Operations`
   - This will create a new folder in the current location
2. Create or reuse a Python virtual environment (Python 3.10) and activate it
3. While the virtual environment is active, run the following commands
   1. `py -m pip install --upgrade pip`
   2. `pip install -r requirements.txt`
4. Run `dvc remote list` and check to see if it points to the correct `dvc-storage` folder inside the cloned repository
   - If it's incorrect, then run `dvc remote modify storage ./dvc-storage` or go into the file `.\.dvc\config` and change `url` to `../dvc-storage`
5. Run `dvc pull` to get the actual csv files into the `data` folder
6. Yippee!!!

To get the `requirements.txt`, run `poetry export --format requirements.txt --output requirements.txt`.