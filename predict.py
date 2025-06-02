import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

industry_buckets = {
    'Technology': [
        'Software', 'IT Services', 'Business Intelligence (BI) Software',
        'Database & File Management Software', 'Security Software',
        'Telecommunication Equipment', 'Engineering Software',
        'Custom Software & IT Services', 'Technology Hardware, Storage & Peripherals',
        'Content & Collaboration Software', 'Mobile App Development',
        'Storage & System Management Software', 'Multimedia, Games & Graphics Software',
        'Computer Equipment & Peripherals', 'Financial Software',
        'Human Resources Software'
    ],
    'Healthcare': [
        'Health Care Providers & Services', 'Hospitals & Physicians Clinics',
        'Medical Specialists', 'Medical Devices & Equipment',
        'Biotechnology', 'Pharmaceuticals', 'Health Care Equipment & Supplies',
        'Health Care Equipment & Services', 'Healthcare Software',
        'Medical Laboratories & Imaging Centers', 'Vitamins, Supplements & Health Stores',
        'Physicians Clinics', 'Dental Offices', 'Elderly Care Services',
        'Health & Nutrition Products'
    ],
    'Finance': [
        'Banks', 'Banking', 'Capital Markets', 'Lending & Brokerage',
        'Investment Banking', 'Credit Cards & Transaction Processing',
        'Diversified Financial Services', 'Insurance', 'Finance',
        'Venture Capital & Private Equity'
    ],
    'Retail & Consumer': [
        'Retail', 'Retailing', 'Specialty Retail', 'Consumer Services',
        'Food & Beverage', 'Food Products', 'Grocery Retail',
        'Flowers, Gifts & Specialty Stores', 'Drug Stores & Pharmacies',
        'Department Stores, Shopping Centers & Superstores',
        'Home Improvement & Hardware Retail', 'Consumer Electronics & Computers Retail',
        'Apparel & Accessories Retail', 'Toys & Games', 'Personal Products',
        'Cosmetics, Beauty Supply & Personal Care Products'
    ],
    'Manufacturing & Industrials': [
        'Industrial Machinery & Equipment', 'Machinery', 'Engineering',
        'Construction', 'Industrial Conglomerates', 'Electronics',
        'Automotive', 'Automotive Parts', 'Electrical Equipment',
        'Containers & Packaging', 'Wire & Cable', 'Appliances',
        'Engineering Software', 'Manufacturing', 'Automotive Service & Collision Repair',
        'Motor Vehicles', 'Semiconductors & Semiconductor Equipment'
    ],
    'Media & Entertainment': [
        'Media', 'Broadcasting', 'Music Production & Services', 'Sports Teams & Leagues',
        'Performing Arts Theaters', 'Multimedia & Graphic Design',
        'Newspapers & News Services', 'Publishing'
    ],
    'Education': [
        'Education', 'Education Services', 'Colleges & Universities',
        'K-12 Schools', 'Training'
    ],
    'Hospitality & Leisure': [
        'Lodging & Resorts', 'Hotels, Restaurants & Leisure',
        'Restaurants', 'Fitness & Dance Facilities', 'Leisure Products'
    ],
    'Transportation & Logistics': [
        'Airlines', 'Air Freight & Logistics', 'Marine Shipping & Transportation',
        'Road & Rail', 'Car & Truck Rental', 'Freight & Logistics Services',
        'Rail, Bus & Taxi', 'Marine', 'Transportation'
    ],
    'Public Sector & Nonprofit': [
        'Government', 'State', 'Federal', 'Non-Profit & Charitable Organizations',
        'Religious Organizations', 'Membership Organizations', 'Organizations'
    ],
    'Professional Services': [
        'Accounting Services', 'Law Firms & Legal Services',
        'Management Consulting', 'Business Services', 'HR & Staffing',
        'Architecture, Engineering & Design', 'Cleaning Services',
        'Photography Studio', 'Childcare', 'Repair Services',
        'Barber Shops & Beauty Salons', 'Legal Software'
    ],
    'Utilities & Energy': [
        'Utilities', 'Electric Utilities', 'Gas Utilities',
        'Renewable Electricity', 'Energy, Utilities & Waste', 'Water Treatment'
    ],
    'Other': [
        'Unknown'  # You can exclude or keep separately
    ]
}

# Set page config
st.set_page_config(
    page_title="Email Engagement Dashboard",
    page_icon="📧",
    layout="wide"
)

# Add title and description
st.title("📧 Email Engagement Dashboard")
st.markdown("""
This dashboard shows email engagement metrics and lead characteristics.
""")

# Load data
@st.cache_data
def load_data():
    with st.spinner('Loading data...'):
        # Load processed data
        df = df = pd.read_csv('Processed_Cleaned.csv')
        return df

# Main app
def main():
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Industry filter
    # industries = ['All'] + sorted(df['industry'].unique().tolist())
    # selected_industry = st.sidebar.selectbox('Select Industry', industries)

    industry_map = {fine: broad 
                for broad, fines in industry_buckets.items() 
                for fine in fines}

    df['industry_group'] = df['industry'].map(industry_map).fillna('Other')
    industries = ['All'] + sorted(df['industry_group'].unique().tolist())
    selected_industry = st.sidebar.selectbox('Select Industry', industries)
    
    # Lead source filter
    lead_sources = ['All'] + sorted(df['leadsource'].unique().tolist())
    selected_source = st.sidebar.selectbox('Select Lead Source', lead_sources)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_industry != 'All':
        filtered_df = filtered_df[filtered_df['industry_group'] == selected_industry]
    if selected_source != 'All':
        filtered_df = filtered_df[filtered_df['leadsource'] == selected_source]
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Leads", len(filtered_df))
    
    with col2:
        open_rate = (filtered_df['opened'] > 0).mean() * 100
        st.metric("Open Rate", f"{open_rate:.1f}%")
    
    with col3:
        click_rate = (filtered_df['clicked'] > 0).mean() * 100
        st.metric("Click Rate", f"{click_rate:.1f}%")
    
    with col4:
        # avg_age = filtered_df['account_age_days'].mean()
        # st.metric("Avg Account Age (days)", f"{avg_age:.1f}")

        # Count opens per send hour (only rows where opened > 0)
        # Count opens per send‐hour
        counts = (
            filtered_df.loc[filtered_df['opened'] > 0, 'createddate_hour']
            .value_counts()
        )

        # Try to grab the 2nd‐highest hour; if that fails, fall back to the highest; if still empty, None
        try:
            top_hour = counts.index[1]
        except IndexError:
            try:
                top_hour = counts.index[0]
            except IndexError:
                top_hour = None

        # Format for display
        hour_str = f"{int(top_hour)}:00" if top_hour is not None else "No opens"
        st.metric("Hour with Most Opens", hour_str)
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Engagement Metrics", "Lead Characteristics", "Time Analysis", "GenAI Playbook"])
    
    with tab1:
        # Engagement metrics
        st.subheader("Engagement Metrics")
        
        # Open and Click rates by industry
        fig = px.bar(
            filtered_df.groupby('industry_group').agg({
                'opened': 'mean',
                'clicked': 'mean'
            }).reset_index().melt(id_vars=['industry_group'], value_vars=['opened', 'clicked']),
            x='industry_group',
            y='value',
            color='variable',
            title='Open and Click Rates by Industry',
            labels={'value': 'Rate', 'variable': 'Metric'},
            barmode='group'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribution of engagement metrics
        col1, col2 = st.columns(2)
        with col1:
            # Calculate total opens from the filtered DataFrame
            total_opens = (filtered_df['opened'] > 0).sum()

            # Option 1: Big header
            st.header(f"Total Opens: {total_opens}")

        with col2:
            # Calculate total opens from the filtered DataFrame
            total_clicks = (filtered_df['clicked'] > 0).sum()

            # Option 1: Big header
            st.header(f"Total Clicks: {total_clicks}")
        
        # with col2:
        #     fig = px.histogram(
        #         filtered_df[filtered_df['clicked'] > 0],
        #         x='clicked',
        #         title='Distribution of Clicks',
        #         nbins=2
        #     )
        #     st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Lead characteristics
        st.subheader("Lead Characteristics")

        # Industry distribution (exclude the "Other" bucket)
        industry_df = filtered_df[filtered_df['industry_group'] != 'Other']
        
        # Industry distribution
        fig = px.pie(
            industry_df,
            names='industry_group',
            title='Lead Distribution by Industry'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Lead source distribution
        fig = px.bar(
            filtered_df['leadsource'].value_counts().reset_index(),
            x='count',
            y='leadsource',
            title='Lead Distribution by Source',
            labels={'index': 'Lead Source', 'leadsource': 'Count'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Time analysis
        st.subheader("Time Analysis")
        
        # Account age distribution
        fig = px.histogram(
            filtered_df,
            x='account_age_days',
            title='Distribution of Account Age',
            nbins=50
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Days since last activity
        fig = px.histogram(
            filtered_df,
            x='days_since_last_activity',
            title='Distribution of Days Since Last Activity',
            nbins=50
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # load once
        prompts_df = pd.read_csv('genai_playbook_prompts_website.csv')
        # industry_map = {fine: broad 
        #         for broad, fines in industry_buckets.items() 
        #         for fine in fines}
        # prompts_df['industry_group'] = (
        #     prompts_df['industry_group']
        #     .map(industry_map)
        #     .fillna('Other')
        # )
        st.header("GenAI Playbook Prompts")
        st.write("Below are the personas we’ve identified and example prompts to use with them.")

        # apply the industry_group filter
        if selected_industry == "All":
            df_playbook = prompts_df
        else:
            df_playbook = prompts_df[prompts_df['industry_group'] == selected_industry]

        # iterate over each row of the CSV
        for _, row in df_playbook.iterrows():
            # use the persona column as the expander title
            with st.expander(row["persona"].split("\n")[0]):  
                # show the full persona text
                st.markdown(f"**Persona Details:**  \n{row['persona']}")
                # show the playbook prompt
                # st.markdown(f"**Prompt:**  \n{row['playbook_prompt']}")

        # # apply the industry_group filter
        # if selected_industry == "All":
        #     df_playbook = prompts_df
        # else:
        #     df_playbook = prompts_df[prompts_df['industry_group'] == selected_industry]

        # # now only show the prompts for that industry
        # for i, prompt in enumerate(df_playbook['playbook_prompt'], start=1):
        #     st.subheader(f"Prompt {i}")
        #     st.write(prompt)


    

if __name__ == "__main__":
    main()




