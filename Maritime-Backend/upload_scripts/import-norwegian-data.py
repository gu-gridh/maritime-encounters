from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, ADM5
from apps.resources.models import *
import os
import sys
import django
import json
import pandas as pd
from datetime import datetime
from django.contrib.gis.geos import Point
import numpy as np
from ast import literal_eval

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')

# Set up Django
django.setup()

# Replace 'your_app' with the name of your Django app

csv_file_path = ''

# Load the CSV data
df = pd.read_csv(csv_file_path).replace(np.nan, None).replace('[]', None)
