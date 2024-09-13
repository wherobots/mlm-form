import json
import pystac

with open("test.json", mode="r") as f:
    mlm_item = json.loads(f.read())
    mlm_item = pystac.read_dict(mlm_item)
    assert mlm_item.validate(), f"Model metadata is not valid. Check that validation passes against the following schema {SCHEMA_URI}."