import logging
import sys

logger = logging.getLogger()
# if root.handlers:
#     for handler in root.handlers:
#         root.removeHandler(handler)
# logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
#
# logger = logging.getLogger()


for h in logger.handlers:
    logger.removeHandler(h)
h = logging.StreamHandler(sys.stdout)
# use whatever format you want here
FORMAT = '%(asctime)-15s %(process)d-%(thread)d %(name)s [%(filename)s:%(lineno)d] :%(levelname)8s: %(message)s'
h.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(h)
logger.setLevel(logging.DEBUG)
# Suppress the more verbose modules
logging.getLogger('__main__').setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('boto').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
