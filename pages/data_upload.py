import streamlit as st
import os
import pandas as pd
import numpy as np
import db
from utilities import custom_sidebar
from utils.validation import validate_file_upload, validate_csv_structure
from auth import require_auth, get_current_user
from db import save_upload_record
import base64
from auth import logout
from config import Config

st.set_page_config(page_title="SalesSight - Data Upload", layout="wide")

# Authentication check
require_auth()

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

custom_sidebar()



st.markdown(
    f"""
    <style>
        [data-testid="stSidebar"] {{
            background-color: #ffffff !important;
            padding-top: 0 !important;
        }}
        [data-testid="stSidebarNav"]::before {{
            content: "";
            display: flex;
            align-items: center;
            justify-content: flex-start;
            height: 60px;
            width: 100%;
            background-color: #ffffff;
            background-image: url("data:image/png;base64,{logo_base64}");
            background-repeat: no-repeat;
            background-size: 26px 26px;
            background-position: 18px center;
            border-bottom: 1px solid #f2f2f2;
            position: relative;
            z-index: 1;
            pointer-events: none;
        }}
        [data-testid="stSidebarNav"]::after {{
            content: "{title}";
            position: absolute;
            top: 18px;
            left: 52px;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 18px;
            color: #1E90FF;
            z-index: 1;
            pointer-events: none;
        }}
        [data-testid="stSidebarNav"] {{
            margin-top: -60px !important;
            position: relative;
            z-index: 0;
        }}
        [data-testid="stSidebarNav"] ul {{
            padding-left: 10px;
        }}
        [data-testid="stSidebarNav"] li a {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 14px;
            border-radius: 8px;
            text-decoration: none;
            font-family: 'Inter', sans-serif;
            font-size: 15px;
            font-weight: 500;
            color: #4B5563 !important;
            transition: all 0.2s ease-in-out;
        }}
        [data-testid="stSidebarNav"] li a[data-testid="stSidebarNavLinkActive"] {{
            background-color: #bbddfc !important;
            color: #1E90FF !important;
            font-weight: 600 !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/data_upload.py", label="📂 Upload")
    st.page_link("pages/sales_forecasting.py", label="📈 Sales Forecasting")
    st.page_link("pages/setting.py", label="⚙️ Settings")
    if st.button("Logout"):
        logout()


# ============================================
# Data Quality Functions (Feature E)
# ============================================

def analyze_data_quality(df: pd.DataFrame) -> dict:
    """
    Analyze data quality and provide recommendations.
    
    Returns:
        Dictionary with quality metrics and recommendations
    """
    issues = []
    recommendations = []
    
    # Check for missing values
    missing_count = df.isnull().sum().sum()
    missing_pct = (missing_count / (df.shape[0] * df.shape[1])) * 100
    
    if missing_pct > 0:
        issues.append(f"Found {missing_count} missing values ({missing_pct:.1f}%)")
        recommendations.append("Consider filling missing values or removing incomplete rows")
    
    # Check for duplicate rows
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        issues.append(f"Found {duplicate_count} duplicate rows")
        recommendations.append("Remove duplicate entries to avoid skewed analysis")
    
    # Check Date column
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        invalid_dates = df['Date'].isnull().sum()
        if invalid_dates > 0:
            issues.append(f"Found {invalid_dates} invalid dates")
            recommendations.append("Ensure dates follow format: YYYY-MM-DD or MM/DD/YYYY")
        
        # Check for date gaps
        if not df['Date'].isnull().all():
            date_range = pd.date_range(df['Date'].min(), df['Date'].max(), freq='D')
            missing_dates = len(date_range) - df['Date'].nunique()
            if missing_dates > 0:
                issues.append(f"Found {missing_dates} missing dates in the range")
                recommendations.append("Data has gaps - consider if this affects your analysis")
    
    # Check Sales column
    if 'Sales' in df.columns:
        df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
        
        # Check for negative sales
        negative_sales = (df['Sales'] < 0).sum()
        if negative_sales > 0:
            issues.append(f"Found {negative_sales} negative sales values")
            recommendations.append("Review negative sales - they might indicate returns or errors")
        
        # Check for outliers using IQR method
        Q1 = df['Sales'].quantile(0.25)
        Q3 = df['Sales'].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df['Sales'] < (Q1 - 1.5 * IQR)) | (df['Sales'] > (Q3 + 1.5 * IQR))).sum()
        
        if outliers > 0:
            issues.append(f"Found {outliers} potential outliers in sales data")
            recommendations.append("Review extreme values to ensure data accuracy")
        
        # Check for zero sales
        zero_sales = (df['Sales'] == 0).sum()
        if zero_sales > 0:
            issues.append(f"Found {zero_sales} rows with zero sales")
    
    # Calculate quality score (0-100)
    quality_score = 100
    quality_score -= min(missing_pct * 2, 30)  # Penalize missing values
    quality_score -= min((duplicate_count / len(df)) * 100, 20)  # Penalize duplicates
    quality_score -= min((outliers / len(df)) * 100, 15) if 'Sales' in df.columns else 0
    quality_score = max(0, quality_score)
    
    return {
        'score': round(quality_score, 1),
        'issues': issues,
        'recommendations': recommendations,
        'stats': {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': int(missing_count),
            'duplicate_rows': int(duplicate_count),
            'date_range': f"{df['Date'].min()} to {df['Date'].max()}" if 'Date' in df.columns and not df['Date'].isnull().all() else "N/A"
        }
    }


def data_extraction(file_path):
    """Extract metrics from uploaded data file."""
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return {"error": "File not found"}
    except Exception as e:
        return {"error": f"Error reading file: {e}"}

    # Validate required columns
    required_cols = ['Sales', 'Date']
    for col in required_cols:
        if col not in df.columns:
            return {"error": f"Missing required column: {col}"}

    # Clean and sort data
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date', 'Sales']).sort_values('Date')

    # Compute KPIs
    total_sales = df['Sales'].sum()
    avg_sales = df['Sales'].mean()
    latest_sales = df['Sales'].iloc[-1] if len(df) > 0 else 0
    growth = ((df['Sales'].iloc[-1] - df['Sales'].iloc[-2]) / df['Sales'].iloc[-2] * 100) if len(df) > 1 else 0

    # Sales trend over time (monthly aggregation)
    sales_trend = (
        df.groupby(df['Date'].dt.to_period('M'))['Sales']
        .sum()
        .reset_index()
        .sort_values('Date')
    )
    sales_trend['Date'] = sales_trend['Date'].dt.to_timestamp()

    # Top products by sales (if Product column exists)
    if 'Product' in df.columns:
        top_products = (
            df.groupby('Product')['Sales']
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )
    else:
        top_products = None

    metrics = {
        "total_sales": round(total_sales, 2),
        "avg_sales": round(avg_sales, 2),
        "latest_sales": round(latest_sales, 2),
        "growth": round(growth, 2),
        "sales_trend": sales_trend,
        "top_products": top_products
    }

    return metrics


# ============================================
# Main UI
# ============================================

st.title("📤 Upload Sales Data")
st.write("Upload your sales data file to start analyzing")

col1, col2 = st.columns([1.5, 1])

with col1:
    uploaded_files = st.file_uploader(
        "Choose CSV or Excel file",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        label_visibility="visible",
        help="Maximum file size: 200MB"
    )

with col2:
    st.markdown(
        """
        <div style="
            border: 1px solid #B3D4FC;
            background-color: #F0F7FF;
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 20px;
            font-family: 'Segoe UI', sans-serif;
        ">
            <strong style="color:#2C6BED; font-size:16px;">📘 File Requirements</strong>
            <ul style="margin-top: 10px; margin-bottom: 0; color:#333; font-size:14px;">
                <li><strong>File formats:</strong> CSV, XLSX</li>
                <li><strong>Maximum size:</strong> 200 MB</li>
                <li><strong>Required columns:</strong> Date, Sales</li>
                <li><strong>Optional:</strong> Product, Category</li>
                <li><strong>Date format:</strong> YYYY-MM-DD or MM/DD/YYYY</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

# Initialize session state
if "file_status" not in st.session_state:
    st.session_state.file_status = {}
if "save_path" not in st.session_state:
    st.session_state.save_path = None
if "quality_report" not in st.session_state:
    st.session_state.quality_report = None

# Process uploaded files
if uploaded_files:
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    user = get_current_user()
    
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        
        # Validate file
        is_valid, error_msg = validate_file_upload(uploaded_file)
        
        if not is_valid:
            st.error(f"❌ {file_name}: {error_msg}")
            st.session_state.file_status[file_name] = f"❌ {error_msg}"
            continue
        
        # Create unique filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{user['id']}_{timestamp}_{file_name}"
        save_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        
        try:
            # Save file
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Read and validate CSV structure
            df = pd.read_csv(save_path) if file_name.endswith('.csv') else pd.read_excel(save_path)
            
            is_valid, error_msg = validate_csv_structure(df)
            
            if not is_valid:
                st.error(f"❌ {file_name}: {error_msg}")
                st.session_state.file_status[file_name] = f"❌ {error_msg}"
                os.remove(save_path)
                continue
            
            # Analyze data quality (Feature E)
            quality_report = analyze_data_quality(df)
            st.session_state.quality_report = quality_report
            
            # Save to database with file path
            if user:
                upload_id = db.save_upload_record(
                    user_id=user['id'],
                    filename=file_name,
                    file_path=save_path,  # NEW: Save the full path
                    file_size=uploaded_file.size,
                    row_count=len(df)
                )
                
                if upload_id:
                    # Save to session for immediate use
                    st.session_state.save_path = save_path
                    st.session_state.current_upload_id = upload_id
                    st.session_state.file_status[file_name] = "✅ Completed"
                    st.success(f"✅ {file_name} uploaded successfully! (Upload ID: {upload_id})")
                else:
                    st.error(f"❌ Failed to save upload record for {file_name}")
                    st.session_state.file_status[file_name] = "❌ Database save failed"
            else:
                st.error("❌ User not authenticated")
                st.session_state.file_status[file_name] = "❌ Authentication error"
            
        except Exception as e:
            st.error(f"❌ Error processing {file_name}: {str(e)}")
            st.session_state.file_status[file_name] = f"❌ Error: {str(e)}"
            # Clean up file if it was created
            if os.path.exists(save_path):
                os.remove(save_path)
# Display uploaded files
st.subheader("📋 Uploaded Files")
if st.session_state.file_status:
    for file, status in st.session_state.file_status.items():
        if "✅" in status:
            st.success(f"{file} {status}")
        elif "⏳" in status:
            st.warning(f"{file} {status}")
        else:
            st.error(f"{file} {status}")
else:
    st.info("No files uploaded yet.")

# Display Data Quality Report (Feature E)
if st.session_state.quality_report:
    st.markdown("---")
    st.subheader("🔍 Data Quality Report")
    
    quality = st.session_state.quality_report
    
    # Quality Score Badge
    score = quality['score']
    if score >= 80:
        color = "#10b981"
        badge = "Excellent"
    elif score >= 60:
        color = "#f59e0b"
        badge = "Good"
    else:
        color = "#ef4444"
        badge = "Needs Improvement"
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Quality Score", f"{score}/100", badge)
    col2.metric("Total Rows", quality['stats']['total_rows'])
    col3.metric("Missing Values", quality['stats']['missing_values'])
    col4.metric("Duplicate Rows", quality['stats']['duplicate_rows'])
    
    if quality['issues']:
        st.warning("⚠️ **Issues Found:**")
        for issue in quality['issues']:
            st.write(f"• {issue}")
    
    if quality['recommendations']:
        st.info("💡 **Recommendations:**")
        for rec in quality['recommendations']:
            st.write(f"• {rec}")
    
    # Data preview
    with st.expander("📊 Data Preview (First 10 Rows)"):
        if st.session_state.save_path:
            df_preview = pd.read_csv(st.session_state.save_path).head(10)
            st.dataframe(df_preview, use_container_width=True)