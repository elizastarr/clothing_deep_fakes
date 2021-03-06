'''
    Code coming from cp-vton-plus: https://github.com/minar09/cp-vton-plus
    License at the root directory.

    Changes:
        - CPDataset: added transformation_greyscale() to adapt to newer torchvision versions
        - CPDataLoader: added display() function to visualize a few GMM inputs
        - main: changed default arguments
'''

# coding=utf-8
import torch
import torch.utils.data as data
import torchvision.transforms as transforms

from PIL import Image
from PIL import ImageDraw

import os.path as osp
import numpy as np
import json


class CPDataset(data.Dataset):
    '''
        Dataset for CP-VTON+.
    '''

    def __init__(self, 
        dataroot: str = None, 
        datamode: str = None, 
        stage = "GMM",
        data_list = "train_pairs.txt",
        fine_height = 256,
        fine_width = 192,
        radius = 3):

        super(CPDataset, self).__init__()
        # base setting
        self.root = dataroot
        self.datamode = datamode  # train or test or self-defined
        self.stage = stage  # GMM or TOM
        self.data_list = data_list
        self.fine_height = fine_height
        self.fine_width = fine_width
        self.radius = radius
        self.data_path = osp.join(dataroot, datamode)
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,0.5,0.5), (0.5,0.5,0.5))])
        
        # uncomment when using a newer version of torchvision (google colab)
        ''' 
        self.transform_greyscale = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(0.5, 0.5)])
        '''

        # load data list
        im_names = []
        c_names = []
        with open(osp.join(self.root, self.data_list), 'r') as f:
            for line in f.readlines():
                im_name, c_name = line.strip().split()
                im_names.append(im_name)
                c_names.append(c_name)

        self.im_names = im_names
        self.c_names = c_names

    def name(self):
        return "CPDataset"

    def __getitem__(self, index):
        c_name = self.c_names[index]
        im_name = self.im_names[index]

        if self.stage == 'GMM':
            c = Image.open(osp.join(self.data_path, 'cloth', c_name))
            cm = Image.open(osp.join(self.data_path, 'cloth-mask', c_name)).convert('L')  # to greyscale
        else:
            c = Image.open(osp.join(self.data_path, 'warp-cloth', im_name))    # c_name, if that is used when saved
            cm = Image.open(osp.join(self.data_path, 'warp-mask', im_name)).convert('L')    # c_name, if that is used when saved

        c = self.transform(c)  # [-1,1] Normalize all target clothing images
        cm_array = np.array(cm)
        cm_array = (cm_array >= 128).astype(np.float32)  # light colors to 1, else 0
        cm = torch.from_numpy(cm_array)  # [0,1]
        cm.unsqueeze_(0)

        # person image
        im = Image.open(osp.join(self.data_path, 'image', im_name))
        im = self.transform(im)  # [-1,1]  # normalize reference image

        """
        LIP labels
        
        [(0, 0, 0),    # 0=Background
         (128, 0, 0),  # 1=Hat
         (255, 0, 0),  # 2=Hair
         (0, 85, 0),   # 3=Glove
         (170, 0, 51),  # 4=SunGlasses
         (255, 85, 0),  # 5=UpperClothes
         (0, 0, 85),     # 6=Dress
         (0, 119, 221),  # 7=Coat
         (85, 85, 0),    # 8=Socks
         (0, 85, 85),    # 9=Pants
         (85, 51, 0),    # 10=Jumpsuits
         (52, 86, 128),  # 11=Scarf
         (0, 128, 0),    # 12=Skirt
         (0, 0, 255),    # 13=Face
         (51, 170, 221),  # 14=LeftArm
         (0, 255, 255),   # 15=RightArm
         (85, 255, 170),  # 16=LeftLeg
         (170, 255, 85),  # 17=RightLeg
         (255, 255, 0),   # 18=LeftShoe
         (255, 170, 0)    # 19=RightShoe
         (170, 170, 50)   # 20=Skin/Neck/Chest (Newly added after running dataset_neck_skin_correction.py)
         ]
         """

        # load parsing image 
        parse_name = im_name.replace('.jpg', '.png')
        im_parse = Image.open(
            # osp.join(self.data_path, 'image-parse', parse_name)).convert('L')
            osp.join(self.data_path, 'image-parse-new', parse_name)).convert('L')   # updated new segmentation
        parse_array = np.array(im_parse)
        im_mask = Image.open(
            osp.join(self.data_path, 'image-mask', parse_name)).convert('L')
        mask_array = np.array(im_mask)

        # parse_shape = (parse_array > 0).astype(np.float32)  # CP-VTON body shape
        # Get shape from body mask (CP-VTON+)
        parse_shape = (mask_array > 0).astype(np.float32)  # If x>0 then 1

        if self.stage == 'GMM':  # Collect only hat, sunglasses, and Face
            parse_head = (parse_array == 1).astype(np.float32) + \
                (parse_array == 4).astype(np.float32) + \
                (parse_array == 13).astype(
                    np.float32)  # CP-VTON+ GMM input (reserved regions)
        else:
            parse_head = (parse_array == 1).astype(np.float32) + \
                (parse_array == 2).astype(np.float32) + \
                (parse_array == 4).astype(np.float32) + \
                (parse_array == 9).astype(np.float32) + \
                (parse_array == 12).astype(np.float32) + \
                (parse_array == 13).astype(np.float32) + \
                (parse_array == 16).astype(np.float32) + \
                (parse_array == 17).astype(
                np.float32)  # CP-VTON+ TOM input (reserved regions)

        parse_cloth = (parse_array == 5).astype(np.float32) + \
            (parse_array == 6).astype(np.float32) + \
            (parse_array == 7).astype(np.float32)    # upper-clothes labels

        # shape downsample
        parse_shape_ori = Image.fromarray((parse_shape*255).astype(np.uint8))
        parse_shape = parse_shape_ori.resize(
            (self.fine_width//16, self.fine_height//16), Image.BILINEAR)
        parse_shape = parse_shape.resize(
            (self.fine_width, self.fine_height), Image.BILINEAR)
        parse_shape_ori = parse_shape_ori.resize(
            (self.fine_width, self.fine_height), Image.BILINEAR)
        
        try:
            shape_ori = self.transform_greyscale(parse_shape_ori)  # [-1,1]
            shape = self.transform_greyscale(parse_shape)  # [-1,1]
        except AttributeError:
            shape_ori = self.transform(parse_shape_ori)  # [-1,1]
            shape = self.transform(parse_shape)  # [-1,1]

        phead = torch.from_numpy(parse_head)  # [0,1]
        # phand = torch.from_numpy(parse_hand)  # [0,1]
        pcm = torch.from_numpy(parse_cloth)  # [0,1]

        # upper cloth
        im_c = im * pcm + (1 - pcm)  # [-1,1], fill 1 for other parts
        im_h = im * phead - (1 - phead)  # [-1,1], fill -1 for other parts

        # load pose points from json
        pose_name = im_name.replace('.jpg', '_keypoints.json')
        with open(osp.join(self.data_path, 'pose', pose_name), 'r') as f:
            pose_label = json.load(f)
            pose_data = pose_label['people'][0]['pose_keypoints']
            pose_data = np.array(pose_data)
            pose_data = pose_data.reshape((-1, 3))

        point_num = pose_data.shape[0]
        pose_map = torch.zeros(point_num, self.fine_height, self.fine_width)
        r = self.radius

        # Make image from pose points
        im_pose = Image.new('L', (self.fine_width, self.fine_height))
        pose_draw = ImageDraw.Draw(im_pose)
        for i in range(point_num):  
            one_map = Image.new('L', (self.fine_width, self.fine_height))
            draw = ImageDraw.Draw(one_map)
            pointx = pose_data[i, 0]
            pointy = pose_data[i, 1]
            if pointx > 1 and pointy > 1:
                draw.rectangle((pointx-r, pointy-r, pointx +
                                r, pointy+r), 'white', 'white')
                pose_draw.rectangle(
                    (pointx-r, pointy-r, pointx+r, pointy+r), 'white', 'white')
            try:
                one_map = self.transform_greyscale(one_map)
            except AttributeError:
                one_map = self.transform(one_map)

            pose_map[i] = one_map[0]

        # just for visualization
        try:
            im_pose = self.transform_greyscale(im_pose)
        except AttributeError:
            im_pose = self.transform(im_pose)

        # cloth-agnostic representation 
        agnostic = torch.cat([shape, im_h, pose_map], 0)

        if self.stage == 'GMM':
            im_g = Image.open(osp.join(self.root, 'grid.png'))
            im_g = self.transform(im_g)
        else:
            im_g = ''

        pcm.unsqueeze_(0)  # CP-VTON+

        result = {
            'c_name':   c_name,             # for visualization
            'im_name':  im_name,            # for visualization or ground truth
            'cloth':    c,                  # for input
            'cloth_mask':     cm,           # for input
            'image':    im,                 # for visualization
            'agnostic': agnostic,           # for input
            'parse_cloth': im_c,            # for ground truth
            'shape': shape,                 # for visualization
            'head': im_h,                   # for visualization
            'pose_image': im_pose,          # for visualization
            'grid_image': im_g,             # for visualization
            'parse_cloth_mask': pcm,        # for CP-VTON+, TOM input
            'shape_ori': shape_ori,         # original body shape without resize
        }

        return result

    def __len__(self):
        return len(self.im_names)


class CPDataLoader(object):
    def __init__(self, 
        shuffle = True, 
        batch_size = 4, 
        workers = 1, 
        dataset = None):
        super(CPDataLoader, self).__init__()

        self.batch_size = batch_size

        if shuffle:
            train_sampler = torch.utils.data.sampler.RandomSampler(dataset)
        else:
            train_sampler = None

        self.data_loader = torch.utils.data.DataLoader(
            dataset, batch_size=self.batch_size, shuffle=(
                train_sampler is None),
            num_workers=workers, pin_memory=True, sampler=train_sampler)
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
            Show two images and their clothing-agnostic person representations.
        '''
        import matplotlib.pyplot as plt

        batch = self.next_batch()

        for i in range( min( len(batch), 2 ) ):
            print(batch['image'][i].permute(1, 2, 0).size())
            plt.imshow(batch['image'][i].permute(1, 2, 0))
            plt.show()
            
            # pose
            print(batch['pose_image'][i].permute(1, 2, 0).size())
            a = batch['pose_image'][i].permute(1, 2, 0)
            plt.imshow(a, cmap='gray')
            plt.show()
            # body shape
            plt.imshow(batch['shape'][i].permute(1, 2, 0))
            plt.show()
            # face and hair regions
            plt.imshow(batch['head'][i].permute(1, 2, 0))
            plt.show()


if __name__ == "__main__":
    print("Check the dataset for geometric matching module.")

    import argparse
    parser = argparse.ArgumentParser()

    # dataroot when running locally
    parser.add_argument("--dataroot", default="/Users/elizastarr/git/clothing_deep_fakes/data/external")
    # dataroot when running in colab
    #parser.add_argument("--dataroot", default="/content/drive/MyDrive/ColabNotebooks/Resleeve/clothing_deep_fakes/data/external")
    
    parser.add_argument("--datamode", default="train")
    parser.add_argument("--stage", default="GMM")
    parser.add_argument("--data_list", default="train_pairs.txt")
    parser.add_argument("--fine_height", type=int, default=256)
    parser.add_argument("--fine_width", type=int, default=192)
    
    parser.add_argument("--radius", type=int, default=3)
    parser.add_argument("--shuffle", action='store_true',
                        help='shuffle input data')
    parser.add_argument('-b', '--batch-size', type=int, default=4)
    parser.add_argument('-j', '--workers', type=int, default=1)

    opt = parser.parse_args()
    if opt.datamode=='train':
        opt.data_list = 'train_pairs.txt'
    else:
        opt.data_list = 'test_pairs.txt'

    dataset = CPDataset(opt.dataroot, 
        opt.datamode, 
        opt.stage,
        opt.data_list,
        opt.fine_height,
        opt.fine_width,
        opt.radius)
    data_loader = CPDataLoader(opt.shuffle, 
        opt.batch_size, 
        opt.workers, 
        dataset)

    print('Size of the dataset: %05d, dataloader: %04d'
          % (len(dataset), len(data_loader.data_loader)))
    first_item = dataset.__getitem__(0)

    first_batch = data_loader.next_batch()  # Contains 13 keys, each with a list of 4 values
    data_loader.display()  # Preview 2 images from the batch
