import pandas as pd

# Load the CSV file
file_path = 'C:/Users/Chuks/Documents/NBA Team Building/playoffStats.csv'
data = pd.read_csv(file_path)

# Group by season and then by team_id
grouped = data.groupby(['season', 'team_id'])

# Create a dictionary to store subsets
subsets = {}

# Iterate through the groups and store the subsets
for (season, team_id), group in grouped:
    if season not in subsets:
        subsets[season] = {}
    subsets[season][team_id] = group

# Displaying keys to verify the structure
for season in subsets:
    print(f"Season: {season}")
    for team_id in subsets[season]:
        print(f"  Team ID: {team_id}, Number of Players: {len(subsets[season][team_id])}")

# Filter data for seasons from 2021 onwards
data_recent = data[data['season'] >= 2020].copy()

# Engineer the playoff indicator: 1 if the team made the playoffs, 0 otherwise
data_recent['made_playoffs'] = 1

# Display the structure of data_recent to ensure 'made_playoffs' is present
print(data_recent.head())

# Group by season and team, then sum the 'made_playoffs' to get team-level playoff appearance
team_playoffs = data_recent.groupby(['season', 'team_id'], as_index=False).sum(numeric_only=True)[['season', 'team_id', 'made_playoffs']]

# Display the structure of team_playoffs to ensure it includes 'made_playoffs'
print(team_playoffs.head())

# Ensure team_id and season are included in numeric_data_recent
numeric_data_recent = data_recent.select_dtypes(include='number').copy()
numeric_data_recent['season'] = data_recent['season']
numeric_data_recent['team_id'] = data_recent['team_id']

# Display the structure of numeric_data_recent to ensure it includes 'season' and 'team_id'
print(numeric_data_recent.head())

# Merge team playoffs with numeric data
team_stats = numeric_data_recent.merge(team_playoffs, on=['season', 'team_id'], how='left', suffixes=('', '_team'))

# Display the structure of team_stats to ensure 'made_playoffs' is present
print(team_stats.head())

# Fill NaNs in 'made_playoffs_team' with 0 (for teams that didn't make the playoffs)
if 'made_playoffs_team' in team_stats.columns:
    team_stats['made_playoffs_team'] = team_stats['made_playoffs_team'].fillna(0)
else:
    raise KeyError("Column 'made_playoffs_team' not found in team_stats after merge.")

# Select only numeric columns for correlation calculation
numeric_columns = team_stats.select_dtypes(include='number')

# Calculate the correlation matrix
correlation_matrix = numeric_columns.corr()

# Get the correlation of each stat with 'made_playoffs_team'
playoff_correlation = correlation_matrix['made_playoffs_team'].sort_values(ascending=False)

# Display the top correlations
print(playoff_correlation.head(10))

