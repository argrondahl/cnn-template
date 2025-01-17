
import os
import json
from itertools import product
from deoxys.utils import load_json_config

dirs = os.listdir('./templates')

base_template = {
    "train_params": {
        "epochs": 200,
        "callbacks": [
            {
                "class_name": "EarlyStopping",
                "config": {
                    "monitor": "val_loss",
                    "patience": 30
                }
            }
        ]
    }
}

base_path = 'templates/'
ds_params_path = base_path + 'dataset_params/'
preprocess_path = ds_params_path + 'options/'
inp_param_path = base_path + 'input_params/'
model_param_path = base_path + 'model_params/'
architecture_path = base_path + 'architecture/'


def generate_config(data, preprocess='CT_W_PET', aug=False,
                    model_params='adam_1e4',
                    architecture='2d_unet'):
    # loading data reader
    # 36fold_x / 86fold_x
    data_reader = load_json_config(f'{ds_params_path}{data}.json')
    preprocess = load_json_config(f'{preprocess_path}{preprocess}.json')
    data_reader['config'].update(preprocess)
    if aug:
        aug = load_json_config(f'{ds_params_path}aug/aug.json')
        data_reader['config'].update(aug)

    # load input params
    # print(preprocess)
    channel_selector = preprocess['preprocessors'][0]
    if channel_selector['class_name'] != 'ChannelSelector':
        print('SOMETHING IS WRONG! CHECK!')
    channel = channel_selector['config']['channel']
    if type(channel) == int:
        data = '1c'
    elif len(channel) == 2:
        data = '2c'
    elif len(channel) == 3:
        data = '3c'
    else:
        print('SOMETHING IS WRONG!')
    input_params = load_json_config(
        f'{inp_param_path}{data}.json')

    # load model params
    model_params = load_json_config(
        f'{model_param_path}{model_params}.json')

    # load architecture
    if architecture:
        architecture = load_json_config(
            f'{architecture_path}{architecture}.json')

    config = base_template.copy()
    config['dataset_params'] = data_reader
    config['input_params'] = input_params
    config['model_params'] = model_params
    if architecture:
        config['architecture'] = architecture

    return config


def generate_multi_config(output_path='config/', **kwargs):
    params = []
    name_list = []
    arg_list = []
    for key, items in kwargs.items():
        params.append(key)
        if type(items) != list:
            name, val = items
            name_list.append([name])
            arg_list.append([val])
        else:
            name_list.append([item[0] for item in items])
            arg_list.append([item[1] for item in items])

    for name, args in zip(product(*name_list), product(*arg_list)):
        filename = '_'.join(name).replace('__', '_').strip('_')
        key_num = len(params)
        generate_config_params = {params[i]: args[i] for i in range(key_num)}
        content = generate_config(**generate_config_params)

        with open(f'{output_path}{filename}.json', 'w') as f:
            json.dump(content, f)

# 50 exps for the 86 dataset
generate_multi_config(output_path='config/86/', data=[('86_f0', '86fold_0'),('86_f1', '86fold_1'),('86_f2', '86fold_2'),('86_f3', '86fold_3'),('86_f4', '86fold_4')],
                      architecture=[('2d', '2d_unet'),
                                    ],
                      preprocess=[('CECT', 'CECT'),
                                  ('LDCT', 'LDCT'),
                                  ('PET', 'PET'),
                                  ('PET_CECT', 'PET_CECT'),
                                  ('PET_LDCT', 'PET_LDCT'),
                                  ],
                      aug=[('', False),
                           ('aug', True)],
                      )



generate_multi_config(output_path='config/36/', data=[('36_f0', '36fold_0'),('36_f1', '36fold_1'),('36_f2', '36fold_2'),('36_f3', '36fold_3'),('36_f4', '36fold_4')],
                      architecture=[('2d', '2d_unet'),
                                    ],
                      preprocess=[('CECT', 'CECT'),
                                  ('LDCT', 'LDCT'),
                                  ('PET', 'PET'),
                                  ('PET_CECT', 'PET_CECT'),
                                  ('PET_LDCT', 'PET_LDCT'),
                                  ('T2W', 'T2W'),
                                  ('ADC', 'ADC'),
                                  ('T2W_CECT', 'T2W_CECT'),
                                  ('T2W_LDCT', 'T2W_LDCT'),
                                  ('T2W_ADC', 'T2W_ADC'),
                                  ('PET_T2W', 'PET_T2W'),
                                  ('PET_CECT_T2W', 'PET_CECT_T2W'),
                                  ('PET_LDCT_T2W', 'PET_LDCT_T2W'),
                                  ],
                      aug=[('', False),
                           ('aug', True)],
                      )
