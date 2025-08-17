# Analyze bot results - save as analyze_bot_results.py

import pandas as pd
import glob


def analyze_bot_data():
    """
    Analyze bot test results to check if field_maybe_none bug is fixed
    """

    # Find the most recent CSV export
    csv_files = glob.glob("*.csv")
    if not csv_files:
        print("No CSV files found. Make sure to run:")
        print("otree test User_Engagement_with_Social_Media_Posts 25 --export")
        return

    # Get the most recent file
    latest_file = max(csv_files, key=lambda x: x)
    print(f"Analyzing file: {latest_file}")

    # Load the data
    df = pd.read_csv(latest_file)
    print(f"Total participants: {len(df)}")

    # Check for the problematic feelstrue variables
    feelstrue_vars = [
        'image_feelstrue_ai', 'image_feelstrue_binary_ai',
        'image_feelstrue_real', 'image_feelstrue_binary_real'
    ]

    print("\n" + "=" * 50)
    print("FEELSTRUE DATA ANALYSIS")
    print("=" * 50)

    # Check if columns exist
    existing_vars = [var for var in feelstrue_vars if var in df.columns]
    print(f"Feelstrue columns found: {existing_vars}")

    if not existing_vars:
        print("No feelstrue columns found in data!")
        return

    # Check for missing data
    missing_feelstrue = df[existing_vars].isna().all(axis=1)
    missing_count = missing_feelstrue.sum()

    print(
        f"\nParticipants missing ALL feelstrue data: {missing_count}/{len(df)} ({missing_count / len(df) * 100:.1f}%)")

    if missing_count == 0:
        print("🎉 SUCCESS! No missing feelstrue data found!")
        print("The field_maybe_none() bug appears to be FIXED!")
    else:
        print(f"⚠️  ISSUE: {missing_count} participants still have missing feelstrue data")

        # Check behavioral evidence for missing participants
        behavioral_vars = [
            'click_x_ai', 'click_y_ai', 'click_x_real', 'click_y_real',
            'why_click_ai', 'why_click_real'
        ]

        problem_participants = df[missing_feelstrue]

        print("\nBehavioral evidence for participants with missing feelstrue data:")
        for var in behavioral_vars:
            if var in df.columns:
                has_data = problem_participants[var].notna().sum()
                total = len(problem_participants)
                pct = has_data / total * 100 if total > 0 else 0
                print(f"  {var}: {has_data}/{total} ({pct:.1f}%) have data")

    # Check individual feelstrue variables
    print("\nIndividual feelstrue variable analysis:")
    for var in existing_vars:
        missing = df[var].isna().sum()
        pct = missing / len(df) * 100
        print(f"  {var}: {missing}/{len(df)} ({pct:.1f}%) missing")

    # Check randomization patterns for missing data
    if missing_count > 0:
        print("\nRandomization patterns for missing participants:")
        randomization_vars = ['first_question', 'watermark_condition', 'device_type']

        for var in randomization_vars:
            if var in df.columns:
                print(f"\n{var}:")
                missing_breakdown = df[missing_feelstrue][var].value_counts()
                total_breakdown = df[var].value_counts()

                for value in missing_breakdown.index:
                    missing_val = missing_breakdown[value]
                    total_val = total_breakdown.get(value, 0)
                    pct = missing_val / total_val * 100 if total_val > 0 else 0
                    print(f"  {value}: {missing_val}/{total_val} ({pct:.1f}%) missing")

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    if missing_count == 0:
        print("✅ All bots completed successfully with complete feelstrue data")
        print("✅ The field_maybe_none() bug has been FIXED!")
        print("✅ Ready for real participant testing")
    else:
        print(f"❌ {missing_count} bots still have missing feelstrue data")
        print("❌ The field_maybe_none() bug may still exist")
        print("❌ Check your code for remaining field_maybe_none() calls")

    return df


if __name__ == "__main__":
    analyze_bot_data()