from Backend import ModifyCSV as MCSV
from Backend import convertUseful as cU
from Backend import ModelTesting as MT
import pandas as pd

def process_uploaded_file(name ,input_file_path):
        
    Average_confidence = cU.process_csv1(input_file_path,'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/{name}_vf1.csv')
    firstCSV = MCSV.process_csv2('C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/{name}_vf1.csv')
    finalCSV = MT.test_model_with_history(name,'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/{name}_vf2.csv','C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/{name}_FINAL.csv')    
    return Average_confidence
