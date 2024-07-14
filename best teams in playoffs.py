import pandas as pd

def load_data(file_path):
    return pd.read_csv(file_path)

def group_by_season_and_team(data):
    grouped = data.groupby(['season', 'team_id'])
    subsets = {}
    for (season, team_id), group in grouped:
        if season not in subsets:
            subsets[season] = {}
        subsets[season][team_id] = group
    return subsets

def display_structure(subsets):
    for season in subsets:
        print(f"Season: {season}")
        for team_id in subsets[season]:
            print(f"  Team ID: {team_id}, Number of Players: {len(subsets[season][team_id])}")

def filter_data(data, start_season):
    return data[data['season'] >= start_season].copy()

def playoff_indicator(data):
    data['made_playoffs'] = 1
    return data

def made_playoffs(data):
    return data.groupby(['season', 'team_id'], as_index=False).sum(numeric_only=True)[['season', 'team_id', 'made_playoffs']]

def merge_team_stats(numeric_data, team_playoffs):
    return numeric_data.merge(team_playoffs, on=['season', 'team_id'], how='left', suffixes=('', '_team'))

def fill_na_and_calculate_correlation(team_stats):
    if 'made_playoffs_team' in team_stats.columns:
        team_stats['made_playoffs_team'] = team_stats['made_playoffs_team'].fillna(0)
    else:
        raise KeyError("Column 'made_playoffs_team' not found in team_stats after merge.")
    numeric_columns = team_stats.select_dtypes(include='number')
    correlation_matrix = numeric_columns.corr()
    return correlation_matrix['made_playoffs_team'].sort_values(ascending=False)

def calculate_team_mean_stats(data, associated_stats):
    team_stats = data[associated_stats]
    return team_stats.groupby(['season', 'team_id']).mean().reset_index()

def find_best_teams(team_mean_stats, associated_stats):
    best_teams = {}
    for stat in associated_stats[2:]:
        best_team = team_mean_stats.loc[team_mean_stats[stat].idxmax()]
        best_teams[stat] = best_team
    return best_teams

def display_best_teams(best_teams):
    for stat, best_team in best_teams.items():
        print(f"Best team for {stat}: Season {best_team['season']}, Team {best_team['team_id']}, Value {best_team[stat]}")

def rank_teams(team_mean_stats, associated_stats):
    rankings = {}
    for stat in associated_stats[2:]:
        rankings[stat] = team_mean_stats[['season', 'team_id', stat]].sort_values(by=stat, ascending=False).reset_index(drop=True)
        rankings[stat]['Rank'] = rankings[stat].index + 1
    return rankings

def display_team_rankings(rankings):
    for stat, ranking in rankings.items():
        print(f"\nRanking for {stat}:")
        print(ranking.head(10))  # Display top 10 teams for each stat

def get_team_rankings_and_stats(team_mean_stats, nba_finals_teams, associated_stats):
    rankings = rank_teams(team_mean_stats, associated_stats)
    results = []
    for team, year in nba_finals_teams:
        team_stats = team_mean_stats[(team_mean_stats['team_id'] == team) & (team_mean_stats['season'] == year)]
        if not team_stats.empty:
            team_result = {'season': year, 'team_id': team}
            for stat in associated_stats[2:]:
                rank = rankings[stat][(rankings[stat]['team_id'] == team) & (rankings[stat]['season'] == year)]['Rank']
                if not rank.empty:
                    team_result[stat] = team_stats[stat].values[0]
                    team_result[f'{stat}_rank'] = rank.values[0]
                else:
                    team_result[stat] = None
                    team_result[f'{stat}_rank'] = None
            results.append(team_result)
        else:
            print(f"No data found for {team} in {year}")
    return pd.DataFrame(results)

def calculate_thresholds(team_rankings_and_stats):
    thresholds = {}
    for column in team_rankings_and_stats.columns:
        if column.endswith('_rank'):
            thresholds[column] = team_rankings_and_stats[column].max()
    return thresholds

def predict_finals_teams(team_mean_stats, thresholds, associated_stats):
    rankings = rank_teams(team_mean_stats, associated_stats)
    potential_teams = []
    for index, row in team_mean_stats.iterrows():
        qualifies = True
        for stat in associated_stats[2:]:
            if row[stat] != row[stat]:  # Check for NaN
                qualifies = False
                break
            rank_column = f'{stat}_rank'
            rank = rankings[stat][(rankings[stat]['team_id'] == row['team_id']) & (rankings[stat]['season'] == row['season'])]['Rank'].values[0]
            if rank > thresholds[rank_column]:
                qualifies = False
                break
        if qualifies:
            potential_teams.append(row)
    return pd.DataFrame(potential_teams)

# Main script
file_path = 'C:/Users/Chuks/Documents/NBA Team Building/playoffStats.csv'
data = load_data(file_path)

# Check unique values in team_id and season
print("Unique team IDs:", data['team_id'].unique())
print("Unique seasons:", data['season'].unique())

subsets = group_by_season_and_team(data)
display_structure(subsets)

data_recent = filter_data(data, 2019)
data_recent = playoff_indicator(data_recent)
team_playoffs = made_playoffs(data_recent)

numeric_data_recent = data_recent.select_dtypes(include='number').copy()
numeric_data_recent['season'] = data_recent['season']
numeric_data_recent['team_id'] = data_recent['team_id']

team_stats = merge_team_stats(numeric_data_recent, team_playoffs)
playoff_correlation = fill_na_and_calculate_correlation(team_stats)
print(playoff_correlation.head(10))

associated_stats = ['season', 'team_id', 'vorp', 'gs', 'ws_per_48', 'fg2_pct', 'dws', 'ws', 'ows']
team_mean_stats = calculate_team_mean_stats(data_recent, associated_stats)

best_teams = find_best_teams(team_mean_stats, associated_stats)
display_best_teams(best_teams)

rankings = rank_teams(team_mean_stats, associated_stats)
display_team_rankings(rankings)

# Teams and years to check
nba_finals_teams = [("TOR", 2019), ("GSW", 2019), ("LAL", 2020), ("MIA", 2020), ("MIL", 2021), ("PHO", 2021), ("GSW", 2022), ("BOS", 2022)]

team_rankings_and_stats = get_team_rankings_and_stats(team_mean_stats, nba_finals_teams, associated_stats)
print("\nTeam Rankings and Stats for Specified Teams and Years:")
print(team_rankings_and_stats)

# Calculate thresholds for each statistic
thresholds = calculate_thresholds(team_rankings_and_stats)
print("\nThresholds for each statistic to be included in NBA Finals teams list:")
print(thresholds)

# Predict future NBA Finals teams
#future_finals_teams = predict_finals_teams(team_mean_stats, thresholds, associated_stats)
#print("\nPredicted Future NBA Finals Teams:")
#print(future_finals_teams)
