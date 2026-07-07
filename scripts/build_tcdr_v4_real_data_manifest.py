from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"
OUT_DIR.mkdir(parents=True, exist_ok=True)


SOURCE_ROWS = [
    {
        "source_id": "SPARC_SAMPLE_TABLE",
        "dataset": "SPARC galaxy sample table",
        "url": "https://astroweb.case.edu/SPARC/SPARC_Lelli2016c.mrt",
        "paper_or_dataset_reference": "Lelli et al. 2016 SPARC master sample",
        "tcdr_role": "sample_metadata_control",
        "readout_channel": "dynamics_context",
        "allowed_for_source_label": "conditional",
        "allowed_for_endpoint_scoring": "no",
        "forbidden_for": "post-hoc morphology rescue; endpoint residual inspection",
        "notes": "May provide names, distances, inclinations, luminosity-scale metadata, and original rotation-curve provenance; do not use endpoint residuals from the same source to choose Tau labels.",
    },
    {
        "source_id": "SPARC_MASS_MODELS_TABLE",
        "dataset": "SPARC Newtonian mass-model table",
        "url": "https://astroweb.case.edu/SPARC/MassModels_Lelli2016c.mrt",
        "paper_or_dataset_reference": "Lelli et al. 2016 SPARC mass models",
        "tcdr_role": "baseline_and_endpoint_component",
        "readout_channel": "dynamics_endpoint",
        "allowed_for_source_label": "no",
        "allowed_for_endpoint_scoring": "yes",
        "forbidden_for": "morphology family choice; seed coefficient freeze",
        "notes": "Endpoint-side rotation/baryonic model data. It can score a frozen candidate but must not define the candidate label.",
    },
    {
        "source_id": "SPARC_ROTMOD_ZIP",
        "dataset": "SPARC rotation-curve mass-model files",
        "url": "https://astroweb.case.edu/SPARC/Rotmod_LTG.zip",
        "paper_or_dataset_reference": "Lelli et al. 2016 SPARC rotation curves and baryonic contributions",
        "tcdr_role": "endpoint_data",
        "readout_channel": "dynamics_endpoint",
        "allowed_for_source_label": "no",
        "allowed_for_endpoint_scoring": "yes",
        "forbidden_for": "source-side morphology refinement after seeing residuals",
        "notes": "Compact downloadable endpoint package. Use only after labels, families, and controls are frozen.",
    },
    {
        "source_id": "S4G_IRSA",
        "dataset": "Spitzer Survey of Stellar Structure in Galaxies",
        "url": "https://irsa.ipac.caltech.edu/data/SPITZER/S4G/overview.html",
        "paper_or_dataset_reference": "Sheth et al. 2010; Munoz-Mateos et al. 2013; Querejeta et al. 2015; Watkins et al. 2022; IRSA DOI 10.26131/IRSA425",
        "tcdr_role": "source_side_morphology",
        "readout_channel": "morphology_seed",
        "allowed_for_source_label": "yes",
        "allowed_for_endpoint_scoring": "no",
        "forbidden_for": "rotation-curve residual scoring",
        "notes": "Preferred source-side morphology/modeling route: 3.6/4.5 micron imaging, ellipse/Galfit/model products, and stellar component structure.",
    },
    {
        "source_id": "GALAXY_ZOO_DATA",
        "dataset": "Galaxy Zoo morphology catalogues",
        "url": "https://data.galaxyzoo.org/",
        "paper_or_dataset_reference": "Galaxy Zoo data releases including GZ1/GZ2/GZ DESI morphology products",
        "tcdr_role": "source_side_morphology_crosscheck",
        "readout_channel": "morphology_seed",
        "allowed_for_source_label": "yes",
        "allowed_for_endpoint_scoring": "no",
        "forbidden_for": "endpoint rescue if classifications are selected after residual inspection",
        "notes": "Use as independent morphology/structure crosscheck where objects overlap. GZ DESI offers broad-sky automated morphology but must be frozen before scoring.",
    },
    {
        "source_id": "COSMICFLOWS_EDD",
        "dataset": "Extragalactic Distance Database / Cosmicflows",
        "url": "https://edd.ifa.hawaii.edu/",
        "paper_or_dataset_reference": "Cosmicflows distance and velocity catalogues",
        "tcdr_role": "distance_environment_control",
        "readout_channel": "environment_and_distance_control",
        "allowed_for_source_label": "conditional",
        "allowed_for_endpoint_scoring": "conditional",
        "forbidden_for": "post-hoc amplitude tuning",
        "notes": "Useful for distance, peculiar-velocity, and environment controls. Any amplitude use must be frozen before endpoint scoring.",
    },
]


FIELDNAMES = list(SOURCE_ROWS[0].keys())


def main() -> None:
    out = OUT_DIR / "tcdr_v4_real_data_source_manifest_v0_1.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(SOURCE_ROWS)
    print(f"WROTE {out}")


if __name__ == "__main__":
    main()
