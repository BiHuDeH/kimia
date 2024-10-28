import streamlit as st
import pandas as pd
import io

# Set up page title and styling
st.set_page_config(page_title="گزارش تراکنش", layout="centered")
st.markdown("<h1 style='text-align: center; color: #333;'>گزارش تراکنش</h1>", unsafe_allow_html=True)

# Section: File Upload
st.markdown("### بارگذاری فایل")
uploaded_file = st.file_uploader("لطفا فایل اکسل خود را بارگذاری کنید", type=["xlsx"])

# Process data and generate report
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
    total_row = {
        'Date': f"{report['Date'].nunique()} روز",
        'Card_to_Card': f"{int(df['Deposit'][deposit_filter].sum()):,}",
        'فروش': f"{int(report['فروش'].str.replace(',', '').astype(int).sum()):,}",
        'مالیات': f"{int(report['مالیات'].str.replace(',', '').astype(int).sum()):,}",
        'Fee': f"{int(df['Withdrawal'][withdrawal_filter].sum()):,}"
    }

    # Append total row to the report DataFrame
    report = report.append(total_row, ignore_index=True)
    report.columns = ['تاریخ', 'کارت به کارت', 'فروش', 'مالیات', 'کارمزد']
    
    return report

# Generate report if file is uploaded
if uploaded_file:
    with st.spinner("در حال پردازش گزارش..."):
        report = process_data(uploaded_file)
    
    # Display the report in the app
    st.markdown("### گزارش روزانه تراکنش‌ها")
    st.dataframe(report.style.set_properties(**{'text-align': 'center'}).set_table_styles(
        [{'selector': 'th', 'props': [('font-weight', 'bold'), ('background-color', '#f0f0f0')]}]
    ), height=400)
    
    # Convert report to Excel for download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        report.to_excel(writer, index=False, sheet_name='گزارش')
    
    # Add download button
    st.download_button(
        label="📥 دانلود گزارش به صورت فایل اکسل",
        data=output.getvalue(),
        file_name="گزارش_تراکنش_روزانه.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="روی دکمه کلیک کنید تا گزارش دانلود شود"
    )
else:
    st.info("برای مشاهده گزارش، ابتدا فایل اکسل را بارگذاری کنید.")
