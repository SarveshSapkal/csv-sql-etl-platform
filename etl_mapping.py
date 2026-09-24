import pandas as pd

def load_mapping(mapping_file):
    mapping_df = pd.read_csv(mapping_file)
    
    mapping = dict(
        zip(
            mapping_df["csv_column"],
            mapping_df["sql_column"]
        )
    )
    
    return mapping

def apply_mapping(data_df,mapping):
    mapped_df = data_df.rename(columns=mapping)
    
    return mapped_df

if __name__ == "__main__":
    csv_file = "employees_sample.csv"
    mapping_file = "config/mapping.csv"
    
    # Read CSV
    data_df = pd.read_csv(csv_file)
    
    print("\nCSV Columns:")
    print(list(data_df.columns))
    
    # Read Mapping
    mapping = load_mapping(mapping_file)
    
    print("\nMapping")
    print(mapping)
    
    # apply mapping
    mapped_df = apply_mapping(data_df,mapping)
    
    print("\nMapped Columns:")
    print(list(mapped_df.columns))
    
    print("\nMapped Data:")
    print(mapped_df)