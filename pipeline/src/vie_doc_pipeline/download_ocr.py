from typing import Annotated

import typer

from gc_vision_adapter.ocr.download import DownloadOcrResultToLocalCommand, OcrResultDownloader

app = typer.Typer()

@app.command()
def main(
    project_id: Annotated[str, typer.Option()],
    src_bucket: Annotated[str, typer.Option()],
    src_file_prefix: Annotated[str, typer.Option()],
    dst_dirpath: Annotated[str, typer.Option()],
    workers: Annotated[int, typer.Option(min=1)] = 1
):
    cmd = DownloadOcrResultToLocalCommand(
        src_bucket=src_bucket,
        src_file_prefix=src_file_prefix,
        dst_dirpath=dst_dirpath
    )
    OcrResultDownloader(project_id, workers=workers).download(cmd)
