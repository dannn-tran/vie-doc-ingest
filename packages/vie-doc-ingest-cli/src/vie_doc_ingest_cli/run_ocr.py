from typing import Annotated

import typer

from gc_vision_adapter.ocr import DEFAULT_OCR_INPUT_BATCHSIZE, DEFAULT_OCR_OUTPUT_BATCHSIZE, \
    DEFAULT_OCR_BATCH_PROCESS_TIMEOUT_SECONDS, OcrService, RunBatchOcrCommand
from vie_doc_ingest_cli.validated import Validated


def main(
    project_id: Annotated[str, typer.Option()],
    input_bucket_name: Annotated[str, typer.Option()],
    input_file_prefix: Annotated[str, typer.Option()],
    input_file_exts: Annotated[str, typer.Option()],
    input_batchsize: Annotated[int, typer.Option(DEFAULT_OCR_INPUT_BATCHSIZE)],
    output_bucket_name: Annotated[str, typer.Option()],
    output_dir: Annotated[str, typer.Option()],
    output_batchsize: Annotated[int, typer.Option(DEFAULT_OCR_OUTPUT_BATCHSIZE)],
    language_hints: Annotated[str, typer.Option("")],
    batch_process_timeout_seconds: Annotated[int, typer.Option(DEFAULT_OCR_BATCH_PROCESS_TIMEOUT_SECONDS)]
):
    validated_input_file_exts = _validate_input_file_exts(input_file_exts)
    if not validated_input_file_exts.is_valid:
        raise Exception(validated_input_file_exts.error)

    cmd = RunBatchOcrCommand(
        input_bucket_name=input_bucket_name,
        input_file_prefix=input_file_prefix,
        input_file_exts=validated_input_file_exts.value,
        input_batchsize=input_batchsize,
        output_bucket_name=output_bucket_name,
        output_dir=output_dir,
        output_batchsize=output_batchsize,
        language_hints=language_hints,
        batch_process_timeout_seconds=batch_process_timeout_seconds
    )

    OcrService(project_id).batch_ocr(cmd)


def _validate_input_file_exts(exts: str) -> Validated[str, tuple[str, ...]]:
    split_exts = tuple(e.strip() for e in exts.split(","))
    invalid_exts = [e for e in split_exts if not e.isalnum()]

    if invalid_exts:
        return Validated(False, "Invalid file extensions: " + ", ".join(invalid_exts), ())
    return Validated(True, "", split_exts)


if __name__ == "__main__":
    typer.run(main)