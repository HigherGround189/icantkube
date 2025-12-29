from sklearn import datasets
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from main import Status

class ModelTrainingPipeline():
    def __init__(self, X, y, sample_dataset: bool=False, test_size: float=0.2 , random_number: int=42):
        self.X = X
        self.y = y
        self.sample_dataset = sample_dataset

        self.status = "pending"
        self.progress = 0
        self.result = ''
        self.error = ''

        self.random_number = random_number
        self.test_size = test_size
    
    def data_preparation(self):
        X_train, X_test, y_train, y_test = train_test_split(self.X, 
                                                            self.y,
                                                            test_size=self.test_size, 
                                                            random_state=self.random_number)
        return X_train, X_test, y_train, y_test

    def train_sample(self) -> None:
        try:
            self.status = Status.RUNNING.value

            iris = datasets.load_iris()
            self.X = iris.data
            self.y = iris.target 

            X_train, X_test, y_train, y_test = self.data_preparation()

            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('pca', PCA(n_components=2)),
                ('classifier', LogisticRegression())
            ])

            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)

            acc = self.metrics(y_pred, y_test)
            self.result = {"accuracy": acc}
            self.status = Status.COMPLETED.value
            self.progress = 100

        except Exception as e:
            self.status = Status.FAILED.value
            self.error = f"An error occurred: {e}"
    
    def metrics(self, y_pred, y_test) -> float:
        acc = accuracy_score(y_pred, y_test)
        return acc
    
    def run(self) -> None:
        if self.sample_dataset:
            self.train_sample()
        
if __name__ == "__main__":
    pipeline = ModelTrainingPipeline(X=None, y=None, sample_dataset=True)
    pipeline.run()
    print("Status", pipeline.status)
    print("Result", pipeline.result)
    print("Error", pipeline.error)