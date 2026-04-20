import streamlit as st
from src.data_loader import SupernovaDataLoader
from src.data_processor import SupernovaDataProcessor

def render_pipeline_tester():
    """Renders a simple UI to trigger and validate the data loading pipeline."""
    st.title("Data Pipeline Validation")
    st.markdown("Click the button below to fetch, parse, and display the Supernova dataset.")

    if st.button("Execute Data Loader"):
        execute_and_display_pipeline()

def execute_and_display_pipeline():
    """Executes the data loading steps and displays the resulting DataFrame."""
    pipeline_loader = SupernovaDataLoader()
    data_processor = SupernovaDataProcessor()
    
    with st.spinner("Fetching, flattening, and processing data..."):
        try:
            # Step 1: Extract
            pipeline_loader.fetch_and_save_json()
            raw_supernova_records = pipeline_loader.parse_supernova_objects()
            
            # Step 2: Transform
            clean_supernova_dataframe = data_processor.process_raw_records(raw_supernova_records)
            
            # Step 3: Validate
            show_success_metrics(clean_supernova_dataframe)
            
        except Exception as error:
            st.error(f"Pipeline Execution Failed: {error}")

def show_success_metrics(dataframe):
    """Displays success metrics and the first 50 rows of the dataframe."""
    st.success(f"Success! Parsed {len(dataframe)} supernova objects.")
    
    st.subheader("Data Preview (Top 50 Rows)")
    # Streamlit renders DataFrames natively as interactive tables
    st.dataframe(dataframe.head(50), use_container_width=True)
    
    st.subheader("Data Types Check")
    # Useful to verify that redshift and magnitude parsed as floats, not strings
    st.write(dataframe.dtypes.astype(str))

if __name__ == "__main__":
    # Configure page to be wide for better data table viewing
    st.set_page_config(page_title="Pipeline Tester", layout="wide")
    render_pipeline_tester()
