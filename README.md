# Vietnamese Print Publication Index

## Public-facing features

- Explore by periodicals
- Search by keywords
- Filter by publication date range
- Explore by writers

## Admin features
- Review AI annotations


## Pipeline
- OCR inference: run Google Vision API in batches and save results to GCS.
  - Inference outputs are archived for future needs e.g. re-run the entire post-processing and enrichment pipeline.
  - May wanna record inference timestamp and input arguments.
- Post-processing:
  - Data explosion: explode batched responses to individual files for more fine-grained handling.
    - Could be saved to a local machine or the same GCS/S3 bucket.
    - Note: egress cost of cloud storage.
  - Enrichment: manual and AI-assisted labelling of additional fields e.g. `publication_date`.
    - Ideally, a unified UI for manual labelling and revision of AI-generated labels.
