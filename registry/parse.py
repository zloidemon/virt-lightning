import tomllib

def gen_angie_map(configuration):
    for name, distro in configuration["images"].items():
        url = distro["url"]
        filename = distro["file"]
        for image in distro["base"]:
            _url = image.get("url", url)
            _file = image.get("file", filename)

            url_template = "/v2/library/{name}/blobs/{tag} " + "/".join([_url, _file]) + ";"

            print(url_template.format(name=name, **image))

with open('config.toml', mode='rb') as fh:
    configuration = tomllib.load(fh)

gen_angie_map(configuration)
