import pandas as pd
import streamlit as st

def process_data(file):
    # Load the data
    df = pd.read_excel(file)
    df.columns = ['Index', 'Branch Code', 'Branch', 'Date', 'Time', 'Document Number', 
                  'Receipt Number', 'Check Number', 'Description', 'Withdrawal', 
                  'Deposit', 'Balance', 'Notes']
    
    # Filters for deposits and withdrawals based on Persian descriptions
    deposit_filter = df['Description'].str.contains('کارت', na=False)
    withdrawal_filter = df['Description'].str.contains('کارمزد', na=False)
    
    # Group and calculate sums for relevant fields
    report = df.groupby('Date').agg(
        Card_to_Card=('Deposit', lambda x: x[deposit_filter].sum()),
        Fee=('Withdrawal', lambda x: x[withdrawal_filter].sum())
    ).reset_index()
    
    # Calculate sales and tax
    report['فروش'] = report['Card_to_Card'] / 1.1  # Deducting 10% tax
    report['مالیات'] = report['Card_to_Card'] - report['فروش']
    
    # Format values with thousands separator and no decimal points
    report['Card_to_Card'] = report['Card_to_Card'].apply(lambda x: f"{int(x):,}")
    report['فروش'] = report['فروش'].apply(lambda x: f"{int(x):,}")
    report['مالیات'] = report['مالیات'].apply(lambda x: f"{int(x):,}")
    report['Fee'] = report['Fee'].apply(lambda x: f"{int(x):,}")

    # Calculate total row values without affecting the formatted report values
    total_row = pd.DataFrame({
        'Date': [f"{report['Date'].nunique()} روز"],
        'Card_to_Card': [f"{int(df['Deposit'][deposit_filter].sum()):,}"],
        'فروش': [f"{int(df['Deposit'][deposit_filter].sum() / 1.1):,}"],  # Corrected sales calculation
        'مالیات': [f"{int(df['Deposit'][deposit_filter].sum() - (df['Deposit'][deposit_filter].sum() / 1.1)):,}"],  # Corrected tax calculation
        'Fee': [f"{int(df['Withdrawal'][withdrawal_filter].sum()):,}"]
    })

    # Concatenate the total row to the report DataFrame
    report = pd.concat([report, total_row], ignore_index=True)

    # Ensure correct column names and order based on the screenshot provided
    report.columns = ['تاریخ', 'کارت به کارت', 'کارمزد', 'فروش', 'مالیات']
    
    return report

# Streamlit main app setup
def main():
    st.title("Financial Data Report")
    
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    if uploaded_file:
        # Process and display the data
        report = process_data(uploaded_file)
        st.write("### Processed Report")
        st.dataframe(report)

if __name__ == "__main__":
    main()