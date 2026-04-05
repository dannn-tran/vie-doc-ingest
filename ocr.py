import logging
from itertools import islice

from google.api_core.client_options import ClientOptions
from google.cloud import vision
from google.cloud import storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ID = "vie-ocr"
BUCKET_NAME = "vie-doc"
RESOURCE_PREFIX = "thanh-nghi/images"
OUTPUT_URI = "gs://vie-doc/thanh-nghi/ocr-outputs"

IMG_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.tif')
LANGUAGE_HINTS = ['vi']

INPUT_BATCHSIZE = 100
OUTPUT_BATCHSIZE = 20
TIMEOUT_PER_BATCH = 900


def iter_batches(iterable, size: int):
    """Yield successive chunks of `size` from any iterable. Works on Python 3.10+."""
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk


def batch_ocr(bucket_name: str, prefix: str, output_uri: str):
    output_uri = output_uri.rstrip("/")

    storage_client = storage.Client(project=PROJECT_ID)
    vision_client = vision.ImageAnnotatorClient(
        client_options=ClientOptions(quota_project_id=PROJECT_ID)
    )

    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    image_uris = (
        f"gs://{bucket_name}/{blob.name}"
        for blob in blobs
        if blob.name.lower().endswith(IMG_EXTENSIONS)
    )

    # Phase 1: submit all batches without blocking
    operations = []
    total_images = 0

    for i, chunk in enumerate(iter_batches(image_uris, INPUT_BATCHSIZE)):
        batch_output_uri = f"{output_uri}/batch_{i}/"

        requests = [
            vision.AnnotateImageRequest(
                image=vision.Image(source=vision.ImageSource(image_uri=uri)),
                features=[vision.Feature(type=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)],
                image_context=vision.ImageContext(language_hints=LANGUAGE_HINTS),
            )
            for uri in chunk
        ]

        operation = vision_client.async_batch_annotate_images(
            requests=requests,
            output_config=vision.OutputConfig(
                gcs_destination=vision.GcsDestination(uri=batch_output_uri),
                batch_size=OUTPUT_BATCHSIZE,
            ),
        )

        operations.append((i, len(chunk), operation))
        total_images += len(chunk)
        logger.info(f"Submitted batch {i} ({len(chunk)} images) → {batch_output_uri}")

    logger.info(f"All {len(operations)} batches submitted ({total_images} images total). Waiting...")

    # Phase 2: wait for all operations, collecting failures
    failed_batches = []

    for i, n_images, operation in operations:
        try:
            operation.result(timeout=TIMEOUT_PER_BATCH)
            logger.info(f"Batch {i} completed ({n_images} images)")
        except Exception as e:
            logger.error(f"Batch {i} failed: {e}")
            failed_batches.append(i)

    if failed_batches:
        logger.warning(f"Done with errors. Failed batches: {failed_batches}")
    else:
        logger.info("All batches completed successfully.")


if __name__ == "__main__":
    batch_ocr(BUCKET_NAME, RESOURCE_PREFIX, OUTPUT_URI)