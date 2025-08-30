```markdown
# Settle3 FAQs

## Overview

This document provides answers to Frequently Asked Questions (FAQs) for Settle3. If you can't find an answer to your question after reading these FAQs:

1. Use the Search feature in the Help system.
2. Contact Rocscience technical support at support@rocscience.com.

## FAQs

### 1. Can the program model non-horizontal soil layers?

While Settle3 doesn't directly support 3D modeling of non-horizontal soil layers, you can analyze variable soil profiles for single-point queries using the Boussinesq stress computation method.  Modify the soil profile in the Soil Layers dialog for each query location and re-run the analysis. Refer to the theory manual on non-horizontal surface layers and extruded sections for more information on modeling soil with varying surface elevations.

### 2. Is it possible to model loads with a rigid foundation?

Yes, Settle3 supports loads with rigid foundations. However, rigid loads are not compatible with time-dependent consolidation. Only elastic settlement or long-term consolidation can be modeled with rigid loading.

### 3. When to use flexible load vs rigid loads?

Refer to the Modelling page for more information.

### 4. How does rigid load work and why do I see higher stresses around the edges of the loading region?

Rigid loads restrain uniform/planar settlement, which influences the calculation of loading stresses.  Higher stresses often occur around the edges of the loading region due to this restraint.  An example of a 10 kPa rigid load applied to a soil medium and its settlement contour plot is illustrative.

### 5. How does Settle3 handle rebound/heave during unloading when immediate settlement is not used?

For non-linear materials, strain during unloading is calculated using Cr (recompression index) instead of Cc (compression index). Cr is typically less than Cc, resulting in less displacement during unloading than loading.  Similarly, Car is used instead of Ca for secondary consolidation during unloading.

### 6. Subgrade modulus reaction is yielding negative results. What's happening?

Negative subgrade modulus values can occur when excavations or other elements (like rigid loads) cause negative total settlement. The modulus is calculated based on loading stress (excluding excavation) divided by total settlement. If the applied load after excavation doesn't result in positive total settlement, the calculation yields a negative value.

**Tips:**

* Check if the final loading stress is enough to counteract rebound/heave.
* Use the reference staging option (referencing the excavation stage) to ignore excavation effects in subgrade modulus results. Note that if loads aren't large enough to offset heaving, the modulus may still be negative.

### 7. Poisson's ratio does not seem to affect the analysis results, why?

Poisson's ratio is only relevant when using mean 3D stress, multiple layers, Westergaard stress computation, or rigid loading. See the Soil Properties topic for details.

### 8. Different staging factors for soil materials do not seem to change the results for constant load in different stages for immediate settlement. Why?

Immediate settlement is based on stress changes.  A constant load across stages means the immediate settlement is calculated once and applied to all stages. To see the effect of staging factors, remove and re-apply the load in different stages.

### 9. How does Settle3 compute pore pressure when material is excavated below the water table?

When excavation extends below the water table, the table is locally lowered to the excavation bottom to ensure a dry excavation. Query points inside see a pore water pressure drop, while external points are unaffected. This approach is conservative, overestimating settlement compared to a 3D groundwater analysis, as it doesn't account for horizontal water flow.

### 10. How does a time point query work for staged loading?

A Time Point Query calculates time based on the current load at the time point stage. It doesn't consider load changes after the time point. For staged loading, add the time point at the final loading stage of interest.

### 11. When should I consider immediate settlement?

Refer to the linked article for guidance on using immediate settlement, primary consolidation, or both.

### 12. Secondary settlement is yielding zero results for dry soil/when I remove groundwater. Why?

Secondary settlement in Settle3 is based on primary consolidation settlement.  When groundwater is removed, the soil is considered dry, resulting in a dry consolidation settlement with no vertical strain change over time, hence zero secondary settlement.

### 13. What happens to my model with no groundwater or a piezometric line at the bottom of the soil with primary consolidation analysis enabled?

With immediate settlement enabled, you'll see immediate settlement in a dry state. With primary consolidation enabled, you'll see primary consolidation settlement even in a dry state. The calculation method is detailed in the Theory Manual (Section 3.2).

### 14. My program crashes when I open the file. What should I do?

File corruption can occur due to simultaneous editing on a network drive.

* If the file extension is .s3d, copy it to an empty folder and try opening.
* If the extension is .s3z, rename to .zip, extract the contents, copy the .s3d file to an empty folder, and try opening.

### 15. RSLog boreholes from previous versions are not visible. What should I do?

Create the .s3d file (see question 14), open the RSLog borehole data in a text editor, and replace all instances of "ILOG Borehole" with "RSLog Borehole".
```