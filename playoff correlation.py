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

# Save subsets to CSV files
for season in subsets:
    for team_id in subsets[season]:
        file_name = f'subset_season_{season}_team_{team_id}.csv'
        subsets[season][team_id].to_csv(f'/mnt/data/{file_name}', index=False)

# Filter data for seasons from 2021 onwards
data_recent = data[data['season'] >= 2021]

# Determine unique teams that made the playoffs since 2021
teams = data_recent['team_id'].unique()

# Create a dataframe to store playoff appearances
playoff_appearances = pd.DataFrame(index=teams, columns=range(2021, data_recent['season'].max() + 1))

# Mark playoff appearances
for season in playoff_appearances.columns:
    season_teams = data_recent[data_recent['season'] == season]['team_id'].unique()
    playoff_appearances[season] = playoff_appearances.index.isin(season_teams).astype(int)

# Calculate correlation matrix
correlation_matrix = playoff_appearances.corr()

# Display the correlation matrix
print(correlation_matrix)
