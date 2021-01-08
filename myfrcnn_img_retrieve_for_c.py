# import cv2
import keras
import numpy as np
import colorsys
import pickle
import os
import nets.myfrcnn_retrieve as myfrcnn_retrieve
from nets.frcnn_training import get_new_img_size
from keras import backend as K
from keras.layers import Input
from keras.applications.imagenet_utils import preprocess_input
from PIL import Image, ImageFont, ImageDraw
from utils.utils import BBoxUtility
from utils.anchors import get_anchors
from utils.config import Config
import copy
import math


# --------------------------------------------#
#   使用自己训练好的模型预测需要修改2个参数
#   model_path和classes_path都需要修改！
# --------------------------------------------#
class myFRCNN_img_retrieve(object):
    _defaults = {
        "model_path": 'F:/faster-rcnn-keras-master/logs/epoch216-loss0.685-rpn0.265-roi0.420.h5',
        "classes_path": 'F:/faster-rcnn-keras-master/model_data/myclasses.txt',
        "confidence": 0.01,
    }

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    # ---------------------------------------------------#
    #   初始化faster RCNN
    # ---------------------------------------------------#
    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        self.class_names = self._get_class()
        self.sess = K.get_session()
        self.config = Config()
        self.generate()
        self.bbox_util = BBoxUtility()

    # ---------------------------------------------------#
    #   获得所有的分类
    # ---------------------------------------------------#
    def _get_class(self):
        classes_path = os.path.expanduser(self.classes_path)
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names

    # ---------------------------------------------------#
    #   获得所有的分类
    # ---------------------------------------------------#
    def generate(self):
        model_path = os.path.expanduser(self.model_path)
        assert model_path.endswith('.h5'), 'Keras model or weights must be a .h5 file.'

        # 计算总的种类
        self.num_classes = len(self.class_names) + 1

        # 载入模型，如果原来的模型里已经包括了模型结构则直接载入。
        # 否则先构建模型再载入
        self.model_rpn, self.model_classifier = myfrcnn_retrieve.get_predict_model(self.config, self.num_classes)
        self.model_rpn.load_weights(self.model_path, by_name=True)
        self.model_classifier.load_weights(self.model_path, by_name=True, skip_mismatch=True)

        self.mode_ROIout = myfrcnn_retrieve.get_ROIout_model(self.config, self.num_classes)
        self.mode_ROIout.load_weights(self.model_path, by_name=True, skip_mismatch=True)

        self.featuremap_model = myfrcnn_retrieve.get_featuremap_model(self.config, self.num_classes)
        self.featuremap_model.load_weights(self.model_path, by_name=True, skip_mismatch=True)

        print('{} model, anchors, and classes loaded.'.format(model_path))

        # 画框设置不同的颜色
        hsv_tuples = [(x / len(self.class_names), 1., 1.)
                      for x in range(len(self.class_names))]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        self.colors = list(
            map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
                self.colors))

    def get_img_output_length(self, width, height):
        def get_output_length(input_length):
            # input_length += 6
            filter_sizes = [7, 3, 1, 1]
            padding = [3, 1, 0, 0]
            stride = 2
            for i in range(4):
                # input_length = (input_length - filter_size + stride) // stride
                input_length = (input_length + 2 * padding[i] - filter_sizes[i]) // stride + 1
            return input_length

        return get_output_length(width), get_output_length(height)

        # ---------------------------------------------------#

    #   提取特征
    # ---------------------------------------------------#
    def extract_feature(self, image):
        #        image_shape = np.array(np.shape(image)[0:2])
        #        old_width = image_shape[1]#原始图片的宽高
        #        old_height = image_shape[0]
        #        old_image = copy.deepcopy(image)
        #        width,height = get_new_img_size(old_width,old_height, img_min_side=416)
        #
        #        image.resize([width,height])
        image = np.array(image, dtype=np.float64)  # 416*416
        assert image.shape == (416, 416)
        photo = np.stack((image, image, image), axis=2)  # （416，416，3）

        # 图片预处理，归一化
        photo = preprocess_input(np.expand_dims(photo, 0), mode='tf')  # （1,416,416,3）
        #        preds = self.model_rpn.predict(photo) #输出是粗分类(1,6048,1) 粗框调整参数(1,6048,4) 和feature map(1,26,26,1024)
        #        featuremap = preds[2] #featuremap

        myfeature_map = self.featuremap_model.predict(photo)
        return myfeature_map

    # ---------------------------------------------------#
    #   检测图片
    # ---------------------------------------------------#
    def detect_image(self, image):
        image_shape = np.array(np.shape(image)[0:2])
        old_width = image_shape[1]  # 原始图片的宽高
        old_height = image_shape[0]
        old_image = copy.deepcopy(image)
        width, height = get_new_img_size(old_width, old_height, img_min_side=416)

        image.resize([width, height])
        photo = np.array(image, dtype=np.float64)
        try:
            temp = photo.shape[2]
        except:
            photo = np.stack((photo, photo, photo), axis=2)
        else:
            pass

        # 图片预处理，归一化
        photo = preprocess_input(np.expand_dims(photo, 0))
        preds = self.model_rpn.predict(photo)  # 输出是粗分类 粗框调整参数 和feature map
        # 将预测结果进行解码
        anchors = get_anchors(self.get_img_output_length(width, height), width, height)
        # rpn_results labels, confs, good_boxes
        rpn_results = self.bbox_util.detection_out(preds, anchors, 1,
                                                   confidence_threshold=0)  # confidence_threshold的值？现在还未分类 有和无
        R = rpn_results[0][:, 2:]  # 很多数量的建议框 需要分批传入classifier来进一步处理

        R[:, 0] = np.array(np.round(R[:, 0] * width / self.config.rpn_stride), dtype=np.int32)  # 对应featuremap大小
        R[:, 1] = np.array(np.round(R[:, 1] * height / self.config.rpn_stride), dtype=np.int32)
        R[:, 2] = np.array(np.round(R[:, 2] * width / self.config.rpn_stride), dtype=np.int32)
        R[:, 3] = np.array(np.round(R[:, 3] * height / self.config.rpn_stride), dtype=np.int32)
        # convert from (x1,y1,x2,y2) to (x,y,w,h)
        R[:, 2] -= R[:, 0]
        R[:, 3] -= R[:, 1]
        base_layer = preds[2]  # featuremap

        delete_line = []
        for i, r in enumerate(R):
            if r[2] < 1 or r[3] < 1:
                delete_line.append(i)
        R = np.delete(R, delete_line, axis=0)

        bboxes = []
        probs = []
        labels = []
        for jk in range(R.shape[0] // self.config.num_rois + 1):
            ROIs = np.expand_dims(R[self.config.num_rois * jk:self.config.num_rois * (jk + 1), :], axis=0)
            # 一个批次的建议框
            if ROIs.shape[1] == 0:
                break

            if jk == R.shape[0] // self.config.num_rois:
                # pad R 填充 不够一个批次的建议框
                curr_shape = ROIs.shape
                target_shape = (curr_shape[0], self.config.num_rois, curr_shape[2])
                ROIs_padded = np.zeros(target_shape).astype(ROIs.dtype)
                ROIs_padded[:, :curr_shape[1], :] = ROIs
                ROIs_padded[0, curr_shape[1]:, :] = ROIs[0, 0, :]
                ROIs = ROIs_padded

            [P_cls, P_regr] = self.model_classifier.predict([base_layer, ROIs])  # 类别和调整位置参数

            for ii in range(P_cls.shape[1]):
                if np.max(P_cls[0, ii, :-1]) < self.confidence:
                    continue

                label = np.argmax(P_cls[0, ii, :-1])

                (x, y, w, h) = ROIs[0, ii, :]

                cls_num = np.argmax(P_cls[0, ii, :-1])

                (tx, ty, tw, th) = P_regr[0, ii, 4 * cls_num:4 * (cls_num + 1)]
                tx /= self.config.classifier_regr_std[0]  # 处理系数
                ty /= self.config.classifier_regr_std[1]
                tw /= self.config.classifier_regr_std[2]
                th /= self.config.classifier_regr_std[3]

                cx = x + w / 2.  # 建议框中心点
                cy = y + h / 2.
                cx1 = tx * w + cx  # 调整后的建议框中心
                cy1 = ty * h + cy
                w1 = math.exp(tw) * w
                h1 = math.exp(th) * h

                x1 = cx1 - w1 / 2.  # 调整后的建议框的左上 右下
                y1 = cy1 - h1 / 2.

                x2 = cx1 + w1 / 2
                y2 = cy1 + h1 / 2

                x1 = int(round(x1))
                y1 = int(round(y1))
                x2 = int(round(x2))
                y2 = int(round(y2))

                bboxes.append([x1, y1, x2, y2])
                probs.append(np.max(P_cls[0, ii, :-1]))
                labels.append(label)

        if len(bboxes) == 0:
            return old_image

        # 筛选出其中得分高于confidence的框
        labels = np.array(labels)
        probs = np.array(probs)
        boxes = np.array(bboxes, dtype=np.float32)
        boxes[:, 0] = boxes[:, 0] * self.config.rpn_stride / width
        boxes[:, 1] = boxes[:, 1] * self.config.rpn_stride / height
        boxes[:, 2] = boxes[:, 2] * self.config.rpn_stride / width
        boxes[:, 3] = boxes[:, 3] * self.config.rpn_stride / height
        results = np.array(
            self.bbox_util.nms_for_out(np.array(labels), np.array(probs), np.array(boxes), self.num_classes - 1, 0.4))

        top_label_indices = results[:, 0]
        top_conf = results[:, 1]
        boxes = results[:, 2:]
        boxes[:, 0] = boxes[:, 0] * old_width
        boxes[:, 1] = boxes[:, 1] * old_height
        boxes[:, 2] = boxes[:, 2] * old_width
        boxes[:, 3] = boxes[:, 3] * old_height

        font = ImageFont.truetype(font='model_data/simhei.ttf',
                                  size=np.floor(3e-2 * np.shape(image)[1] + 0.5).astype('int32'))

        thickness = (np.shape(old_image)[0] + np.shape(old_image)[1]) // old_width * 2
        image = old_image
        for i, c in enumerate(top_label_indices):
            predicted_class = self.class_names[int(c)]
            score = top_conf[i]

            left, top, right, bottom = boxes[i]
            top = top - 5
            left = left - 5
            bottom = bottom + 5
            right = right + 5

            top = max(0, np.floor(top + 0.5).astype('int32'))
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(np.shape(image)[0], np.floor(bottom + 0.5).astype('int32'))
            right = min(np.shape(image)[1], np.floor(right + 0.5).astype('int32'))

            # 画框框
            label = '{} {:.2f}'.format(predicted_class, score)
            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label, font)
            label = label.encode('utf-8')
            print(label)

            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    #                    outline=self.colors[int(c)])
                    outline=None)
            draw.rectangle(
                [tuple(text_origin), tuple(text_origin + label_size)],
                #                fill=self.colors[int(c)])
                fill=None)
            try:
                draw.text(text_origin, str(label, 'UTF-8'), fill=(250,), font=font)
            except:
                draw.text(text_origin, str(label, 'UTF-8'), fill=(250, 250, 250), font=font)
            else:
                pass
            del draw
        return image

    def close_session(self):
        self.sess.close()
