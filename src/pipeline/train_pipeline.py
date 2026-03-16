from src.components.model_trainer import ModelTrainer
from src.logger import logging


class TrainPipeline:

    def __init__(self):
        pass

    def run_pipeline(self):

        logging.info("Starting training pipeline")

        train_path = "data/processed/train_engineered.csv"
        test_path = "data/processed/test_engineered.csv"

        trainer = ModelTrainer()

        results_df = trainer.initiate_model_training(
            train_path=train_path,
            test_path=test_path
        )

        logging.info("Training completed successfully")

        print("\nTraining Completed Successfully\n")
        print(results_df)


if __name__ == "__main__":

    pipeline = TrainPipeline()

    pipeline.run_pipeline()