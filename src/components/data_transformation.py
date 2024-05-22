import sys
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer #used to create data pipeline with all transformation steps
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object

@dataclass
class DataTransformationConfig:
    # provide input to Data Transformation
    preprocessor_ob_file_path= os.path.join('artifacts','preprocessor.pkl')
    
class DataTransformation:
    def __init__(self):
        self.data_transformation_config= DataTransformationConfig()
        
    def get_data_transformer_object(self):
        #create pickle files for all transformation steps
        '''
        This function is responsible for data transformation steps
        '''
        try:
            numerical_columns=["writing_score","reading_score"]
            categorical_columns=["gender","race_ethnicity","parental_level_of_education","lunch","test_preparation_course"]
            
            #1. Create numerical pipeline
            num_pipeline= Pipeline(
                steps=[
                    ("imputer",SimpleImputer(strategy="median")), #handling missing values with median
                       ("scaler", StandardScaler())# Standardization of data
                       ] 
            )
            #2. Create categorical data pipeline
            cat_pipeline=Pipeline(
                steps=[
                    ("imputer",SimpleImputer(strategy="most_frequent")), #handling missing values with mode
                    ("one_hot_encoder",OneHotEncoder()), #converting categorical to numerical values
                    ("scaler",StandardScaler(with_mean=False)) #Standardization of data
                ] 
            )
            
            logging.info(f"Numerical columns: {numerical_columns}")
            logging.info(f"Categorical columns: {categorical_columns}")
            
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
            
            logging.info("Read Train and Test data completed")
            logging.info("Obtaining Preprocessing object")
            
            preprocessing_obj=self.get_data_transformer_object()
            
            target_column_name="math_score"
            
            numerical_columns=["writing_score","reading_score"]
            
            input_feature_train_df= train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df= train_df[target_column_name]
            
            input_feature_test_df= test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df= test_df[target_column_name]
            
            logging.info("Applying preprocessing object on training and testing dataframe")
            
            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr= preprocessing_obj.transform(input_feature_test_df)
            
            train_arr= np.c_[input_feature_train_arr,np.array(target_feature_train_df)]
            test_arr= np.c_[input_feature_test_arr,np.array(target_feature_test_df)]
            logging.info("Saved preprocessing object")
            
            save_object(
                file_path=self.data_transformation_config.preprocessor_ob_file_path,
                obj=preprocessing_obj
                )
            
            return(train_arr,test_arr,self.data_transformation_config.preprocessor_ob_file_path)
        except Exception as e:
            raise CustomException(e,sys)
        

        
         
