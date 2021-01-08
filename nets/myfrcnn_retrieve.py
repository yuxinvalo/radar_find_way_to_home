from nets.resnet import ResNet50,classifier_layers
from keras.layers import Conv2D,Input,TimeDistributed,Flatten,Dense,Reshape
from keras.models import Model
from nets.RoiPoolingConv import RoiPoolingConv
def get_rpn(base_layers, num_anchors):
    x = Conv2D(512, (3, 3), padding='same', activation='relu', kernel_initializer='normal', name='rpn_conv1')(base_layers)

    x_class = Conv2D(num_anchors, (1, 1), activation='sigmoid', kernel_initializer='uniform', name='rpn_out_class')(x)
    x_regr = Conv2D(num_anchors * 4, (1, 1), activation='linear', kernel_initializer='zero', name='rpn_out_regress')(x)
    
    x_class = Reshape((-1,1),name="classification")(x_class)
    x_regr = Reshape((-1,4),name="regression")(x_regr) #输出的是38*38*9个anchor的调整参数
    return [x_class, x_regr, base_layers]

def get_classifier(base_layers, input_rois, num_rois, nb_classes=21, trainable=False):#input_rois （None，4）若干个建议框
    pooling_regions = 14 
    input_shape = (num_rois, 14, 14, 1024)
    out_roi_pool = RoiPoolingConv(pooling_regions, num_rois)([base_layers, input_rois]) #输入featuremap和建议框 返回num_rois个14*14的roi
    out = classifier_layers(out_roi_pool, input_shape=input_shape, trainable=True)
    out = TimeDistributed(Flatten())(out)
    out_class = TimeDistributed(Dense(nb_classes, activation='softmax', kernel_initializer='zero'), name='dense_class_{}'.format(nb_classes))(out)
    out_regr = TimeDistributed(Dense(4 * (nb_classes-1), activation='linear', kernel_initializer='zero'), name='dense_regress_{}'.format(nb_classes))(out)
    return [out_class, out_regr] #返回num_rois*(num_class+1) 和 num_rois*(num_class*4)

# resnet和VGG的不一样 这个ROIout可能和VGG的ROIpooling对应
def get_ROIout(base_layers, input_rois, num_rois, nb_classes=21, trainable=False):#input_rois （None，4）若干个建议框
    pooling_regions = 14 
    out_roi_pool = RoiPoolingConv(pooling_regions, num_rois)([base_layers, input_rois]) #输入featuremap和建议框 返回num_rois个14*14的roi
    return out_roi_pool 


def get_model(config,num_classes):
    inputs = Input(shape=(None, None, 3))
    roi_input = Input(shape=(None, 4))
    base_layers = ResNet50(inputs) # base_layer是ResNet提取的特征图

    num_anchors = len(config.anchor_box_scales) * len(config.anchor_box_ratios)#3*3
    rpn = get_rpn(base_layers, num_anchors) #RPN的输出是粗分类和粗定位
    model_rpn = Model(inputs, rpn[:2])
#classifier是网络的最后输出 包括精分类和精定位 RoiPooling
    classifier = get_classifier(base_layers, roi_input, config.num_rois, nb_classes=num_classes, trainable=True)
    model_classifier = Model([inputs, roi_input], classifier)

    model_all = Model([inputs, roi_input], rpn[:2]+classifier)
    return model_rpn,model_classifier,model_all

def get_predict_model(config,num_classes):
    inputs = Input(shape=(None, None, 3))
    roi_input = Input(shape=(None, 4))
    feature_map_input = Input(shape=(None,None,1024))

    base_layers = ResNet50(inputs)
    num_anchors = len(config.anchor_box_scales) * len(config.anchor_box_ratios)
    rpn = get_rpn(base_layers, num_anchors)
    model_rpn = Model(inputs, rpn)

    classifier = get_classifier(feature_map_input, roi_input, config.num_rois, nb_classes=num_classes, trainable=True)
    model_classifier_only = Model([feature_map_input, roi_input], classifier)

    return model_rpn,model_classifier_only


def get_ROIout_model(config,num_classes):
    roi_input = Input(shape=(None, 4))
    feature_map_input = Input(shape=(None,None,1024))

    ROIout = get_ROIout(feature_map_input, roi_input, config.num_rois, nb_classes=num_classes, trainable=True)
    model_ROIout_only = Model([feature_map_input, roi_input], ROIout)

    return model_ROIout_only

def get_featuremap_model(config,num_classes):
    inputs = Input(shape=(None, None, 3))
    base_layers = ResNet50(inputs)

    featuremap_model = Model(inputs, base_layers)

    return featuremap_model