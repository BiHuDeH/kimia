import pandas as pd
import streamlit as st
from io import BytesIO

def process_data(df):
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

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    output.seek(0)  # Set the pointer to the beginning of the stream
    return output.getvalue()

# Streamlit main app setup
def main():
    st.title("Financial Data Report")
    
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file:
        # Load and process the data
        df = pd.read_excel(uploaded_file, skiprows=2)
        df.columns = ['Index', 'Branch Code', 'Branch', 'Date', 'Time', 'Document Number', 
                      'Receipt Number', 'Check Number', 'Description', 'Withdrawal', 
                      'Deposit', 'Balance', 'Notes']
        
        report = process_data(df)

        # Convert the report DataFrame to Excel for download
        excel_data = convert_df_to_excel(report)

        # Create columns to arrange Preview and Download buttons side by side
        col1, col2 = st.columns(2)

        with col1:
            # Preview button: Show the report in a table format only when clicked
            if st.button("Preview Report"):
                st.write("### Report Preview")
                st.dataframe(report)

        with col2:
            # Download button
            st.download_button(
                label="Download Report as Excel",
                data=excel_data,
                file_name="Financial_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
