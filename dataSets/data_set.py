import os
import torch
import pandas as pd
from skimage import io, transform
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset


class LinesDataSet(Dataset):

    def __init__(self, csv_file, root_dir, transform=None):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.labels = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):

            idx = idx.tolist()

        img0_path = os.path.join(self.root_dir, self.labels.iloc[idx, 0])
        img1_path = os.path.join(self.root_dir, self.labels.iloc[idx, 1])
        img0 = io.imread(img0_path)
        img1 = io.imread(img1_path)

        label = self.labels.iloc[idx, 2]

        if self.transform:
            self.transform(img0)
            self.transform(img1)

        return img0, img1, torch.from_numpy(np.array([int(label)],dtype=np.float32))

class LinesDataSetTriplet(Dataset):

    def __init__(self, csv_file, root_dir, transform=None):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.labels = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):

            idx = idx.tolist()

        img0_path = os.path.join(self.root_dir, self.labels.iloc[idx, 0])
        img1_path = os.path.join(self.root_dir, self.labels.iloc[idx, 1])
        img2_path = os.path.join(self.root_dir, self.labels.iloc[idx, 2])
        img0 = io.imread(img0_path)
        img1 = io.imread(img1_path)
        img2 = io.imread(img2_path)

        if self.transform:
            self.transform(img0)
            self.transform(img1)
            self.transform(img2)

        return img0, img1, img2

class LinesDataSetTripletWithLabel(Dataset):

    def __init__(self, csv_file, root_dir, transform=None):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.labels = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):

            idx = idx.tolist()

        img0_path = os.path.join(self.root_dir, self.labels.iloc[idx, 0])
        img1_path = os.path.join(self.root_dir, self.labels.iloc[idx, 1])
        img2_path = os.path.join(self.root_dir, self.labels.iloc[idx, 2])
        label = self.labels.iloc[idx, 3]
        img0 = io.imread(img0_path)
        img1 = io.imread(img1_path)
        img2 = io.imread(img2_path)

        if self.transform:
            self.transform(img0)
            self.transform(img1)
            self.transform(img2)

        return img0, img1, img2, torch.from_numpy(np.array([int(label)],dtype=np.float32))
