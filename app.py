import pandas as pd
import streamlit as st

def process_data(file):
    # Load the data
    df = pd.read_excel(file)
    df.columns = ['Index', 'Branch Code', 'Branch', 'Date', 'Time', 'Document Number', 
                  'Receipt Number', 'Check Number', 'Description', 'Withdrawal', 
                  'Deposit', 'Balance', 'Notes']
    
    # Filters for Card-to-Card and Fee based on specific keywords
    card_to_card_filter = df['Description'].str.contains('انتقال از', na=False)
    fee_filter = df['Description'].str.contains('کارمزد', na=False)
    
    # Group by date and aggregate data
    report = df.groupby('Date').agg(
        Card_to_Card=('Deposit', lambda x: x[card_to_card_filter].sum()),
        Fee=('Withdrawal', lambda x: x[fee_filter].sum())
    ).reset_index()
    
    # Calculate Sales and Tax from Card-to-Card
    report['Sales'] = report['Card_to_Card'] / 1.1  # Calculating Sales by removing 10% Tax
    report['Tax'] = report['Card_to_Card'] - report['Sales']  # Calculating Tax as 10% of Sales
    
    # Format values with thousands separator for better readability
    report['Card_to_Card'] = report['Card_to_Card'].apply(lambda x: f"{int(x):,}")
    report['Sales'] = report['Sales'].apply(lambda x: f"{int(x):,}")
    report['Tax'] = report['Tax'].apply(lambda x: f"{int(x):,}")
    report['Fee'] = report['Fee'].apply(lambda x: f"{int(x):,}")

    # Total row calculations without affecting formatted report values
    total_row = pd.DataFrame({
        'Date': [f"{report['Date'].nunique()} days"],
        'Card_to_Card': [f"{int(df['Deposit'][card_to_card_filter].sum()):,}"],
        'Sales': [f"{int(df['Deposit'][card_to_card_filter].sum() / 1.1):,}"],  # Total Sales
        'Tax': [f"{int(df['Deposit'][card_to_card_filter].sum() - (df['Deposit'][card_to_card_filter].sum() / 1.1)):,}"],  # Total Tax
        'Fee': [f"{int(df['Withdrawal'][fee_filter].sum()):,}"]
    })

    # Append the total row to the report DataFrame
    report = pd.concat([report, total_row], ignore_index=True)

    # Set final column names in English for simplicity
    report.columns = ['Date', 'Card_to_Card', 'Sales', 'Tax', 'Fee']
    
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