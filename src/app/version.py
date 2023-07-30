from configparser import ConfigParser


def read_config():
    cf = ConfigParser()
    cf.read('pyproject.toml')
    return cf


def get_api_version():
    cf = read_config()
    return cf['tool.poetry']['version'].strip('"')


def main():
    cf = read_config()
    print(f"{cf['tool.poetry']['name'].title()} running at version: {cf['tool.poetry']['version']}")


if __name__ == "__main__":
    main()
