from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

class SVMModel:
    def __init__(self):
        """
        Initializes the SVMModel class, setting up placeholders for the model, scaler, etc.
        """
        self.model = SVC(kernel='rbf', C=1.0, gamma='scale')
        self.scaler = StandardScaler()

    def split_data(self, X, y, test_size=0.2):
        """
        Splits the data into training and test sets.
        
        Args:
            X (pd.DataFrame): Feature set.
            y (pd.Series): Target labels.
            test_size (float): Proportion of data to reserve for testing.

        Returns:
            X_train, X_test, y_train, y_test: Splits of the data.
        """
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        return X_train, X_test, y_train, y_test

    def scale_features(self, X_train, X_test):
        """
        Scales the features using StandardScaler.
        
        Args:
            X_train (pd.DataFrame): Training feature set.
            X_test (pd.DataFrame): Test feature set.

        Returns:
            Scaled X_train and X_test.
        """
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        return X_train_scaled, X_test_scaled

    def train(self, X_train, y_train):
        """
        Trains the SVM model on the training set.
        
        Args:
            X_train (np.array): Scaled training feature set.
            y_train (pd.Series): Training labels.
        """
        self.model.fit(X_train, y_train)

    def evaluate(self, X_test, y_test):
        """
        Evaluates the SVM model on the test set, printing accuracy and a classification report.
        
        Args:
            X_test (np.array): Scaled test feature set.
            y_test (pd.Series): Test labels.
        """
        y_pred = self.model.predict(X_test)
        print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
        print(classification_report(y_test, y_pred))
