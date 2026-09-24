import streamlit as st 
import pandas as pd
from datetime import datetime


from etl_mapping import load_mapping,apply_mapping
from etl_validation import validate_columns,validate_rows
from etl_database import load_to_staging,upsert_employees
from etl_logging import log_etl_run,log_etl_errors



# Page Config

st.set_page_config(
    page_title="CSV ETL Platform",
    page_icon="🔄",
    layout="wide"
)

st.title("CSV → SQL Server ETL Platform")
st.caption("CSV data integration and ETL processing")

MAPPING_FILE = "config/mapping.csv"

# SQL Server Connection Test

st.subheader("SQL Server Status")

try:
    from etl_database import get_connection
    connection = get_connection()
    connection.close()
    st.success("SQL Server Connected")
    database_available = True

except Exception:
    st.warning("SQL Server is not connected. Running in Demo Mode.")
    database_available = False

# CSV UPLOAD

st.divider()

st.subheader("1. Upload CSV File")

uploaded_file = st.file_uploader(
    "Select a CSV File",
    type=["csv"]
)


if uploaded_file is not None:

    try:

        # Read CSV

        data_df = pd.read_csv(uploaded_file)

        st.success(
            f"CSV loaded successfully - {len(data_df)} records found"
        )


        # CSV Preview

        st.subheader("2. CSV Preview")

        st.dataframe(
            data_df,
            use_container_width='stretch',
            hide_index=True
        )


        # Column Mapping

        st.subheader("3. Column Mapping")

        mapping = load_mapping(MAPPING_FILE)

        mapping_df = pd.DataFrame(
            list(mapping.items()),
            columns=["CSV Column", "SQL Column"]
        )

        st.dataframe(
            mapping_df,
            use_container_width='stretch',
            hide_index=True
        )


        # Apply Mapping

        mapped_df = apply_mapping(
            data_df,
            mapping
        )


        # Column Validation

        st.subheader("4. Validation")

        column_errors = validate_columns(
            mapped_df
        )

        if column_errors:

            st.error("Column Validation failed")

            for error in column_errors:
                st.error(error)

            st.stop()

        st.success("Column validation passed")


        # Run ETL

        st.divider()

        st.subheader("5. Run ETL")

        run_button = st.button(
            "Run ETL",
            type="primary",
            use_container_width='stretch'
        )


        if run_button:

            start_time = datetime.now()

            with st.spinner("Running ETL process..."):

                # Row Validation

                valid_df, error_records = validate_rows(
                    mapped_df
                )

                total_records = len(mapped_df)
                valid_records = len(valid_df)
                failed_records = len(error_records)


                # Error Logging

                if error_records:

                    log_etl_errors(
                        error_records
                    )


                # No Valid Records

                if valid_records == 0:

                    end_time = datetime.now()

                    log_etl_run(
                        start_time=start_time,
                        end_time=end_time,
                        total_records=total_records,
                        updated_records=0,
                        inserted_records=0,
                        failed_records=failed_records,
                        status="FAILED"
                    )

                    st.error(
                        "ETL failed. No valid records available"
                    )

                    st.stop()


                # Load to Staging

                load_to_staging(
                    valid_df
                )


                # UPSERT

                updated_records, inserted_records = (
                    upsert_employees()
                )


                # Status

                end_time = datetime.now()

                if failed_records == 0:

                    status = "Success"

                else:

                    status = "Partial Success"


                # Run Log

                log_etl_run(
                    start_time=start_time,
                    end_time=end_time,
                    total_records=total_records,
                    updated_records=updated_records,
                    inserted_records=inserted_records,
                    failed_records=failed_records,
                    status=status
                )


                # Result

                st.success(
                    "ETL process completed successfully"
                )

                st.subheader("ETL Result")


                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Total Records",
                        total_records
                    )

                with col2:

                    st.metric(
                        "Valid Records",
                        valid_records
                    )

                with col3:

                    st.metric(
                        "Updated",
                        updated_records
                    )

                with col4:

                    st.metric(
                        "Inserted",
                        inserted_records
                    )


                col5, col6 = st.columns(2)

                with col5:

                    st.metric(
                        "Failed",
                        failed_records
                    )

                with col6:

                    st.metric(
                        "Status",
                        status
                    )


                # Error Details

                if error_records:

                    st.subheader(
                        "Invalid Records"
                    )

                    error_df = pd.DataFrame(
                        error_records
                    )

                    st.dataframe(
                        error_df,
                        use_container_width='stretch',
                        hide_index=True
                    )
                    
    except Exception as e:
        print(e)


else:

    st.info(
        "Please upload a CSV file to begin"
    )