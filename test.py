from hsi_utils.datasets import load_raw_data
from pathlib import Path

path = Path(__file__).parent / "input" / "482x512_31.mat"

print(load_raw_data(path)["metadata"])
print(load_raw_data(path)["data"]["bands"])