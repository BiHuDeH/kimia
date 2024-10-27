import streamlit as st
import pandas as pd
import io

# Title for Streamlit app
st.title("گزارش تراکنش")

# Upload file
uploaded_file = st.file_uploader("لطفا فایل اکسل خود را بارگذاری کنید", type=["xlsx"])

# Function to process the uploaded file
def process_data(file):
    # Read Excel file
    df = pd.read_excel(file)
    
    # Rename columns internally for easier processing
    df.columns = ['Index', 'Branch Code', 'Branch', 'Date', 'Time', 'Document Number', 
                  'Receipt Number', 'Check Number', 'Description', 'Withdrawal', 
                  'Deposit', 'Balance', 'Notes']
    
    # Define filters for Persian keywords
    deposit_filter = df['Description'].str.contains('کارت', na=False)
    withdrawal_filter = df['Description'].str.contains('کارمزد', na=False)
    
    # Group by date and sum deposits and withdrawals based on filters
    report = df.groupby('Date').agg(
        Total_Deposits=('Deposit', lambda x: x[deposit_filter].sum()),
        Total_Withdrawals=('Withdrawal', lambda x: x[withdrawal_filter].sum())
    ).reset_index()
    
    # Rename columns in Persian for the output report
    report.columns = ['تاریخ', 'جمع واریزی‌ها', 'جمع برداشت‌ها']
    
    return report

if uploaded_file:
    # Process the file and generate the report
    report = process_data(uploaded_file)
    
    # Display the report in the app
    st.write("گزارش روزانه تراکنش‌ها", report)
    
    # Convert report to Excel for download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        report.to_excel(writer, index=False, sheet_name='گزارش')
        writer.save()
    
    # Set up download button
    st.download_button(
        label="دانلود گزارش به صورت فایل اکسل",
        data=output.getvalue(),
        file_name="گزارش_تراکنش_روزانه.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
