# import os
# import json
# import pandas as pd
# import streamlit as st
# from dotenv import load_dotenv
# import gspread
# from google.oauth2.service_account import Credentials

# load_dotenv()

# # Configure page
# st.set_page_config(page_title="Retail Margin Calculator", page_icon="🚗", layout="wide")

# st.title("🚗 Retail Margin Calculator")
# st.markdown("---")

# # Google Sheets authentication
# def get_sheet_data():
#     try:
#         # Load service account credentials
#         scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        
#         # Try Streamlit secrets first (for cloud deployment), then local file
#         try:
#             creds_dict = json.loads(st.secrets["google_credentials"])
#         except:
#             # Local development: load from service_account.json
#             with open('service_account.json', 'r') as f:
#                 creds_dict = json.load(f)
        
#         credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
        
#         # Authorize and access the sheet
#         gc = gspread.authorize(credentials)
#         spreadsheet_id = os.getenv("SPREADSHEET_ID")
#         sheet = gc.open_by_key(spreadsheet_id).worksheet("Procurment_Backup")
        
#         # Get all data - read raw data to handle duplicate headers
#         all_data = sheet.get_all_values()
        
#         # Use first row as headers, but make them unique
#         headers = all_data[0]
#         seen = {}
#         unique_headers = []
#         for i, h in enumerate(headers):
#             if h in seen:
#                 seen[h] += 1
#                 unique_headers.append(f"{h}_{seen[h]}")
#             else:
#                 seen[h] = 1
#                 unique_headers.append(h)
        
#         # Create DataFrame with unique headers
#         df = pd.DataFrame(all_data[1:], columns=unique_headers)
#         return df
#     except Exception as e:
#         st.error(f"Error accessing Google Sheet: {str(e)}")
#         return None

# # Main app
# registration_number = st.text_input("Enter Registration Number:", placeholder="e.g., ABC1234")

# # Initialize session state for storing vehicle data
# if 'vehicle_data' not in st.session_state:
#     st.session_state.vehicle_data = None
#     st.session_state.display_columns = None

# if st.button("Search", type="primary"):
#     if registration_number:
#         with st.spinner("Fetching data..."):
#             df = get_sheet_data()
            
#             if df is not None and not df.empty:
#                 # Search for the registration number (assuming it's in one of the columns)
#                 result = df[df.apply(lambda row: registration_number.upper() in str(row.values).upper(), axis=1)]
                
#                 if not result.empty:
#                     st.success(f"Found {len(result)} record(s)")
                    
#                     # Display the required columns
#                     # Column mappings based on user requirements:
#                     # AC -> Concat Rank & Vehicle Number
#                     # AI -> Final MMVF
#                     # AA -> Expected Selling Price To Customer
#                     # AB -> Margin %
#                     # K -> Seller Name
#                     # G -> Ageing1
#                     # Y -> New Landed Cost Including all
#                     # Z -> Procurement Price
                    
#                     display_columns = {
#                         'Concat Rank & Vehicle Number': None,  # AC (column 28)
#                         'Final MMVF': None,  # AI (column 34)
#                         'Expected Selling Price To Customer': None,  # AA (column 26)
#                         'Margin %': None,  # AB (column 27)
#                         'Seller Name': None,  # K (column 10)
#                         'Ageing1': None,  # G (column 6)
#                         'New Landed Cost Including all': None,  # Y
#                         'Procurement Price': None  # Z
#                     }
                    
#                     # Try to map by column index if column names don't match
#                     if len(result.columns) > 34:
#                         display_columns['Concat Rank & Vehicle Number'] = result.columns[28]  # AC
#                         display_columns['Final MMVF'] = result.columns[34]  # AI
#                         display_columns['Expected Selling Price To Customer'] = result.columns[26]  # AA
#                         display_columns['Margin %'] = result.columns[27]  # AB
#                         display_columns['Seller Name'] = result.columns[10]  # K
#                         display_columns['Ageing1'] = result.columns[6]  # G
                    
#                     # Find Y and Z columns by name
#                     for col in result.columns:
#                         if 'New Landed Cost Including all' in str(col):
#                             display_columns['New Landed Cost Including all'] = col
#                         if 'Procurement Price' in str(col):
#                             display_columns['Procurement Price'] = col
                    
#                     # Store in session state
#                     st.session_state.vehicle_data = result.iloc[0]
#                     st.session_state.display_columns = display_columns
                    
#                     # Create display dataframe
#                     display_data = []
#                     for idx, row in result.iterrows():
#                         # Get margin value and reduce by 2%
#                         margin_value = row.get(display_columns['Margin %'], 'N/A')
#                         if margin_value != 'N/A' and margin_value:
#                             try:
#                                 margin_clean = str(margin_value).replace('%', '').strip()
#                                 margin_float = float(margin_clean)
#                                 adjusted_margin = margin_float - 2
#                                 adjusted_margin = round(adjusted_margin, 2)
#                                 margin_value = f"{adjusted_margin}%"
#                             except:
#                                 margin_value = margin_value
                        
#                         display_data.append({
#                             'Concat Rank & Vehicle Number': row.get(display_columns['Concat Rank & Vehicle Number'], 'N/A'),
#                             'Final MMVF': row.get(display_columns['Final MMVF'], 'N/A'),
#                             'Expected Selling Price To Customer': row.get(display_columns['Expected Selling Price To Customer'], 'N/A'),
#                             'Margin %': margin_value,
#                             'Seller Name': row.get(display_columns['Seller Name'], 'N/A'),
#                             'Ageing1': row.get(display_columns['Ageing1'], 'N/A')
#                         })
                    
#                     display_df = pd.DataFrame(display_data)
#                     st.session_state.display_df = display_df
#                 else:
#                     st.warning(f"No records found for Registration Number: {registration_number}")
#                     st.session_state.vehicle_data = None
#     else:
#         st.warning("Please enter a Registration Number")

# # Display vehicle details if we have data
# if st.session_state.vehicle_data is not None:
#     st.dataframe(st.session_state.display_df, use_container_width=True, hide_index=True)
    
#     # Add price input field below vehicle details
#     st.markdown("---")
#     st.subheader("Calculate Expected Margin")
#     user_price = st.number_input("Paste your price:", min_value=0.0, step=100.0, format="%.2f", key="user_price")
    
#     # Add a calculate button
#     if st.button("Calculate", type="secondary"):
#         if user_price > 0:
#             # Get the first row's values for Y and Z from session state
#             row = st.session_state.vehicle_data
#             display_columns = st.session_state.display_columns
            
#             y_value = row.get(display_columns['New Landed Cost Including all'], 0)
#             z_value = row.get(display_columns['Procurement Price'], 0)
            
#             # Convert to float
#             try:
#                 y_float = float(str(y_value).replace(',', '').strip())
#                 z_float = float(str(z_value).replace(',', '').strip())
#             except:
#                 y_float = 0
#                 z_float = 0
            
#             # Calculate internally
#             margin_for_gst = user_price - z_float
#             gst_amount = margin_for_gst - (margin_for_gst / 1.18)
#             margin_net_of_gst = user_price - y_float - gst_amount
            
#             # Expected Margin (subtract 2% as per requirement)
#             denominator = user_price - gst_amount
#             if denominator != 0:
#                 expected_margin = (margin_net_of_gst / denominator) * 100
#                 expected_margin = expected_margin - 2  # Subtract 2%
#                 expected_margin = round(expected_margin, 2)
#                 st.metric(label="Expected Margin", value=f"{expected_margin}%")
#             else:
#                 st.error("Cannot calculate Expected Margin: Division by zero")
#         else:
#             st.warning("Please enter a price value")

# # Add instructions
# st.markdown("---")
# st.info("💡 **Note:** This application securely fetches data from Google Sheets using service account authentication. Your sheet credentials are never exposed.")

import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

# Configure page
st.set_page_config(page_title="Retail Margin Calculator", page_icon="🚗", layout="wide")

st.title("🚗 Retail Margin Calculator")
st.markdown("---")

# Google Sheets authentication
def get_sheet_data():
    try:
        # Load service account credentials
        scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        
        # Try Streamlit secrets first (for cloud deployment), then local file
        try:
            creds_dict = json.loads(st.secrets["google_credentials"])
        except:
            # Local development: load from service_account.json
            with open('service_account.json', 'r') as f:
                creds_dict = json.load(f)
        
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
        
        # Authorize and access the sheet
        gc = gspread.authorize(credentials)
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        sheet = gc.open_by_key(spreadsheet_id).worksheet("Procurment_Backup")
        
        # Get all data - read raw data to handle duplicate headers
        all_data = sheet.get_all_values()
        
        # Use first row as headers, but make them unique
        headers = all_data[0]
        seen = {}
        unique_headers = []
        for i, h in enumerate(headers):
            if h in seen:
                seen[h] += 1
                unique_headers.append(f"{h}_{seen[h]}")
            else:
                seen[h] = 1
                unique_headers.append(h)
        
        # Create DataFrame with unique headers
        df = pd.DataFrame(all_data[1:], columns=unique_headers)
        return df
    except Exception as e:
        st.error(f"Error accessing Google Sheet: {str(e)}")
        return None

# Main app
registration_number = st.text_input("Enter Registration Number:", placeholder="e.g., ABC1234")

# Initialize session state for storing vehicle data
if 'vehicle_data' not in st.session_state:
    st.session_state.vehicle_data = None
    st.session_state.display_columns = None

if st.button("Search", type="primary"):
    if registration_number:
        with st.spinner("Fetching data..."):
            df = get_sheet_data()
            
            if df is not None and not df.empty:
                # Search for the registration number (assuming it's in one of the columns)
                result = df[df.apply(lambda row: registration_number.upper() in str(row.values).upper(), axis=1)]
                
                if not result.empty:
                    st.success(f"Found {len(result)} record(s)")
                    
                    # Display the required columns
                    # Column mappings based on user requirements:
                    # AC -> Concat Rank & Vehicle Number
                    # AI -> Final MMVF
                    # AA -> Expected Selling Price To Customer
                    # AB -> Margin %
                    # K -> Seller Name
                    # G -> Ageing1
                    # X -> Final Auction Won Status
                    # Y -> New Landed Cost Including all
                    # Z -> Procurement Price
                    
                    display_columns = {
                        'Concat Rank & Vehicle Number': None,  # AC (column 28)
                        'Final MMVF': None,  # AI (column 34)
                        'Expected Selling Price To Customer': None,  # AA (column 26)
                        'Margin %': None,  # AB (column 27)
                        'Seller Name': None,  # K (column 10)
                        'Ageing1': None,  # G (column 6)
                        'Final Auction Won Status': None,  # X (column 23)
                        'New Landed Cost Including all': None,  # Y
                        'Procurement Price': None  # Z
                    }
                    
                    # Try to map by column index if column names don't match
                    if len(result.columns) > 34:
                        display_columns['Concat Rank & Vehicle Number'] = result.columns[28]  # AC
                        display_columns['Final MMVF'] = result.columns[34]  # AI
                        display_columns['Expected Selling Price To Customer'] = result.columns[26]  # AA
                        display_columns['Margin %'] = result.columns[27]  # AB
                        display_columns['Seller Name'] = result.columns[10]  # K
                        display_columns['Ageing1'] = result.columns[6]  # G
                        display_columns['Final Auction Won Status'] = result.columns[23]  # X
                    
                    # Find X, Y and Z columns by name
                    for col in result.columns:
                        if 'Final Auction Won Status' in str(col):
                            display_columns['Final Auction Won Status'] = col
                        if 'New Landed Cost Including all' in str(col):
                            display_columns['New Landed Cost Including all'] = col
                        if 'Procurement Price' in str(col):
                            display_columns['Procurement Price'] = col
                    
                    # Filter result to only show records where Final Auction Won Status is ATS or Booked
                    if display_columns['Final Auction Won Status']:
                        result = result[
                            result[display_columns['Final Auction Won Status']].str.upper().isin(['ATS', 'BOOKED'])
                        ]
                    
                    # Store in session state
                    st.session_state.vehicle_data = result.iloc[0]
                    st.session_state.display_columns = display_columns
                    
                    # Create display dataframe
                    display_data = []
                    for idx, row in result.iterrows():
                        # Get margin value and reduce by 2%
                        margin_value = row.get(display_columns['Margin %'], 'N/A')
                        if margin_value != 'N/A' and margin_value:
                            try:
                                margin_clean = str(margin_value).replace('%', '').strip()
                                margin_float = float(margin_clean)
                                adjusted_margin = margin_float - 2
                                adjusted_margin = round(adjusted_margin, 2)
                                margin_value = f"{adjusted_margin}%"
                            except:
                                margin_value = margin_value
                        
                        display_data.append({
                            'Concat Rank & Vehicle Number': row.get(display_columns['Concat Rank & Vehicle Number'], 'N/A'),
                            'Final MMVF': row.get(display_columns['Final MMVF'], 'N/A'),
                            'Expected Selling Price To Customer': row.get(display_columns['Expected Selling Price To Customer'], 'N/A'),
                            'Margin %': margin_value,
                            'Seller Name': row.get(display_columns['Seller Name'], 'N/A'),
                            'Ageing1': row.get(display_columns['Ageing1'], 'N/A')
                        })
                    
                    display_df = pd.DataFrame(display_data)
                    st.session_state.display_df = display_df
                else:
                    st.warning(f"No records found for Registration Number: {registration_number}")
                    st.session_state.vehicle_data = None
    else:
        st.warning("Please enter a Registration Number")

# Display vehicle details if we have data
if st.session_state.vehicle_data is not None:
    st.dataframe(st.session_state.display_df, use_container_width=True, hide_index=True)
    
    # Add price input field below vehicle details
    st.markdown("---")
    st.subheader("Calculate Expected Margin")
    user_price = st.number_input("Paste your price:", min_value=0.0, step=100.0, format="%.2f", key="user_price")
    
    # Add a calculate button
    if st.button("Calculate", type="secondary"):
        if user_price > 0:
            # Get the first row's values for Y and Z from session state
            row = st.session_state.vehicle_data
            display_columns = st.session_state.display_columns
            
            y_value = row.get(display_columns['New Landed Cost Including all'], 0)
            z_value = row.get(display_columns['Procurement Price'], 0)
            
            # Convert to float
            try:
                y_float = float(str(y_value).replace(',', '').strip())
                z_float = float(str(z_value).replace(',', '').strip())
            except:
                y_float = 0
                z_float = 0
            
            # Calculate internally
            margin_for_gst = user_price - z_float
            gst_amount = margin_for_gst - (margin_for_gst / 1.18)
            margin_net_of_gst = user_price - y_float - gst_amount
            
            # Expected Margin (subtract 2% as per requirement)
            denominator = user_price - gst_amount
            if denominator != 0:
                expected_margin = (margin_net_of_gst / denominator) * 100
                expected_margin = expected_margin - 2  # Subtract 2%
                expected_margin = round(expected_margin, 2)
                st.metric(label="Expected Margin", value=f"{expected_margin}%")
            else:
                st.error("Cannot calculate Expected Margin: Division by zero")
        else:
            st.warning("Please enter a price value")

# Add instructions
st.markdown("---")
st.info("💡 **Note:** This application securely fetches data from Google Sheets using service account authentication. Your sheet credentials are never exposed.")

