import logging
import pathlib
import urllib.request

from virt_lightning.exceptions import ImageNotFoundUpstreamError
from virt_lightning.idownloader import IDownloader

logger = logging.getLogger("virt_lightning")


class DownloaderNative(IDownloader):
    def __init__(self, configuration, storage_dir):
        self.configuration = configuration
        self.storage_dir = storage_dir

    def __progress_callback(self, filename, cur, length):
        percent = (cur * 100) / length
        done = int(cur / self.__to_mb(1))
        full = int(length / self.__to_mb(1))
        line = f"[{percent:06.2f}%] {done:6}MB/{full}MB {filename}\r"
        print(line, end="")  # noqa: T001

    def __to_mb(self, val):
        return 1024 * 1000 * val

    def __fetch_from_url(self, url=None, **kwargs):
        """Retrieve a VM image from a given url."""
        target_file = pathlib.PosixPath(
            "{storage_dir}/upstream/{distro}.qcow2".format(**kwargs)
        )
        temp_file = target_file.with_suffix(".temp")
        if target_file.exists():
            logger.info("File already exists: %s", target_file)
            return

        class RedirectFilter(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, hdrs, newurl):
                logger.info("Start downloading image from: %s", newurl)
                return urllib.request.HTTPRedirectHandler.redirect_request(
                    self, req, fp, code, msg, hdrs, newurl
                )

        opener = urllib.request.build_opener(RedirectFilter)
        urllib.request.install_opener(opener)

        parent_url = url.format(**kwargs)
        try:
            r = urllib.request.urlopen(
                "{url}/{distro}.qcow2".format(url=parent_url, **kwargs)
            )
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ImageNotFoundUpstreamError(kwargs["distro"]) from None
            raise
        last_modified = r.headers["Last-Modified"]
        logger.debug("Date: %s", last_modified)
        size = r.headers["Content-Length"]
        logger.debug("Size: %s", size)
        length = int(size)
        chunk_size = self.__to_mb(1)
        with temp_file.open("wb") as fd:
            while fd.tell() < length:
                chunk = r.read(chunk_size)
                fd.write(chunk)
                self.__progress_callback(temp_file, fd.tell(), length)
        temp_file.rename(target_file)
        try:
            r = urllib.request.urlopen(f"{parent_url}/{kwargs['distro']}.yaml")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                pass
        with target_file.with_suffix(".yaml").open("wb") as fd:
            fd.write(r.read())
        logger.info(f"Image {kwargs['distro']} is ready!")

    def pull(self, **kwargs):
        """Retrieve a VM image from Internet."""

        for registry in self.configuration.registry_urls:
            try:
                self.__fetch_from_url(
                    storage_dir=self.storage_dir,
                    url=registry.entrypoint,
                    **kwargs,
                )
                break
            except ImageNotFoundUpstreamError:
                logger.info(
                    "Image: %s not found from url: %s",
                    kwargs["distro"],
                    registry.entrypoint,
                )
