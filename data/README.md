# Data Directory

Raw negotiation artifacts copied from `/Users/liz/Desktop/Test Data` live under `data/raw/` to keep source materials inside the experiment repository.

## Structure
- `data/raw/professional_services_msa/`
  - `professional_services_msa_base.docx` — baseline agreement.
  - `professional_services_msa_widget_round_1.docx` — first redline round focused on the Widget vendor scenario.
  - `professional_services_msa_showing.docx` — walkthrough/example version.
- `data/raw/msa_2/`
  - `abc_msa.docx` — alternate MSA matter.
- `data/raw/review_data.xlsx` — spreadsheet with reviewer notes and decision metadata (useful for ground-truth extraction).

## Next Steps
- Parse each `.docx` into clause spans using the extraction notebook/script once available.
- Normalize `review_data.xlsx` into JSON (`data/ground_truth/` schema) so KPIs can be computed.
- Maintain original files here; derived artifacts should live in `data/processed/` or `data/ground_truth/` (create as needed).
