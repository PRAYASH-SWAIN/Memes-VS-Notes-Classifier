# -*- coding: utf-8 -*-
"""MvsN-CNN(PyTorch).ipynb

Automatically generated by Colaboratory.

"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import matplotlib.pyplot as plt
import cv2 
import numpy as np
import os

device = None
if torch.cuda.is_available():
  print("GPU BEING USED")
  print("GPU name :" ,torch.cuda.get_device_name(0))
  device = torch.device('cuda')
else:
  print('GPU UNAVAILABLE')

from zipfile import ZipFile 

with ZipFile("Stage_2.zip",'r') as zipfile:
    zipfile.extractall()
    print('Files loaded')

memes_dir = "Stage_2/Memes"
notes_dir = "Stage_2/Notes"

def var_store(path,label):
  images = []
  labels = []
  for file in os.listdir(path):
    img = cv2.imread(path + "/" + file)
    images.append(img)
    labels.append(label)
  return images,labels

memes, memesout = var_store(memes_dir, 1)
notes, notesout = var_store(notes_dir, 0)
memes,memesout = np.array(memes),np.array(memesout)
notes,notesout = np.array(notes),np.array(notesout)
memes = memes.reshape(800,3,256,256)
notes = notes.reshape(800,3,256,256)
#memes[56:]
#notes[56

memewhole = list(zip(memes, memesout))
notewhole = list(zip(notes, notesout))

temp = []
temp = memewhole[0:750] + notewhole[0:750]
np.random.shuffle(temp)
train_X, train_Y = list(zip(*temp))
temp.clear()
temp = memewhole[750:780] + notewhole[750:780]
np.random.shuffle(temp)
dev_X, dev_Y = list(zip(*temp))
temp.clear()
temp = memewhole[780:] + notewhole[780:]
np.random.shuffle(temp)
test_X, test_Y = list(zip(*temp))

train_X = torch.Tensor(train_X)
test_X = torch.Tensor(test_X)
dev_X = torch.Tensor(dev_X)

train_Y = torch.Tensor(train_Y)
test_Y = torch.Tensor(test_Y)
dev_Y = torch.Tensor(dev_Y)

train_X/=255.0
test_X/=255.0
dev_X /=255.0
#train_X.size()

class Net(nn.Module):
  def __init__(self):
    super(Net, self).__init__()                                         
    #Making sure nn.Model runs
    self.conv1 = nn.Conv2d(in_channels=3 , out_channels=6 , kernel_size=3)   
    self.conv2 = nn.Conv2d(in_channels=6 , out_channels=12 , kernel_size=2)  
    
    self.fc1 = nn.Linear(in_features=12*63*63 , out_features=100 , bias=True) 
    self.fc2 = nn.Linear(in_features=100 , out_features=20 , bias=True)       
    self.fc3 = nn.Linear(in_features=20 , out_features=2 , bias=True)        
  
  def forward(self, X):
      
    X = self.conv1(X)                               # LAYER 1
    X = F.relu(X)
    X = F.max_pool2d(X ,kernel_size=2 ,stride=2)
    
    X = self.conv2(X)                               # LAYER 2
    X = F.relu(X)
    X = F.max_pool2d(X ,kernel_size=2 ,stride=2)
    
    X = X.view(-1,12*63*63)                      # LAYER 3(DENSE), flattening
    X = self.fc1(X)
    X = F.relu(X)
    
    X = self.fc2(X)                                 # LAYER 4(DENSE)
    X = F.relu(X)
    
    X = self.fc3(X)                                 # LAYER 5(DENSE)
    return X

network = Net()
network.to(device)
optimizer = optim.Adam(network.parameters(), lr=0.01)

def accuracyfun(outputs, batch_y):
  #outputs.size()
  #batch_y.size()
  temp1 = outputs.argmax(dim=1)
  temp2 = temp1.eq(batch_y).sum()
  return temp2

Batchsize = 25
losstracker = []
correcttracker = []
for epoch in range(6):
  loss_epoch = 0
  correct_epoch = 0
  temp = 0
  for i in range(0, len(train_X), Batchsize): 
    batch_X = train_X[i: i + Batchsize]
    batch_X = batch_X.view(-1, 3, 256, 256)
    batch_X = batch_X.cuda()

    batch_y = train_Y[i: i + Batchsize]
    batch_y = batch_y.cuda()
    outputs = network(batch_X)
    loss = F.cross_entropy(outputs, batch_y.long())
    
    network.zero_grad()
    optimizer.zero_grad()
    
    loss.backward()
    optimizer.step()    
    loss_epoch += loss
    correct_epoch = accuracyfun(outputs,batch_y.long()) 
    temp += 1 
  loss_epoch/=temp
  losstracker.append(loss_epoch)
  correcttracker.append(correct_epoch)
  print("Epoch number", (epoch+1)) 
  print("Accuracy:", (int(correct_epoch)*100)/len(train_X))
  print("Loss:", loss_epoch)

plt.plot(range(6), losstracker)
plt.xlabel('no. of epochs')
plt.ylabel('total loss')
plt.show()

plt.plot(range(6),correcttracker)
plt.xlabel('no. of epochs')
plt.ylabel('correct outputs')
plt.show()
