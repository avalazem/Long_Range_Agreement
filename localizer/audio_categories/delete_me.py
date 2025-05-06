import pandas as pd
import numpy as np
import re
import random

visual_path = "/home/avalazem/Desktop/Work/Single_Word_Processing_Stage/SWP_Pilot_2/localizer/audio_categories/sub02_audio.csv"

def extract_category(stim_name):
    """Extracts the category part (text before numbers) from a stimulus name."""
    match = re.match(r'^([a-zA-Z_]+)', stim_name)
    return match.group(1) if match else None

def constrained_shuffle(items, get_key_func):
    """
    Shuffles a list of items ensuring no two adjacent items have the same key.
    Tries multiple random shuffles and attempts to fix violations.
    """
    if not items:
        return []

    max_attempts = len(items) * 10 # Heuristic limit for attempts

    for attempt in range(max_attempts):
        shuffled_items = items[:] # Create a copy
        random.shuffle(shuffled_items)
        is_valid = True
        needs_fix = True

        # Iteratively try to fix violations
        fix_passes = 0
        max_fix_passes = len(shuffled_items) # Limit passes to prevent infinite loops

        while needs_fix and fix_passes < max_fix_passes:
            needs_fix = False
            fix_passes += 1
            for i in range(len(shuffled_items) - 1):
                if get_key_func(shuffled_items[i]) == get_key_func(shuffled_items[i+1]):
                    is_valid = False
                    needs_fix = True # Found a violation, need another pass after fixing
                    # Try to find a swap for item i+1
                    found_swap = False
                    for j in range(i + 2, len(shuffled_items)):
                        # Check if swapping i+1 and j resolves the immediate conflict
                        # and doesn't create a new conflict at j-1
                        if get_key_func(shuffled_items[j]) != get_key_func(shuffled_items[i]) and \
                           get_key_func(shuffled_items[i+1]) != get_key_func(shuffled_items[j-1]):
                           # Check potential conflict after swap at i+1
                           if (i+2 >= len(shuffled_items)) or \
                              (get_key_func(shuffled_items[j]) != get_key_func(shuffled_items[i+2])):

                                shuffled_items[i+1], shuffled_items[j] = shuffled_items[j], shuffled_items[i+1]
                                found_swap = True
                                break # Break inner loop (j) after finding a swap

                    if not found_swap:
                        # If no swap could fix this specific violation, this shuffle attempt fails
                        # Break the inner loop (i) and try a new random shuffle
                        is_valid = False
                        break
            # If the inner loop (i) completed without needing a fix, the list is valid for now
            if not needs_fix:
                 is_valid = True


        if is_valid:
            print(f"Constrained shuffle successful after {attempt + 1} attempts.")
            return shuffled_items # Return the valid shuffle

    # If loop finishes without returning, no valid shuffle found
    print("Warning: Could not guarantee non-adjacent blocks of the same category after multiple attempts. Using last shuffle attempt.")
    return shuffled_items # Return the last attempt


# Read the CSV file
try:
    df = pd.read_csv(visual_path)
    print("CSV file read successfully. First 5 rows:")
    print(df.head())
    print("\nColumn names:")
    print(df.columns)

    stim_col = 'stim'
    onset_col = 'onset'

    if stim_col not in df.columns or onset_col not in df.columns:
        print(f"Error: Expected columns '{stim_col}' and '{onset_col}' not found in the CSV.")
        print(f"Actual columns: {df.columns.tolist()}")
    else:
        # 1. Store original onset times
        original_onsets = df[onset_col].copy().tolist()
        original_columns = df.columns.tolist() # Store original column order

        # 2. Identify original blocks based on consecutive category
        blocks = []
        current_block_rows = []
        current_category = None
        start_index = 0

        df['temp_category'] = df[stim_col].apply(extract_category)

        for i in range(len(df)):
            row_category = df.loc[i, 'temp_category']
            if i == 0:
                current_category = row_category

            # Condition to end a block: category changes OR it's the last row
            if row_category != current_category or i == len(df) - 1:
                # Determine end index for slicing
                end_index = i if row_category != current_category else i + 1
                # Create block DataFrame
                block_df = df.iloc[start_index:end_index].copy()
                # Shuffle within the block
                shuffled_block_df = block_df.sample(frac=1).reset_index(drop=True)
                blocks.append({'category': current_category, 'df': shuffled_block_df})

                # Start new block info
                current_category = row_category
                start_index = i

                # Special case: if the last row triggered the block end due to category change,
                # it needs to form its own block of size 1.
                if row_category != blocks[-1]['category'] and i == len(df) - 1:
                     single_row_df = df.iloc[i:i+1].copy()
                     blocks.append({'category': current_category, 'df': single_row_df})


        print(f"\nIdentified {len(blocks)} original blocks.")

        # 3. Perform constrained shuffle on the list of blocks
        shuffled_blocks = constrained_shuffle(blocks, lambda block: block['category'])

        # 4. Concatenate shuffled blocks
        if shuffled_blocks:
            final_df_list = [block['df'] for block in shuffled_blocks]
            randomized_df = pd.concat(final_df_list).reset_index(drop=True)

            # Remove temporary category column
            randomized_df = randomized_df.drop(columns=['temp_category'])

            # 5. Assign original onset times back
            if len(original_onsets) == len(randomized_df):
                randomized_df[onset_col] = original_onsets
                print("\nRandomization complete. First 5 rows of randomized data:")
                # Ensure columns are in original order
                print(randomized_df[original_columns].head())

                # 6. Save the randomized data to a new file
                output_path = visual_path.replace(".csv", "_randomized_constrained.csv")
                # Save with original columns order
                randomized_df[original_columns].to_csv(output_path, index=False)
                print(f"\nRandomized data saved to: {output_path}")
            else:
                print("\nError: Number of rows changed during processing. Cannot assign original onsets.")
                print(f"Original rows: {len(original_onsets)}, Randomized rows: {len(randomized_df)}")
        else:
            print("\nError: No blocks were identified or shuffled.")


except FileNotFoundError:
    print(f"Error: File not found at {visual_path}")
except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
