# Replace 'your_app' with the name of your Django app
from apps.resources.models import *
from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, ADM5
import os
import sys
import django
import json
import pandas as pd
from datetime import datetime

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')

# Set up Django
django.setup()


# Path to your CSV file
json_file_path = '../../resources/c_horn_metalwork.json'

# Load the CSV data
df = pd.json_normalize(json.load(open(json_file_path)))
# Import data into ADM levels

for row in df.rows(index=False):
    ()

print("Data imported successfully")
