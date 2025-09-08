# Settle3 User Guide - Modelling

## Modelling

This document addresses common Settle3 technical support questions related to modelling.

## Does Settle3 automatically assign any drainage conditions to layers?

No. Settle3 does not automatically assign drainage conditions to sand layers (layers with consolidation turned off) or any other layers not specified in the drainage conditions dialog.

If drainage is assigned to the top/bottom of a sand layer, this condition will propagate through the non-consolidating layer.  To make sand layers act as a drain, you must explicitly define this drainage condition.

## Can I model a pyramid-shaped load?

Yes, using either polygonal loads or an embankment.  An embankment will approximate the pyramid shape since the start and end points cannot be identical.

## How can I speed up the calculation time for multi-layer analysis mode?

Multi-layer analysis is computationally intensive compared to Boussinesq or Westergaard solutions. Calculation time increases with the number of loads.

For faster computation, use query points or line queries instead of grid queries.

## How can I model sand piles?

Two options exist:

* **Ground Improvement:** Define a smeared improved region under footings.
* **Wick Drains:** Sand piles often act as vertical drains, reducing consolidation settlement. Excess pore pressure generation depends on the distance between the sand pile and the measurement point. Model sand piles indirectly using the wick drain option.

## How do I determine the time to end of primary consolidation?

Use a Time Query to compute the time to a certain degree of consolidation below an embankment.

## To set up a Time Query:

Select `Query > Time Points > Add Time Point`.  The Time Point Properties dialog will appear.

**Time Point Properties Dialog:**

Choose to base the query on either "Degree of Consolidation" or "Total Settlement" and enter the desired value. Specify the stage for time calculation and the depth for value checking.

**Note:** A Time Point Query computes time based on the *current* load state. Changes to the load after the time point stage are not considered. For staged loading, add the time point at the *final* loading stage.

After calculation, you can create a new stage corresponding to the calculated time.

## How can I model a ring load?

Two indirect methods:

1. **Polygonal Loads:** Define the inner and outer circles using polygonal loads. This requires careful coordinate entry, ensuring the start and end coordinates connect the inner and outer circles. This method also applies to other entities with coordinates (wick drain region, ground improvement region, etc.).

2. **Two Circles:** Use two circles: one with a positive load for the outer boundary and another with a negative load for the inner boundary.

## When do I use rigid load or flexible load?

Engineering judgement is required.

**Flexible Load:** Applies planar stress throughout the loading region, then calculates settlement from the applied stress.

**Rigid Load:** Applies planar settlement, then calculates loading stress.

Understanding these assumptions helps choose the appropriate load type for your analysis.

## When should hydroconsolidation be used?

Use hydroconsolidation for soils sensitive to moisture content, experiencing swelling or collapse due to wetting.

Settlement calculation depends on the user-provided pressure vs. Δ void ratio curve.  Steeper curves result in larger settlements.

Elastic solutions do not include hydroconsolidation effects, which are based on small strain theory.

Hydroconsolidation influences all soil layers within the specified region, affecting settlement calculations due to strain changes.

## Is the Unit Weight for soil in Settle3 a dry or wet density?

Settle3 uses moist (unsaturated, degree of saturation < 1) unit weight for material above the phreatic surface.  Saturated unit weight for material below the phreatic surface can be defined separately.

Do not use submerged unit weight below the water table.

## What is a typical range for the B-Bar coefficient of a clay or clayey silt?

Start with a fully saturated value of 1, then modify to check sensitivity.  For undrained loading, B-bar is typically 1 for a degree of saturation of 1, with exceptions like highly overconsolidated clays.  Refer to the B-bar vs. Degree of Saturation figure (omitted here) and the following paper for more details:

Skempton, A.W. (1954) "The Pore-Pressure Coefficients A and B". Geotechnique (4)143-147