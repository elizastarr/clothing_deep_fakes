'''
    Code adapted from cp-vton-plus cp_dataset: https://github.com/minar09/cp-vton-plus
    License at the root directory.
    s
    The EvaluateDataset and Evaluate DataLoader classes return the original and output images.
    The main function computes the Structural Similarity Index Measure between each image pair.
        - https://en.wikipedia.org/wiki/Structural_similarity
'''

import torch
import torch.utils.data as data
import torchvision.transforms as transforms
from torchmetrics.functional import ssim, iou

from PIL import Image

import os.path as osp


class EvaluateDataset(data.Dataset):

    def __init__(self, 
        dataroot: str = "/Users/elizastarr/git/clothing_deep_fakes/data/results/TOM/test", 
        data_list: str = "test_pairs.txt",
        fine_height = 256,
        fine_width = 192,
        radius = 3):

        super(EvaluateDataset, self).__init__()
        # base setting
        self.root = dataroot
        self.data_list = data_list
        self.fine_height = fine_height
        self.fine_width = fine_width
        self.radius = radius
        self.data_path = osp.join(dataroot)
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            ])

        # load data list
        im_names = []
        with open(osp.join(self.root, self.data_list), 'r') as f:
            for line in f.readlines():
                im_name, _ = line.strip().split()
                im_names.append(im_name)

        self.im_names = im_names

    def name(self):
        return "EvaluateDataset"

    def __getitem__(self, index):
        im_name = self.im_names[index]

        # person image
        im = Image.open(osp.join(self.data_path, 'image', im_name))
        try_on = Image.open(osp.join(self.data_path, 'try-on', im_name))
        im = self.transform(im)  # [-1,1]  # normalize reference image
        try_on = self.transform(try_on)  # [-1,1]  # normalize reference image

        result = {
            'image':    im,         # for visualization
            'try-on':   try_on
        }

        return result

    def __len__(self):
        return len(self.im_names)


class EvaluateDataLoader(object):
    def __init__(self, 
        shuffle = True, 
        batch_size = 4, 
        workers = 1, 
        dataset = EvaluateDataset()):
        super(EvaluateDataLoader, self).__init__()

        self.batch_size = batch_size

        if shuffle:
            train_sampler = torch.utils.data.sampler.RandomSampler(dataset)
        else:
            train_sampler = None

        self.data_loader = torch.utils.data.DataLoader(
            dataset, batch_size=self.batch_size, shuffle=(
                train_sampler is None), pin_memory=True,)
        self.dataset = dataset
        self.data_iter = self.data_loader.__iter__()

    def next_batch(self):
        try:
            batch = self.data_iter.__next__()
        except StopIteration:
            self.data_iter = self.data_loader.__iter__()
            batch = self.data_iter.__next__()

        return batch

    def display(self):
        ''' 
            Show two images and their translations.
        '''
        import matplotlib.pyplot as plt

        batch = self.next_batch()

        for i in range( 2 ):
            print(batch['image'][i].permute(1, 2, 0).size())
            plt.imshow(batch['image'][i].permute(1, 2, 0))
            plt.show()
            
            print(batch['try-on'][i].permute(1, 2, 0).size())
            plt.imshow(batch['try-on'][i].permute(1, 2, 0))
            plt.show()


if __name__ == "__main__":


    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataroot", default="/Users/elizastarr/git/clothing_deep_fakes/data/results/TOM/test")
    
    parser.add_argument("--data_list", default="test_pairs.txt")
    parser.add_argument("--fine_height", type=int, default=256)
    parser.add_argument("--fine_width", type=int, default=192)

    parser.add_argument("--shuffle", action='store_true',
                        help='shuffle input data')
    
    parser.add_argument("--radius", type=int, default=3)
    parser.add_argument('-b', '--batch-size', type=int, default=4)
    parser.add_argument('-j', '--workers', type=int, default=1)

    opt = parser.parse_args()
    dataset = EvaluateDataset(opt.dataroot, 
        opt.data_list,
        opt.fine_height,
        opt.fine_width,
        opt.radius)
    data_loader = EvaluateDataLoader(batch_size= 100, #len(dataset), 
        shuffle = opt.shuffle, 
        dataset=dataset)

    batch = data_loader.next_batch()  # load the entire dataset


    print("SSIM:", ssim(batch['image'], batch['try-on']))  # 0.7298

    data_loader.display()


    # This implementation of IoU is not for this application
    #print("IoU:", iou(batch['image'], batch['try-on'].int()))  # 0.1235

