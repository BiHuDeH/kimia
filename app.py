def process_data(df):
    # Drop any rows without a date (non-data rows)
    df = df.dropna(subset=['Date'])

    # Filters for Card-to-Card, Fee, and Daily Withdrawal based on keywords in "Description"
    card_to_card_filter = df['Description'].str.contains("انتقال از", na=False)
    fee_filter = df['Description'].str.contains("کارمزد", na=False)
    daily_withdrawal_filter = df['Description'].str.contains("انتقال وجه", na=False)
    
    # Group by date and aggregate data for Card-to-Card, Fee, and Daily Withdrawal
    card_to_card_sum = df[card_to_card_filter].groupby('Date')['Deposit'].sum()
    fee_sum = df[fee_filter].groupby('Date')['Withdrawal'].sum()
    daily_withdrawal_sum = df[daily_withdrawal_filter].groupby('Date')['Withdrawal'].sum()

    # Create the report DataFrame with aligned data
    report = pd.DataFrame({
        'Date': card_to_card_sum.index,
        'Card_to_Card': card_to_card_sum.values,
        'Fee': fee_sum.reindex(card_to_card_sum.index, fill_value=0).values,  # Align fee_sum by date
        'Daily_Withdrawal': daily_withdrawal_sum.reindex(card_to_card_sum.index, fill_value=0).values  # Align daily_withdrawal by date
    })

    # Calculate Sales and Tax
    report['Sales'] = report['Card_to_Card'] / 1.1  # Removing 10% tax
    report['Tax'] = report['Card_to_Card'] - report['Sales']  # Calculating Tax as 10% of Sales
    
    # Format values with two decimal places and thousands separator for readability
    report[['Card_to_Card', 'Fee', 'Daily_Withdrawal', 'Sales', 'Tax']] = report[['Card_to_Card', 'Fee', 'Daily_Withdrawal', 'Sales', 'Tax']].applymap(lambda x: f"{x:,.2f}")

    # Set final column names in Persian for display
    report.columns = ['تاریخ', 'کارت به کارت', 'کارمزد', 'برداشت روز', 'فروش', 'مالیات']
    
    return report
