# Great circle distance computes the shortest path distance of two projections on the surface of earth.
import torchvision.transforms as T
import torchvision
from torch.utils import data
import torch
from torchvision import datasets, transforms
from PIL import Image
import os
import numpy as np
import shutil
import glob
import geojson
from math import radians, degrees, sin, cos, asin, acos, sqrt

def haversine(lat1, lat2, long1, long2):
    r = 6371 #km
    long1, lat1, long2, lat2 = map(radians, [long1, lat1, long2, lat2])
    dist_longtitude = long2-long1
    dist_latitude = lat2 - lat1

    a = sin(dist_latitude/2)**2 + cos(lat1)*cos(lat2)*sin(dist_longtitude/2)**2
    return 2*r*asin(sqrt(a))

# print(haversine(37.72,41.8781, -89.2167,-86.6297))


def train_validation_split(root_dir="mapmatched_rainfall", output_dir="output", train_ratio = 0.8, val_ratio=0.1):

    try:
        os.makedirs(output_dir + '/train')
        os.makedirs(output_dir + '/validation')
        os.makedirs(output_dir + '/test')
    except OSError:
        pass

    geofile = os.listdir(root_dir)
    np.random.shuffle(geofile)

    train_folder, validation_folder, test_folder = np.split(
        np.array(geofile), [int(len(geofile)*train_ratio), int(len(geofile)*(train_ratio+val_ratio))])

    train_files = [root_dir + '/' + name for name in train_folder.tolist()]
    validation_files = [root_dir + '/' +
                        name for name in validation_folder.tolist()]
    test_files = [root_dir + '/' + name for name in test_folder.tolist()]

    print("Size of train:", len(train_files))
    print("Size of validation:", len(validation_files))
    print("Size of test:", len(test_files)) 

    for geojson in train_files:
        shutil.copy(geojson, output_dir + "/train")

    for geojson in validation_files:
        shutil.copy(geojson, output_dir + "/validation")

    for geojson in test_files:
        shutil.copy(geojson, output_dir + "/test")


def computeNormalisation(dir='geopoints'):

    global mean, var
    dataset = datasets.ImageFolder(dir, transform=transforms.Compose([transforms.Resize(512),
                                                                    transforms.CenterCrop(512),
                                                                    transforms.ToTensor()])
                                                                    )

    loader = data.DataLoader(dataset,
                        batch_size=10,
                        num_workers=0,
                        shuffle=False)

    mean = 0.0
    for images, _ in loader:
        batch_samples = images.size(0)
        images = images.view(batch_samples, images.size(1), -1)
        mean += images.mean(2).sum(0)
    mean = mean / len(loader.dataset)

    var = 0.0
    for images, _ in loader:
        batch_samples = images.size(0)
        images = images.view(batch_samples, images.size(1), -1)
        var += ((images - mean.unsqueeze(1))**2).sum([0, 2])
    std = torch.sqrt(var / (len(loader.dataset)*512*512))
