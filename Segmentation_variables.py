import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df_segmented = pd.read_csv("df.csv")
columns_to_keep = [
    'rcid_hash', 'abonnement', 'num_devices', 'subscription_duration', 'duration_category',
    'day_watching', 'unique_programs', 'total_watch_time', 'avg_watch_time', 'pct_not_logged_in',
    'pct_gratuit', 'pct_enchainement', 'pct_reprise', 'pct_actif', 'pct_progress_75',
    'pct_progress_95', 'avg_videoinitiate', 'Alimentation', 'Biographie', 'Nature et environnement',
    'Histoire', 'Magazine', 'Science', 'Société', 'Économie et politique', 'Art', 'Actualité',
    'Animation', 'Comédie', 'Drame', 'Humour et variété', 'Suspense et horreur', 'Science-fiction et fantastique',
    'Policier', 'Entrevues et talk-show', 'Docu-réalité', 'Spectacle', 'Aventure', 'Jeunesse', 'Jeu', 'Sport et aventure',
    'Pour la famille', 'Pour les petits', 'ados', 'Pour les plus grands'
]

# Create a new dataframe with only the relevant features for segmentation
df_segmented = df_segmented[columns_to_keep].drop_duplicates()

df_segmented.shape
df_segmented.columns


############3 data cleaning and data exploration and dimension reduction

df_segmented['abonnement'] = df_segmented['abonnement'].astype(int)


# Visualize 'num_devices' distribution
plt.figure(figsize=(10, 5))
sns.boxplot(x=df_segmented['num_devices'])
plt.title("Box Plot of 'num_devices' Feature")
plt.xlabel("Number of Devices")
plt.show()

# Compute IQR (Interquartile Range)
Q1 = df_segmented['num_devices'].quantile(0.25)
Q3 = df_segmented['num_devices'].quantile(0.75)
IQR = Q3 - Q1

# Define Outlier Bounds
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Filter Out Outliers
df_segmented = df_segmented[(df_segmented['num_devices'] >= lower_bound) &
                                      (df_segmented['num_devices'] <= upper_bound)]

# Display confirmation
print(f"\n✅ Outliers removed! Remaining records: {df_segmented.shape[0]}")



plt.figure(figsize=(12, 5))

# Histogram
plt.subplot(1, 2, 1)
sns.histplot(df_segmented['subscription_duration'], bins=30, kde=True, color='blue')
plt.title("Histogram of Subscription Duration")
plt.xlabel("Subscription Duration (Days)")
plt.ylabel("Frequency")

# Box Plot
plt.subplot(1, 2, 2)
sns.boxplot(x=df_segmented['subscription_duration'], color='blue')
plt.title("Box Plot of Subscription Duration")
plt.xlabel("Subscription Duration (Days)")

plt.tight_layout()
plt.show()

######

df_segmented = df_segmented.drop(columns=['duration_category'])

# Step 1: Create 'watch_rate' feature (days watched per subscription duration)
df_segmented['watch_rate'] = df_segmented['day_watching'] / df_segmented['subscription_duration']

# Step 2: Visualize 'watch_rate' distribution
plt.figure(figsize=(12, 5))

# Histogram
plt.subplot(1, 2, 1)
sns.histplot(df_segmented['watch_rate'], bins=30, kde=True, color='green')
plt.title("Histogram of Watch Rate")
plt.xlabel("Watch Rate (Days Watched / Subscription Duration)")
plt.ylabel("Frequency")

# Box Plot
plt.subplot(1, 2, 2)
sns.boxplot(x=df_segmented['watch_rate'], color='green')
plt.title("Box Plot of Watch Rate")
plt.xlabel("Watch Rate")

plt.tight_layout()
plt.show()

###########

# Define features to visualize
features_to_plot = ['unique_programs', 'total_watch_time', 'avg_watch_time']

# Create histograms and box plots for each feature
plt.figure(figsize=(15, 10))

for i, feature in enumerate(features_to_plot, 1):
    plt.subplot(3, 2, 2 * i - 1)
    sns.histplot(df_segmented[feature], bins=30, kde=True, color='blue')
    plt.title(f"Histogram of {feature}")
    plt.xlabel(feature)
    plt.ylabel("Frequency")

    plt.subplot(3, 2, 2 * i)
    sns.boxplot(x=df_segmented[feature], color='blue')
    plt.title(f"Box Plot of {feature}")
    plt.xlabel(feature)

plt.tight_layout()
plt.show()

#######
df_segmented = df_segmented.drop(columns=['day_watching', 'total_watch_time'])

##########


# Drop Unknown columns
df_segmented.drop(columns=['Unknown_x', 'Unknown_y'], inplace=True)

# Grouping the genres based on the new categories

# Group 1: Educational and Informational
df_segmented['Educational_Informational'] = df_segmented[['Alimentation', 'Biographie', 'Nature et environnement', 'Histoire', 'Magazine', 'Science', 'Société', 'Économie et politique', 'Art', 'Actualité']].sum(axis=1)

# Group 2: Fiction and Entertainment
df_segmented['Fiction_Entertainment'] = df_segmented[['Animation', 'Comédie', 'Drame', 'Humour et variété', 'Suspense et horreur', 'Science-fiction et fantastique', 'Policier']].sum(axis=1)

# Group 3: Talk Shows and Reality
df_segmented['Talk_Show_Reality'] = df_segmented[['Entrevues et talk-show', 'Docu-réalité', 'Spectacle']].sum(axis=1)

# Group 4: Adventure and Youth
df_segmented['Adventure_Youth'] = df_segmented[['Aventure', 'Jeunesse', 'Jeu', 'Sport et aventure']].sum(axis=1)

# Drop original detailed genre columns
df_segmented.drop(columns=[
    'Alimentation', 'Biographie', 'Nature et environnement', 'Histoire', 'Magazine', 'Science', 'Société', 'Économie et politique', 'Art', 'Actualité',
    'Animation', 'Comédie', 'Drame', 'Humour et variété', 'Suspense et horreur', 'Science-fiction et fantastique', 'Policier',
    'Entrevues et talk-show', 'Docu-réalité', 'Spectacle',
    'Aventure', 'Jeunesse', 'Jeu', 'Sport et aventure'
], inplace=True)

print("\n✅ Genre Aggregation Complete! The dataset is now more compact with 4 main groups.")


df_segmented['For_All_Ages'] = df_segmented[['Pour la famille', 'Pour les petits']].sum(axis=1)
df_segmented.drop(columns=['Pour la famille', 'Pour les petits'], inplace=True)

df_segmented.drop(columns=['pct_progress_95'], inplace=True)

# Define the features to visualize
features_to_plot = ['pct_not_logged_in', 'pct_gratuit', 'pct_enchainement', 'pct_reprise',
                    'pct_actif', 'pct_progress_75', 'pct_progress_95', 'avg_videoinitiate',
                    'Actualité', 'Alimentation', 'Animation', 'Art', 'Aventure',
                    'Biographie', 'Comédie', 'Docu-réalité', 'Drame',
                    'Entrevues et talk-show', 'Histoire', 'Humour et variété', 'Jeu',
                    'Jeunesse', 'Magazine', 'Nature et environnement', 'Policier',
                    'Science', 'Science-fiction et fantastique', 'Société', 'Spectacle',
                    'Sport et aventure', 'Suspense et horreur', 'Unknown_x',
                    'Économie et politique', 'Ados', 'Pour la famille', 'Pour les petits',
                    'Pour les plus grands', 'Unknown_y']

# Set up the figure for histograms
plt.figure(figsize=(15, 40))
for i, feature in enumerate(features_to_plot, 1):
    plt.subplot(len(features_to_plot) // 3 + 1, 3, i)
    sns.histplot(df_segmented[feature], bins=30, kde=True, color='blue')
    plt.title(f"Histogram of {feature}")
    plt.xlabel(feature)
    plt.ylabel("Frequency")

plt.tight_layout()
plt.show()

# Set up the figure for box plots
plt.figure(figsize=(15, 40))
for i, feature in enumerate(features_to_plot, 1):
    plt.subplot(len(features_to_plot) // 3 + 1, 3, i)
    sns.boxplot(x=df_segmented[feature], color='blue')
    plt.title(f"Box Plot of {feature}")
    plt.xlabel(feature)

plt.tight_layout()
plt.show()


########## correlation matrix

df = df_segmented.drop(columns=["rcid_hash"])  # Drop ID column if present

import seaborn as sb

# Compute the correlation matrix
correlation_matrix = df.corr()

# Plotting the correlation heatmap
plt.figure(figsize=(12, 8))
sb.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', cbar=True, square=True)
plt.title("Correlation Heatmap of Features")
plt.show()

# Save the cleaned dataset
df_segmented.to_csv("df_segmented.csv", index=False)
print("\n✅ Prepared dataset for segmentation saved as 'df_segmented.csv'.")

