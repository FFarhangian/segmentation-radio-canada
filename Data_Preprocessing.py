##### Libraries

import pandas as pd
from pandas.tseries.holiday import HolidayCalendarFactory, AbstractHolidayCalendar
from pandas.tseries.holiday import USFederalHolidayCalendar
import numpy as np
import calendar
import calmap
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from lifelines import KaplanMeierFitter


##### Data Loading
def load_and_inspect(filename):
    """Load a CSV file and display basic info."""
    df = pd.read_csv(filename)
    print(f"\n--- {filename} ---")
    print(df.info())
    print(df.head())
    return df

abo = load_and_inspect("abo.csv")
visionnements = load_and_inspect("visionnements.csv")
cms = load_and_inspect("cms.csv")

# Check for duplicate IDs
duplicate_count = abo['rcid_hash'].duplicated().sum()
unique_count = abo['rcid_hash'].nunique()
total_records = len(abo)

# Check duplicate IDs in visionnements.csv
visionnements_duplicate_count = visionnements['rcid_hash'].duplicated().sum()
visionnements_unique_count = visionnements['rcid_hash'].nunique()
visionnements_total_records = len(visionnements)

# Check duplicate entries in cms.csv
cms_duplicate_count = cms['emission'].duplicated().sum()
cms_unique_count = cms['emission'].nunique()
cms_total_records = len(cms)

print(f"Total Records: {total_records}")
print(f"Unique IDs: {unique_count}")
print(f"Duplicate IDs: {duplicate_count}")

print("**visionnements.csv Analysis**")
print(f"Total Records: {visionnements_total_records}")
print(f"Unique rcid_hash: {visionnements_unique_count}")
print(f"Duplicate rcid_hash: {visionnements_duplicate_count}\n")

print("**cms.csv Analysis**")
print(f"Total Records: {cms_total_records}")
print(f"Unique emission: {cms_unique_count}")

# Convert dates to datetime format
abo['subscribe_on'] = pd.to_datetime(abo['subscribe_on'])
abo['cancelled_on'] = pd.to_datetime(abo['cancelled_on'])
visionnements['date'] = pd.to_datetime(visionnements['date'])


############## cms.csv Data exploration

theme_counts = cms['theme'].value_counts()
audience_counts = cms['audience'].value_counts()
theme_audience_counts = cms.groupby(['theme', 'audience']).size().unstack().fillna(0)
theme_audience_percentage = theme_audience_counts.div(theme_audience_counts.sum(axis=1), axis=0) * 100

print("\nTheme Frequency:\n", theme_counts)
print("\nAudience Frequency:\n", audience_counts)
print("\nTheme-Audience Distribution (%):\n", theme_audience_percentage)

def add_percentage_labels(ax, total_count):
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            percentage = f"{(height / total_count) * 100:.1f}%"
            ax.annotate(percentage, (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=8, color='black', rotation=90)

plt.figure(figsize=(14, 6))
ax = sns.barplot(x=theme_counts.index, y=theme_counts.values, palette="Blues_r", hue=theme_counts.index, dodge=False, legend=False)
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.title("Theme Frequency", fontsize=12)
plt.xlabel("Theme", fontsize=10)
plt.ylabel("Count", fontsize=10)
add_percentage_labels(ax, theme_counts.sum())
plt.show()

plt.figure(figsize=(14, 6))
ax = sns.barplot(x=audience_counts.index, y=audience_counts.values, palette="Greens_r", hue=audience_counts.index, dodge=False, legend=False)
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.title("Audience Frequency", fontsize=12)
plt.xlabel("Audience Category", fontsize=10)
plt.ylabel("Count", fontsize=10)
add_percentage_labels(ax, audience_counts.sum())
plt.show()

plt.figure(figsize=(14, 8))
sns.heatmap(theme_audience_percentage, annot=True, fmt=".1f", cmap="coolwarm", linewidths=0.5, cbar=True)
plt.title("Theme-Audience Distribution (%)", fontsize=12)
plt.xlabel("Audience", fontsize=10)
plt.ylabel("Theme", fontsize=10)
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.show()


################# abo.csv Data exploration

# Check for duplicate IDs
duplicate_count = abo['rcid_hash'].duplicated().sum()
unique_count = abo['rcid_hash'].nunique()
total_records = len(abo)

# Determine if the dataset is longitudinal
longitudinal = duplicate_count > 0

print(f"Total Records: {total_records}")
print(f"Unique IDs: {unique_count}")
print(f"Duplicate IDs (Longitudinal): {duplicate_count}")
print(f"Is the dataset longitudinal? {'Yes' if longitudinal else 'No'}")

# Check for missing values in the cancellation column
missing_cancellations = abo['cancelled_on'].isna().sum()
total_records = len(abo)

# Calculate the percentage of missing cancellations
missing_percentage = (missing_cancellations / total_records) * 100

# Print the results
print(f"Total Records: {total_records}")
print(f"Missing Cancellations: {missing_cancellations}")
print(f"Percentage of Missing Cancellations: {missing_percentage:.2f}%")

# Create subscription and cancellation month columns
abo['subscribe_month'] = abo['subscribe_on'].dt.strftime('%B')  # Extract full month name
abo['cancel_month'] = abo['cancelled_on'].dt.strftime('%B')  # Extract full month name

# Ensure months are in correct order
month_order = list(calendar.month_name[1:])  # January to December
abo['subscribe_month'] = pd.Categorical(abo['subscribe_month'], categories=month_order, ordered=True)
abo['cancel_month'] = pd.Categorical(abo['cancel_month'], categories=month_order, ordered=True)

# Count subscriptions and cancellations by month
subscribe_counts = abo['subscribe_month'].value_counts().sort_index()
cancel_counts = abo['cancel_month'].value_counts().sort_index()

# Calculate percentages
total_counts = subscribe_counts + cancel_counts.reindex(subscribe_counts.index, fill_value=0)
subscribe_percent = (subscribe_counts / total_counts * 100).fillna(0)
cancel_percent = (cancel_counts / total_counts * 100).fillna(0)

# Plot Subscriptions & Cancellations by Month with Percentages
plt.figure(figsize=(12, 6))
bar_width = 0.4
bars1 = plt.bar(subscribe_counts.index, subscribe_counts.values, color='blue', alpha=0.7, label="Subscriptions")
bars2 = plt.bar(cancel_counts.index, cancel_counts.values, color='red', alpha=0.7, label="Cancellations",
                bottom=subscribe_counts.reindex(cancel_counts.index, fill_value=0).values)

# Annotate percentages
for bar, percent in zip(bars1, subscribe_percent):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, f"{percent:.1f}%", ha='center', va='center', color='white', fontsize=10)
for bar, percent in zip(bars2, cancel_percent):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, f"{percent:.1f}%", ha='center', va='center', color='white', fontsize=10)

plt.xticks(rotation=45)
plt.title("Subscriptions & Cancellations by Month (with Percentage)")
plt.xlabel("Month")
plt.ylabel("Count")
plt.legend()
plt.show()

# Create subscription and cancellation weekday columns
abo['subscribe_weekday'] = abo['subscribe_on'].dt.strftime('%A')  # Extract full weekday name
abo['cancel_weekday'] = abo['cancelled_on'].dt.strftime('%A')  # Extract full weekday name

# Ensure weekdays are in correct order
day_order = list(calendar.day_name)  # Monday to Sunday
abo['subscribe_weekday'] = pd.Categorical(abo['subscribe_weekday'], categories=day_order, ordered=True)
abo['cancel_weekday'] = pd.Categorical(abo['cancel_weekday'], categories=day_order, ordered=True)

# Count subscriptions and cancellations by weekday
subscribe_counts_day = abo['subscribe_weekday'].value_counts().sort_index()
cancel_counts_day = abo['cancel_weekday'].value_counts().sort_index()

# Calculate percentages
total_counts_day = subscribe_counts_day + cancel_counts_day.reindex(subscribe_counts_day.index, fill_value=0)
subscribe_percent_day = (subscribe_counts_day / total_counts_day * 100).fillna(0)
cancel_percent_day = (cancel_counts_day / total_counts_day * 100).fillna(0)

# Plot Subscriptions & Cancellations by Day of the Week with Percentages
plt.figure(figsize=(12, 6))
bars1 = plt.bar(subscribe_counts_day.index, subscribe_counts_day.values, color='blue', alpha=0.7, label="Subscriptions")
bars2 = plt.bar(cancel_counts_day.index, cancel_counts_day.values, color='red', alpha=0.7, label="Cancellations",
                bottom=subscribe_counts_day.reindex(cancel_counts_day.index, fill_value=0).values)

# Annotate percentages for weekdays
for bar, percent in zip(bars1, subscribe_percent_day):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, f"{percent:.1f}%", ha='center', va='center', color='white', fontsize=10)
for bar, percent in zip(bars2, cancel_percent_day):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, f"{percent:.1f}%", ha='center', va='center', color='white', fontsize=10)

plt.xticks(rotation=45)
plt.title("Subscriptions & Cancellations by Day of the Week (with Percentage)")
plt.xlabel("Day of the Week")
plt.ylabel("Count")
plt.legend()
plt.show()


# Compute subscription duration (fill active users with 365 days)
abo['subscription_duration'] = (abo['cancelled_on'] - abo['subscribe_on']).dt.days.fillna(365)

# Adjusted subscription duration categories based on distribution
abo['duration_category'] = pd.cut(abo['subscription_duration'],
                                  bins=[0, 30, 90, 180, 365, 730, abo['subscription_duration'].max()],
                                  labels=['<1M', '1-3M', '3-6M', '6-12M', '1-2Y', '2Y+'])

# Count duration categories
duration_counts = abo['duration_category'].value_counts().sort_index()

total_counts = duration_counts.sum()
duration_percent = (duration_counts / total_counts * 100).fillna(0)

# Combined Box Plot and Histogram for Subscription Duration
fig, ax = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 3]})

# Box Plot (above the histogram)
sns.boxplot(x=abo['subscription_duration'], ax=ax[0], color='purple')
ax[0].set_title('Subscription Duration Box Plot')
ax[0].set_xlabel('')

# Histogram
sns.histplot(abo['subscription_duration'], bins=30, kde=True, color='purple', ax=ax[1])
ax[1].set_title('Subscription Duration Distribution')
ax[1].set_xlabel('Duration (Days)')
ax[1].set_ylabel('Frequency')

plt.tight_layout()
plt.show()

# Plot Duration Categories with Percentages
plt.figure(figsize=(8, 5))
bars = plt.bar(duration_counts.index, duration_counts.values, color="blue", alpha=0.7)

# Annotate percentages
for bar, percent in zip(bars, duration_percent):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, f"{percent:.1f}%", ha='center', va='center', color='white', fontsize=10)

plt.title("Subscription Duration Categories (with Percentage)")
plt.xlabel("Duration Category")
plt.ylabel("Count")
plt.show()


# Aggregate data monthly
abo_ts = abo.groupby(abo['subscribe_on'].dt.to_period("M")).size()
abo_cancel_ts = abo.groupby(abo['cancelled_on'].dt.to_period("M")).size()

# Plot Monthly Trends
plt.figure(figsize=(12, 6))
sns.lineplot(x=abo_ts.index.astype(str), y=abo_ts.values, label='Subscriptions', marker='o', color='blue')
sns.lineplot(x=abo_cancel_ts.index.astype(str), y=abo_cancel_ts.values, label='Cancellations', marker='o', color='red')
plt.xticks(rotation=45)
plt.title('Monthly Subscription & Cancellation Trends')
plt.xlabel('Month')
plt.ylabel('Count')
plt.legend()
plt.show()

subscription_date_range = (abo['subscribe_on'].min(), abo['subscribe_on'].max())
cancellation_date_range = (abo['cancelled_on'].min(), abo['cancelled_on'].max())
print(f"Subscription Date Range: {subscription_date_range[0]} to {subscription_date_range[1]}")
print(f"Cancellation Date Range: {cancellation_date_range[0]} to {cancellation_date_range[1]}")

# Count subscriptions and cancellations by month
subscribe_counts = abo['subscribe_month'].value_counts().sort_index()
cancel_counts = abo['cancel_month'].value_counts().sort_index()

# Plot Subscriptions & Cancellations by Month with Percentages
total_counts = subscribe_counts + cancel_counts.reindex(subscribe_counts.index, fill_value=0)
subscribe_percent = (subscribe_counts / total_counts * 100).fillna(0)
cancel_percent = (cancel_counts / total_counts * 100).fillna(0)

plt.figure(figsize=(12, 6))
bar_width = 0.4
bars1 = plt.bar(subscribe_counts.index, subscribe_counts.values, color='blue', alpha=0.7, label="Subscriptions")
bars2 = plt.bar(cancel_counts.index, cancel_counts.values, color='red', alpha=0.7, label="Cancellations",
                bottom=subscribe_counts.reindex(cancel_counts.index, fill_value=0).values)
for bar, percent in zip(bars1, subscribe_percent):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, f"{percent:.1f}%", ha='center', va='center', color='white', fontsize=10)
for bar, percent in zip(bars2, cancel_percent):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, f"{percent:.1f}%", ha='center', va='center', color='white', fontsize=10)

plt.xticks(rotation=45)
plt.title("Subscriptions & Cancellations by Month (with Percentage)")
plt.xlabel("Month")
plt.ylabel("Count")
plt.legend()
plt.show()


# Plot Subscriptions & Cancellations by Day of the Week with Percentages
subscribe_counts_day = abo['subscribe_weekday'].value_counts().sort_index()
cancel_counts_day = abo['cancel_weekday'].value_counts().sort_index()
total_counts_day = subscribe_counts_day + cancel_counts_day.reindex(subscribe_counts_day.index, fill_value=0)
subscribe_percent_day = (subscribe_counts_day / total_counts_day * 100).fillna(0)
cancel_percent_day = (cancel_counts_day / total_counts_day * 100).fillna(0)

plt.figure(figsize=(12, 6))
bars1 = plt.bar(subscribe_counts_day.index, subscribe_counts_day.values, color='blue', alpha=0.7, label="Subscriptions")
bars2 = plt.bar(cancel_counts_day.index, cancel_counts_day.values, color='red', alpha=0.7, label="Cancellations",
                bottom=subscribe_counts_day.reindex(cancel_counts_day.index, fill_value=0).values)

for bar, percent in zip(bars1, subscribe_percent_day):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, f"{percent:.1f}%", ha='center', va='center', color='white', fontsize=10)
for bar, percent in zip(bars2, cancel_percent_day):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, f"{percent:.1f}%", ha='center', va='center', color='white', fontsize=10)

plt.xticks(rotation=45)
plt.title("Subscriptions & Cancellations by Day of the Week (with Percentage)")
plt.xlabel("Day of the Week")
plt.ylabel("Count")
plt.legend()
plt.show()



# Plot Duration Categories with Percentages
duration_counts = abo['duration_category'].value_counts().sort_index()
total_counts = duration_counts.sum()
duration_percent = (duration_counts / total_counts * 100).fillna(0)

fig, ax = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 3]})

sns.boxplot(x=abo['subscription_duration'], ax=ax[0], color='purple')
ax[0].set_title('Subscription Duration Box Plot')
ax[0].set_xlabel('')

sns.histplot(abo['subscription_duration'], bins=30, kde=True, color='purple', ax=ax[1])
ax[1].set_title('Subscription Duration Distribution')
ax[1].set_xlabel('Duration (Days)')
ax[1].set_ylabel('Frequency')

plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 5))
bars = plt.bar(duration_counts.index, duration_counts.values, color="blue", alpha=0.7)

for bar, percent in zip(bars, duration_percent):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, f"{percent:.1f}%", ha='center', va='center', color='white', fontsize=10)

plt.title("Subscription Duration Categories (with Percentage)")
plt.xlabel("Duration Category")
plt.ylabel("Count")
plt.show()

# Create Calendar Heatmap for Subscriptions
abo_subscribe.index = pd.to_datetime(abo_subscribe['subscribe_on'])
dates = pd.date_range(start='2018-01-01', end='2019-12-30', freq='D')

aggregated_subscribe = pd.DataFrame(index=dates)
aggregated_subscribe['AverageCount'] = abo_subscribe.groupby(abo_subscribe.index)['subscribe_on'].count()
aggregated_subscribe = aggregated_subscribe.fillna(0)

plt.figure(figsize=(12, 6))
calmap.yearplot(aggregated_subscribe['AverageCount'], year=2019, cmap='Blues')
plt.xlabel('Month')
plt.ylabel('Day')
plt.title('Subscription Calendar Heatmap')
plt.show()

# Create Calendar Heatmap for Cancellations
abo_cancel.index = pd.to_datetime(abo_cancel['cancelled_on'])
dates = pd.date_range(start='2019-01-02', end='2020-04-30', freq='D')

aggregated_cancel = pd.DataFrame(index=dates)
aggregated_cancel['AverageCount'] = abo_cancel.groupby(abo_cancel.index)['cancelled_on'].count()
aggregated_cancel = aggregated_cancel.fillna(0)

plt.figure(figsize=(12, 6))
calmap.yearplot(aggregated_cancel['AverageCount'], year=2019, cmap='Reds')
plt.xlabel('Month')
plt.ylabel('Day')
plt.title('Cancellation Calendar Heatmap')
plt.show()



# Aggregate data monthly
abo_ts = abo.groupby(abo['subscribe_on'].dt.to_period("M")).size()
abo_cancel_ts = abo.groupby(abo['cancelled_on'].dt.to_period("M")).size()

# Plot Monthly Trends
plt.figure(figsize=(12, 6))
sns.lineplot(x=abo_ts.index.astype(str), y=abo_ts.values, label='Subscriptions', marker='o', color='blue')
sns.lineplot(x=abo_cancel_ts.index.astype(str), y=abo_cancel_ts.values, label='Cancellations', marker='o', color='red')
plt.xticks(rotation=45)
plt.title('Monthly Subscription & Cancellation Trends')
plt.xlabel('Month')
plt.ylabel('Count')
plt.legend()
plt.show()



# Fit Kaplan-Meier model only for subscription duration
kmf = KaplanMeierFitter()

# Fit the model (since all cancellations are observed, no censoring is applied)
kmf.fit(abo['subscription_duration'])

# Plot survival curve
plt.figure(figsize=(10, 5))
kmf.plot_survival_function()
plt.title("Survival Curve of Subscription Duration")
plt.xlabel("Time (Days)")
plt.ylabel("Probability of Remaining Subscribed")
plt.show()


##### Data Merging & Cleaning

# Extract 'programme', 'saison', and 'épisode' from 'titre'
visionnements[['programme', 'saison', 'épisode']] = visionnements['titre'].str.split(':', expand=True)
visionnements['saison'] = visionnements['saison'].str.extract(r'(\d+)').astype('Int64')
visionnements['épisode'] = visionnements['épisode'].str.extract(r'(\d+)').astype('Int64')

# Merge datasets
merged_df = visionnements.merge(cms, left_on='programme', right_on='emission', how='left')
df = merged_df.merge(abo, on='rcid_hash', how='left')

print("\nFinal Merged Dataset Info:")
print(df.info())

# Save merged dataset
df.to_csv("df.csv", index=False)
print("\nMerged dataset saved as 'df.csv'.")

##### Data Preprocessing & Feature Engineering

df = df.drop(columns=['titre', 'emission'])

# Convert date columns to datetime format
date_columns = ['date', 'subscribe_on', 'cancelled_on']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# Convert ID columns to string
df['visitor_id_hash'] = df['visitor_id_hash'].astype(str)
df['rcid_hash'] = df['rcid_hash'].astype(str)

# Display date ranges
print(f"\nSubscription Date Range: {df['subscribe_on'].min()} to {df['subscribe_on'].max()}")
print(f"Cancellation Date Range: {df['cancelled_on'].min()} to {df['cancelled_on'].max()}")
print(f"Overall Date Range: {df['date'].min()} to {df['date'].max()}")

# Create date-related features
for col in date_columns:
    df[f'{col}_year'] = df[col].dt.year
    df[f'{col}_month'] = df[col].dt.month
    df[f'{col}_day'] = df[col].dt.day
    df[f'{col}_weekday'] = df[col].dt.day_name()
    df[f'{col}_week_number'] = df[col].dt.isocalendar().week
    df[f'{col}_is_weekend'] = df[col].dt.weekday.isin([5, 6])  # Saturday (5) & Sunday (6)

### Check longitudinality

# Count users who have a subscription date but no cancellation date (right-censored)
right_censored_users = df[(df['subscribe_on'].notna()) & (df['cancelled_on'].isna())]
num_right_censored_users = right_censored_users['rcid_hash'].nunique()
print(f"\nNumber of Right-Censored Users (Active Subscribers): {num_right_censored_users}")

# Count how many times each user appears with different subscription periods
multi_subscription_users = df.groupby('rcid_hash')['subscribe_on'].nunique()
users_with_multiple_subscriptions = multi_subscription_users[multi_subscription_users > 1].count()
print(f"\nUsers with Multiple Subscription Periods (Longitudinal Users): {users_with_multiple_subscriptions}")

# Create 'abonnement' feature (True if subscribed one time, False if 'subscribe_on' is missing)
df['abonnement'] = df['subscribe_on'].notna()

# Create Number of device
user_device_counts = df.groupby('rcid_hash')['visitor_id_hash'].nunique()
df['num_devices'] = df['rcid_hash'].map(user_device_counts)

# Compute subscription duration (fill active users with 365 days)
df['subscription_duration'] = (df['cancelled_on'] - df['subscribe_on']).dt.days.fillna(365)
df['duration_category'] = pd.cut(df['subscription_duration'],
                                  bins=[0, 30, 90, 180, 365, 730, df['subscription_duration'].max()],
                                  labels=['<1M', '1-3M', '3-6M', '6-12M', '1-2Y', '2Y+'])

# Count number of unique days each user watched content
user_day_watching = df.groupby('rcid_hash')['date'].nunique().reset_index()
user_day_watching.columns = ['rcid_hash', 'day_watching']
df = df.merge(user_day_watching, on='rcid_hash', how='left')


# Count number of unique programs each user watched
user_unique_programs = df.groupby('rcid_hash')['programme'].nunique().reset_index()
user_unique_programs.columns = ['rcid_hash', 'unique_programs']
df = df.merge(user_unique_programs, on='rcid_hash', how='left')


# Aggregate total and average watch time per user
user_watch_time = df.groupby('rcid_hash')['content_time_spent'].agg(['sum', 'mean']).reset_index()
user_watch_time.columns = ['rcid_hash', 'total_watch_time', 'avg_watch_time']
df = df.merge(user_watch_time, on='rcid_hash', how='left')


# Percentage of sessions where user was not logged in
df['pct_not_logged_in'] = df.groupby('rcid_hash')['statut_connexion'].transform(lambda x: (x == False).mean() * 100)

# Percentage of free content watched
df['pct_gratuit'] = df.groupby('rcid_hash')['modele'].transform(lambda x: (x == 'gratuit').mean() * 100)

# Percentage of videos that were auto-played
df['pct_enchainement'] = df.groupby('rcid_hash')['enchainement'].transform(lambda x: (x == 'enchainement').mean() * 100)

# Percentage of videos that were resumed
df['pct_reprise'] = df.groupby('rcid_hash')['reprise_media'].transform(lambda x: (x == 'reprise').mean() * 100)

# Percentage of manually started videos
df['pct_actif'] = df.groupby('rcid_hash')['type_declenchement'].transform(lambda x: (x == 'actif').mean() * 100)

# Percentage of videos where user reached 75% of content
df['pct_progress_75'] = df.groupby('rcid_hash')['progress_marker_75_percent'].transform(lambda x: (x == 1).mean() * 100)

# Percentage of videos where user reached 95% of content
df['pct_progress_95'] = df.groupby('rcid_hash')['progress_marker_95_percent'].transform(lambda x: (x == 1).mean() * 100)

# Average number of video starts per user
df['avg_videoinitiate'] = df.groupby('rcid_hash')['videoinitiate'].transform('mean')

df['theme'] = df['theme'].fillna("Unknown")
theme_pivot = df.pivot_table(index='rcid_hash', columns='theme', aggfunc='size', fill_value=0)
theme_pivot = theme_pivot.div(theme_pivot.sum(axis=1), axis=0).mul(100)
theme_pivot = theme_pivot.reset_index()

df['audience'] = df['audience'].fillna("Unknown")
audience_pivot = df.pivot_table(index='rcid_hash', columns='audience', aggfunc='size', fill_value=0)
audience_pivot = audience_pivot.div(audience_pivot.sum(axis=1), axis=0).mul(100)
audience_pivot = audience_pivot.reset_index()

df = df.merge(theme_pivot, on='rcid_hash', how='left')
df = df.merge(audience_pivot, on='rcid_hash', how='left')


#### Missing Value Analysis

# Check missing values for each column
missing_values = df.isnull().sum()
print("\n Missing Values in Dataset:")
print(missing_values[missing_values > 0])

missing_percentage = (df.isnull().sum() / len(df)) * 100
missing_percentage_df = missing_percentage.reset_index()
missing_percentage_df.columns = ["Feature", "Missing Percentage"]
print("\n Missing Data Percentage:")
print(missing_percentage_df.sort_values(by="Missing Percentage", ascending=False))


# Define engagement-related features
missing_features = ['enchainement', 'type_declenchement', 'reprise_media', 'progress_marker_75_percent', 'progress_marker_95_percent']
missing_by_modele = df.groupby('modele')[missing_features].apply(lambda x: x.isnull().mean() * 100)
print("\n Missing Data by Content Type (Modele):")
print(missing_by_modele)

# Check missing percentages for each feature by 'theme'
missing_by_theme = df.groupby('theme')[missing_features].apply(lambda x: x.isnull().mean() * 100)
print("\n Missing Data by Theme:")
print(missing_by_theme)

# Filter users with missing progress markers
missing_progress_users = df[df['progress_marker_75_percent'].isna() | df['progress_marker_95_percent'].isna()]
progress_vs_watch_time = missing_progress_users['content_time_spent'].describe()
print("\n Watch Time Statistics for Users with Missing Progress Markers:")
print(progress_vs_watch_time)

# Filter only rows where 'subscribe_on' is missing
missing_subscription_df = df[df['subscribe_on'].isna()]
missing_subscription_analysis = missing_subscription_df.groupby(['modele', 'statut_connexion']).size().reset_index(name='Count')
missing_subscription_analysis['Percentage'] = (missing_subscription_analysis['Count'] / missing_subscription_analysis['Count'].sum()) * 100
print("\n Modele, Subscription & Login Status Analysis:")
print(missing_subscription_analysis)

# Count occurrences of "anonyme" in rcid_hash
anonyme_count = df[df['rcid_hash'] == "anonyme"].shape[0]
non_hash_values = df[~df['rcid_hash'].str.match(r'^[a-fA-F0-9]+$', na=False)]
print(f"\n Number of 'anonyme' entries in rcid_hash: {anonyme_count}")
print("\n Non-Hash rcid_hash Values (first 20 unique):")
print(non_hash_values[['rcid_hash']].drop_duplicates())


df.to_csv("df.csv", index=False)





