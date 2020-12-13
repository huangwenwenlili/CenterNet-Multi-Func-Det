# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from PIL import Image, ImageDraw
import os
import numpy as np
from matplotlib.pyplot import imshow
# import cv2
import math
import json


def load_keypoint_from_pts(img_pts):
    fr = open(img_pts, 'r').readlines()
    valid_info = fr[3:-1]
    point_dict = {}
    for idx, pixel_coordinate in enumerate(valid_info):
        point_x, point_y = (float)(pixel_coordinate.strip().split(' ')[0]), (float)(
            pixel_coordinate.strip().split(' ')[1])
        point_dict[int(idx)] = (point_x, point_y)
    return point_dict


def load_img(img_path):
    img = Image.open(img_path)
    # img.show()
    return img


def show_keypoint(img, keypoint_dict):
    draw = ImageDraw.Draw(img)
    for kepoint in keypoint_dict.keys():
        draw.point(keypoint_dict[kepoint])
    img.show()


def crop_head(img, keypoint_dict, wanna_size):
    points_coordinate = np.zeros([len(keypoint_dict), 2])
    for key_point in keypoint_dict.keys():
        points_coordinate[key_point] = keypoint_dict[key_point]
    min_left = np.min(points_coordinate, axis=0)[0]
    max_right = np.max(points_coordinate, axis=0)[0]
    center_x = (max_right - min_left) / 2 + min_left
    print(center_x)
    crop_box_left, crop_box_right = center_x - wanna_size / 2, center_x + wanna_size / 2

    lefteye_center = np.mean(points_coordinate[36:42], axis=0)
    righteye_center = np.mean(points_coordinate[42:48], axis=0)
    print(lefteye_center)

    eye_center = (lefteye_center[1] + righteye_center[1]) / 2

    lip_center = np.mean(points_coordinate[48:68], axis=0)
    print(lip_center, eye_center)
    middle_length = lip_center[1] - eye_center

    crop_box_top, crop_box_bottom = eye_center - (wanna_size - middle_length) / 2, lip_center[1] + (
                wanna_size - middle_length) / 2

    crop_box_left, crop_box_top, crop_box_right, crop_box_bottom = [int(i) for i in
                                                                    [crop_box_left, crop_box_top, crop_box_right,
                                                                     crop_box_bottom]]
    crop_img = img.crop((crop_box_left, crop_box_top, crop_box_right, crop_box_bottom))
    crop_img.show()
    return crop_box_left, crop_box_top, crop_box_right, crop_box_bottom, crop_img


def crop_head_v2(img, keypoint_dict, wanna_size):
    points_coordinate = np.zeros([len(keypoint_dict), 2])
    for key_point in keypoint_dict.keys():
        points_coordinate[key_point] = keypoint_dict[key_point]
    max_left = np.min(points_coordinate, axis=0)[0]
    max_right = np.max(points_coordinate, axis=0)[0]
    max_top = np.min(points_coordinate, axis=0)[1]
    max_bottom = np.max(points_coordinate, axis=0)[1]

    fake_left = abs(points_coordinate[34][0] - max_left)
    fake_right = abs(points_coordinate[34][0] - max_right)
    fake_top = abs(points_coordinate[34][1] - max_top)
    fake_bottom = abs(points_coordinate[34][1] - max_bottom)
    max_radical = max(fake_bottom, fake_left, fake_right, fake_top)
    center_x, center_y = points_coordinate[34][0], points_coordinate[34][1]
    if max_radical < wanna_size / 2:
        max_radical = wanna_size / 2
        left, right = center_x - max_radical, center_x + max_radical
        top, bottom = center_y - max_radical, center_y + max_radical
    else:
        expand_factor = 10
        left, right = center_x - max_radical - expand_factor, center_x + max_radical + expand_factor
        top, bottom = center_y - max_radical - expand_factor, center_y + max_radical + expand_factor
    crop_box_left, crop_box_top, crop_box_right, crop_box_bottom = [int(i) for i in [left, top, right, bottom]]
    crop_img = img.crop((crop_box_left, crop_box_top, crop_box_right, crop_box_bottom))
    print(crop_img.size)
    # crop_img.show()

    return crop_box_left, crop_box_top, crop_box_right, crop_box_bottom, crop_img


def calculate_coordinate_crop(keypoint_dict, crop_box_top, crop_box_left):
    for key_point in keypoint_dict.keys():
        keypoint_dict[key_point] = (
        keypoint_dict[key_point][0] - crop_box_left, keypoint_dict[key_point][1] - crop_box_top)
    return keypoint_dict


def process_categories():
    category_dict = {'supercategory': 'person',
                     'keypoints': [i for i in range(1, 69)],
                     'skeleton': [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 9], [9, 10], [10, 11],
                                  [11, 12], [12, 13], [13, 14], [14, 15], [15, 16], [16, 17],
                                  [18, 19], [19, 20], [20, 21], [21, 22], [23, 24], [24, 25], [25, 26], [26, 27],
                                  [28, 29], [29, 30], [30, 31],
                                  [32, 33], [33, 34], [34, 35], [35, 36],
                                  [37, 38], [38, 39], [39, 40], [40, 41], [41, 42], [37, 42],
                                  [43, 44], [44, 45], [45, 46], [46, 47], [47, 48], [43, 48],
                                  [49, 50], [50, 51], [51, 52], [52, 53], [53, 54], [54, 55], [55, 56], [56, 57],
                                  [57, 58], [58, 59], [59, 60], [49, 60],
                                  [61, 62], [62, 63], [63, 64], [64, 65], [65, 66], [66, 67], [67, 68], [61, 68]],

                     'id': 1,
                     'name': 'person'}
    return category_dict


def _300w2cocokp(org_img_dir, tar_img_dir):
    anno_dict = {'license': [],
                 'categories': [],
                 'images': [],
                 'annotations': [],
                 'info': {}}

    img_list = []
    pts_list = []
    for adir in org_img_dir:
        files = os.listdir(adir)

        for file in files:
            file_path = os.path.join(adir, file)
            if file.split('.')[1] == 'pts':
                pts_list.append(file_path)
            else:
                img_list.append(file_path)
    img_list.sort()
    pts_list.sort()
    image_list = []
    annotations_list = []
    for idx in range(len(img_list)):
        img_pts = pts_list[idx]
        point_dict = load_keypoint_from_pts(img_pts)
        org_point_dict = load_keypoint_from_pts(img_pts)
        img_path = img_list[idx]
        org_img = load_img(img_path)
        org_width, org_height = org_img.size
        crop_box_left, crop_box_top, crop_box_right, crop_box_bottom, crop_img = crop_head_v2(org_img, point_dict, 140)
        new_keypoint_dict = calculate_coordinate_crop(point_dict, crop_box_top, crop_box_left)
        new_file_name = str(idx).zfill(6) + 'crop.jpg'
        new_file_path = os.path.join(tar_img_dir, new_file_name)
        org_file_name = str(idx).zfill(6) + '.jpg'
        org_file_path = os.path.join(tar_img_dir, org_file_name)
        crop_img.save(new_file_path, "JPEG")
        org_img.save(org_file_path, "JPEG")
        w, h = crop_img.size
        image_dict = {'org_height': org_height, 'org_width': org_width,'height': h, 'width': w, 'id': idx, 'flickr_url': '', 'license': 0, 'file_name': org_file_name}
        image_list.append(image_dict)

        anno = {'area': -1,
                'bbox': [],
                'org_bbox': [],
                'category_id': 1,
                'keypoints': [],
                'org_keypoints': [],
                'num_keypoints': 68,
                'image_id': idx,
                'id': idx,
                'segmentations': []}
        for key in new_keypoint_dict.keys():
            print('crop', key)
            anno['keypoints'].append(new_keypoint_dict[key][0])
            anno['keypoints'].append(new_keypoint_dict[key][1])
            anno['keypoints'].append(2)
        for key in org_point_dict.keys():
            print('org', key)
            anno['org_keypoints'].append(org_point_dict[key][0])
            anno['org_keypoints'].append(org_point_dict[key][1])
            anno['org_keypoints'].append(2)
        points_coordinate = np.zeros([len(new_keypoint_dict), 2])
        for key_point in new_keypoint_dict.keys():
            points_coordinate[key_point] = new_keypoint_dict[key_point]
        max_left = np.min(points_coordinate, axis=0)[0]
        max_right = np.max(points_coordinate, axis=0)[0]
        max_top = np.min(points_coordinate, axis=0)[1]
        max_bottom = np.max(points_coordinate, axis=0)[1]
        anno['bbox'] = [max_left, max_top, max_right, max_bottom]

        org_points_coordinate = np.zeros([len(org_point_dict), 2])
        for key_point in org_point_dict.keys():
            org_points_coordinate[key_point] = org_point_dict[key_point]
        max_left = np.min(org_points_coordinate, axis=0)[0]
        max_right = np.max(org_points_coordinate, axis=0)[0]
        max_top = np.min(org_points_coordinate, axis=0)[1]
        max_bottom = np.max(org_points_coordinate, axis=0)[1]
        anno['org_bbox'] = [max_left, max_top, max_right, max_bottom]

        annotations_list.append(anno)
    anno_dict['images'] = image_list
    anno_dict['annotations'] = annotations_list
    anno_dict['categories'].append(process_categories())
    assert len(img_list) == len(pts_list)
    # print(img_list[1000], pts_list[1000])
    return anno_dict


def checkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

if __name__ == '__main__':

    img_train_dir = '/data/mry/DataSet/landmark/300W/paper_public_use/images/train'
    img_test_dir = '/data/mry/DataSet/landmark/300W/paper_public_use/images/val'
    img_common_set = '/data/mry/DataSet/landmark/300W/paper_public_use/images/commonsubset'
    img_challenge_set = '/data/mry/DataSet/landmark/300W/paper_public_use/images/challengesubset'
    img_full_set = '/data/mry/DataSet/landmark/300W/paper_public_use/images/fullset'
    anno_dir = '/data/mry/DataSet/landmark/300W/paper_public_use/annotations'
    if not os.path.exists(img_train_dir):
        os.makedirs(img_train_dir)
    if not os.path.exists(img_test_dir):
        os.makedirs(img_test_dir)
    if not os.path.exists(anno_dir):
        os.makedirs(anno_dir)
    checkdir(img_common_set)
    checkdir(img_challenge_set)
    checkdir(img_full_set)

    train_img_dir = ['/data/mry/DataSet/landmark/300W/origial_data/lfpw/trainset',
                     '/data/mry/DataSet/landmark/300W/origial_data/helen/trainset', '/data/mry/DataSet/landmark/300W/origial_data/afw']
    test_img_dir = ['/data/mry/DataSet/landmark/300W/origial_data/helen/testset',
                    '/data/mry/DataSet/landmark/300W/origial_data/lfpw/testset', '/data/mry/DataSet/landmark/300W/origial_data/ibug']
    full_img_dir = ['/data/mry/DataSet/landmark/300W/origial_data/helen/testset',
                    '/data/mry/DataSet/landmark/300W/origial_data/lfpw/testset', '/data/mry/DataSet/landmark/300W/origial_data/ibug']

    common_img_dir = ['/data/mry/DataSet/landmark/300W/origial_data/helen/testset',
                    '/data/mry/DataSet/landmark/300W/origial_data/lfpw/testset']

    challenge_img_dir = ['/data/mry/DataSet/landmark/300W/origial_data/ibug']

    fw = open(os.path.join(anno_dir, 'val.json'), 'w')
    test_anno_dict = _300w2cocokp(test_img_dir, img_test_dir)
    json.dump(test_anno_dict, fw)

    fw = open(os.path.join(anno_dir, 'train.json'), 'w')
    train_anno_dict = _300w2cocokp(train_img_dir, img_train_dir)
    json.dump(train_anno_dict, fw)


    fw = open(os.path.join(anno_dir, 'common.json'), 'w')
    common_anno_dict = _300w2cocokp(common_img_dir, img_common_set)
    json.dump(common_anno_dict, fw)

    fw = open(os.path.join(anno_dir, 'challenge.json'), 'w')
    challenge_anno_dict = _300w2cocokp(challenge_img_dir, img_challenge_set)
    json.dump(challenge_anno_dict, fw)

    fw = open(os.path.join(anno_dir, 'full.json'), 'w')
    full_anno_dict = _300w2cocokp(full_img_dir, img_full_set)
    json.dump(full_anno_dict, fw)

    #fw = open(os.path.join(anno_dir, 'train.json'), 'w')
    #train_anno_dict = _300w2cocokp(train_img_dir, img_train_dir)
    #json.dump(train_anno_dict, fw)

    fw.close()




