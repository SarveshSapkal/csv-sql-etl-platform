import pandas as pd
from datetime import datetime

from etl_mapping import load_mapping,apply_mapping
from etl_validation import validate_columns,validate_rows
from etl_database import load_to_staging,upsert_employees
from etl_logging import log_etl_run,log_etl_errors

CSV_FILE = "employees_sample.csv"
MAPPING_FILE = "config/mapping.csv"

def run_etl():
    
    start_time = datetime.now()
    
    print("\n============================")
    print("ETL PROCESS STARTED")
    print("==============================")
    
    # Step 1 : Read csv
    
    print("\n[1] Reading CSV...")
    
    data_df = pd.read_csv(CSV_FILE)
    
    print(f"CSV records read: {len(data_df)}")
    
    # Step 2 : Load Mapping
    
    print("\n[2] Loading column mapping...")
    
    mapping = load_mapping(MAPPING_FILE)
    
    print("Mapping loaded successfully")
    
    print(mapping)
    
    # Step 3 : Apply Mapping
    
    print("\n[3] Apply column mapping...")
    
    mapped_df = apply_mapping(
        data_df,
        mapping
    )
    
    print("column mapping completed")
    
    # Step 4 : Validate columns
    
    print("\n[4] Validating Columns...")
    
    column_errors = validate_columns(
        mapped_df
    )
    
    if column_errors:
        print("Column validation failed")
        
        for error in column_errors:
            print("ERROR",error)
        return
    print("column validation passed")
    
    
    # 5 Row Level Validation
    
    print("\n[5] validating individual records...")
    
    valid_df,error_records = validate_rows(
        mapped_df
    )
    
    print("Valid records :",len(valid_df))
    print("Failed records :",len(error_records))
    
    # Log Invalid records
    
    if error_records:
        
        print("\nInvalid records found.")
        
        log_etl_errors(
            error_records
        )
    
    else:
        
        print("No invalid records")
        
    if len(valid_df) == 0:
        print("\nNo valid records available for processing.")
        
        end_time = datetime.now()
        
        log_etl_run(
            start_time=start_time,
            end_time=end_time,
            total_records=len(mapped_df),
            updated_records=0,
            inserted_records=0,
            failed_records=len(error_records),
            status="FAILED"
        )
        
        return
    
    # step 6 : Load staging data
    
    print("\n[6] Loading data into staging table...")
    
    load_to_staging(
        valid_df
    )
    
    print("staging load complete")
    
    # 7 : Upsert
    
    print("\n[7] Running UPSERT...")
    
    updated_records,inserted_records = (
        upsert_employees()
    )
    
    print("\nUpsert Completed.")
    
    # 8 : ETL RUN LOG
    
    end_time = datetime.now()
    
    failed_records = len(error_records)
    
    if failed_records == 0:
        status = "Success"
    else:
        status = "Partial Success"
    
    log_etl_run(
        start_time=start_time,
        end_time=end_time,
        total_records=len(mapped_df),
        updated_records=updated_records,
        inserted_records=inserted_records,
        failed_records=failed_records,
        status=status
    )
    
    # FINAL RESULT
    
    print("\n=============================")
    print("ETL PROCESS COMPLETE")
    print("===============================")
    
    print("Total Records :",len(mapped_df))
    print("Updates       :",updated_records)
    print("Inserted      :",inserted_records)
    print("Failed        :", failed_records)
    print("Status        :", status)
    
if __name__ == "__main__":
        
    try:
            
        run_etl()
    except Exception as error:
        
        print("\n=======================")
        print("ETL PROCESS FAILED")
        print("=========================")
        
        print("Error:",error)