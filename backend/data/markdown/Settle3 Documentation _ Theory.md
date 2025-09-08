```markdown
# Settle3 User Guide - Theory

## Theory

This document addresses common Settle3 technical support questions regarding theory.

## Consolidation

### How is secondary consolidation considered in terms of setting up stages?

Secondary consolidation (creep) calculations begin at the end of primary consolidation.  Since 100% primary consolidation theoretically requires infinite time, a default value of 95% primary consolidation marks the starting point for secondary consolidation calculations.  This means secondary settlement is calculated in the current stage only if the degree of consolidation in the previous stage reached the specified value (e.g., 95%).

When setting up a time-dependent consolidation analysis, remember that a stage represents a specific point in time, not a time interval. Settlement occurs *between* stages.  If a load is applied in Stage 1, primary consolidation occurs between Stage 1 and Stage 2.  Since the check for secondary consolidation occurs after some primary consolidation, the earliest secondary consolidation can begin is Stage 2.  Therefore, secondary consolidation cannot occur between Stage 1 and Stage 2.  Consequently, when analyzing secondary consolidation, use multiple stages during primary consolidation to accurately determine when secondary consolidation begins.

The `Time Point` option can pinpoint when secondary consolidation starts, allowing you to add a stage at that precise time.

### What is the difference between Degree of Consolidation and Average Degree of Consolidation?

Settle3 calculates both Degree of Consolidation and Average Degree of Consolidation.

The Degree of Consolidation (U) is calculated as:

```
U = (compression at time t) / (compression at end of consolidation)
```

Consolidation settlements are used in this calculation.  See the *Theory Manual* for a more detailed explanation.

The Average Degree of Consolidation is the average consolidation over the depth of the soil layer.

### How does Settle3 calculate Degree of Consolidation?

Settle3 computes degree of consolidation at numerous locations along queries, similar to consolidation settlement. The maximum degree of consolidation reported in the Report Generator is the maximum value among all these locations.  Since the location of maximum degree of consolidation might differ from the location of maximum consolidation settlement, you cannot use the maximum consolidation settlement from the Report Generator to calculate the maximum degree of consolidation.  You must use settlements from the same location to compute the degree of consolidation.

### When should the "Generate excess pore pressures above water table" option be selected?

The "Generate excess pore pressures above water table" option determines whether immediate or long-term consolidation settlement is calculated above the water table.  In most cases, enabling this option and including consolidation above the water table in the total consolidation settlement is appropriate.

When this option is disabled, and no excess pore water pressure is generated above the water table, the layers above the water table experience immediate consolidation settlement:

```
Δε = (Cc/(1+eo)) * log(p/σ'i) + (Cs/(1+e)) * log(p/σ'f)
```

This option is most influential when the water table is low within the clay layer.  See the *Groundwater* topic for further details.

## Loading

### How is an excavation calculated in Settle3?

Settle3 treats an excavation as a negative load.

Modeling only the excavation, the loading stress is `-γd`, where 'd' is the excavation depth and 'γ' is the soil unit weight. This loading stress is the negative of the overburden stress.  The total stress becomes 0 kPa (assuming metric units) because the overburden stress is added to the loading stress.

If you specify a load of, say, 100 kPa at the excavation bottom, the calculated loading stress becomes `100 kPa + (-γd)`.  The overburden stress is then added, resulting in a total stress of 100 kPa.  To model a specific loading stress at the excavation bottom, specify a stress equal to the sum of the external load stress and the overburden stress.

### Can Settle3 account for interaction between rigid loads?

Settle3 does not consider interaction between multiple rigid loads, making results unreliable for closely spaced rigid loads.  It also ignores interaction between rigid and flexible loads. Only interaction between flexible loads is considered. Excavations are treated as flexible loads.

### What are the limitations of modeling time-dependent consolidation under a rigid load?

Settle3's time-dependent consolidation settlement calculation for rigid loads has two complexities:

1.  Settle3 uses an uncoupled solution for load and excess pore water pressure. The rigid load creates high load concentration at its boundary, accelerating pore water dissipation but not triggering load redistribution.
2.  Settle3 uses a 1D consolidation formulation, preventing excess pore water pressure redistribution in the x-direction.

Both issues can cause problems for time-dependent consolidation analyses.

Settle3 models a rigid foundation as a fully contacting load.  For semi-rigid, no-tension scenarios, a different numerical technique like the finite element method might be more suitable.

### When is the "use average properties to compute layered stresses" option in the Advanced tab of the Project Settings applicable?

This option applies in these cases:

*   Multiple Layer stress computation method is selected.
*   Westergaard stress computation method is selected.
*   Boussinesq stress computation method is selected *and* "Use mean 3D stress" option is selected.

## Advanced Analysis Options

### How is buoyancy considered in Settle3?

As a point in Settle3 moves downward, it goes further below the water table, increasing pore pressure and decreasing effective stress at that point.  If soil initially above the water table settles below it, the soil becomes saturated, potentially increasing unit weight and effective stress at all points below the submerged soil.

By default, this effect is ignored in settlement calculations due to its typically small magnitude.  For cases where buoyancy is significant, enable the "Include Buoyancy Effect" checkbox in the Advanced Settings dialog.

Several assumptions are associated with this option, detailed in the *Settle3 Theory Manual* (accessible through Online Help).  Using buoyancy as a default setting is not recommended. Compare Settle3 results with field measurements to determine the setting's appropriateness.

### What is the settlement cutoff option?

This option specifies the minimum loading stress required to induce settlement. If the loading stress at a given depth falls below the specified fraction of the in-situ effective stress, no settlement occurs below that point.
```