# Detection Methods Reference — red-tide-algal-bloom-monitoring

## Satellite Remote Sensing

### Ocean Color Sensors

| Sensor | Platform | Resolution | Bands | Revisit | Status |
|--------|----------|-----------|-------|---------|--------|
| OLCI | Sentinel-3A/3B | 300m/1.2km | 21 | 1-2 days | Operational |
| MODIS | Aqua/Terra | 250m-1km | 36 | 1-2 days | Operational |
| VIIRS | Suomi-NPP/JPSS-1 | 375-750m | 22 | 1 day | Operational |
| OCI | PACE | 1km | Hyperspectral | 1-2 days | Operational (2024+) |
| MERIS | Envisat | 300m/1.2km | 15 | 2-3 days | Historical only |

### Chlorophyll-a Algorithms

**OCx Family (Ocean Color):**
- **OC4:** 4-band maximum band ratio for oligotrophic to mesotrophic
- **OC3:** 3-band variant optimized for coastal turbid waters
- **OLCI Neural Net:** Sentinel-3 specific, handles Case-2 waters
- **GIOP:** Generalized Inherent Optical Properties — adaptable to sensor

**Fluorescence-Based:**
- **FLH:** Fluorescence Line Height (MODIS band 13/14/15) — less CDOM interference
- **MCI:** Maximum Chlorophyll Index (MERIS/OLCI band 8/9/10) — detects surface scums
- **SABI:** Surface Algal Bloom Index — ratio of NIR to red bands

**Red Tide Specific:**
- **RBD:** Red Band Difference — K. brevis-specific algorithm
- **CIcyano:** Cyanobacteria Index — phycocyanin peak at 620nm
- **K. brevis index:** Backscattering/absorption ratios at 555nm

### Limitations & Corrections

| Issue | Impact | Correction |
|-------|--------|------------|
| Atmospheric correction | Systematic biases | SeaDAS l2gen, POLYMER, ACOLITE |
| CDOM interference | Overestimates chl-a | FLH, MCI instead of band-ratio |
| Bottom reflectance | Shallow water errors | Depth filtering (>10m) |
| Cloud cover | Data gaps | Multi-day composites, gap-filling |
| Sun glint | Striping artifacts | Glint correction, BRDF models |

## In-Situ Methods

### Fluorometry

**Active Fluorometers:**
- **WET Labs ECO FLNTU:** Combined chl-a + turbidity
- **Turner Designs C3/C6:** Multi-parameter fluorometers
- **bbe Moldaenke AlgaeTorch:** In-vivo chl-a with algal class differentiation
- **Sea-Bird ECO Puck:** Compact fluorometer for profiling/moorings

**Passive Fluorometers:**
- FRRF (Fast Repetition Rate Fluorometry) — photosynthetic efficiency
- PAM (Pulse Amplitude Modulated) — maximum quantum yield

**Deployment Modes:**
- Profiling CTD rosette (discrete profiles)
- Ship underway (continuous surface)
- Moorings/buoys (time series)
- AUV/gliders (spatial mapping)
- FerryBox (ships of opportunity)

### Cell Counting & Identification

| Method | Throughput | Specificity | Cost | Turnaround |
|--------|-----------|-------------|------|------------|
| Light microscopy | Low | High (species) | Low | Hours |
| SEM/TEM | Very low | Very high (ultrastructure) | High | Days |
| Flow cytometry | High | Low (size + pigments) | Medium | Minutes |
| Imaging FlowCytobot | High | High (automated ID) | High | Minutes-hours |
| qPCR/ddPCR | Medium | Very high (species/strain) | Medium | Hours |
| Metabarcoding (HTS) | High | Very high (community) | High | Days-weeks |
| ELISA (toxin) | High | Medium (toxin class) | Low | Hours |
| Lateral flow immunoassay | Very high | Low (presence/absence) | Very low | Minutes |

### Environmental Parameters

| Parameter | Instrument | Deployment |
|-----------|-----------|------------|
| Temperature, Salinity | CTD (SBE 19/37/49) | Profile, mooring |
| Dissolved Oxygen | Optode (Aanderaa, RBR) | Mooring |
| Nutrients (NO3, PO4, SiO4) | Wet chemistry, ISUS | Discrete |
| pH, pCO2 | SAMI, HydroC | Mooring |
| Turbidity | ECO NTU, OBS | Profile, mooring |
| Currents | ADCP | Mooring, vessel |
| PAR/Light | PAR sensor, radiometer | Profile, mooring |

### Toxin Detection

**Chemical Methods:**
| Method | Analytes | LOD | Throughput | Reference |
|--------|----------|-----|------------|-----------|
| LC-MS/MS | Multi-toxin | pg/mL | Medium | AOAC 2011.27 (lipophilic) |
| LC-FLD | PSP toxins | ng/mL | Low | AOAC 2005.06 / 2011.02 |
| LC-UV | Domoic acid | μg/g | Low | AOAC 2006.02 |
| ELISA kits | Single class | ng/mL | High | Various commercial |
| Lateral flow | Single class | ng/mL | Very high | Various commercial |

**Functional Assays:**
| Method | Target | Throughput | Note |
|--------|--------|------------|------|
| Receptor binding assay (RBA) | PSP (Na+ channel) | Medium | Replaces mouse bioassay |
| Phosphatase inhibition (PPIA) | DSP (OA class) | High | Screening only |
| N2a neuroblastoma assay | PSP, NSP, CFP | Low | Functional confirmation |
| Mouse bioassay | Multiple classes | Low | Phasing out globally |

## Analytical Quality Control

### Calibration Standards
- Certified reference materials (CRMs) from NRC Canada, NIST
- In-house reference materials with inter-calibration
- Regular proficiency testing (QUASIMEME, IOC-UNESCO)

### Quality Assurance
- ≥10% duplicate analysis
- ≥5% blanks
- Matrix-certified reference materials per batch
- Control charts for long-term trends
- Method detection limits (MDL) determined annually
- Measurement uncertainty documented per ISO 17025

## Cross-Reference

See `hab_species_reference.md` for species-specific detection thresholds and satellite signatures. See `toxin_profiles.md` for regulatory limits and toxin chemistry.
