import pandas as pd
import streamlit as st
import time

# Function to simulate loading data from Google Sheets
def load_gsheet():
    # For actual implementation, use Google Sheets API to fetch the data.
    # This is a placeholder for demo purposes.
    gsheet_url = 'your_google_sheet_url_here'
    df = pd.read_csv(gsheet_url)  # Replace with gsheet fetching function
    return df

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

# Load the data into a dataframe
df = load_gsheet()

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
