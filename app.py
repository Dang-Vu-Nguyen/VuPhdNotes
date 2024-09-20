import pandas as pd
import streamlit as st
import time
import requests
import os

# Access the API key from Streamlit's secrets
google_api_key = st.secrets["api_keys"]["google_api_key"]

# Function to get data from Google Sheets API
def get_google_sheet_data(spreadsheet_id, sheet_name, api_key):
    # Construct the URL for the Google Sheets API
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}!A1:Z?alt=json&key={api_key}'

    try:
        # Make a GET request to retrieve data from the Google Sheets API
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        st.error(f"An error occurred: {e}")
        return None

# Configuration
spreadsheet_id = '1-5pPM5sJye6nROpJIcDcyzMskbnScBnkBZ9XjvBgtGM'  # Replace with your spreadsheet ID
api_key = google_api_key
sheet_name = 'Sheet1'  # Replace with your sheet name

# Fetch the data
sheet_data = get_google_sheet_data(spreadsheet_id, sheet_name, api_key)

# Function to convert the data into a pandas DataFrame
def convert_to_dataframe(sheet_data):
    if sheet_data:
        # Extract the headers and rows
        headers = sheet_data['values'][0]  # First row contains the headers
        rows = sheet_data['values'][1:]  # Remaining rows are the data

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=headers)
        return df
    else:
        return None

# Convert to DataFrame
df = convert_to_dataframe(sheet_data)

# Display the data
if df is not None:
    st.write(df)
else:
    st.write("No data found.")

# Function to display a random row from a given dataframe sectioned by subject
def display_random_row(df, section_title):
    if df.empty:
        st.write(f"No data available for {section_title}")
        return

    random_row = df.sample(n=1).iloc[0]

    # Display the selected row
    st.subheader(f"Subject: {section_title}")
    st.write(f"- **Key Concept**: {random_row['Key concepts']}")
    st.write(f"- **Date Created**: {random_row['Date']}")
    st.write(f"- **Checked**: {random_row['Checked?']}")
    for i in range(1, 6):
        st.write(f"- **Note{i}**: {random_row.get(f'Note{i}', 'N/A')}")
    st.write("---")


# Set up Streamlit page
st.set_page_config(page_title="Vu's PhD Notes", layout="wide")

# App description
st.markdown('''
Mình dùng nơi nay để lưu trữ và ôn tập lại những kiến thức đã học. 

Mình để nội dung ở đây công khai vì hy vọng nó sẽ có ích cho ai đó.

Rất hoan nghênh nếu bạn tham khảo với cho mục đích học tập cá nhân thuần túy.

Với những mục đích sử dụng khác, phiền bạn liên hệ để trao đổi trước với mình qua địa chỉ email: nguyendangvu.mailbox@gmail.com
''')

st.divider()

st.markdown('''
Các link khác:

- Blog cá nhân: [Vu's notes] (vunotes.com)
- Youtube học tiếng Trung: [Luyện Tiếng Trung 2] (https://www.youtube.com/@luyentiengtrung2)
- Youtube học tiếng Trung (cũ): [Luyện Tiếng Trung] (https://www.youtube.com/@luyentiengtrung)
''')

# Get unique subjects
unique_subjects = df['Subject'].unique()

# Create sections for each subject
subject_sections = {subject: st.empty() for subject in unique_subjects}

# Infinite loop to update the content every 30 seconds
while True:
    for subject in unique_subjects:
        subject_df = df[df['Subject'] == subject]  # Filter data by subject
        with subject_sections[subject]:
            display_random_row(subject_df, subject)

    # Timer for 30 seconds
    for i in range(30, 0, -1):
        st.write(f"Next update in {i} seconds...")
        time.sleep(1)
