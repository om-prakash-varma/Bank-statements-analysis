import matplotlib
matplotlib.use('Agg')  # << Force non-GUI backend for image generation

import pandas as pd
import os
from datetime import datetime

def analyze_sbi_statement(file_path):

    # === Create Output Folder for This Run ===
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_folder = os.path.join("reports", f"SBI_Report_{timestamp}")
    os.makedirs(output_folder, exist_ok=True)

    # === Step 1: Load Clean CSV (skip garbage rows) ===
    df = pd.read_csv(file_path, skiprows=20)

    # === Step 2: Clean & Rename Columns ===
    df.columns = [col.strip() for col in df.columns]  # remove extra spaces

    # Rename date column for ease
    df.rename(columns={'Txn Date': 'Date'}, inplace=True)

    # === Step 3: Drop Useless Columns ===
    columns_to_drop = ['Value Date', 'Description', 'Ref No./Cheque No.', 'Balance']
    df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True, errors='ignore')

    # === Step 4: Parse Date & Amount Columns ===
    df['Date'] = pd.to_datetime(df['Date'], format='%d %b %Y', errors='coerce')
    df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
    df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)

    # === Step 5: Add Month Column ===
    df['Month'] = df['Date'].dt.to_period('M').astype(str)

    # === Step 6: Generate Summary ===
    total_in    = df['Credit'].sum()
    total_out = df['Debit'].sum()
    net_change = total_in - total_out

    summary_df = pd.DataFrame({
        'Metric': ['Total Money In', 'Total Money Out', 'Net Change'],
        'Amount': [total_in, total_out, net_change]
    })

    # === Step 7: Monthly Summary ===
    monthly_summary = df.groupby('Month')[['Debit', 'Credit']].sum().reset_index()

    # === Step 8: Advanced Analysis ===

    # Extract year and month separately
    df['Year'] = df['Date'].dt.year
    df['MonthOnly'] = df['Date'].dt.month

    # Group by Year & Month to get monthly totals
    month_analysis = df.groupby(['Year', 'MonthOnly']).agg({
        'Debit': 'sum',
        'Credit': 'sum'
    }).reset_index()

    # Label months
    import calendar
    month_analysis['MonthName'] = month_analysis['MonthOnly'].apply(lambda x: calendar.month_abbr[x])

    # Identify loss months
    month_analysis['SpentMoreThanEarned'] = month_analysis['Debit'] > month_analysis['Credit']

    # Split year-wise data
    years_available = sorted(month_analysis['Year'].unique())

    insights = []
    years_available = sorted(month_analysis['Year'].unique())
    month_analysis['Net'] = month_analysis['Credit'] - month_analysis['Debit']

    if len(years_available) == 1:
        year = years_available[0]
        overspent = month_analysis[month_analysis['Net'] < 0]
        if overspent.empty:
            insights.append(f"🎉 Great job! In {year}, you did not spend more than you earned in any month.")
        else:
            insights.append(f"⚠ In {year}, you spent more than you earned in {len(overspent)} month(s):")
            for _, row in overspent.iterrows():
                insights.append(
                    f" - In {row['MonthName']} {year}, your account change went negative (Credit: ₹{row['Credit']:.2f}, Debit: ₹{row['Debit']:.2f})"
                )
    else:
        for y in years_available:
            overspent = month_analysis[(month_analysis['Year'] == y) & (month_analysis['Net'] < 0)]
            if overspent.empty:
                insights.append(f"🎉 In {y}, you did not spend more than you earned in any month.")
            else:
                insights.append(f"⚠ In {y}, you spent more than you earned in {len(overspent)} month(s):")
                for _, row in overspent.iterrows():
                    insights.append(
                        f" - In {row['MonthName']} {y}, your account change went negative (Credit: ₹{row['Credit']:.2f}, Debit: ₹{row['Debit']:.2f})"
                    )
    # === Cross-Year Negative Month Comparison ===
    if len(years_available) >= 2:
        insights.append("\n📊 Common Months with Negative Net Change Across Years:")

        # Filter only negative months
        neg_months = month_analysis[month_analysis['Net'] < 0]

        # Group by MonthOnly to find overlaps across years
        month_groups = neg_months.groupby('MonthOnly')

        common_neg_months = []

        for month, group in month_groups:
            years_with_loss = group['Year'].unique()
            if len(years_with_loss) >= 2:
                common_neg_months.append((calendar.month_abbr[month], sorted(years_with_loss)))

        if common_neg_months:
            for month_name, years in common_neg_months:
                year_list = ', '.join(str(y) for y in years)
                insights.append(f" - In {month_name}, your account went negative in years: {year_list}.")
        else:
            insights.append("🎉 No common months with negative net change across years.")

    # Function to save the text into a white image
    from PIL import Image, ImageDraw, ImageFont

    def save_summary_as_image(text_lines, output_path):
        # A4 at 300 DPI = 2480 x 3508 pixels
        width, height = 2480, 3508
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 40)  # Bigger font now
        except:
            font = ImageFont.load_default()

        x = 100
        y = 100
        line_spacing = 60

        for line in text_lines:
            draw.text((x, y), line, fill="black", font=font)
            y += line_spacing

        img.save(output_path)

    # Chart generation:
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Use a cleaner style
    sns.set_style("whitegrid")

    # === Chart 1: Bar Chart (Credit vs Debit by Month) ===

    # === Bar Chart: Credit vs Debit per Month (Side by Side) ===
    import numpy as np
    plt.figure(figsize=(10, 6))
    monthly_summary_sorted = monthly_summary.sort_values("Month")
    x = monthly_summary_sorted['Month']
    credit = monthly_summary_sorted['Credit']
    debit = monthly_summary_sorted['Debit']

    x_pos = np.arange(len(x))
    bar_width = 0.4

    plt.bar(x_pos - bar_width/2, credit, width=bar_width, label='Credit (In)', color='green', alpha=0.8)
    plt.bar(x_pos + bar_width/2, debit, width=bar_width, label='Debit (Out)', color='red', alpha=0.8)

    plt.xticks(ticks=x_pos, labels=x, rotation=45)
    plt.title("Credit vs Debit by Month")
    plt.xlabel("Month")
    plt.ylabel("Amount (₹)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "bar_credit_debit.png"))
    plt.close()

    # === Chart 2: Line Chart (Net Change Over Time) ===
    plt.figure(figsize=(10, 6))
    net_change_line = credit - debit
    plt.plot(x, net_change_line, marker='o', linestyle='-', color='blue')
    plt.xticks(rotation=45)
    plt.title("Net Change (Credit - Debit) Over Time")
    plt.xlabel("Month")
    plt.ylabel("Net Change (₹)")
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "line_net_change.png"))
    plt.close()

    # === Chart 3: Pie Chart (Top Spending Categories) ===
    # Requires 'Description' column
    if 'Description' in df.columns and not df['Description'].isnull().all():
        top_spends = df[df['Debit'] > 0]
        top_spends['Category'] = top_spends['Description'].str.extract(r'(?i)(UPI|ATM|NEFT|IMPS|POS|Online|Recharge|Rent|Amazon|Flipkart|IRCTC|ZOMATO|SWIGGY|Google|PhonePe)', expand=False).fillna('Others')
        category_summary = top_spends.groupby('Category')['Debit'].sum().sort_values(ascending=False)
        category_summary = category_summary.head(7)  # top 7 categories

        plt.figure(figsize=(7, 7))
        plt.pie(category_summary, labels=category_summary.index, autopct='%1.1f%%', startangle=140)
        plt.title("Spending by Category")
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, "pie_spending_categories.png"))
        plt.close()

    # === Step 9: Top 10 Expenses ===
    top_expenses = df[df['Debit'] > 0].sort_values(by='Debit', ascending=False).head(10)

    # === Step 10: Write to Excel ===
    min_year = df['Date'].min().year
    max_year = df['Date'].max().year
    output_path = os.path.join(output_folder, f"SBI_Analysis_{min_year}_{max_year}.xlsx")

    #  Save everything to Excel with insights on last sheet
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        # 1. Write Summary and Raw Data
        summary_df.to_excel(writer, sheet_name='Raw Data', startrow=0, index=False)
        df.to_excel(writer, sheet_name='Raw Data', startrow=5, index=False)

        # 2. Write Summary Tabs
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        monthly_summary.to_excel(writer, sheet_name='Monthly Summary', index=False)
        top_expenses.to_excel(writer, sheet_name='Top Expenses', index=False)

        # 3. Write Insights Tab – FORCE IT
        # Force 2D DataFrame (sometimes single column lists bug out)
        insights_df = pd.DataFrame(insights, columns=["Insight"])
        print("📢 Writing Insights Sheet...")  # Confirm this prints
        insights_df.to_excel(writer, sheet_name='Insights', index=False)
        
        # Embed Charts into Excel
        workbook = writer.book
        worksheet = workbook.add_worksheet("Charts")
        writer.sheets["Charts"] = worksheet

        # Insert bar chart
        worksheet.insert_image("A1", os.path.join(output_folder, "bar_credit_debit.png"),{'x_scale': 0.8, 'y_scale': 0.8})

        # Insert line chart
        worksheet.insert_image("A20", os.path.join(output_folder, "line_net_change.png"),{'x_scale': 0.8, 'y_scale': 0.8})

        # Insert pie chart if it exists
        pie_path = os.path.join(output_folder, "pie_spending_categories.png")
        if os.path.exists(pie_path):
            worksheet.insert_image("A40", pie_path,{'x_scale': 0.8, 'y_scale': 0.8})

    return {
    "total_in": total_in,
    "total_out": total_out,
    "net_change": net_change,
    "insights": insights,
    "bar_chart": os.path.join(output_folder, "bar_credit_debit.png"),
    "line_chart": os.path.join(output_folder, "line_net_change.png"),
    "pie_chart": pie_path if os.path.exists(pie_path) else None,
    "excel_file": output_path
}