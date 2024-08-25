# tasks.py
import csv
from django.db import connection
from .models import Company, City, State, Country, Industry, YearFounded

def get_or_create_location(locality_str):
    city_name, state_name, country_name = (locality_str.split(',') + [None, None])[:3]

    if country_name:
        country, _ = Country.objects.get_or_create(name=country_name.strip())
    else:
        country = None

    if state_name and country:
        state, _ = State.objects.get_or_create(name=state_name.strip(), country=country)
    else:
        state = None

    if city_name and state:
        city, _ = City.objects.get_or_create(name=city_name.strip(), state=state)
    else:
        city = None

    return city, state, country

def get_or_create_industry(industry_name):
    if industry_name:
        industry, _ = Industry.objects.get_or_create(name=industry_name.strip())
        return industry
    return None

def get_or_create_year_founded(year):
    if year and year.isdigit():
        year_int = int(year)
        year_founded, _ = YearFounded.objects.get_or_create(year=year_int)
        return year_founded
    return None

def clean_size_range(size_range):
    if size_range and size_range.endswith('+'):
        return size_range[:-1]
    return size_range

def is_valid_row(row):
    """Check if a row has sufficient valid data to be processed."""
    return row.get('name') and row.get('domain')

def process_csv_chunk(chunk):
    try:
        bulk_data = []
        for row in chunk:
            if not is_valid_row(row):
                continue  # Skip empty or invalid rows

            year_founded = get_or_create_year_founded(row.get('year founded', ''))
            current_employee_estimate = int(row.get('current employee estimate', '') or 0) if row.get('current employee estimate', '').isdigit() else None
            total_employee_estimate = int(row.get('total employee estimate', '') or 0) if row.get('total employee estimate', '').isdigit() else None
            
            city, state, country = get_or_create_location(row.get('locality', ''))
            industry = get_or_create_industry(row.get('industry', ''))

            # Only create record if there's at least some meaningful data
            if row.get('name') or row.get('domain') or industry or city:
                bulk_data.append(Company(
                    sr=row.get('sr', None),
                    name=row.get('name', None),
                    domain=row.get('domain', None),
                    year_founded=year_founded,
                    industry=industry,
                    size_range=clean_size_range(row.get('size range', None)),
                    city=city,
                    state=state,
                    country=country,
                    linkedin_url=row.get('linkedin url', None),
                    current_employee_estimate=current_employee_estimate,
                    total_employee_estimate=total_employee_estimate,
                ))

            if len(bulk_data) >= 1000:
                Company.objects.bulk_create(bulk_data)
                bulk_data = []

        if bulk_data:
            Company.objects.bulk_create(bulk_data)

        print(f"Processed a chunk of size {len(chunk)}.")
    except Exception as e:
        print(f"Error processing chunk: {e}")
    finally:
        connection.close()  
