import pyodbc
import pandas as pd

SERVER = r"localhost\SQLEXPRESS"
DATABASE = "ExcelETL"
DRIVER = "ODBC Driver 17 for SQL Server"

def get_connection():
    connection_string = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes"
    )
    
    connection = pyodbc.connect(connection_string)
    
    return connection

def load_to_staging(data_df):
    
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        
        # clear previous staging data
        cursor.execute(
            "DELETE FROM Staging_employees"
        )
        
        # Insert current csv data
        insert_query = """
            INSERT INTO staging_Employees
            (ID,Name,Department,Salary)
            VALUES(?,?,?,?)
        """
        
        for _,row in data_df.iterrows():
            
            cursor.execute(
                insert_query,
                row["ID"],
                row["Name"],
                row["Department"],
                row["Salary"]
            )
        connection.commit()
        
        print(
            f"{len(data_df)} records loaded into Staging_Employees"
        )
    
    except Exception as error:
        connection.rollback()
        
        print("Failed to load data into Staging_Employees")
        print("Error",error)
        
        raise
    
    finally:
        cursor.close()
        connection.close()
        
def upsert_employees():
    
    connection = get_connection()
    cursor = connection.cursor()
    
    updated_records = 0
    inserted_records = 0
    
    try:
        
        # get all staging records
        cursor.execute("""
                       SELECT ID,Name,Department,Salary
                       FROM Staging_Employees
                       """)
        
        staging_records = cursor.fetchall()
        
        for row in staging_records:
            
            employee_id = row[0]
            name = row[1]
            department = row[2]
            salary = row[3]
            
            # check whether ID already exists
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM Employees
                           WHERE [ID] = ?
                           """,
                           employee_id
                           )
            exists = cursor.fetchone()[0]
            
            if exists:
                
                # Existing record -> update
                
                cursor.execute(
                    """
                    UPDATE Employees
                    SET 
                    [Name] = ?,
                    [Department] = ?,
                    [Salary] = ?
                    WHERE [ID] = ?
                    """,
                    name,
                    department,
                    salary,
                    employee_id
                )
                
                updated_records += 1
                
            else:
                
                # new record -> insert
                cursor.execute(
                    """
                    INSERT INTO Employees
                    ([ID] ,[Name] ,[Department] ,[Salary])
                    VALUES (?,?,?,?)
                    """,
                    employee_id,
                    name,
                    department,
                    salary
                )
                
                inserted_records += 1
                
        connection.commit()
        
        print("\nUPSERT completed successfully")
        print("Updated Records :",updated_records)
        print("Inserted Records :",inserted_records)
        
        return updated_records,inserted_records
    
    except Exception as error:
        
        connection.rollback()
        
        print("\nUPSERT failed")
        print("Error",error)
        
        raise
    
    finally:
        
        cursor.close()
        connection.close()

if __name__ == "__main__":

    try:

        updated, inserted = upsert_employees()

        print("\nFinal Result")
        print("Updated :", updated)
        print("Inserted:", inserted)

    except Exception as error:

        print("ETL UPSERT failed.")
        print("Error:", error)
        
        