import re

import pandas as pd
from rest_framework import status

from core.common.erro_message_type import APPErrorTypes
from core.exceptions.base import ApiError

# Define allowed database column names with more variations
ALLOWED_COLUMNS = {
    'full_name':
        [
            "Full Name", "Full name", "full Name",
            'FullName', 'full name', 'fullname',
            'fullName', 'full_name'
        ],
    'first_name':
        [
            "First Name", "First name", "first Name",
            'FirstName', 'first name', 'firstname',
            'firstName', 'first_name'
        ],
    'last_name':
        [
            "Last Name", "Last name", "last Name",
            'LastName', 'last name', 'lastname',
            'lastName', 'last_name'
        ],
    'email':
        [
            "Email", "email", "Email Address",
            "email address", "emailAddress",
            "EmailAddress", 'email_address', 'email_address'
        ],
    'gender': ["Gender", "gender", "Sex", "sex"],
    'address_1':
        [
            "Address 1", "Address1", "address 1",
            "address1", "Address Line 1", "address line 1",
            'address_1'
        ],
    'address_2':
        [
            "Address 2", "Address2", "address 2",
            "address2", "Address Line 2", "address line 2",
            'address_2'
        ],
    'city': ["City", "city", "Town", "town"],
    'country': ["Country", "country", "Nation", "nation"],
    'zip_code':
        [
            "Zip Code", "ZipCode", "zip code",
            "zipcode", "Postal Code", "postal code",
            "postalcode", 'zip_code', 'postal_code'
        ],
    'profession': ["Profession", "profession", "Field", "field", "Sector", "sector", "industry"],
    'phone_number':
        [
            "Phone Number", "Phone", "phone",
            "phone number", "PhoneNumber", "Phone number",
            "Phonenumber", "Mobile", "mobile", "Mobile Number",
            "mobile number", "Contact", "contact",
            "contact number", 'phone_number', 'mobile number'
        ]
}


def normalize_header(header):
    """Normalize the CSV header to match allowed DB column names."""
    header = header.strip().lower()  # Remove extra spaces and convert to lowercase
    for normalized_column, variations in ALLOWED_COLUMNS.items():
        if header in variations:
            return normalized_column
    return None  # Return None if the column is not allowed


# Validation functions
def is_valid_email(email):
    """Check if the email format is valid."""
    pattern = r"[^@]+@[^@]+\.[^@]+"
    return re.match(pattern, email) is not None


def is_valid_phone_number(phone_number):
    """Check if the phone number is valid (only digits and length of 10-15)."""
    pattern = r"^\+?\d{10,15}$"
    return re.match(pattern, str(phone_number)) is not None


def is_non_empty(value):
    """Check if the value is non-empty."""
    return value and value.strip() != ""


def preprocess_csv(df: pd.DataFrame):
    """Preprocess CSV headers, map them to DB column names, and validate the values."""
    processed_data = []

    # Get original headers
    original_headers = list(df.columns)

    # Create a mapping of normalized headers
    header_mapping = {header: normalize_header(header) for header in original_headers}

    # Remove any columns that don't have an allowed DB column name
    valid_headers = {k: v for k, v in header_mapping.items() if v is not None}

    # Remove duplicates based on the email column
    email_column = None
    for header, db_column in valid_headers.items():
        if db_column == "email":
            email_column = header
            break

    if email_column:
        df = df.drop_duplicates(subset=email_column, keep="first")  # Remove duplicate emails

    for _, row in df.iterrows():
        processed_row = {}

        # Validate each row for required fields
        for header in valid_headers:
            db_column = valid_headers[header]
            value = row[header]

            # Add validation for key fields
            if db_column == "email" and not is_valid_email(value):
                raise_api_error(f"Invalid email format: {value}")
            if db_column == "phone_number" and not is_valid_phone_number(value):
                raise_api_error(f"Invalid phone number: {value}")
            if db_column in ["first_name", "last_name"] and not is_non_empty(value):
                raise_api_error(f"{db_column} cannot be empty.")

            # Add to processed row after passing validation
            processed_row[db_column] = str(value)
        processed_data.append(processed_row)

    return processed_data


def raise_api_error(message: str):
    raise ApiError(
        errors=message,
        status_code=status.HTTP_400_BAD_REQUEST,
        message=message,
        error_type=APPErrorTypes.VALIDATION_ERROR.value
    )
