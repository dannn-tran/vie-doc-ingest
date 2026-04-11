import json
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import PurePosixPath, Path

from google.cloud import storage


@dataclass
class DownloadOcrResultToLocalCommand:
    src_bucket: str
    src_file_prefix: str
    dst_dirpath: str


class OcrResultDownloader:
    _logger = None

    def __init__(self, project_id: str, workers: int = 4):
        if OcrResultDownloader._logger is None:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s")
            OcrResultDownloader._logger = logging.getLogger(self.__class__.__name__)

        self._storage_client = storage.Client(project=project_id)
        self._workers = workers

    def download(self, cmd: DownloadOcrResultToLocalCommand):
        dst_dirpath = Path(cmd.dst_dirpath)

        download_one = self._make_download_one(dst_dirpath)
        blobs = self._storage_client.list_blobs(cmd.src_bucket, prefix=cmd.src_file_prefix)

        if self._workers < 2:
            for b in blobs:
                download_one(b)
            return

        with ThreadPoolExecutor(max_workers=self._workers) as executor:
            for _ in executor.map(download_one, blobs):
                pass

    def _make_download_one(self, dst_dirpath: Path):
        def download_one(blob: storage.Blob):
            if not blob.name.endswith('.json'):
                return
            # TODO: skip download if file already downloaded
            for uri, resp in self._explode(blob):
                p = PurePosixPath(uri)
                fdir = dst_dirpath / p.parent.name
                fdir.mkdir(parents=True, exist_ok=True)
                dst = fdir / f"{p.stem}.json"
                with open(dst, "w") as f:
                    json.dump(resp, f)
                self._logger.info(f"Written {dst}.")
        return download_one

    def _explode(self, blob: storage.Blob):
        self._logger.info(f"Download starting - {blob.name}...")
        raw = blob.download_as_bytes()
        self._logger.info(f"Download finished - {blob.name}.")

        responses: list[dict] = json.loads(raw).get("responses", [])
        if not responses:
            self._logger.info(f"No responses in {blob.name}")

        for i, resp in enumerate(responses):
            uri = resp.get('context', dict()).get('uri')
            if not uri:
                self._logger.warn(f"No URI found for response at index {i} of {blob.name}")
                continue
            yield uri, resp
