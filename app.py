import streamlit as st
import pandas as pd
import io

# Set app title
st.set_page_config(page_title="GSD-121: Sandhub")
st.title("GSD-121: Sandhub")


def process_file(file):
    # Determine file type and read accordingly
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file, header=None)
    elif file.name.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(file, header=None)
    else:
        st.error("Unsupported file format. Please upload a CSV or Excel file.")
        return None

    # Check if the dataframe is empty
    if df.empty:
        st.error("The uploaded file is empty.")
        return None

    # Assign column names to the original data
    df.columns = [
        "Debtor Reference",
        "Document Number",
        "Document Date",
        "Document Balance",
        "Transaction Type",
        "Due Date",
    ]

    # Process the data according to requirements

    # 0. Remove rows where at least one field is empty
    df = df.dropna(how="any")

    # 1. Remove redundant apostrophes from Document Number
    df["Document Number"] = df["Document Number"].str.replace("'", "")

    # 2. Convert Transaction Type: "I" to "INV", "C" to "CRD"
    df["Transaction Type"] = df["Transaction Type"].apply(
        lambda x: "INV"
        if x.strip("'") == "I"
        else ("CRD" if x.strip("'") == "C" else x)
    )

    # 3. Format Document Date as dd/mm/yyyy
    def format_date(date_str):
        try:
            # Try to parse the date
            date_obj = pd.to_datetime(date_str, dayfirst=True)
            # Format as dd/mm/yyyy
            return date_obj.strftime("%d/%m/%Y")
        except Exception:
            # Return original if parsing fails
            return date_str

    df["Document Date"] = df["Document Date"].apply(format_date)

    # 4. Format Document Balance to have 2 decimal places and make negative if Transaction Type is CRD
    df["Document Balance"] = df.apply(
        lambda row: f"-{float(row['Document Balance']):.2f}"
        if row["Transaction Type"] == "CRD"
        else f"{float(row['Document Balance']):.2f}",
        axis=1,
    )

    # 5. Reorder columns and drop Due Date
    result_df = df[
        [
            "Debtor Reference",
            "Transaction Type",
            "Document Number",
            "Document Date",
            "Document Balance",
        ]
    ]

    # 6. Reset the index
    result_df = result_df.reset_index(drop=True)
    
    return result_df


def get_csv_download_link(df):
    # Generate CSV file for download
    csv = df.to_csv(index=False)
    csv_bytes = csv.encode()
    buffer = io.BytesIO(csv_bytes)
    return buffer


# File uploader
st.write("Upload your Excel or CSV file:")
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    # Process the file
    processed_df = process_file(uploaded_file)

    if processed_df is not None:
        # Display the processed data
        st.write("Processed Data:")
        st.dataframe(processed_df)

        # Download button
        csv_buffer = get_csv_download_link(processed_df)
        st.download_button(
            label="Download Processed File",
            data=csv_buffer,
            file_name="processed_data.csv",
            mime="text/csv",
        )
