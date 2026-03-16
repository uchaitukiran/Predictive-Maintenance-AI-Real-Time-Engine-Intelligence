from src.components.hyperparameter_tuner import HyperparameterTuner


class TuningPipeline:

    def run_pipeline(self):

        tuner = HyperparameterTuner()

        tuner.tune_model(
            train_path="data/processed/train_engineered.csv",
            test_path="data/processed/test_engineered.csv"
        )


if __name__ == "__main__":

    pipeline = TuningPipeline()

    pipeline.run_pipeline()