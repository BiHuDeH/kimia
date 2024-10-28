import pandas as pd
import streamlit as st

def process_data(file):
    # Load the data
    df = pd.read_excel(file, skiprows=2)
    df.columns = ['Index', 'Branch Code', 'Branch', 'Date', 'Time', 'Document Number', 
                  'Receipt Number', 'Check Number', 'Description', 'Withdrawal', 
                  'Deposit', 'Balance', 'Notes']
    
    # Drop any rows without a date (non-data rows)
    df = df.dropna(subset=['Date'])

    # Filters for Card-to-Card and Fee based on specific keywords in "Description"
    card_to_card_filter = df['Description'].str.contains("انتقال از", na=False)
    fee_filter = df['Description'].str.contains("کارمزد", na=False)
    
    # Group by date and aggregate data for Card-to-Card and Fee
    card_to_card_sum = df[card_to_card_filter].groupby('Date')['Deposit'].sum()
    fee_sum = df[fee_filter].groupby('Date')['Withdrawal'].sum()

    # Create the report DataFrame with aligned data
    report = pd.DataFrame({
        'Date': card_to_card_sum.index,
        'Card_to_Card': card_to_card_sum.values,
        'Fee': fee_sum.reindex(card_to_card_sum.index, fill_value=0).values  # Align fee_sum by date
    })

    # Calculate Sales and Tax
    report['Sales'] = report['Card_to_Card'] / 1.1  # Removing 10% tax
    report['Tax'] = report['Card_to_Card'] - report['Sales']  # Calculating Tax as 10% of Sales
    
    # Format values with thousands separator for better readability
    report[['Card_to_Card', 'Sales', 'Tax', 'Fee']] = report[['Card_to_Card', 'Sales', 'Tax', 'Fee']].applymap(lambda x: f"{int(x):,}")

    # Set final column names in Persian for display
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
