# FAIR-SEA: Fairness Assessment in Representation for Southeast Asia

An open-source Python toolkit for evaluating socio-cultural bias in Large Language Models (LLMs) with a focus on the Southeast Asian context.

Guide to set up the FAIR-SEA development environment
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

# Everyday Workflow
Each time you start working on the project, remember to activate the virtual environment first by navigating to the project folder in your terminal and running the activation command for your OS.

Guide to production environment : 
Step 1: Navigate to the GitHub Repository
    Please visit our project repository at the following URL:
    https://github.com/HartantoLs/FAIR-SEA

Step 2: Access the Published Packages
    On the main repository page, look for the "Packages" section on the right-hand sidebar. This section contains all the official releases of our toolkit.

Step 3: Download the Latest Version
    Click on the latest version of the fairsea package. On the package page, you can download the distributable files (specifically the .whl file), which represent the complete, installable version of our project.