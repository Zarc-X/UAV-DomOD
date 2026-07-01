_base_ = ['./codetr_all_in_one_strong_aug.py']

# Separate config file for modality-specific augmentation experiments.
# This file avoids touching the existing baseline/strong-aug configs.

image_size = (640, 512)
transform_broadcast = dict(
    type='BugFreeTransformBroadcaster',
    mapping={
        'img': ['tir', 'img'],
        'img_shape': ['img_shape', 'img_shape'],
        'gt_bboxes': ['gt_bboxes', 'gt_bboxes'],
        'gt_bboxes_labels': ['gt_bboxes_labels', 'gt_bboxes_labels'],
        'gt_ignore_flags': ['gt_ignore_flags', 'gt_ignore_flags'],
        'scale_factor': ['scale_factor', 'scale_factor'],
        'flip': ['flip', 'flip'],
        'flip_direction': ['flip_direction', 'flip_direction'],
    },
    auto_remap=True,
    share_random_params=True,
)

# Stage-1: stronger modality-specific perturbation
train_pipeline_stage1 = [
    dict(
        type='MultiInputMixPadding',
        keys=['img', 'tir'],
        size=image_size,
        block_if_below=0.5,
        pad_val=(114, 114, 114),
        individual_pipeline=[
            dict(type='LoadImageFromFile'),
            dict(type='LoadTirFromPath'),
            dict(type='LoadAnnotations', with_bbox=True),

            # RGB-only augmentation
            dict(type='RandomBrightnessContrastByKey', key='img', prob=0.6, brightness_delta=28.0, contrast_range=(0.75, 1.25)),
            dict(type='RandomGaussianNoiseByKey', key='img', prob=0.4, std_range=(2.0, 10.0)),

            # TIR-only augmentation
            dict(type='RandomGaussianBlurByKey', key='tir', prob=0.35, kernel_sizes=(3, 5), sigma_range=(0.1, 1.2)),
            dict(type='RandomEdgeEnhanceByKey', key='tir', prob=0.35, strength_range=(0.4, 1.2), sigma_range=(0.8, 2.0)),
            dict(type='RandomGaussianNoiseByKey', key='tir', prob=0.4, std_range=(2.0, 10.0)),

            # Existing alignment-focused perturbation
            dict(type='RandomShiftOnlyImg', max_shift_px=12, prob=0.7),

            dict(
                **transform_broadcast,
                transforms=[
                    dict(type='RandomResize', scale=image_size, ratio_range=(0.7, 1.5), keep_ratio=True),
                    dict(type='RandomCrop', crop_type='absolute', crop_size=image_size, allow_negative_crop=False),
                    dict(type='RandomRotate90', dir=['l'], prob=0.5),
                    dict(type='RandomFlip', prob=0.5, direction=['horizontal', 'vertical', 'diagonal']),
                ]
            ),
        ]
    ),
    dict(type='CustomPackDetInputs'),
]

# Stage-2: keep modality-specific augmentation but reduce strength
train_pipeline_stage2 = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadTirFromPath'),
    dict(type='LoadAnnotations', with_bbox=True),

    dict(type='RandomBrightnessContrastByKey', key='img', prob=0.35, brightness_delta=20.0, contrast_range=(0.85, 1.15)),
    dict(type='RandomGaussianNoiseByKey', key='img', prob=0.25, std_range=(1.5, 7.0)),

    dict(type='RandomGaussianBlurByKey', key='tir', prob=0.2, kernel_sizes=(3, 5), sigma_range=(0.1, 0.8)),
    dict(type='RandomEdgeEnhanceByKey', key='tir', prob=0.2, strength_range=(0.3, 0.9), sigma_range=(0.8, 1.6)),
    dict(type='RandomGaussianNoiseByKey', key='tir', prob=0.25, std_range=(1.5, 7.0)),

    dict(type='RandomShiftOnlyImg', max_shift_px=10, prob=0.5),
    dict(
        **transform_broadcast,
        transforms=[
            dict(type='RandomResize', scale=image_size, ratio_range=(0.75, 1.5), keep_ratio=True),
            dict(type='RandomCrop', crop_type='absolute', crop_size=image_size, allow_negative_crop=False),
            dict(type='RandomFlip', prob=0.5),
            dict(type='Pad', size=image_size, pad_val=dict(img=(114, 114, 114))),
        ]
    ),
    dict(type='CustomPackDetInputs'),
]

train_dataloader = dict(
    dataset=dict(
        pipeline=train_pipeline_stage1,
    ),
)

default_hooks = dict(
    switch=dict(
        type='PipelineSwitchHook',
        switch_epoch=7,
        switch_pipeline=train_pipeline_stage2,
    )
)
