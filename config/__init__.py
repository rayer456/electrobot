import pathlib
import tomllib


path = pathlib.Path(__file__).parent / "config.toml"
with path.open(mode="rb") as fp:
    config_file = tomllib.load(fp)