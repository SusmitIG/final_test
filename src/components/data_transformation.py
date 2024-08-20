import sys
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from src.exception import CustomException
from src.logger import logging
from src.utils import save_object
from dataclasses import dataclass

@dataclass
class DataTransformationConfig:
    preprocessor_ob_file_path = os.path.join('artifacts','preprocessor.pkl')

class DataTransformation:
    def __init__(self):
        self.data_transformation_config=DataTransformationConfig()

    def get_data_transformation_object(self):
        '''
        Responsible for column transformation
        '''
        try:
            numerical_columns = ['reading_score', 'writing_score']
            categorical_columns = [
                'gender',
                'race_ethnicity',
                'parental_level_of_education',
                'lunch',
                'test_preparation_course'
            ]

            num_pipeline=Pipeline(
                steps=[
                ("imputer",SimpleImputer(strategy='median')),
                ("scaler",StandardScaler(with_mean=False))
                ]
            )
            logging.info("numeric missing_value_imputation+scaling completed")
            cat_pipeline=Pipeline(
                steps=[
                ("imputer",SimpleImputer(strategy='most_frequent')),
                ("one_hot_encoder",OneHotEncoder()),
                ("scaler",StandardScaler(with_mean=False))
                ]
            )
            logging.info("categorical missing_value_imputation+ohe+scaling completed")

            preprocessor=ColumnTransformer(
                [
                ("num_pipeline",num_pipeline,numerical_columns),
                ("cat_pipeline",cat_pipeline,categorical_columns)
                ]
            )
            return preprocessor
        except Exception as e:
            raise CustomException(e,sys)
    
    def initiate_data_transformation(self,train_path,test_path):

        try:
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)

            logging.info("Read train-test data completed")

            logging.info("Obtaining preprocessing object")

            preprocessing_obj=self.get_data_transformation_object()

            target_column_name="math_score"
            numerical_columns = ['reading_score', 'writing_score']

            input_feature_train_df=train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df=train_df[target_column_name]

            input_feature_test_df=test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df=test_df[target_column_name]

            logging.info(
                f"applying preprocessing on training as well as test dataframe"
            )

            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr=preprocessing_obj.transform(input_feature_test_df)


            # np.c_ concatenates column wise concatinating 2arrs inp+target colwise to create full train_arr (np.r_ will concatenate row wise stack one arr on another)
            train_arr=np.c_[
                input_feature_train_arr,np.array(target_feature_train_df)
            ]

            test_arr=np.c_[
                input_feature_test_arr,np.array(target_feature_test_df)
            ]

            logging.info('Saved preprocessing object')
            
            save_object(
                file_path=self.data_transformation_config.preprocessor_ob_file_path,
                obj=preprocessing_obj
            )

            return(
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_ob_file_path
            )


        except Exception as e:
            raise CustomException(e,sys)
