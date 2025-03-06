import pandas as pd
import numpy as np


def tsheki_data_processor():
    XLS_FILE = 'tshekid_office2003.xls'
    OUTPUT_FIMI_FILE = 'input1.txt'
    TRESHOLD = 69

    df = pd.read_excel(XLS_FILE, header=None, usecols=[0,1], names=['raw_id','raw_item'])
    print("Original data:")
    print(df.head())

    df['item'] = (df['raw_item'].astype(str).str.lower().str.replace(r'\s+', '_', regex=True).str.replace(',', '_'))

    offset_map = {}
    last_id = None
    adjusted_ids = []

    for row_id in df['raw_id']:
        try:
            row_id = int(row_id)
        except ValueError:
            adjusted_ids.append(row_id)
            continue
        if row_id not in offset_map:
            offset_map[row_id] = 0
        else:
            if row_id != last_id:
                offset_map[row_id] += 1

        new_id = row_id + offset_map[row_id] * TRESHOLD
        adjusted_ids.append(new_id)
        last_id = row_id

    df['adjusted_id'] = adjusted_ids

    print("Original data:")
    print(df.head())

    df = df.drop(0)

    print("Processed data:")
    print(df.head())

    grouped = (df.groupby('adjusted_id')['item'].apply(lambda items: ' '.join(items)).reset_index(name='transaction'))

    grouped['transaction'] = grouped['transaction'].apply(lambda row: ' '.join(sorted(set(row.split()))))

    with open(OUTPUT_FIMI_FILE, 'w', encoding='utf-8') as f:
        for row in grouped['transaction']:
            f.write(row + '\n')

    print(f"Saved {len(grouped)} transactions to '{OUTPUT_FIMI_FILE}'.")


def bank_data_processor():

    CSV_FILE = 'bank-data.csv'
    OUTPUT_FIMI_FILE = 'input2.txt'
    COLUMNS_TO_REMOVE = ['id']
    NUMERIC_TO_DISCRETIZE = ['age', 'income']
    N_BINS = 5

    df = pd.read_csv(CSV_FILE)
    print("Original data:")
    print(df.head())

    df = df.drop(columns=COLUMNS_TO_REMOVE, errors='ignore')
    print("\nAfter dropping columns:")
    print(df.head())

    for col in NUMERIC_TO_DISCRETIZE:
        if col in df.columns:
            col_min = df[col].min()
            col_max = df[col].max()
            edges = np.linspace(col_min, col_max, N_BINS + 1)
            df[col] = pd.cut(df[col], bins=edges, include_lowest=True, right=False)
            df[col] = df[col].apply(lambda iv: f"{col}_{iv.left:.1f}_{iv.right:.1f}" if pd.notna(iv) else "")
    print("\nAfter discretization:")
    print(df.head())

    transactions = []
    for _, row in df.iterrows():
        items = []
        for col, val in row.items():
            if pd.notna(val) and val != "":
                if col in NUMERIC_TO_DISCRETIZE:
                    items.append(str(val))
                else:
                    items.append(f"{col}_{val}")
        transactions.append(" ".join(items))

    with open(OUTPUT_FIMI_FILE, 'w') as f:
        for trans in transactions:
            f.write(trans + "\n")

    print(f"\nFIMI transactions saved to '{OUTPUT_FIMI_FILE}'.")



