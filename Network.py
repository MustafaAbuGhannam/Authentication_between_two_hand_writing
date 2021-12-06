from pickle import FALSE
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
import torchvision.transforms.functional as fn
from torch.utils.data import DataLoader,Dataset
import matplotlib.pyplot as plt
import os
import numpy as np
from data_set import LinesDataSet

class ContrastiveLoss(nn.Module):
    "Contrastive loss function"
    def __init__(self, margin=1):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin
            
    def forward(self, output1, output2, label):
        cos  = torch.nn.CosineSimilarity(dim=1, eps=1e-8)
        # euclidean_distance = F.pairwise_distance(output1, output2,keepdim=True)
        sim = cos(output1, output2) + 1
        loss_contrastive = torch.mean((1-label)* torch.pow(sim, 2) +
                                      (label) * torch.pow(torch.clamp(self.margin - sim, min=0.0), 2))

        return loss_contrastive



def train ( model , loss_function, optimizer,train_loader,loss_history, epoch):
    model.train()
    for indx , data in enumerate(train_loader):
        image1, image2, label = data
        image1 = image1.float().cuda()
        image2 = image2.float().cuda()
        image1 = image1[:,None,:,:]
        image2 = image2[:,None,:,:]
        label = label.cuda()
        optimizer.zero_grad()
        output1 = model(image1)
        output2 = model(image2)
        loss = loss_function(output1, output2, label)
        print("epoch Number: {} bathc_loss: {}".format(epoch, loss.item()))
        loss_history.append(loss.cpu().item())
        loss.backward() 
        optimizer.step()


def test ( model, test_loader, acc_history):
    model.eval()
    for indx , data in enumerate(test_loader):
        image1, image2, label = data
        image1 = image1.float().cuda()
        image2 = image2.float().cuda()
        image1 = image1[:,None,:,:]
        image2 = image2[:,None,:,:]
        label = label.cuda()
        output1 = model(image1)
        output2 = model(image2)
        # dist_ = F.pairwise_distance(output1, output2)
        # dist_ = torch.pow(dist_, 2)
        cos  = torch.nn.CosineSimilarity(dim=1, eps=1e-8)
        sim = cos(output1, output2)

        if label.item() == 1. and  sim.item() >= 1.: 
            acc_history.append(1)
        elif label.item() == 0.  and sim.item() < 1.:
            acc_history.append(1)
        else:
            acc_history.append(0)



if __name__ == "__main__":
    train_line_data_set = LinesDataSet(csv_file="Train_Labels.csv", root_dir="data_for_each_person", transform=transforms.Compose([transforms.ToTensor()]))
    test_line_data_set = LinesDataSet(csv_file="Test_Labels.csv", root_dir='data_for_each_person', transform=transforms.Compose([transforms.ToTensor()]))
    train_line_data_loader = DataLoader(train_line_data_set,shuffle=True,batch_size=50)
    test_line_data_loader = DataLoader(test_line_data_set, shuffle=True, batch_size=1)
    loss_function = ContrastiveLoss()
    model = torchvision.models.resnet18(pretrained = False)
    model.conv1=torch.nn.Conv2d(1, 64, 7, 2, 3, bias=False)
    num_features = model.fc.in_features
    print(num_features)
    model.fc = nn.Linear(num_features, 128)
    model = model.cuda()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    loss_history = []
    

    for i in range (10):

        print("epoch number: {}".format(i+1))
        train(model, loss_function, optimizer, train_line_data_loader, loss_history, i + 1)

        print('testing...')
        acc_history = []
        test(model, test_line_data_loader, acc_history)
        print("acc: {}".format(sum(acc_history) / len(acc_history)))


    torch.save(model.state_dict(), 'model.pt')

    # model.load_state_dict(torch.load('model.pt', map_location='cuda:0'))

    # test(model, test_line_data_loader, acc_history)

    # print(sum(acc_history) / len(acc_history))
    plt.plot(loss_history)
    plt.show()

  


