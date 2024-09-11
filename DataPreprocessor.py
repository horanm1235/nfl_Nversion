class DataPreprocessor:
    def __init__(self, df):
        """
        Initialize the preprocessor with a DataFrame containing raw NFL data.
        
        Args:
            df (pd.DataFrame): Raw DataFrame with NFL statistics.
        """
        self.df = df

    def handle_missing_values(self):
        """
        Handles missing values in the dataset by replacing zeroes with NaN and imputing where necessary.
        """
        import numpy as np
        from sklearn.impute import SimpleImputer

        # Replace zeros with NaN where appropriate
        self.df.replace(0, np.nan, inplace=True)

        # Numerical columns to impute
        numerical_columns = ['rush_att', 'rush_yds', 'rush_tds', 'pass_cmp', 'pass_att', 
                             'pass_yds', 'pass_tds', 'pass_int', 'passer_rating', 'net_pass_yds', 
                             'total_yds', 'times_sacked', 'yds_sacked_for', 'fumbles', 'fumbles_lost', 
                             'turnovers', 'penalties', 'penalty_yds', 'first_downs', 'third_down_conv', 
                             'third_down_att', 'third_down_conv_pct', 'fourth_down_conv', 
                             'fourth_down_att', 'fourth_down_conv_pct', 'time_of_possession', 
                             'temperature', 'humidity_pct', 'wind_speed']

        imputer = SimpleImputer(strategy='mean')
        self.df[numerical_columns] = imputer.fit_transform(self.df[numerical_columns])

        # Categorical columns
        categorical_columns = ['roof_type', 'surface_type', 'tm_location', 'opp_location', 'opponent']
        imputer_cat = SimpleImputer(strategy='most_frequent')
        self.df[categorical_columns] = imputer_cat.fit_transform(self.df[categorical_columns])

    def encode_categorical_variables(self):
        """
        Converts categorical variables to numeric form using one-hot encoding.
        """
        categorical_columns = ['roof_type', 'surface_type', 'tm_location', 'opp_location', 'opponent']
        self.df = pd.get_dummies(self.df, columns=categorical_columns, drop_first=True)

    def add_target_variable(self):
        """
        Creates a target variable `covered_spread` based on the team score, opponent score, and spread.
        """
        self.df['covered_spread'] = (self.df['tm_score'] + self.df['tm_spread']) > self.df['opp_score']
        self.df['covered_spread'] = self.df['covered_spread'].astype(int)

    def get_features_and_target(self):
        """
        Returns the features (X) and target (y) for modeling.
        
        Returns:
            X (pd.DataFrame): DataFrame containing feature columns.
            y (pd.Series): Series containing target labels.
        """
        X = self.df.drop(columns=['tm_score', 'opp_score', 'covered_spread'])
        y = self.df['covered_spread']
        return X, y
