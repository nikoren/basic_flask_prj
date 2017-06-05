import os


curdir = os.path.abspath(__file__)
print curdir

file_path = os.path.join(os.path.dirname(curdir), os.pardir, 'cryptotrader2_config.yml')
print file_path

with open(file_path) as f:
    for line in f:
        print line