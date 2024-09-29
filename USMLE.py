import pandas as pd
import streamlit as st
import requests
import random  # Import random module


# Set up Streamlit page
st.set_page_config(page_title="USMLE", layout="wide")

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
sheet_name = 'USMLE'  # Replace with your sheet name

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
    st.write(f"**Review Count:** {random_row.get('Review Count', 'N/A')} &nbsp;&nbsp; **Level:** {random_row.get('Status', 'N/A')}")
    st.write(f"Topic: {section_title} (total questions = {len(df)})")
    st.subheader(f"{random_row.get('Topics', 'N/A')}")

    # Map numbers to letters
    letter_mapping = {1: 'A.', 2: 'B.', 3: 'C.', 4: 'D.', 5: 'E.'}

    # Loop through Op, Ans, Extra columns
    for i in range(1, 6):
        op = random_row.get(f'Op{i}', '').strip()
        ans = random_row.get(f'Ans{i}', '').strip()
        extra = random_row.get(f'Extra{i}', '').strip()

        if op:
            st.write(f"**{letter_mapping[i]}** {op}")

            # Create unique keys for the visibility state
            ans_key = f"ans_visible_{section_title}_{i}"
            extra_key = f"extra_visible_{section_title}_{i}"

            # Initialize the visibility state in session_state if not present
            if ans_key not in st.session_state:
                st.session_state[ans_key] = False
            if extra_key not in st.session_state:
                st.session_state[extra_key] = False

            # Define callbacks to toggle the visibility state
            def toggle_visibility(key):
                st.session_state[key] = not st.session_state[key]

            # Create buttons that toggle the visibility
            col1, col2 = st.columns(2)
            with col1:
                st.button("Answer", key=f"btn_ans_{section_title}_{i}", on_click=partial(toggle_visibility, ans_key))
            with col2:
                st.button("Extra", key=f"btn_extra_{section_title}_{i}", on_click=partial(toggle_visibility, extra_key))

            # Display the content if visible
            if st.session_state[ans_key]:
                st.write(f"**Answer:** {ans if ans else 'N/A'}")
            if st.session_state[extra_key]:
                st.write(f"**Extra:** {extra if extra else 'N/A'}")

            st.write("")  # Add space between each set    
    # # Loop through Op, Ans, Extra columns
    # for i in range(1, 6):
    #     op = random_row.get(f'Op{i}', 'N/A')
    #     ans = random_row.get(f'Ans{i}', 'N/A')
    #     extra = random_row.get(f'Extra{i}', 'N/A')

    #     st.write(f"**Op{i}:** {op}")
    #     st.write(f"**Ans{i}:** {ans}")
    #     st.write(f"**Extra{i}:** {extra}")
    #     st.write("")  # Add space between each set
        
    # Define a callback function to pick a new random row
    def pick_new_random_row():
        if len(df) > 1:
            df_new = df.drop(random_row.name) if random_row is not None else df
            new_random_row = df_new.sample(n=1).iloc[0]
        else:
            new_random_row = df.iloc[0]
        st.session_state[f"random_row_{section_title}"] = new_random_row

    # Button to pick a new random row, placed after the display
    st.button('Click for another question', key=f'button_{section_title}', on_click=pick_new_random_row)
    st.write("---")

    
st.title('USMLE')

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
