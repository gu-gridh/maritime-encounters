import os
import sys
import django
import pandas as pd
from ast import literal_eval


# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')

# Set up Django
django.setup()

from apps.resources.models import *  # Replace 'your_app' with the name of your Django app

# Path to your CSV file
csv_file_path = '../../resources/maritime_c14_site_types.csv'

# Load the CSV data
df = pd.read_csv(csv_file_path, on_bad_lines='skip')

# Function to convert string representation of list to actual list
def convert_to_list(value):
    try:
        return literal_eval(value)
    except (ValueError, SyntaxError):
        return value

# Apply the function to the column
df['new_site_type'] = df['new_site_type'].apply(convert_to_list)

# Import data into ADM levels

for sites_type in df[['new_site_type']].drop_duplicates().values:
    sites_type = sites_type[0]
    for t in sites_type:
        SiteType.objects.get_or_create(
            text = t
    )