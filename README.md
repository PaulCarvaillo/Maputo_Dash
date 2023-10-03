# Maputo_Dash
Dash app to visualize acoustic spaces occupied by birds using dimensionality reduction techniques.

1. Extracts and cleans data for Xenocanto.org
2. Detects Regions of interest
3. Computes acoustic features
4. Dimensionality reduction: PCA, TSNe or UMAP
5. Add context information (biotope, order, family, genus)
6. Visualize clusters

This is a demo for a proof of concept on a specific study case (Maputo Special Reserve).
Currently steps 3-4-5-6 do not use the automatic detection of step 2 but a fixed dataset annotated manually by Glenn Le Floch to which we added meta information such as biotope.
