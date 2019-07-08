import pandas as pd
import numpy as np

class FrameSplitter:
    def __init__(self, y_col, ignore_cols):
        self.y_col = y_col
        self.ignore_cols = ignore_cols

    def reformat( self, df ):
        y = df[self.y_col]
        csv = pd.concat( [y, df.drop(self.y_col,axis=1).drop(self.ignore_cols,axis=1)], axis=1)
        return csv

    def map_sets( fun, dfs ):
        '''
        fun - function that operates on a df
        dfs - [[name1, df1], [name2,df2],...]
        
        returns - [result1, result2,...]
        '''
        
        return [[name,fun(df)] for [name, df] in dfs]
    
    def to_csv( self, df, file, sepr=','):
        '''
        Write a CSV that meets Sagemaker's requirements for training instances:
            - y columns are at [0]
            - non-x, non-y columns are dropped so they don't affect training
        '''
        df.to_csv( path_or_buf=file, sep=sepr,index=False, header=False)
    
    def split_frame( self, df, train_frac ):
        '''
        df - DataFrame (or array) containing rows of data for training, testing, and validation
        train_frac - Decimal representing how much of the set should be used for training.
        After reserving train_frac * len(df) rows for training, divide the remainder in half for testing and validation 
        populations.
        returns - list of dataframes as [training, testing, validation]
        '''
        l = len(df)
        test_frac = (1-train_frac)/2
        tr = int(train_frac * l)
        te = int(tr + test_frac * l)

        train = df[:tr]
        test = df[tr:te]
        val = df[te:]
        return [train, test, val]
    
    def train_split( self, df, y_split=.8 ):
        '''
        df - dataframe of training data with one labeled column
        y_col - column containing labels 1 or 0
        Given a dataset with rows in two classes, distinguished by a column y_col with values 1 or 0,
        split the dataset into [train, test, validate] sets containing values from both classes.       
        '''
        y1 = df[df[self.y_col]==1]
        y0 = df[df[self.y_col]==0]

        y1 = self.split_frame(y1, y_split)
        y0 = self.split_frame(y0, y_split)

        dfs = []
        for i in range(3):
            # Dropping the session # because we don't want to train on it.
            # Also leaves our label - BadActor - in the 0 column, as XGBoost requires for CSV
            dfi = y1[i].append(y0[i]).sample(frac=1)
            dfs.append( dfi )
    
        return dfs
    
    def train_splits( self, dfs, split=0.4, sepr=',', ext='csv'):
        '''
        dfs - list of named dfs as [name, df] pairs
        sepr - separator char for output files - typically , or \t
        ext - file extension for output files, typically csv or txv
        Split a list of named dfs into train, test, validate csv's organized into subdirectories by the df names
        returns - list of output filenames in [train, test, validate] triples, in same order as source files in dfs
        '''
        splits = []
        splits = [[name, self.train_split (df, split)] for [name, df] in dfs]
        
        return splits
    
    def get_csv_names(self, name, sets ):
        types = zip( sets, [ 'train', 'test', 'validate'])
        return [(os.path.join( csv_path, name + "_" + typ + ".csv"), data) for (data, typ) in types]
    
    def get_all_csv_names( self, dfs ):
        set_names = [get_csv_names( name, sets ) for (name, sets) in dfs]
        return set_names

    
    def write_csvs( self, name, sets):
#         [self.to_csv( data, os.path.join( csv_path, name + "_" + typ + ".csv")) for (data, typ) in zip( sets, [ 'train', 'test', 'validate'])]
        [self.to_csv( data, file_name ) for (data, file_name) in get_csv_names(name, sets)]
        
    def make_all_csvs( self, dfs, split=0.4, sepr=',', ext='csv'):
        '''
        dfs - list of named dfs as [name, df] pairs
        sepr - separator char for output files - typically , or \t
        ext - file extension for output files, typically csv or txv
        Split a list of named dfs into train, test, validate csv's organized into subdirectories by the df names
        returns - list of output filenames in [train, test, validate] triples, in same order as source files in dfs
        '''
        dfs = FrameSplitter.map_sets(self.reformat, dfs) # gives us a clean column set - [name, [y, xs]]...
        splits = self.train_splits( dfs, split, sepr, ext )  # gives us 3 samples - [name, [train, test, val]]
        [self.write_csvs( name, sets ) for (name, sets) in splits]
         
            
