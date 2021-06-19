#!/usr/bin/env
### this script read bson dumped gzip file into pandas dataframe
### necessary packages: pymongo (note that import bson is from pymongo), pandas, gzip

import pandas as pd
import bson
import gzip


def bson_reader(file_path, filesize = "large"):
    """
    input file path should have file with extension: xxx.bson.gz, filesize should be either "large" or "small"
    output: a generator that can read file content row by row or the whole file content in data variable
    """
    with gzip.open(file_path, "rb") as f:
        raw_content = f.read()
        if filesize == "small":
            data = bson.decode_all(raw_content)
            return data
        data_generator = bson.decode_iter(raw_content)
    return data_generator

def bson_to_dataframe(data_generator, chunksize = 100, filesize = "large"):
    """
    input: a file generator, specify how many rows you want to read out using chunksize, if filesize is "small", chunksize is ignored
    output: a dataframe with each row is read from the file generator
    """
    df = pd.DataFrame()
    i = 0
    for row in data_generator:
        df = df.append(row, ignore_index = True)
        i += 1
        if filesize == "small":
            chunksize = None
        elif i == chunksize:
            break
    return df


if __name__ == "__main__":
    print("enter file path: ")
    file_path = input()
    data_gen = bson_reader(file_path, filesize = "small")
    df100 = bson_to_dataframe(data_gen, filesize = "small")
    print(df100.head())
