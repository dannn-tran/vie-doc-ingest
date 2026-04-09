import itertools
import logging
from dataclasses import dataclass
from typing import Sequence

from google.api_core.client_options import ClientOptions
from google.api_core import operation
from google.cloud import storage
from google.cloud import vision


DEFAULT_OCR_INPUT_EXTS = ('png', 'jpg', 'jpeg', 'tiff', 'tif')
DEFAULT_OCR_INPUT_BATCHSIZE = 100
DEFAULT_OCR_OUTPUT_BATCHSIZE = 20
DEFAULT_OCR_BATCH_PROCESS_TIMEOUT_SECONDS = 900


@dataclass
class RunBatchOcrCommand:
    input_bucket_name: str = ""
    input_file_prefix: str = ""
    input_file_exts: tuple[str, ...] = DEFAULT_OCR_INPUT_EXTS
    input_batchsize: int = DEFAULT_OCR_INPUT_BATCHSIZE
    output_bucket_name: str = ""
    output_dir: str = ""
    output_batchsize: int = DEFAULT_OCR_OUTPUT_BATCHSIZE
    language_hints: Sequence[str] = ()
    batch_process_timeout_seconds: int = DEFAULT_OCR_BATCH_PROCESS_TIMEOUT_SECONDS


class OcrService:
    _logger = None

    def __init__(self, project_id: str):
        if OcrService._logger is None:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
            OcrService._logger = logging.getLogger(self.__class__.__name__)

        self._storage_client = storage.Client(project=project_id)
        self._vision_client = vision.ImageAnnotatorClient(
            client_options=ClientOptions(quota_project_id=project_id)
        )

    def batch_ocr(self, cmd: RunBatchOcrCommand):
        blobs = self._storage_client.list_blobs(cmd.input_bucket_name, prefix=cmd.input_file_prefix)
        image_uris = (
            f"gs://{cmd.input_bucket_name}/{blob.name}"
            for blob in blobs
            if not cmd.input_file_exts or
                blob.name.lower().endswith(cmd.input_file_exts)
        )

        # Phase 1: submit all batches without blocking
        output_uri = f"gs://{cmd.output_bucket_name}/{cmd.output_dir}".rstrip("/")
        ocr_ops: list[tuple[int, operation.Operation]] = [
            (i, self._submit_ocr_batch(i, chunk, output_uri, cmd.output_batchsize, cmd.language_hints))
            for i, chunk in enumerate(itertools.batched(image_uris, cmd.input_batchsize))
        ]
        self._logger.info(f"All {len(ocr_ops)} batches submitted ({len(ocr_ops)} images total). Waiting...")

        # Phase 2: wait for all operations, collecting failures
        failed_batches = []

        for i, ocr_op in ocr_ops:
            try:
                ocr_op.result(timeout=cmd.batch_process_timeout_seconds)
                self._logger.info(f"Batch {i} completed")
            except Exception as e:
                self._logger.error(f"Batch {i} failed: {e}")
                failed_batches.append(i)

        if failed_batches:
            self._logger.warning(f"Done with errors. Failed batches: {failed_batches}")
        else:
            self._logger.info("All batches completed successfully.")

    def _submit_ocr_batch(self, batch_id: int, input_uris: tuple[str, ...], output_uri: str, output_batchsize: int,
                          language_hints: Sequence[str]):
        batch_output_uri = f"{output_uri}/batch_{batch_id}/"
        op = self._vision_client.async_batch_annotate_images(
            requests=[
                vision.AnnotateImageRequest(
                    image=vision.Image(source=vision.ImageSource(image_uri=uri)),
                    features=[vision.Feature(type=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)],
                    image_context=vision.ImageContext(language_hints=language_hints),
                )
                for uri in input_uris
            ],
            output_config=vision.OutputConfig(
                gcs_destination=vision.GcsDestination(uri=batch_output_uri),
                batch_size=output_batchsize,
            ),
        )

        self._logger.info(f"Submitted batch {batch_id} ({len(input_uris)} images) → {batch_output_uri}")

        return op