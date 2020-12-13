from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .sample.ddd import DddDataset
from .sample.exdet import EXDetDataset
from .sample.ctdet import CTDetDataset
from .sample.multi_pose import MultiPoseDataset
from .sample.landmark import CenterLandmarkDataset
from .sample.cloth_landmark import DeepFashionDataset
from .sample.gridneighbor import GridNeighborDetDataset

from .dataset.coco import COCO
from .dataset.pascal import PascalVOC
from .dataset.kitti import KITTI
from .dataset.coco_hp import COCOHP
from .dataset._300W import _300W
from .dataset.deepfashion2 import DEEPFASHION2

dataset_factory = {
  'coco': COCO,
  'pascal': PascalVOC,
  'kitti': KITTI,
  'coco_hp': COCOHP,
  '300W' : _300W,
  'deepfashion2' :DEEPFASHION2
}

_sample_factory = {
  'exdet': EXDetDataset,
  'ctdet': CTDetDataset,
  'ddd': DddDataset,
  'multi_pose': MultiPoseDataset,
  'landmark': CenterLandmarkDataset,
  'cloth' : DeepFashionDataset,
  'gridneighbordet': GridNeighborDetDataset
}


def get_dataset(dataset, task):
  class Dataset(dataset_factory[dataset], _sample_factory[task]):
    pass
  return Dataset
  
