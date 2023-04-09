import pathlib
import tomllib


try:
    path = pathlib.Path(__file__).parent / "config.toml"
    with path.open(mode="rb") as fp:
        config_file = tomllib.load(fp)
except FileNotFoundError:
    print('[+] config.toml not found')
    input("[+] Create config.toml in the config folder")