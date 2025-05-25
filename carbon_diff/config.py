import importlib

import yaml

TYPE_MAP = {"aws": "carbon_diff.providers.aws:AWSProvider",
            "gcp": "carbon_diff.providers.gcp:GCPProvider",
            "azure": "carbon_diff.providers.azure:AzureProvider"}

def load_providers(path="cdiff.yml"):
    cfg = yaml.safe_load(open(path))
    providers = []
    for item in cfg["providers"]:
        cls_path = TYPE_MAP[item["type"]]
        module, cls = cls_path.split(":")
        ProviderCls = getattr(importlib.import_module(module), cls)
        providers.append(ProviderCls(**{k:v for k,v in item.items() if k!="type"}))
    return providers
