import pandas as pd
import re
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib.font_manager as fm
from datetime import datetime
import os  # Import os module for file path checks

def preprocess_telegram_data(file_path):
    """
    Preprocesses Telegram data by cleaning text, tokenizing, and handling missing data.
    Keeps both Amharic and English words.
    """
    # Load the DataFrame
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return
    except Exception as e:
        print(f"Error loading the CSV file: {e}")
        return

    # Check for required columns
    required_columns = ['Message', 'Channel Title', 'Channel Username', 'ID']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: The following columns are missing in the CSV file: {missing_columns}")
        return

    # Add a placeholder 'Date' column if it doesn't exist
    if 'Date' not in df.columns:
        print("Adding placeholder 'Date' column with today's date.")
        df['Date'] = datetime.today().strftime('%Y-%m-%d')

    # Check for NaN values in the 'Message' column
    print("Checking for NaN values in the 'Message' column:")
    nan_count = df['Message'].isnull().sum()
    print(f"Number of NaN values in 'Message' column: {nan_count}")

    # Drop NaN values from the 'Message' column
    df = df.dropna(subset=['Message'])

    # Function to clean text by removing unwanted characters
    def clean_message(text):
        if not isinstance(text, str):
            return ""  # Return empty string for non-text data (e.g., NaN)

        # Allow both Amharic (\u1200-\u137F) and English letters (a-z, A-Z)
        text = re.sub(r'[^\w\s\u1200-\u137F]', '', text)  # \w matches [a-zA-Z0-9_]
        return text.strip()

    # Clean the 'Message' column
    df['Cleaned_Message'] = df['Message'].apply(clean_message)

    # Tokenize the cleaned message (split into words)
    df['Tokens'] = df['Cleaned_Message'].apply(lambda x: x.split() if pd.notnull(x) else [])

    # Select relevant columns for the output
    structured_data = df[['Channel Title', 'Channel Username', 'ID', 'Date', 'Cleaned_Message', 'Tokens']]

    # Save the cleaned data to a new CSV file
    output_path = file_path.replace('.csv', '_cleaned.csv')  # Change output filename
    structured_data.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Cleaned data saved successfully to {output_path}")

    return structured_data

def plot(cleaned_data):
    """
    Visualizes the cleaned Telegram data.
    """
    if cleaned_data is None:
        print("No data to plot.")
        return

    # Set a font that supports Amharic
    font_path = 'E:\\DS+ML\\AIM3\\fonts\\AbyssinicaSIL-Regular.ttf'  # Update this path
    if os.path.exists(font_path):
        try:
            # Register the font with Matplotlib
            fm.fontManager.addfont(font_path)
            # Set the default font family
            plt.rcParams['font.family'] = 'Abyssinica SIL'
            font_prop = fm.FontProperties(fname=font_path)
            print("Font 'Abyssinica SIL' registered successfully.")
        except Exception as e:
            print(f"Error registering font: {e}")
            print("Falling back to default font.")
    else:
        print(f"Font file not found at {font_path}. Falling back to default font.")
        font_prop = fm.FontProperties()  # Use default font

    # Plot word frequency
    all_tokens = [word for sublist in cleaned_data['Tokens'] for word in sublist]
    most_common_words = Counter(all_tokens).most_common(10)

    plt.figure(figsize=(10, 6))
    words, counts = zip(*most_common_words)
    plt.bar(words, counts, color='skyblue')
    plt.title('Top 10 Most Common Words', fontproperties=font_prop)
    plt.xlabel('Words', fontproperties=font_prop)
    plt.ylabel('Frequency', fontproperties=font_prop)
    plt.xticks(rotation=45, fontproperties=font_prop)
    plt.show()

    # Message Length Distribution
    cleaned_data['Message_Length'] = cleaned_data['Tokens'].apply(len)
    plt.figure(figsize=(10, 6))
    plt.hist(cleaned_data['Message_Length'], bins=20, color='lightgreen', edgecolor='black')
    plt.title('Distribution of Message Lengths (Number of Words)', fontproperties=font_prop)
    plt.xlabel('Message Length', fontproperties=font_prop)
    plt.ylabel('Frequency', fontproperties=font_prop)
    plt.show()

    # Messages Over Time
    if 'Date' in cleaned_data.columns:
        cleaned_data['Date'] = pd.to_datetime(cleaned_data['Date'])
        cleaned_data.set_index('Date', inplace=True)
        messages_over_time = cleaned_data.resample('D').size()  # Count messages per day

        plt.figure(figsize=(12, 6))
        messages_over_time.plot(color='orange')
        plt.title('Number of Messages Over Time', fontproperties=font_prop)
        plt.xlabel('Date', fontproperties=font_prop)
        plt.ylabel('Number of Messages', fontproperties=font_prop)
        plt.grid(True)
        plt.show()
    else:
        print("Skipping 'Messages Over Time' plot: 'Date' column not found.")
