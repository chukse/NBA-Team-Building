import pandas as pd 
# Load data
def load_data(file_path):
    return pd.read_csv(file_path)

# Mark NBA Finals Teams
def mark_nba_finals_teams(data, nba_finals_teams):
    data['is_nba_finals'] = data.apply(lambda row: (row['team_id'], row['season']) in nba_finals_teams, axis=1)
    return data

# Calculate correlations with the NBA Finals indicator
def calculate_correlations(data, stats, target='is_nba_finals'):
    correlations = data[stats + [target]].corr()[target].sort_values(ascending=False)
    return correlations

# Filter data for particular seasons
def filter_data(data, start_season):
    return data[data['season'] >= start_season].copy()

# Get team averages for the associated stats
def calculate_team_mean_stats(data, associated_stats):
    team_stats = data[associated_stats]
    return team_stats.groupby(['season', 'team_id']).mean().reset_index()

# Rank teams for each statistic within each year
def rank_teams_by_year(team_mean_stats, associated_stats):
    rankings = {}
    for year in team_mean_stats['season'].unique():
        yearly_stats = team_mean_stats[team_mean_stats['season'] == year].copy()
        for stat in associated_stats[2:]:
            yearly_stats = yearly_stats.sort_values(by=stat, ascending=False).reset_index(drop=True)
            yearly_stats[f'{stat}_rank'] = yearly_stats.index + 1
        rankings[year] = yearly_stats
    return rankings

# Get rankings and stats for specific teams and years
def get_team_rankings_and_stats_by_year(rankings, nba_finals_teams, associated_stats):
    results = []
    for team, year in nba_finals_teams:
        if year in rankings:
            team_stats = rankings[year][rankings[year]['team_id'] == team]
            if not team_stats.empty:
                team_result = team_stats.iloc[0].to_dict()
                results.append(team_result)
            else:
                print(f"No data found for {team} in {year}")
        else:
            print(f"No rankings data found for year {year}")
    return pd.DataFrame(results)

# Calculate thresholds for each statistic to be included in NBA Finals teams list
def calculate_thresholds(team_rankings_and_stats):
    thresholds = {}
    for column in team_rankings_and_stats.columns:
        if column.endswith('_rank'):
            thresholds[column] = team_rankings_and_stats[column].max()
    return thresholds

# Predict future NBA Finals teams based on thresholds
def predict_finals_teams(rankings, thresholds, associated_stats):
    potential_teams = []
    for year, yearly_stats in rankings.items():
        for index, row in yearly_stats.iterrows():
            qualifies = True
            for stat in associated_stats[2:]:
                rank_column = f'{stat}_rank'
                if row[rank_column] > thresholds[rank_column]:
                    qualifies = False
                    break
            if qualifies:
                potential_teams.append(row)
    return pd.DataFrame(potential_teams)

# Main script
file_path = 'C:/Users/Chuks/Documents/NBA Team Building/NBA_Dataset.csv'
data = load_data(file_path)

# Define NBA Finals teams
nba_finals_teams = [("TOR", 2019), ("GSW", 2019), ("LAL", 2020), ("MIA", 2020), ("MIL", 2021), ("PHO", 2021), ("GSW", 2022), ("BOS", 2022)]

# Mark NBA Finals teams in the dataset
data = mark_nba_finals_teams(data, nba_finals_teams)

# Define stats to consider (all potential stats)
stats = ['vorp', 'gs', 'ws_per_48', 'fg2_pct', 'dws', 'ws', 'ows']

# Calculate correlations with the NBA Finals indicator
correlations = calculate_correlations(data, stats)

# Select top correlated stats
top_stats = correlations.index[1:7].tolist()  # Exclude 'is_nba_finals' itself
print("Top correlated stats:", top_stats)

# Filter data from 2019 onwards
data_recent = filter_data(data, 2019)

# Calculate team mean stats
associated_stats = ['season', 'team_id'] + top_stats
print("Associated stats:", associated_stats)
team_mean_stats = calculate_team_mean_stats(data_recent, associated_stats)

# Rank teams per year
rankings_by_year = rank_teams_by_year(team_mean_stats, associated_stats)

# Display rankings for debugging
for year, ranking in rankings_by_year.items():
    print(f"\nRankings for {year}:")
    print(ranking[associated_stats])

# Get team rankings and stats for NBA Finals teams
team_rankings_and_stats = get_team_rankings_and_stats_by_year(rankings_by_year, nba_finals_teams, associated_stats)
print("\nTeam Rankings and Stats for Specified Teams and Years:")
print(team_rankings_and_stats)

# Calculate thresholds for each statistic
thresholds = calculate_thresholds(team_rankings_and_stats)
print("\nThresholds for each statistic to make the NBA Finals:")
print(thresholds)

output_file_path = 'C:/Users/Chuks/Documents/NBA Team Building/Team_Rankings_and_Stats.csv'
team_rankings_and_stats.to_csv(output_file_path, index=False)
print(f"\nTeam rankings and stats saved to {output_file_path}")

# Predict future NBA Finals teams
# future_finals_teams = predict_finals_teams(rankings_by_year, thresholds, associated_stats)
# print("\nPredicted Future NBA Finals Teams:")
# print(future_finals_teams)


