from src.components.feature_importance import FeatureImportance


class FeatureImportancePipeline:

    def run_pipeline(self):

        feature = FeatureImportance()

        feature.generate()


if __name__ == "__main__":

    pipeline = FeatureImportancePipeline()

    pipeline.run_pipeline()