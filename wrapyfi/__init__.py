__version__ = "0.4.9"

from wrapyfi.utils import PluginRegistrar

PluginRegistrar.scan()

import logging
logging.getLogger().setLevel(logging.INFO)
