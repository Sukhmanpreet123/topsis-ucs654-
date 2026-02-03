import sys
import os
import pandas as pd
import numpy as np

def main():
    # 1. Check for Correct number of parameters
    if len(sys.argv) != 5:
        print("Error: Wrong number of parameters.")
        print("Usage: python topsis.py <InputDataFile> <Weights> <Impacts> <OutputResultFileName>")
        print('Example: python topsis.py data.csv "1,1,1,2" "+,+,-,+" output.csv')
        sys.exit(1)

    input_file = sys.argv[1]
    weights_str = sys.argv[2]
    impacts_str = sys.argv[3]
    output_file = sys.argv[4]

    # 2. Handling of “File not Found” exception
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' was not found.")
        sys.exit(1)

    try:
        # Determine file type and read
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
        elif input_file.endswith('.xlsx') or input_file.endswith('.xls'):
            df = pd.read_excel(input_file)
        else:
            print("Error: Unsupported file format. Please provide a .csv or .xlsx file.")
            sys.exit(1)

    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # 3. Input file must contain three or more columns
    if df.shape[1] < 3:
        print("Error: Input file must contain three or more columns.")
        sys.exit(1)

    # Separate non-numeric first column (ID/Name) from data
    # Requirement: From 2nd to last columns must contain numeric values only
    data_df = df.iloc[:, 1:].copy()
    
    # 4. Handling of non-numeric values
    # Check if all columns from 2nd to last are numeric
    try:
        data_df = data_df.apply(pd.to_numeric)
    except Exception as e:
        print("Error: From 2nd to last columns must contain numeric values only.")
        sys.exit(1)
        
    # Check for any remaining non-numeric data (like NaNs introduced by coercion if we used coerce)
    if data_df.isnull().values.any():
        print("Error: Input data contains non-numeric values or missing data.")
        sys.exit(1)

    # Parse Weights and Impacts
    try:
        weights = [float(w) for w in weights_str.split(',')]
        impacts = impacts_str.split(',')
    except ValueError:
        print("Error: Weights must be numeric and separated by commas.")
        sys.exit(1)

    # 5. Logical Validations
    num_cols = data_df.shape[1]
    
    # The number of weights, impacts and columns must be the same
    if len(weights) != num_cols or len(impacts) != num_cols:
        print(f"Error: Number of weights ({len(weights)}), impacts ({len(impacts)}), "
              f"and criteria columns ({num_cols}) must be the same.")
        sys.exit(1)

    # Impacts must be either +ve or -ve
    if not all(i in ['+', '-'] for i in impacts):
        print("Error: Impacts must be either '+' or '-'.")
        sys.exit(1)

    # --- TOPSIS ALGORITHM IMPLEMENTATION ---

    try:
        # Step 1: Vector Normalization
        # r_ij = x_ij / sqrt(sum(x_kj^2))
        matrix = data_df.values
        rss = np.sqrt(np.sum(matrix**2, axis=0)) # Root sum of squares
        
        # Avoid division by zero
        if (rss == 0).any():
             print("Error: Standard deviation of a column is zero (cannot normalize).")
             sys.exit(1)
             
        normalized_matrix = matrix / rss

        # Step 2: Weight Assignment
        # v_ij = w_j * r_ij
        weighted_matrix = normalized_matrix * weights

        # Step 3: Find Ideal Best (V+) and Ideal Worst (V-)
        ideal_best = []
        ideal_worst = []

        for i in range(num_cols):
            if impacts[i] == '+':
                ideal_best.append(np.max(weighted_matrix[:, i]))
                ideal_worst.append(np.min(weighted_matrix[:, i]))
            else: # impact is '-'
                ideal_best.append(np.min(weighted_matrix[:, i]))
                ideal_worst.append(np.max(weighted_matrix[:, i]))

        ideal_best = np.array(ideal_best)
        ideal_worst = np.array(ideal_worst)

        # Step 4: Calculate Euclidean Distance from Ideal Best (S+) and Ideal Worst (S-)
        # S_i+ = sqrt(sum((v_ij - V_j+)^2))
        s_plus = np.sqrt(np.sum((weighted_matrix - ideal_best)**2, axis=1))
        s_minus = np.sqrt(np.sum((weighted_matrix - ideal_worst)**2, axis=1))

        # Step 5: Calculate Performance Score
        # P_i = S_i- / (S_i+ + S_i-)
        # Handle potential division by zero if s_plus + s_minus is 0
        total_dist = s_plus + s_minus
        
        # If total distance is 0, score is 0 (should rarely happen in valid data)
        performance_score = np.divide(s_minus, total_dist, out=np.zeros_like(s_minus), where=total_dist!=0)

        # 6. Output Generation
        df['Topsis Score'] = performance_score
        
        # Rank: Higher score is better. rank(method='max') or similar ensures standard ranking
        # We want rank 1 for the highest score.
        df['Rank'] = df['Topsis Score'].rank(ascending=False, method='min').astype(int)

        # Save to output file
        df.to_csv(output_file, index=False)
        print(f"Success: Result saved to {output_file}")

    except Exception as e:
        print(f"An error occurred during calculation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()