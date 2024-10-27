import streamlit as st
import pandas as pd
import io

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
        Card_to_Card=('Deposit', lambda x: x[deposit_filter].sum()),
        Fee=('Withdrawal', lambda x: x[withdrawal_filter].sum())
    ).reset_index()
    
    # Calculate the "فروش" column (Toy Price) by dividing "کارت به کارت" by 1.1
    report['فروش'] = report['Card_to_Card'] / 1.1
    
    # Calculate the "مالیات" column as the difference between "کارت به کارت" and "فروش"
    report['مالیات'] = report['Card_to_Card'] - report['فروش']
    
    # Rename columns in Persian for the output report and arrange in the specified order
    report = report[['Date', 'Card_to_Card', 'فروش', 'مالیات', 'Fee']]
    report.columns = ['تاریخ', 'کارت به کارت', 'فروش', 'مالیات', 'کارمزد']
    
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
    
    # Set up download button
    st.download_button(
        label="دانلود گزارش به صورت فایل اکسل",
        data=output.getvalue(),
        file_name="گزارش_تراکنش_روزانه.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
