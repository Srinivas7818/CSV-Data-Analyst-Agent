
import io
import csv
import hashlib

import pandas as pd
import streamlit as st

from agent import ask_agent


# --------------------------------------------------
# 1. Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="CSV Data Analyst Agent",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# 2. Custom styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #888888;
        font-size: 1rem;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 3. Application heading
# --------------------------------------------------

st.markdown(
    '<div class="main-title">📊 CSV Data Analyst Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Upload your dataset and explore it using natural language '
    'and AI-powered Python analysis.'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# 4. Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("📁 Dataset")

    st.write(
        "Upload a CSV file to begin analyzing your data."
    )

    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=["csv"],
        help="Upload a CSV file up to 200 MB."
    )

    st.divider()

    st.subheader("✨ Available features")

    st.markdown(
        """
        - Dataset overview
        - Numerical analysis
        - Average and maximum values
        - Group-wise analysis
        - Frequency analysis
        - Missing-value information
        """
    )

    st.divider()

    st.caption("Powered by Python, Pandas, Groq and Streamlit.")


# --------------------------------------------------
# 5. Display instructions if no file is uploaded
# --------------------------------------------------

if uploaded_file is None:

    st.info("Upload a CSV file from the sidebar to get started.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📂 Upload")
        st.write("Upload your own CSV dataset.")

    with col2:
        st.markdown("### 🤖 Analyze")
        st.write("Ask questions in natural language.")

    with col3:
        st.markdown("### 📈 Explore")
        st.write("Discover patterns and insights.")

    st.stop()


# --------------------------------------------------
# 6. Check file size
# --------------------------------------------------

MAX_FILE_SIZE_MB = 200

file_bytes = uploaded_file.getvalue()

file_size_mb = len(file_bytes) / (1024 * 1024)

if file_size_mb > MAX_FILE_SIZE_MB:

    st.error(
        f"File is too large. Maximum allowed size is "
        f"{MAX_FILE_SIZE_MB} MB."
    )

    st.stop()


if not file_bytes:

    st.error("The uploaded file is empty.")

    st.stop()


# --------------------------------------------------
# 7. Read CSV with encoding and delimiter detection
# --------------------------------------------------

encodings = [
    "utf-8-sig",
    "utf-8",
    "utf-16",
    "utf-16-le",
    "utf-16-be",
    "cp1252",
    "latin1"
]

df = None
selected_encoding = None
selected_delimiter = None
last_error = None

for encoding in encodings:

    try:

        # Decode the file using the current encoding.
        decoded_content = file_bytes.decode(
            encoding,
            errors="strict"
        )

        # Detect the delimiter.
        sample = decoded_content[:10000]

        try:

            detected_delimiter = csv.Sniffer().sniff(
                sample,
                delimiters=",;\t|"
            ).delimiter

        except csv.Error:

            detected_delimiter = ","

        # Read the CSV.
        temporary_df = pd.read_csv(
            io.StringIO(decoded_content),
            sep=detected_delimiter,
            engine="python",
            on_bad_lines="error"
        )

        df = temporary_df
        selected_encoding = encoding
        selected_delimiter = detected_delimiter

        break

    except (
        UnicodeDecodeError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        csv.Error,
        ValueError
    ) as error:

        last_error = error

    except Exception as error:

        last_error = error


if df is None:

    st.error(
        "Unable to read this CSV file. "
        "Please check its encoding, delimiter and formatting."
    )

    if last_error:
        print("CSV reading error:", last_error)

    st.stop()


# --------------------------------------------------
# 8. Validate uploaded data
# --------------------------------------------------

if len(df.columns) == 0 or df.empty:

    st.error("The uploaded CSV does not contain usable data.")

    st.stop()


if df.columns.duplicated().any():

    st.error(
        "Duplicate column names detected. "
        "Please rename the duplicate columns."
    )

    st.stop()


if any(not str(column).strip() for column in df.columns):

    st.error(
        "One or more column names are empty. "
        "Please provide names for all columns."
    )

    st.stop()


# --------------------------------------------------
# 9. Reset chat when file changes
# --------------------------------------------------

file_hash = hashlib.md5(file_bytes).hexdigest()

if "active_file" not in st.session_state:
    st.session_state.active_file = None

if st.session_state.active_file != file_hash:

    st.session_state.active_file = file_hash
    st.session_state.messages = []
    st.session_state.pending_question = None


if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# --------------------------------------------------
# 10. Dataset heading
# --------------------------------------------------

st.success(
    f"Successfully uploaded: {uploaded_file.name}"
)

st.caption(
    f"Detected encoding: {selected_encoding} | "
    f"Detected separator: {repr(selected_delimiter)}"
)

st.markdown(
    '<div class="section-title">📊 Dataset Overview</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# 11. Dashboard metrics
# --------------------------------------------------

total_rows = len(df)
total_columns = len(df.columns)
missing_values = int(df.isna().sum().sum())
duplicate_rows = int(df.duplicated().sum())

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Rows", f"{total_rows:,}")

with col2:
    st.metric("Total Columns", f"{total_columns:,}")

with col3:
    st.metric("Missing Values", f"{missing_values:,}")

with col4:
    st.metric("Duplicate Rows", f"{duplicate_rows:,}")


# --------------------------------------------------
# 12. Data preview and column information
# --------------------------------------------------

st.markdown(
    '<div class="section-title">🔍 Explore Your Dataset</div>',
    unsafe_allow_html=True
)

preview_tab, column_tab = st.tabs(
    ["📋 Data Preview", "📌 Column Information"]
)


with preview_tab:

    st.caption("Showing the first 10 rows of your dataset.")

    st.dataframe(
        df.head(10),
        width="stretch",
        hide_index=True
    )


with column_tab:

    column_information = pd.DataFrame({
        "Column": df.columns,
        "Data Type": [
            str(dtype) for dtype in df.dtypes
        ],
        "Missing Values": [
            int(value) for value in df.isna().sum()
        ],
        "Unique Values": [
            int(df[column].nunique())
            for column in df.columns
        ]
    })

    st.dataframe(
        column_information,
        width="stretch",
        hide_index=True
    )


# --------------------------------------------------
# 13. Suggested questions
# --------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">💡 Try These Questions</div>',
    unsafe_allow_html=True
)

numeric_columns = list(
    df.select_dtypes(include="number").columns
)

categorical_columns = list(
    df.select_dtypes(exclude="number").columns
)

suggestions = [
    "How many rows and columns are present in this dataset?"
]

if numeric_columns:

    numeric_column = str(numeric_columns[0])

    suggestions.append(
        f"What is the average {numeric_column}?"
    )

    suggestions.append(
        f"What is the highest {numeric_column}?"
    )


if categorical_columns:

    categorical_column = str(categorical_columns[0])

    suggestions.append(
        f"What are the most common values in {categorical_column}?"
    )


def set_suggested_question(question):

    st.session_state.pending_question = question


suggestion_columns = st.columns(2)

for index, suggestion in enumerate(suggestions):

    with suggestion_columns[index % 2]:

        st.button(
            suggestion,
            key=f"suggestion_{index}",
            use_container_width=True,
            on_click=set_suggested_question,
            args=(suggestion,)
        )


# --------------------------------------------------
# 14. Chat interface
# --------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">💬 Chat With Your Data</div>',
    unsafe_allow_html=True
)

st.caption(
    "Ask questions about your uploaded CSV in plain English."
)


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


user_question = st.chat_input(
    "Ask something about your dataset..."
)


question_to_process = user_question

if question_to_process is None:

    question_to_process = st.session_state.pending_question

st.session_state.pending_question = None


# --------------------------------------------------
# 15. Process user question
# --------------------------------------------------

if question_to_process:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question_to_process
        }
    )

    with st.chat_message("user"):

        st.markdown(question_to_process)


    with st.chat_message("assistant"):

        with st.spinner("Analyzing your dataset..."):

            try:

                answer = ask_agent(
                    question_to_process,
                    df
                )

            except Exception as error:

                print("Agent error:", error)

                answer = (
                    "Sorry, I couldn't analyze your question. "
                    "Please try again. Check your API connection "
                    "if the problem continues."
                )

        st.markdown(answer)


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
