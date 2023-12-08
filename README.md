# ECS 272 Final Project
## Analysis of factors affecting COVID-19 through interactive slideshow

This project is built using Python and Dash framework. To install the required libraries, run the following command:

```python3 -m pip install -r requirements.txt```

If you prefer to install it using a conda env, run the following command:

```conda create --name <env_name> --file requirements.txt```

Then activate the conda environment using:

```conda activate <env_name>```

After installing the required libraries, run the project by:

```python3 app.py```

or 

```flask run```

This should show the localhost port number where the application is deployed, open the address shown on the localhost and the slideshow will open.

### Required data files
The project repository by default includes all the data files required to run the application. If, for some reason, there is a need to regenerate the data files, navigate to the data folder, and then each subdirectory. First run the download.sh files using:

```chmod +x download.sh && ./download.sh```

Then run the analysis.ipynb notebooks in each directory.