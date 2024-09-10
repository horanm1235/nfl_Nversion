import nflscraPy
from datetime import datetime, timedelta
import pandas as pd
import os

class NFLGameStats:
    def __init__(self, week=None):
        """Initialize the object with a week number or default to the current week."""
        self.week = week if week else self.get_current_week()
        self.current_season = datetime.today().year
        self.team_stats_list = []
        self.season_start = datetime(2024, 9, 5)  # Season starts on Thursday, 2024-09-05

    def get_current_week(self):
        """Determines the current NFL week based on today's date."""
        today = datetime.today()
        days_since_start = (today - self.season_start).days
        current_week = days_since_start // 7 + 1
        return current_week

    def get_week_start_date(self):
        """Calculates the Thursday date for the given week."""
        return self.season_start + timedelta(weeks=self.week - 1)

    def fetch_games(self):
        """Fetches the games for the given week, from Thursday to Monday."""
        start_date = self.get_week_start_date()
        end_date = start_date + timedelta(days=4)  # Monday is 4 days after Thursday

        print(f"Fetching games from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} for week {self.week}.")

        try:
            # Using _gamelogs to fetch the game logs for the season
            all_games = nflscraPy._gamelogs(self.current_season)
        except Exception as e:
            print(f"Error fetching game logs: {e}")
            return

        # Filter games for the date range (Thursday to Monday)
        games_in_week = all_games[(all_games['event_date'] >= start_date.strftime('%Y-%m-%d')) & 
                                  (all_games['event_date'] <= end_date.strftime('%Y-%m-%d'))]

        if games_in_week.empty:
            print(f"No games scheduled from {start_date} to {end_date}.")
            return

        print(f"Fetching data for {len(games_in_week)} games happening in week {self.week}")
        
        # Loop over games and fetch detailed stats
        for idx, game in games_in_week.iterrows():
            self.process_game(game)

        # Convert the stats list to a DataFrame and display
        self.display_stats()

    def process_game(self, game):
        """Processes a single game and fetches statistics and metadata."""
        game_url = game['boxscore_stats_link']
        print(f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"Processing game between {game['tm_name']} and {game['opp_name']} on {game['event_date']}")
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        # Fetch statistics and metadata
        team1_stats, team2_stats, metadata = self.extract_game_statistics(game_url, game['tm_name'], game['opp_name'])

        if team1_stats and team2_stats:
            # Process and add stats
            self.process_stats(game, team1_stats, team2_stats, metadata)
        else:
            print(f"Game between {game['tm_name']} and {game['opp_name']} has no stats available yet.")

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

        # Ensure that team1_stats corresponds to team1_name and team2_stats to team2_name
        if 'market' in gamelog_statistics.columns:
            if gamelog_statistics.iloc[0]['market'] == team1_name:
                team1_stats = self.extract_team_stats(gamelog_statistics.iloc[0], team1_name)
                team2_stats = self.extract_team_stats(gamelog_statistics.iloc[1], team2_name)
            else:
                team1_stats = self.extract_team_stats(gamelog_statistics.iloc[1], team1_name)
                team2_stats = self.extract_team_stats(gamelog_statistics.iloc[0], team2_name)
        else:
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
        """Extracts specific metadata from the game."""
        cleaned_metadata = {
            'tm_spread': self.clean_value(metadata.get('tm_spread', 0)),
            'opp_spread': self.clean_value(metadata.get('opp_spread', 0)),
            'total': self.clean_value(metadata.get('total', 0)),
            'attendance': self.clean_value(metadata.get('attendance', 0)),
            'duration': self.clean_value(metadata.get('duration', 0)),
            'roof_type': self.clean_value(metadata.get('roof_type', '0'), expected_type='string'),  # Ensure strings are handled
            'surface_type': self.clean_value(metadata.get('surface_type', '0'), expected_type='string'),  # Ensure strings are handled
            'temperature': self.clean_value(metadata.get('temperature', 0)),
            'humidity_pct': self.clean_value(metadata.get('humidity_pct', 0)),
            'wind_speed': self.clean_value(metadata.get('wind_speed', 0)),
        }
        return cleaned_metadata



    def clean_value(self, value, expected_type=None):
        """Cleans individual values by removing leading zeros and replacing None/NaN/N/A with 0."""
        if isinstance(value, pd.Series):
            # If value is a Series, extract the first element
            value = value.iloc[0] if not value.empty else None
        if pd.isna(value) or value in [None, 'N/A', 'None', '']:  # Handle NaN, None, empty, etc.
            return '0' if expected_type == 'string' else 0
        if isinstance(value, str):
            return value.strip() if value.strip() else '0'  # Remove leading/trailing spaces
        return float(value)  # Convert to float if it's a number

    def process_stats(self, game, team1_stats, team2_stats, metadata):
        """Helper function to process and add the stats for both teams."""
        tm_location = game['tm_location']
        opp_location = game['opp_location']
        tm_score = game['tm_score']
        opp_score = game['opp_score']

        # Create metadata for both perspectives (team1, team2)
        metadata_team1 = metadata.copy()
        metadata_team2 = metadata.copy()

        if tm_location == 'H':  # Tm is home
            metadata_team1['tm_spread'] = metadata['tm_spread']
            metadata_team1['opp_spread'] = metadata['opp_spread']
            metadata_team2['tm_spread'] = metadata['opp_spread']
            metadata_team2['opp_spread'] = metadata['tm_spread']
        else:  # Tm is away
            metadata_team1['tm_spread'] = metadata['opp_spread']
            metadata_team1['opp_spread'] = metadata['tm_spread']
            metadata_team2['tm_spread'] = metadata['tm_spread']
            metadata_team2['opp_spread'] = metadata['opp_spread']

        metadata_team1.update({
            'tm_location': tm_location,
            'opp_location': opp_location,
            'tm_score': tm_score,
            'opp_score': opp_score
        })

        metadata_team2.update({
            'tm_location': opp_location,
            'opp_location': tm_location,
            'tm_score': opp_score,
            'opp_score': tm_score
        })

        # Clean stats before adding
        team1_stats = self.clean_stats(team1_stats)
        team2_stats = self.clean_stats(team2_stats)

        # Add both perspectives
        team1_stats.update(metadata_team1)
        team1_stats['team'] = game['tm_name']
        team1_stats['opponent'] = game['opp_name']
        self.team_stats_list.append(team1_stats)

        team2_stats.update(metadata_team2)
        team2_stats['team'] = game['opp_name']
        team2_stats['opponent'] = game['tm_name']
        self.team_stats_list.append(team2_stats)

    def clean_stats(self, stats):
        """Removes leading zeros, handles NaN values, and formats the values correctly."""
        cleaned_stats = {}
        for key, value in stats.items():
            cleaned_stats[key] = self.clean_value(value)  # Use clean_value method to handle cleaning
        return cleaned_stats

    def display_stats(self):
        """Displays the collected statistics in DataFrame format and exports to Excel."""
        if not self.team_stats_list:
            print("No data available to display yet, but some games may still be in progress.")
            return

        df = pd.DataFrame(self.team_stats_list)

        # Save the DataFrame to CSV
        csv_filename = f'nfl_game_stats_week_{self.week}.csv'
        df.to_csv(csv_filename, index=False)
        print(f"Data saved to {csv_filename}")

# Example usage:
week = 1  # Set the week number you want to fetch
nfl_stats = NFLGameStats(week=week)
nfl_stats.fetch_games()
