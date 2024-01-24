# Live Demo
https://crypto-stock-400717.uc.r.appspot.com/

# CryptoAdvisor
This repo is for COSC 540 Advanced Software Engineering - Group 5 project. CryptoAdvisor - A crypto investment recommendation App

## Setup
There are two options for running this application locally.  The first and easiest option, involves nothing more than installing Docker (if not already present) and running the build script.

### Option #1: Run Using Docker

1. Install Docker
```https://www.docker.com/get-started/```

2. Pull Repo
```git clone https://github.com/mgree108/CryptoAdvisor.git``` 

3. Move into repo directory and run the build Script
```
cd CryptoAdvisor
sh run.sh
```

4. Connect to the website using a browser of your choice
```https://127.0.0.1:8080/``` 


### Option #2: Create a Virtual environment and Run in Debug mode.
**For Macos and Linux Users**

1. Create a Python virtual environment using a python3.x binary
```
virtualenv myenv
source myenv/bin/activate
python install -r requirements.txt
```

2. Setup environment variables (See the Secrets folder in Canvas)

**A file named .env should already be present.  If not, you will have to fetch the environment variable credentials, outlined below, from the Secrets folder in Canvas**
```
#macos/linux
export GOOGLE_CLIENT_SECRET="client secret here"
exportGOOGLE_CLIENT_ID="client Id here"
```

3. Run in debug Mode

```
python app.py

You may have to source the binary directly if your environment doesn't detect the 'active' pyenv.
../path/bin/python app.py
```

4. Open the website
```https://127.0.0.1:8080/``` 

**For Windows Users**

1. Setup on Windows
```
cd [%PROJECT_HOME%]/gcp_prototype
pip3 install virtualenv
python -m virtualenv .
cd /myenv/
activate.bat
cd ../
python -m pip install -r ./requirements.txt
python .\app.py
```

2. Open the Website
```https://127.0.0.1:8080/``` 
