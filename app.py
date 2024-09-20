import pandas as pd
import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh
import re

# Set up Streamlit page
st.set_page_config(page_title="Vu's PhD Notes", layout="wide")

# Function to sanitize names for use in JavaScript variable names and HTML IDs
def sanitize_name(name):
    # Remove all non-word characters (everything except numbers and letters)
    name = re.sub(r"[^\w]", '', name)
    # Remove leading characters until we find a letter or underscore
    name = re.sub(r"^[^A-Za-z_]+", '', name)
    return name

# Access the API key from Streamlit's secrets
google_api_key = st.secrets["api_keys"]["google_api_key"]

# Autorefresh every 30 seconds
st_autorefresh(interval=30 * 1000, key="datarefresh")

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
    if sheet_data and 'values' in sheet_data:
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

# Function to display a random row from a given dataframe sectioned by subject
def display_random_row(df, section_title):
    if df.empty:
        st.write(f"No data available for {section_title}")
        return

    # Get total number of rows for this subject
    total_rows = len(df)

    random_row = df.sample(n=1).iloc[0]

    # Display the selected row
    st.write(f"### {section_title} ({total_rows})")  # Updated to header level 3
    st.subheader(f"{random_row.get('Key concepts', 'N/A')}")
    st.write(f"**Created:** {random_row.get('Date', 'N/A')} &nbsp;&nbsp; **Checked Status:** {random_row.get('Checked?', 'N/A')}")
    for i in range(1, 6):
        note = random_row.get(f'Note{i}', 'N/A')
        if note != 'N/A' and note.strip() != '':
            st.write(f"- {note}")
    st.write("---")

    # Sanitize section_title for use in IDs and variable names
    sanitized_title = sanitize_name(section_title)

    # Display the countdown timer with styling
    countdown_html = f"""
        <div style="display: flex; align-items: center;">
            <span>Next in:</span>
            <div id="timer_{sanitized_title}" style="color: black; font-weight: bold; margin-left: 5px;">30 s</div>
        </div>
        <script>
            if (typeof timer_{sanitized_title} !== 'undefined') {{
                clearInterval(timer_{sanitized_title});
            }}

            var timeLeft_{sanitized_title} = 30;
            var timer_{sanitized_title} = setInterval(function(){{
                if(timeLeft_{sanitized_title} <= 0){{
                    clearInterval(timer_{sanitized_title});
                }}
                document.getElementById("timer_{sanitized_title}").innerHTML = timeLeft_{sanitized_title} + " s";
                timeLeft_{sanitized_title} -= 1;
            }}, 1000);
        </script>
    """
    # Use a unique key for each HTML component
    st.components.v1.html(countdown_html, height=40, key=f"timer_{sanitized_title}")

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

- Blog cá nhân: [Vu's notes](https://vunotes.com)
- Youtube học tiếng Trung: [Luyện Tiếng Trung 2](https://www.youtube.com/@luyentiengtrung2)
- Youtube học tiếng Trung (cũ): [Luyện Tiếng Trung](https://www.youtube.com/@luyentiengtrung)
''')

# Get unique subjects
if df is not None and not df.empty:
    if 'Subject' in df.columns:
        unique_subjects = df['Subject'].unique()

        for subject in unique_subjects:
            subject_df = df[df['Subject'] == subject]
            display_random_row(subject_df, subject)
    else:
        st.error("The 'Subject' column is missing from the data.")
else:
    st.error("No data available to display.")
