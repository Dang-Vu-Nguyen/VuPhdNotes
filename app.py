import pandas as pd
import streamlit as st
import time
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

# Load the gsheet from my googlesheet
gsheet = 'a file in my googlesheet'

# Specify the columns to load (including those that need to be removed later)
columns_to_load = 'all available columns

# Load the data into a dataframe
df = pd.gsheet(gsheet, usecols=columns_to_load)


# Set up Streamlit
st.set_page_config(page_title='Vu's PhD Notes')

# App Title and Description
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

st.header("1. Bảng tổng hợp toàn bộ từ vựng")

# Allow users to select which columns to display
selected_columns = st.multiselect(
    "Chọn các cột bạn muốn xem:", 
    options=columns_to_display,  # Provide all available columns
    default=columns_to_display  # Display all by default
)


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    import pandas as pd
    import streamlit as st
    from pandas.api.types import (
        is_categorical_dtype,
        is_numeric_dtype,
    )

    # modify = st.checkbox("Tìm kiếm...", value=True)

    # if not modify:
    #     return df

    df = df.copy()

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Lọc/Tìm kiếm...", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Tìm trong {column}...",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100 if (_max - _min) != 0 else 1
                user_num_input = right.slider(
                    f"Tìm trong {column}...",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            else:
                user_text_input = right.text_input(
                    f"Tìm trong {column}...",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input, na=False, regex=False)]

    return df

# Filterable DataFrame UI
filtered_df = filter_dataframe(df)

# Display the filtered dataframe with only the selected columns
if selected_columns:
    st.dataframe(filtered_df[selected_columns], use_container_width=True)
else:
    st.write("Hãy chọn ít nhất một cột để xem.")

#######################
# New Section: Từ vựng ngẫu nhiên (with Titles in st.write)
#######################

st.header("2. Từ vựng ngẫu nhiên")

# Function to display a random row from a given dataframe
def display_random_row(df, section_title):
    if df.empty:
        st.write(f"No data available for {section_title}")
        return
    
    random_row = df.sample(n=1).iloc[0]
    
    # Combine the section title and all fields into one string for display
    row_display = (
        f"{section_title}\n"  # Display section title, e.g., "HSK 1"
        f"- {random_row.get('Từ vựng', 'N/A')} /{random_row.get('Pinyin', 'N/A')} - {random_row.get('Hán Việt', 'N/A')}/ {random_row.get('Nghĩa Việt', 'N/A')}\n\n"
        f"- {random_row.get('Câu mẫu', 'N/A')}\n\n"
        f"- {random_row.get('Phồn thể', 'N/A')}\n\n"
        f"- {random_row.get('Pinyin câu mẫu', 'N/A')}\n\n"
        f"- {random_row.get('Hán Việt câu mẫu', 'N/A')}\n\n"
        f"- {random_row.get('Nghĩa câu mẫu', 'N/A')}"
    )
    
    # Display all combined fields at once
    st.write(row_display)


# Split the dataframe by levels (HSK1 to HSK5)
hsk1_df = df[df['Level'] == 'HSK 1']
hsk2_df = df[df['Level'] == 'HSK 2']
hsk3_df = df[df['Level'] == 'HSK 3']
hsk4_df = df[df['Level'] == 'HSK 4']
hsk5_df = df[df['Level'] == 'HSK 5']

# Create empty slots for the countdown timer and each HSK level subsection
timer1_section = st.empty()
hsk1_section = st.empty()

timer2_section = st.empty()
hsk2_section = st.empty()

timer3_section = st.empty()
hsk3_section = st.empty()

timer4_section = st.empty()
hsk4_section = st.empty()

timer5_section = st.empty()
hsk5_section = st.empty()

st.divider()

st.markdown('''

Tài liệu được tổng hợp và biên soạn bởi Luyện Tiếng Trung 2. Xin vui lòng không sử dụng với mục đích thương mại mà không có sự cho phép của chúng mình.

Nếu bạn thấy nội dung hữu ích và muốn ủng hộ chúng mình, bạn có thể cân nhắc tặng chúng mình một cốc cà phê tại:
- Techcombank
- 290667040209
- NGUYEN THI HONG KHANH

Cám ơn bạn rất nhiều ạ!


''')

while True:
        
    with hsk1_section:
        display_random_row(hsk1_df, "HSK 1")
    
    with hsk2_section:
        display_random_row(hsk2_df, "HSK 2")
    
    with hsk3_section:
        display_random_row(hsk3_df, "HSK 3")
    
    with hsk4_section:
        display_random_row(hsk4_df, "HSK 4")
    
    with hsk5_section:
        display_random_row(hsk5_df, "HSK 5")
        # Countdown from 9 seconds (to account for processing time)
    for i in range(15, 0, -1):
        # Update the timer messages for each HSK section
        timer1_section.write("({} s)".format(i))
        timer2_section.write("({} s)".format(i))
        timer3_section.write("({} s)".format(i))
        timer4_section.write("({} s)".format(i))
        timer5_section.write("({} s)".format(i))
        
        # Wait for 1 second before updating the countdown
        time.sleep(1)
    
