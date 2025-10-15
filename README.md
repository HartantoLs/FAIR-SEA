# FAIR-SEA: Fairness Assessment in Representation for Southeast Asia

An open-source Python toolkit for evaluating socio-cultural bias in Large Language Models (LLMs) with a focus on the Southeast Asian context.

# Guide to set up the FAIR-SEA development environment
1. Prerequisites
Ensure you have Python 3.11 or a newer version installed. Check by enter this code in terminal:
    python3 --version

2. Clone the Repository
Download the project code from GitHub to your computer:
    git clone https://github.com/HartantoLs/FAIR-SEA.git
    cd FAIR-SEA

3. Create and Activate Virtual Environment
We will use a virtual environment to keep our project dependencies isolated.
Create the environment folder:  
    python3 -m venv venv

Activate the environment (this command is different for Mac vs. Windows):
    On macOS/Linux:
        source venv/bin/activate

    On Windows (PowerShell/CMD):
        .\venv\Scripts\activate

You will see (venv) at the beginning of your terminal prompt once it's active.

4. Install All Dependencies
This command reads the requirements.txt file and installs all the necessary libraries for the project.
pip install -r requirements.txt

5. You are now ready to start developing!

## Everyday Workflow
Each time you start working on the project, remember to activate the virtual environment first by navigating to the project folder in your terminal and running the activation command for your OS.

### Workflow 1: Adding a New Library (Dependency)
Follow these steps whenever you need to add a new library (e.g., matplotlib) to the project.

1. Activate Your Virtual Environment
First, make sure your venv is active in your terminal.
    On macOS/Linux: source venv/bin/activate
    On Windows: .\venv\Scripts\activate

2. Install the New Library
Use pip to install the package you need.
    pip install matplotlib

3. Update the requirements.txt File (Crucial Step!)
After installing the new library, immediately update the project's "master list" by running:
    pip freeze > requirements.txt

4. Commit and Push Your Changes
Commit both your new code that uses the library AND the updated requirements.txt file.
    git add .
    git commit -m "feat: Add matplotlib for data visualization"
    git push

5. For other members
Others will need to run git pull and then sync their own environments by running pip install -r requirements.txt.

### Workflow 2: Adding a New Unit Test for CI
Follow these steps every time you write a new function that needs to be automatically tested by our CI pipeline.
1. Write Your New Function
First, add your new function to the appropriate file in the fairsea/ directory.

2. Create the Corresponding Test Function
Now, open the corresponding test file in the tests/ folder (e.g., tests/test_evaluation.py) and add a new test function. The function name must start with test_.

3. Test Locally (Recommended)
Before pushing your code, run pytest in your terminal to make sure your new test (and all old ones) pass on your machine.

4. Commit and Push
Once your local test passes, commit and push your changes. The CI pipeline on GitHub will automatically run pytest again to verify your changes.

You can then check the "Actions" tab on GitHub to see if the CI pipeline passed.

# Guide to production environment : 
Step 1: Navigate to the GitHub Repository
    Please visit our project repository at the following URL:
    https://github.com/HartantoLs/FAIR-SEA

Step 2: Access the Published Packages
    On the main repository page, look for the "Packages" section on the right-hand sidebar. This section contains all the official releases of our toolkit.

Step 3: Download the Latest Version
    Click on the latest version of the fairsea package. On the package page, you can download the distributable files (specifically the .whl file), which represent the complete, installable version of our project.