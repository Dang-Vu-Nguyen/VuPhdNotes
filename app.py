import pandas as pd
import streamlit as st
import requests
import random  # Import random module


# Set up Streamlit page
st.set_page_config(page_title="Vu's PhD Notes", layout="wide")

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

    # Retrieve the current random row from session state
    current_row = st.session_state.get(f"random_row_{section_title}", None)

    # If not already in session state, pick a random row
    if current_row is None:
        random_row = df.sample(n=1).iloc[0]
        st.session_state[f"random_row_{section_title}"] = random_row
    else:
        random_row = current_row

    # Display the selected row
    random_row = st.session_state[f"random_row_{section_title}"]
    st.write(f"Topic: {section_title} (total concepts = {len(df)})")
    st.subheader(f"{random_row.get('Key concepts', 'N/A')}")
    st.write(f"**Created:** {random_row.get('Date', 'N/A')} &nbsp;&nbsp; **Checked Status:** {random_row.get('Checked?', 'N/A')}")
    for i in range(1, 6):
        note = random_row.get(f'Note{i}', 'N/A')
        if note and str(note).strip():
            st.write(f"- {note}")

    # Define a callback function to pick a new random row
    def pick_new_random_row():
        if len(df) > 1:
            df_new = df.drop(random_row.name) if random_row is not None else df
            new_random_row = df_new.sample(n=1).iloc[0]
        else:
            new_random_row = df.iloc[0]
        st.session_state[f"random_row_{section_title}"] = new_random_row

    # Button to pick a new random row, placed after the display
    st.button('Click to get a different concept', key=f'button_{section_title}', on_click=pick_new_random_row)
    st.write("---")

    
st.title('Vu\'s PhD Notes')

# App description
st.markdown('''
Mình dùng nơi nay để lưu trữ và ôn tập lại những kiến thức đã học.

Mình để nội dung ở đây công khai vì hy vọng nó sẽ có ích cho ai đó cần. Rất hoan nghênh nếu bạn tham khảo với mục đích học tập cá nhân thuần túy.

Với những mục đích sử dụng khác, phiền bạn liên hệ để trao đổi trước với mình qua địa chỉ email nguyendangvu.mailbox@gmail.com

Thân ái,

Vũ
''')

st.divider()

st.markdown('''
Các link khác:

- Blog cá nhân: [Vu's notes](https://vunotes.com)
- Youtube học tiếng Trung: [Luyện Tiếng Trung 2](https://www.youtube.com/@luyentiengtrung2)
- Youtube học tiếng Trung (cũ): [Luyện Tiếng Trung](https://www.youtube.com/@luyentiengtrung)
''')

st.divider()

# Get unique subjects
if df is not None and not df.empty:
    if 'Subject' in df.columns:
        unique_subjects = df['Subject'].unique()
        unique_subjects = unique_subjects.tolist()  # Convert to list for shuffling
        
        # Shuffle the subjects on first load
        if 'shuffled_subjects' not in st.session_state:
            random.shuffle(unique_subjects)
            st.session_state['shuffled_subjects'] = unique_subjects
        else:
            # Use the stored shuffled order
            unique_subjects = st.session_state['shuffled_subjects']
            
        for subject in unique_subjects:
            subject_df = df[df['Subject'] == subject]
            # Reset the index to ensure .drop() works correctly
            subject_df = subject_df.reset_index(drop=True)
            display_random_row(subject_df, subject)
    else:
        st.error("The 'Subject' column is missing from the data.")
else:
    st.error("No data available to display.")
