import pandas as pd

REQUIRED_COLUMNS = [
    "ID",
    "Name",
    "Department",
    "Salary"
]

def validate_columns(data_df):
    csv_columns = set(data_df.columns)
    required_columns = set(REQUIRED_COLUMNS)
    
    missing_columns = required_columns - csv_columns
    unexpected_columns = csv_columns - required_columns
    
    errors = []
    
    # check missing columns
    if missing_columns:
        errors.append(
            f"Missing columns: {sorted(missing_columns)}"
        )
        
    # unexpected columns
    if unexpected_columns:
        errors.append(
            f"Unexcpected columns: {sorted(unexpected_columns)}"
        )
        
    return errors

def validate_data(data_df):
    errors = []
    
    # 1. ID Validation
    
    if data_df["ID"].isna().any():
        errors.append("ID contains empty values")
    
    if not pd.api.types.is_numeric_dtype(data_df["ID"]):
        errors.append("ID must contain numeric values")
    
    if data_df["ID"].duplicated().any():
        duplicate_ids = data_df.loc[
            data_df["ID"].duplicated(),
            "ID"
        ].tolist()
        
        errors.append(
            f"Duplicate ID values found: {duplicate_ids}"
        )
        
    # 2 Name Validation
    
    if data_df['Name'].isna().any():
        errors.append("Name contains empty values")
    elif data_df["Name"].astype(str).str.strip().eq("").any():
        errors.append("Name Contains blank values")
        
    # 3 Department validation
    
    if data_df["Department"].isna().any():
        errors.append("Department contains empty values")
    elif data_df["Department"].astype(str).str.strip().eq("").any():
        errors.append("Department contains blank values")

    # 4 salary validation
    salary_numeric = pd.to_numeric(
        data_df["Salary"],
        errors="coerce"
    )
    
    if salary_numeric.isna().any():
        errors.append(
            "Salary contains non numeric or empty values"
        )
        
    if (salary_numeric < 0).any():
        errors.append(
            "Salary contain negative values"
        )
        
    return errors

def validate_rows(data_df):

    valid_rows = []
    error_records = []

    for _, row in data_df.iterrows():

        row_errors = []

        employee_id = row["ID"]

        
        # ID validation
        

        if pd.isna(employee_id):

            row_errors.append(
                "ID is empty."
            )

        
        # Name validation

        if pd.isna(row["Name"]) or str(row["Name"]).strip() == "":

            row_errors.append(
                "Name is empty."
            )

        
        # Department validation
        

        if (
            pd.isna(row["Department"])
            or str(row["Department"]).strip() == ""
        ):

            row_errors.append(
                "Department is empty."
            )

        
        # Salary validation
        

        salary = pd.to_numeric(
            row["Salary"],
            errors="coerce"
        )

        if pd.isna(salary):

            row_errors.append(
                "Salary is not numeric."
            )

        elif salary < 0:

            row_errors.append(
                "Salary cannot be negative."
            )

        
        # Store result
        

        if row_errors:

            error_records.append(
                {
                    "Employee_ID": employee_id,
                    "Error_Message": "; ".join(row_errors)
                }
            )

        else:

            valid_rows.append(row)

    valid_df = pd.DataFrame(
        valid_rows,
        columns=data_df.columns
    )

    return valid_df, error_records

if __name__ == "__main__":

    csv_file = "employees_sample.csv"

    # Read CSV
    data_df = pd.read_csv(csv_file)

    print("\nCSV Records:")
    print(len(data_df))

    # Validate rows
    valid_df, error_records = validate_rows(data_df)

    print("\nValid Records:")
    print(len(valid_df))

    print("\nError Records:")
    print(len(error_records))

    if error_records:

        print("\nErrors:")

        for error in error_records:
            print(error)

    else:

        print("\nNo row-level errors found.")