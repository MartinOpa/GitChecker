import os
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.distributions as tdist
import torch.nn.functional as F
import torch.nn as nn
import torchmetrics as tm
import pandas as pd
import sys
import random
import time
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

###################################################################
# VVV added parameters to sample test provided for this thesis  VVV
###################################################################
import argparse
import json

parser = argparse.ArgumentParser()

parser.add_argument('--num_time_steps', type=int, default=1)                                    # Kolik casu dozadu sledujeme k provedeni predikce.
parser.add_argument('--num_features_intern0', type=int, default=512)                            # 640#640#512 # Pocty neuronu v dalsich vrstvach
parser.add_argument('--num_features_intern1', type=int, default=256)                            # 256#256#256     # 160#256#160 
parser.add_argument('--num_vars_in_LSTM', type=int, default=128)                                # Kolik vystupnich promennych maji LSTM bloky.
parser.add_argument('--latent_dim', type=int, default=100)
parser.add_argument('--num_epochs', type=int, default=2)                                      # 256 # Kolik epoch se ma pouzit pro uceni.
parser.add_argument('--my_batch_size', type=int, default=10)
parser.add_argument('--anomaly_outer_margin', type=int, default=16)                             # Na kazdou casu od anomalie se tohle povazuje za nejistou oblast.
parser.add_argument('--anomaly_inner_margin', type=int, default=16)
parser.add_argument('--my_learning_rate', type=float, default=3e-4)                             # 0.0005 3e-4
parser.add_argument('--my_amsgrad', type=bool, default=False)
parser.add_argument('--load_trained_model', type=bool, default=False)                           # Loads up loss, weights and epochs
parser.add_argument('--continue_training', type=bool, default=True)                             # Continues to train loaded trained model false if we want to sample from a loaded model
parser.add_argument('--train_diff_dataset', type=bool, default=False)                           # If we want to train on different dataset with loaded model then it is good to save the newest best model
parser.add_argument('--dataScale', type=float, default=1.0)                         
parser.add_argument('--test_file_name', type=str, default="data/michal_anomal_91_dist.txt")     # Jmeno souboru na testovani
parser.add_argument('--anot_test_file_name', type=str, default="data/michal_annot.txt")         # Jmeno souboru s anotaci testu.
parser.add_argument('--train_file_name', type=str, default="data/michal_normal_91_dist.txt")    # Jmeno souboru na trenovani
parser.add_argument('--load_model_file_name', type=str, default="")                             # Jmeno souboru s ulozenym souborem

#pro ulozeni vysledku testu
parser.add_argument('--test_results', type=str, default='test_results.json')

args = parser.parse_args()

num_time_steps = args.num_time_steps                             
num_features_intern0 = args.num_features_intern0       
num_features_intern1 = args.num_features_intern1  
num_vars_in_LSTM = args.num_vars_in_LSTM                       
latent_dim = args.latent_dim                              
num_epochs = args.num_epochs  
my_batch_size = args.my_batch_size                           
anomaly_outer_margin = args.anomaly_outer_margin                     
anomaly_inner_margin = args.anomaly_inner_margin                     
my_learning_rate = args.my_learning_rate
my_amsgrad = args.my_amsgrad    
load_trained_model = args.load_trained_model                    
continue_training = args.continue_training                      
train_diff_dataset = args.train_diff_dataset                    
dataScale = args.dataScale
test_file_name = args.test_file_name
anot_test_file_name = args.anot_test_file_name      
train_file_name = args.train_file_name  
load_model_file_name = args.load_model_file_name   

test_results = args.test_results

print('args:')
# Zobrazeni parametru v logu
for name, value in vars(args).items():
    print(f"{name}: {value}")
print()

###################################################################
# ^^^ added parameters to sample test provided for this thesis  ^^^
###################################################################

# test goes here

###################################################################
# VVV added parameters to sample test provided for this thesis  VVV
###################################################################

acc = ((true_positives + true_negatives) / len(eval_errs)) * 100
print("True positives", true_positives)
print("True negatives", true_negatives)
print("False negatives", false_negatives)
print("False positives", false_positives)
print(f"Accuracy {acc:.2f}")

test_results_json = {
    "Accuracy": acc,
    "True positives": true_positives,
    "True negatives": true_negatives,
    "False positives": false_positives,
    "False negatives": false_negatives,
    "Mean training err": float(mean_training_err),
    "Mean reconst error": float(mean_reconst_err),
    "Abnormal eval": abnormal_eval,
    "Normal eval": normal_eval,
    "SNR": abnormal_eval/normal_eval,
    "Best loss": best_loss
}

with open(test_results, 'w') as file:
    file.write(json.dumps(test_results_json))

###################################################################
# ^^^ added parameters to sample test provided for this thesis  ^^^
###################################################################
