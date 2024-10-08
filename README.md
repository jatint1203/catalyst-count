# Catalyst Count

Catalyst Count is a Django-based web application designed for filtering and counting records from a large dataset stored in a PostgreSQL database. The application allows users to log in, upload CSV files, apply filters, and view the count of records that match the applied filters. It uses Django REST Framework (DRF) for API development and HTML, CSS  and JS for frontend.

## Features

- **User Authentication**: User registration, login, and logout functionality.
- **File Upload**: Users can upload large CSV file with a visual progress indicator.
- **Background Processing**: File uploads and database updates are processed asynchronously to prevent blocking the UI.
- **Data Filtering**: Users can filter uploaded data using a query builder interface and view the count of records matching the filters.
- **Responsive UI**: The application uses Bootstrap 4 for a responsive and user-friendly interface.

## Technologies Used

- **Django**: Python web framework for building the backend.
- **Django REST Framework (DRF)**: For building the API.
- **PostgreSQL**: Database for storing user data and CSV records.
- **django-environ**: For managing environment variables.
- **RaabitMQ** (or **Django Background Tasks**): For asynchronous file processing.
- **Bootstrap 4**: For frontend styling.

## Setup Instructions

### Prerequisites

- Python 3.x
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/jatint1203/catalyst-count.git
cd catalyst-count

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


pip install -r requirements.txt

##Create .env

SECRET_KEY=django-insecure-vs)y09qci^!fhsn9)ghn4^#+ab@%-+9*_7$n@vi&cdllyufb-b
ALLOWED_HOSTS=*

DB_NAME=catalyst_count
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432


#Run these 

python manage.py makemigrations
python manage.py migrate

#create superuser

python manage.py createsuperuser


python manage.py runserver
