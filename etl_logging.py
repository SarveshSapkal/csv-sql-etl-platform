from datetime import datetime

from etl_database import get_connection


def log_etl_run(
    start_time,
    end_time,
    total_records,
    updated_records,
    inserted_records,
    failed_records,
    status
):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        insert_query = """
            INSERT INTO ETL_Run_Log
            (
                Start_Time,
                End_Time,
                Total_Records,
                Updated_Records,
                Inserted_Records,
                Failed_Records,
                Status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(
            insert_query,
            start_time,
            end_time,
            total_records,
            updated_records,
            inserted_records,
            failed_records,
            status
        )

        connection.commit()

        print("ETL run log saved successfully.")

    except Exception as error:

        connection.rollback()

        print("Failed to save ETL run log.")
        print("Error:", error)

        raise

    finally:

        cursor.close()
        connection.close()
        
def log_etl_errors(error_records):
    
    if not error_records:
        print("No ETL error to log")
        return
    
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        
        insert_query = """
        INSERT INTO ETL_Error_Log
        (
            Employee_ID,
            Error_Message,
            Error_Time
        )
        
        VALUES (?, ?, ?)
        """
        error_time = datetime.now()
        
        for error in error_records:
            
            cursor.execute(
                insert_query,
                error["Employee_ID"],
                error["Error_Message"],
                error_time
            )
        
        connection.commit()
        
        print(
            f"{len(error_records)} error records saved to ETL_Error_Log"
        )
        
    except Exception as error:
        connection.rollback()
        
        print("Failed to save ETL errors")
        print("Error:", error)
        
        raise
    
    finally:
        
        cursor.close()
        connection.close()


if __name__ == "__main__":

    test_errors = [
        {
            "Employee_ID": 3,
            "Error_Message": "Name is empty."
        },
        {
            "Employee_ID": 4,
            "Error_Message": "Salary cannot be negative."
        }
    ]

    log_etl_errors(test_errors)