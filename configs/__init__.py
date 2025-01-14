import argparse
import os

import yaml

__all__ = ['get_config', 'print_config']


def get_config(args):

    config = dict2namespace(setdefault(_get_raw_config(args.config), _get_raw_config("default.yml")))

    if not hasattr(config.sampling, "sigma_dist"):
        config.sampling.sigma_dist = config.model.sigma_dist
    if not hasattr(config.biggan, "resolution"):
        config.biggan.resolution = config.data.image_size

    if args.consistent:
        config.sampling.consistent = args.consistent
        config.sampling.noise_first = False
    if args.step_lr:
        config.sampling.step_lr = args.step_lr
    if args.nsigma != 0:
        config.sampling.nsigma = args.nsigma
    if args.step_lr != 0:
        config.sampling.step_lr = args.step_lr
    if args.batch_size != 0:
        config.sampling.batch_size = args.batch_size
        config.fast_fid.batch_size = args.batch_size
    # ToDo: experimental and is only using model_types
    if args.model_types is not None and len(args.model_types)==1 and args.model_types[0] in [0, 6, 23] and config.data.dataset in ['tinyImages', 'CIFAR10']:
        config.sampling.batch_size = min(200, config.sampling.batch_size)
    if args.model_types is not None and len(args.model_types) == 1 and args.model_types[0] in [8] and config.data.dataset in ['tinyImages', 'CIFAR10']:
        config.sampling.batch_size = min(800, config.sampling.batch_size)

    if args.ODI_steps == -1:
        args.ODI_steps = None
    if args.fid_num_samples != 0:
        config.fast_fid.num_samples = args.fid_num_samples
    if args.begin_ckpt != 0:
        config.fast_fid.begin_ckpt = args.begin_ckpt
        config.sampling.ckpt_id = args.begin_ckpt
    if args.end_ckpt != 0:
        config.fast_fid.end_ckpt = args.begin_ckpt
    if args.adam:
        config.optim.beta1 = args.adam_beta[0]
        config.optim.beta2 = args.adam_beta[1]
    if args.D_adam:
        config.optim.adv_beta1 = args.D_adam_beta[0]
        config.optim.adv_beta2 = args.D_adam_beta[1]
    if args.D_steps != 0:
        config.adversarial.D_steps = args.D_steps

    return config


def _get_raw_config(name):
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, name), 'r') as f:
        yaml_dict = yaml.load(f, Loader=yaml.FullLoader)
    return yaml_dict


def setdefault(config, default):
    #print('config is', config, 'default is', default)
    for x in default:
        v = default.get(x)
        if isinstance(v, dict) and x in config:
            setdefault(config.get(x), v)
        else:
            config.setdefault(x, v)
    return config


def dict2namespace(config):
    namespace = argparse.Namespace()
    for key, value in config.items():
        if isinstance(value, dict):
            new_value = dict2namespace(value)
        else:
            new_value = value
        setattr(namespace, key, new_value)
    return namespace


def print_config(config):
    print(">" * 80)
    print(yaml.dump(config, default_flow_style=False))
    print("<" * 80)
