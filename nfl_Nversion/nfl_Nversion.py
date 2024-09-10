import nflscraPy
from datetime import datetime
import pandas as pd
import os

class NFLGameStats:
    def __init__(self, date=None):
        """Initialize the object with a date or default to today's date."""
        self.date = date if date else datetime.today().strftime('%Y-%m-%d')
        self.current_season = datetime.today().year
        self.team_stats_list = []

    def fetch_games(self):
        """Fetches the games for the given date using the '_gamelogs' method."""
        try:
            # Using _gamelogs to fetch the game logs
            all_games = nflscraPy._gamelogs(self.current_season)
        except Exception as e:
            print(f"Error fetching game logs: {e}")
            return

        games_on_date = all_games[all_games['event_date'] == self.date]
       
        if games_on_date.empty:
            print(f"No games scheduled for {self.date}.")
            return
       
        print(f"Fetching data for {len(games_on_date)} games happening on {self.date}")
       
        # Loop over games and fetch detailed stats
        for idx, game in games_on_date.iterrows():
            self.process_game(game)
       
        # Convert the stats list to a DataFrame and display
        self.display_stats()

    def process_game(self, game):
        """Processes a single game and fetches statistics and metadata."""
        game_url = game['boxscore_stats_link']
        print(f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"Processing game between {game['tm_name']} and {game['opp_name']} on {game['event_date']}")
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        # Extract additional fields from the game DataFrame row
        tm_location = game['tm_location']  # Tm's location (H, A, N)
        opp_location = game['opp_location']  # Opp's location (H, A, N)
        tm_score = game['tm_score']  # Tm's score
        opp_score = game['opp_score']  # Opp's score
        week = game['week']  # Week of the game

        # Fetch the statistics for both teams
        team1_stats, team2_stats, metadata = self.extract_game_statistics(game_url, game['tm_name'], game['opp_name'])

        # Add metadata for team 1's perspective
        metadata_team1 = metadata.copy()  # Create a copy of the metadata for each team's entry
        metadata_team1.update({
            'tm_location': tm_location,
            'opp_location': opp_location,
            'tm_score': tm_score,
            'opp_score': opp_score,
            'week': week
        })

        # Add metadata for team 2's perspective, where the locations are swapped
        metadata_team2 = metadata.copy()
        metadata_team2.update({
            'tm_location': opp_location,  # Swapped with the opponent's location
            'opp_location': tm_location,  # Swapped with the team's location
            'tm_score': opp_score,        # Swap scores as well
            'opp_score': tm_score,
            'week': week
        })

        if team1_stats and team2_stats:
            # Add team1's perspective
            team1_stats.update(metadata_team1)
            team1_stats['team'] = game['tm_name']  # Eagles (for example)
            team1_stats['opponent'] = game['opp_name']  # Packers (for example)
            self.team_stats_list.append(team1_stats)

            # Add team2's perspective with the swapped location and score
            team2_stats.update(metadata_team2)
            team2_stats['team'] = game['opp_name']  # Packers
            team2_stats['opponent'] = game['tm_name']  # Eagles
            self.team_stats_list.append(team2_stats)
        else:
            print(f"Stats not available yet for {game_url}")

    def extract_game_statistics(self, game_url, team1_name, team2_name):
        """Extracts game statistics for both teams and metadata."""
        try:
            gamelog_metadata = nflscraPy._gamelog_metadata(game_url)  # Using private method
        except Exception as e:
            print(f"Metadata not available for {game_url}: {e}")
            return None, None, {}

        try:
            gamelog_statistics = nflscraPy._gamelog_statistics(game_url)  # Using private method
        except Exception as e:
            print(f"Statistics not available for {game_url}: {e}")
            return None, None, {}

        # Check the available columns in the gamelog_statistics DataFrame
        print(f"Available columns: {gamelog_statistics.columns}")

        # Ensure that team1_stats corresponds to team1_name (Eagles) and team2_stats to team2_name (Packers)
        if 'market' in gamelog_statistics.columns:
            # Use 'market' as the column for identifying teams
            if gamelog_statistics.iloc[0]['market'] == team1_name:
                team1_stats = self.extract_team_stats(gamelog_statistics.iloc[0], team1_name)
                team2_stats = self.extract_team_stats(gamelog_statistics.iloc[1], team2_name)
            else:
                team1_stats = self.extract_team_stats(gamelog_statistics.iloc[1], team1_name)
                team2_stats = self.extract_team_stats(gamelog_statistics.iloc[0], team2_name)
        else:
            # Handle the case where the expected column is missing
            print("The 'market' column is missing. Please check the column names.")
            return None, None, {}

        metadata = self.extract_game_metadata(gamelog_metadata)
        return team1_stats, team2_stats, metadata

    def extract_team_stats(self, team_data, team_name):
        """Extracts specific team statistics."""
        return {
            'team': team_name,
            'rush_att': team_data.get('rush_att', 0),
            'rush_yds': team_data.get('rush_yds', 0),
            'rush_tds': team_data.get('rush_tds', 0),
            'pass_cmp': team_data.get('pass_cmp', 0),
            'pass_att': team_data.get('pass_att', 0),
            'pass_yds': team_data.get('pass_yds', 0),
            'pass_tds': team_data.get('pass_tds', 0),
            'pass_int': team_data.get('pass_int', 0),
            'passer_rating': team_data.get('passer_rating', 0),
            'net_pass_yds': team_data.get('net_pass_yds', 0),
            'total_yds': team_data.get('total_yds', 0),
            'times_sacked': team_data.get('times_sacked', 0),
            'yds_sacked_for': team_data.get('yds_sacked_for', 0),
            'fumbles': team_data.get('fumbles', 0),
            'fumbles_lost': team_data.get('fumbles_lost', 0),
            'turnovers': team_data.get('turnovers', 0),
            'penalties': team_data.get('penalties', 0),
            'penalty_yds': team_data.get('penalty_yds', 0),
            'first_downs': team_data.get('first_downs', 0),
            'third_down_conv': team_data.get('third_down_conv', 0),
            'third_down_att': team_data.get('third_down_att', 0),
            'third_down_conv_pct': team_data.get('third_down_conv_pct', 0),
            'fourth_down_conv': team_data.get('fourth_down_conv', 0),
            'fourth_down_att': team_data.get('fourth_down_att', 0),
            'fourth_down_conv_pct': team_data.get('fourth_down_conv_pct', 0),
            'time_of_possession': team_data.get('time_of_possession', "00:00"),
        }

    def extract_game_metadata(self, metadata):
        """Extracts specific metadata from the game, removes leading spaces, and formats data."""
    
        # Create the metadata dictionary
        cleaned_metadata = {
            'tm_spread': metadata.get('tm_spread', 0),
            'opp_spread': metadata.get('opp_spread', 0),
            'total': metadata.get('total', 0),
            'attendance': metadata.get('attendance', 0),
            'duration': metadata.get('duration', 0),
            'roof_type': metadata.get('roof_type', 'N/A'),
            'surface_type': metadata.get('surface_type', 'N/A'),
            'won_toss': metadata.get('won_toss', 'N/A'),
            'won_toss_decision': metadata.get('won_toss_decision', 'N/A'),
            'won_toss_overtime': metadata.get('won_toss_overtime', 'N/A'),
            'won_toss_overtime_decision': metadata.get('won_toss_overtime_decision', 'N/A'),
            'temperature': metadata.get('temperature', 'N/A'),
            'humidity_pct': metadata.get('humidity_pct', 'N/A'),
            'wind_speed': metadata.get('wind_speed', 'N/A'),
        }

        # Clean the fields and handle potential None or NaN values
        for key, value in cleaned_metadata.items():
            if isinstance(value, pd.Series):
                value = value.iloc[0]  # Ensure we are working with scalar values
            if value is None or pd.isna(value):
                cleaned_metadata[key] = 0  # Replace None or NaN with 0
            elif isinstance(value, str):
                cleaned_metadata[key] = value.strip()  # Remove leading spaces for strings
            else:
                cleaned_metadata[key] = float(value)  # Format numbers as floats

        return cleaned_metadata


    def display_stats(self):
        """Displays the collected statistics in DataFrame format and exports to Excel."""
        if not self.team_stats_list:
            print("No data available to display.")
            return
    
        df = pd.DataFrame(self.team_stats_list)

        # Ensure proper formatting for numbers and strings
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            elif pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].astype(float)  # Convert all numeric columns to float

        # Display the DataFrame
        print(df)

        # Save the DataFrame to CSV
        csv_filename = f'nfl_game_stats_{self.date}.csv'
        df.to_csv(csv_filename, index=False)
        print(f"Data saved to {csv_filename}")

        # Save the DataFrame to Excel
        excel_filename = f'nfl_game_stats_{self.date}.xlsx'
        with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Game Stats', index=False)
        print(f"Data saved to {excel_filename}")

# Example usage:
input_date = "2024-09-06"
nfl_stats = NFLGameStats(input_date)
nfl_stats.fetch_games()
