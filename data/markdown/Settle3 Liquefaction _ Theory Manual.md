***

ROCSCIENCE

## Settle3

# Liquefaction

### Theory Manual

© 2025 Rocscience Inc.

***

# Table of Contents
1.  **Introduction** ............................................................................................................................................. 5
2.  **Theory** ......................................................................................................................................................... 6
3.  **Cyclic Stress Ratio (CSR)** ..................................................................................................................... 7
4.  **Stress Reduction Factor, r<sub>d</sub>**............................................................................................................... 8
    4.1. NCEER (1997) .................................................................................................................................... 8
    4.2. Idriss (1999) ....................................................................................................................................... 8
    4.3. Kayen (1992) ...................................................................................................................................... 9
    4.4. Cetin et al. (2004).............................................................................................................................. 9
    4.5. Liao and Whitman (1986b) ............................................................................................................ 10
5.  **Magnitude Scaling Factor, MSF**.......................................................................................................... 11
    5.1. Tokimatsu and Seed (1987)............................................................................................................ 11
    5.2. Andrus and Stokoe (1997) .............................................................................................................. 12
    5.3. Youd and Noble (1997) .................................................................................................................... 12
    5.4. Cetin (2004)...................................................................................................................................... 12
    5.5. Idriss (from NCEER report) ............................................................................................................ 13
6.  **Standard Penetration Test (SPT) Based Calculations** ................................................................... 14
    6.1. Pre-Defined Triggering Methods .................................................................................................... 14
    6.2. SPT-N Value Correction Factors..................................................................................................... 15
        6.2.1. Overburden Correction Factor, C<sub>N</sub> ................................................................................ 16
        6.2.2. Hammer Energy Efficiency Correction Factor, C<sub>E</sub>....................................................... 18
        6.2.3. Borehole Diameter Correction Factor, C<sub>B</sub> ................................................................... 19
        6.2.4. Rod Length Correction Factor, C<sub>R</sub>................................................................................ 19
        6.2.5. Sampler Correction Factor, C<sub>s</sub> ...................................................................................... 20
    6.3. Cyclic Resistance Ratio (CRR) ......................................................................................................... 21
        6.3.1. Seed et al. (1984) ................................................................................................................ 22
        6.3.2. NCEER (1997) ...................................................................................................................... 22
        6.3.3. Idriss and Boulanger (2004) .............................................................................................. 24
        6.3.4. Cetin et al. (2004) – Deterministic ..................................................................................... 24
        6.3.5. Japanese Bridge Code (JRA 1990).................................................................................... 24
        6.3.6. Cetin et al. (2004) – Probabilistic...................................................................................... 25
        6.3.7. Liao et al. (1988) – Probabilistic ........................................................................................ 25
        6.3.8. Youd and Noble (2001) – Probabilistic ............................................................................. 2

***

6.4. Relative Density, D<sub>R</sub> ........................................................................................................................ 27
    6.4.1. Skempton (1986) ................................................................................................................... 27
    6.4.2. Ishihara (1979)....................................................................................................................... 27
    6.4.3. Tatsuoka et al. (1980)............................................................................................................. 27
    6.4.4. Idriss and Boulanger (2003) .................................................................................................. 27
    6.4.5. Ishihara, Yasuda, and Yokota (1981) .................................................................................. 27
6.5. Fines Content Correction ................................................................................................................. 28
    6.5.1. Idriss and Boulanger (2008) .................................................................................................. 28
    6.5.2. Youd et al. (2001) .................................................................................................................... 28
    6.5.3. Cetin et al. (2004) .................................................................................................................... 29
6.6. Overburden Correction Factor, K<sub>σ</sub>................................................................................................. 29
    6.6.1. Hynes and Olsen (1999)......................................................................................................... 29
    6.6.2. Idriss and Boulanger (2008) .................................................................................................. 30
    6.6.3. Cetin et al. (2004) .................................................................................................................... 31
6.7. Shear Stress Correction Factor, K<sub>α</sub>................................................................................................ 31
7.  **Cone Penetration Test (CPT) Based Calculations**........................................................................... 33
    7.1. Robertson and Wride (1997) ........................................................................................................... 33
        7.1.1. Calculating I<sub>c</sub> ....................................................................................................................... 33
    7.2. Modified Robertson and Wride (1998) .......................................................................................... 35
        7.2.1. Calculating I<sub>c</sub> ....................................................................................................................... 35
    7.3. Idriss and Boulanger (2004)........................................................................................................... 35
        7.3.1. Calculating q<sub>c1N</sub>................................................................................................................ 36
    7.4. Idriss and Boulanger (2014) ........................................................................................................... 36
    7.5. Moss et al. (2006) – Deterministic................................................................................................ 37
    7.6. Moss et al. (2006) – Probabilistic ................................................................................................. 38
8.  **Shear Wave Velocity (V<sub>s</sub>) Based Calculations** ............................................................................. 39
    8.1. Andrus (2004)................................................................................................................................... 39
    8.2. NCEER (1997) ................................................................................................................................. 40
    8.3. Juang et al. (2001) Probabilistic..................................................................................................... 40
9.  **Post-Liquefaction Lateral Displacement** ......................................................................................... 41
    9.1. Ground Profile.................................................................................................................................. 41
    9.2. SPT γmax Methods .......................................................................................................................... 41
        9.2.1. Zhang, Robertson, and Brachman (2004) ...................................................................... 41
        9.2.2. Tokimatsu and Yoshimi (1983)........................................................................................... 4

***

9.2.3. Shamoto et al. (1998) ........................................................................................................ 44
9.2.4. Wu et al. (2003) .................................................................................................................. 47
9.2.5. Cetin et al. (2009) .............................................................................................................. 47
9.3. CPT γmax Methods......................................................................................................................... 48
    9.3.1. Zhang, Robertson, and Brachman (2004) ...................................................................... 48
    9.3.2. Yoshimine et al. (2006)..................................................................................................... 49
9.4. VST γmax Methods......................................................................................................................... 50
10. **Post-Liquefaction Reconsolidation Settlement** .............................................................................. 51
    10.1. SPT εν Methods.............................................................................................................................. 51
        10.1.1. Ishihara and Yoshimine (1992)....................................................................................... 51
        10.1.2. Tokimatsu and Seed (1984) ........................................................................................... 53
        10.1.3. Shamoto (1984)............................................................................................................... 54
        10.1.4. Wu et al. (2003) ................................................................................................................ 57
        10.1.5. Cetin et al. (2009) ............................................................................................................ 57
        10.1.6. Dry Sand settlement, Pradel (1998) .............................................................................. 58
    10.2. CPT εν Methods .............................................................................................................................. 61
    10.3. VST εν Methods............................................................................................................................... 62
11. **References** ............................................................................................................................................. 6

***

# 1. Introduction
Settle3D offers different methods of calculating the factor of safety associated with liquefaction resistance, probability of liquefaction, and the input parameters required for those calculations. This manual also describes the calculating of lateral spreading displacement as well as the vertical settlement due to liquefaction

***

# 2. Theory
The use of in situ "index" testing is the dominant approach for assessment of the likelihood of "triggering" or initiation of liquefaction. The methods available in Settle3D are:
*   Standard Penetration Test (SPT)
*   Cone Penetration Test (CPT)
*   Shear Wave Velocity (VST)

The potential for liquefaction can be evaluated by comparing the earthquake loading (CSR) with the liquefaction resistance (CRR), expressed as a factor of safety against liquefaction:

> FS = (CRR₇.₅ MSF / CSR) ⋅ K_α K_σ
>
> **1**

where

| | | |
| :--- | :- | :--- |
| CRR₇.₅ | = | cyclic resistance ratio for an earthquake with magnitude 7.5 |
| CSR | = | cyclic stress ratio |
| MSF | = | magnitude scaling factor |
| K_σ | = | overburden stress correction factor |
| K_α | = | ground slope correction factor 

***

# 3. Cyclic Stress Ratio (CSR)
The cyclic stress ratio, CSR, as proposed by Seed and Idriss (1971), is defined as the average cyclic shear stress, τ_av, developed on the horizontal surface of soil layers due to vertically propagating shear waves normalized by the initial vertical effective stress, σ'_v, to incorporate the increase in shear strength due to increase in effective stress. By appropriately weighting the individual stress cycles based on laboratory test data, it has been found that a reasonable amplitude to use for the "average" or equivalent uniform stress, τ_av, is about 65% of the maximum shear stress.

> CSR = τ_av / σ'_v = 0.65 (a_max / g) (σ_v / σ'_v) r_d
>
> **2**

where

| | | |
| :--- | :- | :--- |
| a_max | = | maximum horizontal ground surface acceleration (g) |
| g | = | gravitational acceleration |
| σ_v | = | total overburden pressure at depth z |
| σ'_v | = | effective overburden pressure at depth z |
| r_d | = | stress reduction factor |

This equation is used to calculate CSR for all three analysis types

***

# 4. Stress Reduction Factor, r_d
The stress reduction factor, r_d, is used to determine the maximum shear stress at different depths in the soil. Values generally range 1 at the ground surface to lower values at larger depths.

The SPT, CPT, and VST methods use the same r_d formulations. The following are provided in Settle3D:
*   NCEER (1997)
*   Idriss (1999)
*   Kayen (1992)
*   Cetin et al. (2004)
*   Liao and Whitman (1986b)

## 4.1. NCEER (1997)
> r_d = 1.0 - 0.00765z for z ≤ 9.15m
>
> **3**

## 4.2. Idriss (1999)
> ln(r_d) = α(z) + β(z)M_w
>
> **4**

> α(z) = -1.012 - 1.126 sin(z/11.73 + 5.133)

> β(z) = 0.106 + 0.118 sin(z/11.28 + 5.142)

where

| | | |
| :-- | :- | :--- |
| z | = | depth in meters ≤ 34m |
| M_w | = | earthquake magnitude |

For depths greater than 34m, r_d = 0.5

***

## 4.3. Kayen (1992)
> r<sub>d</sub> = 1 - 0.012z
>
> **5**

where
| | | |
| :-- | :- | :--- |
| z | = | depth in meters |

## 4.4. Cetin et al. (2004)
> r<sub>d</sub>(z, M<sub>w</sub>, a<sub>max</sub>, V*<sub>s,12m</sub>) = [ 1 + ( (-23.013 - 2.949a<sub>max</sub> + 0.999M<sub>w</sub> + 0.0525V*<sub>s,12m</sub>) / (16.258 + 0.201e<sup>0.341(-z+0.0785V*<sub>s,12m</sub>+7.586)</sup>) ) ] / [ 1 + ( (-23.013 - 2.949a<sub>max</sub> + 0.999M<sub>w</sub> + 0.0525V*<sub>s,12m</sub>) / (16.258 + 0.201e<sup>0.341(0.0785V*<sub>s,12m</sub>+7.586)</sup>) ) ] ± σ<sub>εrd</sub>
>
> for z<20 m (65ft)

> r<sub>d</sub>(z, M<sub>w</sub>, a<sub>max</sub>, V*<sub>s,12m</sub>) = { [ 1 + ( (-23.013 - 2.949a<sub>max</sub> + 0.999M<sub>w</sub> + 0.0525V*<sub>s,12m</sub>) / (16.258 + 0.201e<sup>0.341(-20+0.0785V*<sub>s,12m</sub>+7.586)</sup>) ) ] / [ 1 + ( (-23.013 - 2.949a<sub>max</sub> + 0.999M<sub>w</sub> + 0.0525V*<sub>s,12m</sub>) / (16.258 + 0.201e<sup>0.341(0.0785V*<sub>s,12m</sub>+7.586)</sup>) ) ] } - 0.0046(z – 20) ± σ<sub>εrd</sub>
>
> for z≥20m (65ft)

> σ<sub>εrd</sub>(z) = z<sup>0.8500</sup> × 0.0198 &nbsp;&nbsp;&nbsp; for z<12m (40ft)
>
> σ<sub>εrd</sub>(z) = 12<sup>0.8500</sup> × 0.0198 &nbsp;&nbsp;&nbsp; for z≥12m (40ft)
>
> **6**

where

| | | |
| :--- | :- | :--- |
| σ<sub>εrd</sub> | = | standard deviation (assumed to be zero) |
| z | = | depth in meters |
| a<sub>max</sub> | = | gravitational acceleration |
| V*<sub>s,12m</sub> | = | site shear wave velocity over the top 12m 

***

**Notes:**
*   If the site stiffness estimation is difficult, take V*<sub>s,12m</sub> as 150-200m/s.
*   For very soft sites with V*<sub>s,12m</sub> less than 120m/s, use a limiting stiffness of 120m/s in calculations.
*   For very stiff sites, V*<sub>s,12m</sub> with stiffness greater than 250m/s, use 250m/s as the limiting value in calculations.

## 4.5. Liao and Whitman (1986b)
> r<sub>d</sub> = 1.0 - 0.00765z &nbsp;&nbsp;&nbsp; for z≤9.15m
>
> **7**
>
> r<sub>d</sub> = 1.174 - 0.0267z &nbsp;&nbsp;&nbsp; for 9.15 m<z≤ 23 m

where

| | | |
| :-- | :- | :--- |
| z | = | depth below ground surface in meters |

***

# 5. Magnitude Scaling Factor, MSF
If the magnitude of the earthquake is not 7.5, then the CRR values need to be corrected for earthquake magnitude. The following corrections are available:
*   Tokimatsu and Seed (1987)
*   Idriss (1999)
*   Idriss and Boulanger (2014) – SPT and CPT only
*   Andrus and Stokoe (1997)
*   Youd and Noble (1997) – SPT only
*   Cetin (2004)
*   Idriss (NCEER)

## 5.1. Tokimatsu and Seed (1987)
> MSF = 2.5 - 0.2M
>
> **8**

<u>Idriss (1999)</u>
> MSF = 6.9 exp(-M/4) - 0.058 ≤ 1.8
>
> **9**

This method can also be found in Idriss and Boulanger 2004 and 2008.

<u>Idriss and Boulanger (2014)</u>
> MSF = 1 + (MSF<sub>max</sub> - 1) (8.64 exp(-M/4) - 1.325)
>
> **10**

> MSF<sub>max</sub> = 1.09 + (q<sub>c1Ncs</sub> / 180)² ≤ 2.2

> MSF<sub>max</sub> = 1.09 + ((N₁)₆₀cs / 31.5)² ≤ 2.2

***

## 5.2. Andrus and Stokoe (1997)
> MSF = (M<sub>w</sub> / 7.5)<sup>-3.3</sup>
>
> **11**

## 5.3. Youd and Noble (1997)
The summary of the 1996/1998 NCEER Workshop proceedings by Youd and Idriss (2001) outlines various methods for calculating the MSF and provide recommendations for engineering practice.

The following MSF values are for calculated probabilities of liquefaction, the equation for which is also shown.

> Logit(P<sub>L</sub>) = ln( P<sub>L</sub> / (1 - P<sub>L</sub>) ) = -7.0351 + 2.1738M<sub>w</sub> - 0.2678(N₁)₆₀cs + 3.0265 ln(CRR)

> for P<sub>L</sub> < 20% MSF = 10<sup>3.81</sup> / M<sup>4.53</sup> &nbsp;&nbsp;&nbsp; for M<sub>w</sub> < 7
>
> for P<sub>L</sub> < 32% MSF = 10<sup>3.74</sup> / M<sup>4.33</sup> &nbsp;&nbsp;&nbsp; for M<sub>w</sub> < 7
>
> for P<sub>L</sub> < 50% MSF = 10<sup>4.21</sup> / M<sup>4.81</sup> &nbsp;&nbsp;&nbsp; for M<sub>w</sub> < 7.75
>
> for M<sub>w</sub> ≥ 7.5 MSF = 10<sup>2.24</sup> / M<sub>w</sub><sup>2.56</sup>
>
> **12**

## 5.4. Cetin (2004)
> MSF = (7.5 / M<sub>w</sub>)<sup>2.217</sup>
>
> **13**

***

## 5.5. Idriss (from NCEER report)
> MSF = 10<sup>2.24</sup> / M<sup>2.56</sup>
>
> **14**

***

# 6. Standard Penetration Test (SPT) Based Calculations
This section summarizes the methods available for calculating liquefaction resistance based on SPT data. The following are presented:
*   SPT N-Value Correction Factors
*   Cyclic Resistance Ratio (CRR)
*   Relative Density (D<sub>R</sub>)
*   Fines Content Correction
*   Overburden Correction Factor
*   Shear Stress Reduction Factor

SPT-based calculations can be carried out two ways in Settle3D:
1.  **Pre-defined Triggering Methods** – Users choose one of four pre-defined methods for calculating liquefaction. When one of the pre-defined options are chosen, the correction factors and triggering method are automatically selected according to the method and cannot be modified.
2.  **Customized Triggering Methods** – Users can select any combination of correction factors and triggering methods.

## 6.1. Pre-Defined Triggering Methods
The following pre-defined triggering methods are available in Settle3D:
1.  Youd et al. (2001)
2.  Idriss and Boulanger (2008)
3.  Cetin et al. – Deterministic (2004)
4.  Cetin et al. – Probabilistic (2004)

The table below outlines the options that are automatically selected when each pre-defined triggering method is used.

| Triggering Methods | Youd et al. (2001) | Idriss and Boulanger (2008) | Cetin et al. (2004) – Deterministic | Cetin et al. (2004) – Probabilistic |
| :--- | :--- | :--- | :--- | :--- |
| **Triggering Method** | NCEER (1997) | Idriss and Boulanger (2004) | Cetin et al. (2004) Deterministic | Cetin et al. (2004) Probabilistic |

***

| | Depth Correction | Liao & Whitman (1986) | Idriss and Boulanger (2004) | Liao & Whitman (1986) | Liao & Whitman (1986) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| | Sampling Method | Standard | Standard | Standard | Standard |
| **Advanced Settings** | **MSF** | **Idriss (1999)** | **Idriss and Boulanger (2008)** | **None** | **None** |
| | Stress Reduction Factor | Idriss (1999) | Idriss (1999) | Cetin et al. (2004) | Cetin et al. (2004) |
| | Relative Density | Skempton (1986) | Idriss and Boulanger (2003) | Skempton (1986) | Skempton (1986) |
| | Fines Content Correction | Youd et al. (2001) | Idriss and Boulanger (2008) | Cetin et al. (2004) | Cetin et al. (2004) |
| | K sigma | Hynes and Olsen (1999) | Idriss and Boulanger (2008) | Cetin et al. (2004) | Cetin et al. (2004) |
| | K alpha | None | None | None | None |

## 6.2. SPT-N Value Correction Factors
Before the CRR can be calculated, the N values obtained from the SPT must be corrected for the following factors: overburden, rod length, non-standard sampler, borehole diameter, and hammer energy efficiency, resulting in a (N₁)₆₀ value. The equation below illustrates the correction.

> N₆₀ = NC<sub>R</sub>C<sub>S</sub>C<sub>B</sub>C<sub>E</sub>
>
> **15**

> (N₁)₆₀ = N₆₀C<sub>N</sub>
>
> **16**

***

**Table 1: Summary of Correction Factors for Field SPT-N Values**

| Factor | Equipment Variable | Term | Correction |
| :--- | :--- | :--- | :--- |
| Overburden Pressure | | **C<sub>N</sub>** | Section 6.2.1 |
| Energy Ratio | Donut hammer | **C<sub>E</sub>** | 0.5-1.0 |
| | Safety hammer | | 0.7-1.2 |
| | Automatic hammer | | 0.8-1.3 |
| Borehole Diameter | 65 mm -115 mm | **C<sub>B</sub>** | 1.0 |
| | 150 mm | | 1.05 |
| | 200 mm | | 1.12 |
| Rod Length | <3 m | **C<sub>R</sub>** | 0.75 |
| | 3 m – 4 m | | 0.80 |
| | 4 m – 6 m | | 0.85 |
| | 6 m -10 m | | 0.95 |
| | 10 m – 30 m | | 1.00 |
| Sampling Method | Standard Sampler | **C<sub>S</sub>** | 1.0 |
| | Sampler without Liner | | 1.0-1.3 |

### 6.2.1. Overburden Correction Factor, C<sub>N</sub>
The overburden correction factor adjusts N values to the N₁ value that would be measured at the same depth if the effective overburden stress was 1 atm.

The following formulations are available:
*   Liao and Whitman (1986a)
*   Bazaraa (1967)
*   Idriss and Boulanger (2004)
*   Peck (1974)
*   Kayen et al. (1992)

***

<u>Liao and Whitman (1986a)</u>
> C<sub>N</sub> = (P<sub>a</sub> / σ'<sub>v0</sub>)<sup>0.5</sup>
>
> **17**

<u>Bazaraa (1967)</u>
> C<sub>N</sub> = 4 / (1 + 2σ'<sub>v0</sub>) &nbsp;&nbsp;&nbsp; for σ'<sub>v0</sub> ≤ 1.5
>
> **18**
>
> C<sub>N</sub> = 4 / (3.25 + 0.5σ'<sub>v0</sub>) &nbsp;&nbsp;&nbsp; for σ'<sub>v0</sub>' > 1.5

σ'<sub>v</sub> is in ksf

C<sub>N</sub> ≤ 2.0

<u>Idriss and Boulanger (2004)</u>
> C<sub>N</sub> = (P<sub>a</sub> / σ'<sub>v0</sub>)<sup>(0.784-0.0768√(N₁)₆₀)</sup> ≤ 1.7
>
> **19**

(N₁)₆₀ ≤ 46

<u>Peck, Hansen and Thorburn (1974)</u>
> C<sub>N</sub> = 0.77 log(2000 / σ'<sub>v0</sub>)
>
> **20**

σ'<sub>v0</sub> is in kPa ≤ 282 kpa

***

<u>Kayen et al. (1992)</u>
> C<sub>N</sub> = 2.2 / (1.2 + σ'<sub>vo</sub> / P<sub>a</sub>) ≤ 1.7
>
> **21**

#### 6.2.2. Hammer Energy Efficiency Correction Factor, C<sub>E</sub>
The energy efficiency correction factor is calculated using the measured energy ratio as follows.

> C<sub>E</sub> = ER<sub>m</sub> / 60
>
> **22**

It varies from 0.5-1.3. The ranges are taken from Skempton (1986).

| Hammer Type | C<sub>E</sub> |
| :--- | :--- |
| Donut hammer | 0.5-1.0 |
| Safety hammer | 0.7-1.2 |
| Automatic hammer | 0.8-1.3 |

More specifically,

| Hammer Type | C<sub>E</sub> |
| :--- | :--- |
| Automatic Trip | 0.9-1.6 |
| Europe Donut Free fall | 1.0 |
| China Donut Free Fall | 1.0 |
| China Donut Rope& Pulley | 0.83 |
| Japan Donut Free Fall | 1.3 |
| Japan Donut Rope& Pulley | 1.12 |

***

| United States Safety Rope& pulley | 0.89 |
| :--- | :--- |
| United States Donut Rope& pulley | 0.72 |
| United States Automatic Trip Rope& pulley | 1.25 |

#### 6.2.3. Borehole Diameter Correction Factor, C<sub>B</sub>
The following table, from Skempton (1986) summarizes the borehole diameter correction factors for various borehole diameters.

| Borehole Diameter (mm) | C<sub>B</sub> |
| :--- | :--- |
| 65-115 | 1.0 |
| 150 | 1.05 |
| 200 | 1.15 |

#### 6.2.4. Rod Length Correction Factor, C<sub>R</sub>
The rod length correction factor accounts for how energy transferred to the sampling rods is affected by the rod length.

<u>Youd et al. (2001)</u>
The following table from Youd et al (2001) summarizes the rod correction factor for various rod lengths. The rod length above the ground is added to the depth to obtain the total rod length before choosing the appropriate correction factor.

| Rod Length (m) | C<sub>R</sub> |
| :--- | :--- |
| <3 | 0.75 |
| 3-4 | 0.80 |
| 4-6 | 0.85 |
| 6-10 | 0.95 |
| 10-30 | 1.00 |

***

<u>Cetin et al. (2004)</u>
The figure below illustrates the recommended C<sub>R</sub> values (rod length from point of hammer impact to tip of sampler). Note that Cetin assumes a length of 1.2m for rod protrusion, and this is added to the depth before the correction factor is calculated.


**Figure 1: Recommended Cr Values**

#### 6.2.5. Sampler Correction Factor, C<sub>s</sub>
The sampler correction factor is applied in cases when the split spoon sampler has room for liner rings, but those rings were not used.

For the standard sampler, with a liner, the correction is 1.0.

For samplers without liners, the correction factor C<sub>s</sub> ranges from 1.0-1.3 (NCEER, 1997). The following C<sub>s</sub> values are implemented.

| C<sub>s</sub> | Condition | Reference |
| :--- | :--- | :--- |
| C<sub>s</sub> = 1.1 | N₁,₆₀ ≤ 10 | (Cetin et al, 2004) |
| C<sub>s</sub> = 1 + N₁,₆₀/100 | 10 ≤ N₁,₆₀ ≤ 30 | (Cetin et al, 2004) |
| C<sub>s</sub> = 1.3 | N₁,₆₀ ≥ 30 | (Cetin et al, 2004) |

***

## 6.3. Cyclic Resistance Ratio (CRR)
The cyclic resistance ratio is the other term required to calculate the factor of safety against liquefaction. The cyclic resistance ratio represents the maximum CSR at which a given soil can resist liquefaction.

The equation for CRR, corrected for magnitude, is
> CRR = CRR₇.₅ MSF
>
> **23**

The following methods of calculating CRR are available:
*   Seed et al. (1984)
*   NCEER (1997)
*   Idriss and Boulanger (2004)
*   Cetin et al. (2004) Deterministic
*   Japanese Bridge Code (JRA 1990)
*   Cetin et al. (2004) Probabilistic
*   Liao et al. (1988) Probabilistic
*   Youd and Noble (2001) Probabilistic

***

#### 6.3.1. Seed et al. (1984)

**Figure 2: Liquefaction boundary curves - Correlation of (N1)60 values and CRR (M=7.5) (Seed et al. (1984)**

#### 6.3.2. NCEER (1997)
The curves recommended by Youd and Idriss (2001) / NCEER (1997) are based on the Seed et al. (1984) curves.

***


**Figure 3: Simplified Base Curve Recommended for Calculation of CRR from SPT data, with Empirical Liquefaction Data (modified from Seed et al., (1985)**

The equation implemented in **Settle3D** is:
> CRR₇.₅ = 1 / (34 - (N₁)₆₀cs) + (N₁)₆₀cs / 135 + 50 / [10(N₁)₆₀cs + 45]² - 1 / 200
>
> **24**

***

#### 6.3.3. Idriss and Boulanger (2004)
Idriss and Boulanger (2004) recommend the following equation:
> CRR<sub>M=7.5,σ=1</sub> = exp( ((N₁)₆₀cs / 14.1) + ((N₁)₆₀cs / 126)² - ((N₁)₆₀cs / 23.6)³ + ((N₁)₆₀cs / 25.4)⁴ - 2.8 )
>
> **25**

#### 6.3.4. Cetin et al. (2004) – Deterministic
The following equation is used to calculate CRR for a given probability of liquefaction. The correction for fines content is built into the equation.
> CRR((N₁)₆₀, M<sub>w</sub>, σ'<sub>v</sub>, FC, P<sub>L</sub>) = exp [ ( (N₁)₆₀(1 + 0.004FC) – 29.53 ln(M<sub>w</sub>) - 3.70 ln(σ'<sub>v</sub>/P<sub>a</sub>) + 0.05FC + 16.85 + 2.70Φ⁻¹(P<sub>L</sub>) ) / 13.32 ]
>
> **26**

#### 6.3.5. Japanese Bridge Code (JRA 1990)
This method is based on both the equivalent clean sand N value as well as the particle size distribution.

Note that in the equation below σ'<sub>v</sub> is in kg/cm².
> CRR<sub>M=7.5,σ=1</sub> = 0.0882 √( (N₁)₆₀cs / (σ'<sub>v</sub> + 0.7) ) + 0.255 log(0.35/D₅₀) + R₃ &nbsp;&nbsp;&nbsp; for 0.05mm ≤ D₅₀ < 0.6mm

> CRR<sub>M=7.5,σ=1</sub> = 0.0882 √( (N₁)₆₀cs / (σ'<sub>v</sub> + 0.7) ) - 0.05 &nbsp;&nbsp;&nbsp; for 0.6mm ≤ D₅₀ < 2mm

> R₃ = 0 &nbsp;&nbsp;&nbsp; for FC < 40%

> R₃ = 0.004FC – 0.16 &nbsp;&nbsp;&nbsp; for FC ≥ 40%
>
> **27** đã thống nhất.

***

#### 6.3.6. Cetin et al. (2004) – Probabilistic
Similar to the deterministic method, the Cetin et al. (2004) Probabilistic method has the fines content correction built into the P<sub>L</sub> formulation.
> P<sub>L</sub>((N₁)₆₀, CSRₑq, M<sub>w</sub>, σ'<sub>v</sub>, FC) = Φ [ ( (N₁)₆₀(1 + 0.004FC) – 13.32ln(CSRₑq) – 29.53 ln(M<sub>w</sub>) – 3.70 ln(σ'<sub>v</sub>/P<sub>a</sub>) + 0.05FC + 16.85 ) / 2.70 ]
>
> **28**

#### 6.3.7. Liao et al. (1988) – Probabilistic


**Figure 4: Probabilistic SPT-based liquefaction triggering (Liao et al. 1988)**

***

#### 6.3.8. Youd and Noble (2001) – Probabilistic
The Youd and Noble (2001) formulation is outlined below.
> Logit(P<sub>L</sub>) = ln( P<sub>L</sub> / (1 - P<sub>L</sub>) ) = -7.0351 + 2.1738M<sub>w</sub> – 0.2678(N₁)₆₀cs + 3.0265 ln(CRR)
>
> **29**


**Figure 5: Probabilistic SPT-based liquefaction triggering (Youd and Noble, 1997)**

***

## 6.4. Relative Density, D<sub>R</sub>
The relative density, D<sub>R</sub>, of a soil is used in the calculation of the overburden correction factor, C<sub>N</sub>. The following methods are available:
*   Skempton (1986)
*   Ishihara (1979)
*   Tatsuoka et al. (1980)
*   Idriss and Boulanger (2003)
*   Ishihara, Yasuda, and Yokota (1981)

#### 6.4.1. Skempton (1986)
> N₁,₆₀ = 41 * D<sub>R</sub>²
>
> **30**

#### 6.4.2. Ishihara (1979)
> D<sub>R</sub> = 0.9 * (N₁,₆₀ + 14 + 6.51 log₁₀ FC)
>
> **31**

#### 6.4.3. Tatsuoka et al. (1980)
> D<sub>R</sub> = 0.9 * (N₁,₆₀ + 14 + 6.51 log₁₀ FC)
>
> **32**

#### 6.4.4. Idriss and Boulanger (2003)
> D<sub>R</sub> = √( N₁,₆₀ / 46 )
>
> **33**

#### 6.4.5. Ishihara, Yasuda, and Yokota (1981)
> D<sub>R</sub> = 0.0676√N₁,₆₀ + 0.085 log₁₀(0.5/D₅₀)
>
> **34**

***

## 6.5. Fines Content Correction
The following fines content correction methods are available:
*   Idriss and Boulanger (2008)
*   Youd et al. (2001)
*   Cetin et al. (2004)

#### 6.5.1. Idriss and Boulanger (2008)
> (N₁)₆₀cs = (N₁)₆₀ + Δ(N₁)₆₀

> Δ(N₁)₆₀ = exp[ 1.63 + (9.7 / (FC + 0.01)) - (15.7 / (FC + 0.01))² ]
>
> **35**

#### 6.5.2. Youd et al. (2001)
> (N₁)₆₀cs = α + β(N₁)₆₀

> α = 0 &nbsp;&nbsp;&nbsp; for FC ≤ 5%
>
> α = exp[1.76 - (190/FC²)] &nbsp;&nbsp;&nbsp; for 5% < FC < 35%
>
> α = 5.0 &nbsp;&nbsp;&nbsp; for FC ≥ 35%

> β = 1.0 &nbsp;&nbsp;&nbsp; for FC ≤ 5%
>
> β = [0.99 + (FC¹⁵/1000)] &nbsp;&nbsp;&nbsp; for 5% < FC < 35%
>
> β = 1.2 &nbsp;&nbsp;&nbsp; for FC ≥ 35%
>
> **36**

***

#### 6.5.3. Cetin et al. (2004)
> (N₁)₆₀cs = (N₁)₆₀C<sub>FINES</sub>

> C<sub>FINES</sub> = (1 + 0.004FC) + 0.05(FC / N₁,₆₀) &nbsp;&nbsp;&nbsp; for 5% ≤ FC ≤ 35%
>
> **37**

## 6.6. Overburden Correction Factor, K<sub>σ</sub>
In addition to magnitude, the CRR can be corrected for overburden. The CRR of sand depends on the effective overburden stress; liquefaction resistance increases with increasing confining stress.

There are three options available for SPT:
*   Hynes and Olsen (1999) (NCEER)
*   Idriss and Boulanger (2008)
*   Cetin et al. (2004)

#### 6.6.1. Hynes and Olsen (1999)
> K<sub>σ</sub> = (σ'<sub>v0</sub> / P<sub>a</sub>)<sup>(f-1)</sup>

> f = 0.7 – 0.8 &nbsp;&nbsp;&nbsp; for 40% < *relative density* < 60%
>
> f = 0.6 – 0.7 &nbsp;&nbsp;&nbsp; for 60% < *relative density* < 80%
>
> **38**

The parameter f is a function of site conditions, and the estimates below are recommended conservative values for clean and silty sands and gravels.

***


**Figure 6: Recommended curves for estimating K<sub>σ</sub> for engineering practice (from NCEER 1996 workshop)**

#### 6.6.2. Idriss and Boulanger (2008)
This method is essentially the same as the one found in Idriss and Boulanger (2004), except that the limit for K is higher.

> K<sub>σ</sub> = 1 - C<sub>σ</sub> ln(σ'<sub>v0</sub> / P<sub>a</sub>) ≤ 1.1

> C<sub>σ</sub> = 1 / (18.9 - 17.3D<sub>R</sub>) ≤ 0.3

The D<sub>R</sub> can be estimated from the SPT blow count as,
> D<sub>R</sub> = √( (N₁)₆₀cs / C<sub>d</sub> )
>
> **39**

Where the D<sub>R</sub> cannot exceed 100%.

***

#### 6.6.3. Cetin et al. (2004)
The following figure illustrates the recommended values.


**Figure 7: K<sub>σ</sub> values, shown with NCEER recommendations (for n=0.7 and DR<60%) for comparison**

## 6.7. Shear Stress Correction Factor, K<sub>α</sub>
K<sub>α</sub> is the static shear stress correction factor, used to correct CRR values for the effects of static shear stresses. The only option available in Settle3D for this factor is from Idriss and Boulanger (2003).

> K<sub>α</sub> = a + b exp(ξ<sub>R</sub>/c)

> a = 1267 + 636α² – 634 exp(α) – 632 exp(-α)

> b = exp[-1.11 + 12.3α² + 1.31 ln(α + 0.0001)]

> c = 0.138 + 0.126α + 2.52α³

> ξ<sub>R</sub> = 1 / (Q - ln(100p'/P<sub>a</sub>)) - D<sub>R</sub>

***

> α ≤ 0.35

> -0.6 ≤ ξ<sub>R</sub> ≤ 0
>
> **40**

where
| | | |
| :--- | :- | :--- |
| D<sub>R</sub> | = | relative density |
| p' | = | mean effective normal stress |
| Q | = | empirical constant which determines the value of p' at which dilatancy is suppressed and depends on the grain type (Q~10 for quarz and feldspar, 8 for limestone, 7 for anthracite, and 5.5 for chalk; Settle3D uses 8) |
| P<sub>a</sub> | = | atmospheric pressure |
| α | = | tan of slope angle. |

Đã nhận file. Dưới đây là kết quả OCR cho đã thống nhất.

***

# 7. Cone Penetration Test (CPT) Based Calculations
The following methods are available in **Settle3D** for determining triggering of liquefaction:
*   Robertson and Wride (1997)
*   Modified Robertson and Wride (1998)
*   Boulanger and Idriss (2004)
*   Boulanger and Idriss (2014)
*   Moss et al. (2006) – Deterministic
*   Moss et al. (2006) – Probabilistic

As mentioned in previous section, the magnitude scaling factor (MSF) and stress reduction factor (r<sub>d</sub>) equations are the same as for SPT. These equations can be found in sections 4 and 5.

## 7.1. Robertson and Wride (1997)
The following methods are employed in the Robertson and Wride (1997) triggering method:
1.  Calculate I<sub>c</sub> using the procedure outlined in the NCEER summary report.
2.  Calculate q<sub>c1N</sub> using the n value from the I<sub>c</sub> calculation.
3.  Calculate q<sub>c1Ncs</sub>, with K<sub>c</sub> calculated based on the NCEER recommendation. Depths with q<sub>c1Ncs</sub> ≥ 160 are considered not liquefiable.

> K<sub>c</sub> = 1.0 &nbsp;&nbsp;&nbsp; for I<sub>c</sub> ≤ 1.64
>
> K<sub>c</sub> = -0.403I<sub>c</sub>⁴ + 5.581I<sub>c</sub>³ – 21.63I<sub>c</sub>² + 33.75I<sub>c</sub> – 17.88 &nbsp;&nbsp;&nbsp; for I<sub>c</sub> > 1.64
>
> **41**

> q<sub>c1Ncs</sub> = K<sub>c</sub>q<sub>c1N</sub>
>
> **42**

4.  Calculate CRR based on Robertson and Wride (1997).

> CRR₇.₅ = 0.833 [q<sub>c1Ncs</sub> / 1000] + 0.05 &nbsp;&nbsp;&nbsp; if q<sub>c1Ncs</sub> < 50

> CRR₇.₅ = 93 [q<sub>c1Ncs</sub> / 1000]³ + 0.08 &nbsp;&nbsp;&nbsp; if 50 ≤ q<sub>c1Ncs</sub> < 160
>
> **43**

### 7.1.1. Calculating Ic
The soil behavior type index, I<sub>c</sub>, is calculated using the following equation:
> I<sub>c</sub> = [(3.47 - log(Q))² + (1.22 + log(F))²]⁰.⁵
>
> **44**

***

where
> F = [f<sub>s</sub> / (q<sub>c</sub> - σ<sub>v0</sub>)] * 100%
>
> **45**

> Q = [ (q<sub>c</sub> - σ<sub>v0</sub>) / P<sub>a</sub> ] [ P<sub>a</sub> / σ'<sub>v0</sub> ]ⁿ
>
> **46**

The recommended procedure for calculating the soil behavior type index is iterative, as outlined in the NCEER summary report (Robertson and Wride, 1997).
1.  Assume n=1.0 and calculate Q using the following equation.
> Q = [ (q<sub>c</sub> - σ<sub>v0</sub>) / P<sub>a</sub> ] [ P<sub>a</sub> / σ'<sub>v0</sub> ]¹˙⁰ = [ (q<sub>c</sub> - σ<sub>v0</sub>) / σ'<sub>v0</sub> ]
>
> **47**
Calculate I<sub>c</sub> using the equation in the previous section.
2.  If I<sub>c</sub> > 2.6 (or the user-defined I<sub>c,max</sub>), the soil is clayey and not susceptible to liquefaction.
3.  If I<sub>c</sub> < 2.6 (or the user-defined I<sub>c,max</sub>), recalculate Q using n = 0.5, and recalculate I<sub>c</sub>.
4.  If I<sub>c</sub> < 2.6 (or the user-defined I<sub>c,max</sub>), the soil is non-plastic and granular. No further calculation is required.
5.  If I<sub>c</sub> > 2.6 (or the user-defined I<sub>c,max</sub>), the soil is probably silty. Calculate q<sub>c1N</sub> using the equations below, with n = 0.7 in the equation for C<sub>Q</sub>.
> q<sub>c1N</sub> = C<sub>Q</sub> (q<sub>c</sub>/P<sub>a</sub>) ≤ 254
>
> **48**

> C<sub>Q</sub> = (P<sub>a</sub> / σ'<sub>v0</sub>)ⁿ ≤ 1.7
>
> **49**

6.  Calculate I<sub>c</sub> using the q<sub>c1N</sub> value calculated in (5).

***

## 7.2. Modified Robertson and Wride (1998)
The following methods are employed in Modified Robertson and Wride (1998):
1.  Calculate I<sub>c</sub> using the procedure outlined in Robertson and Wride (1998).
2.  Calculate q<sub>c1N</sub> using the n value from the I<sub>c</sub> calculation.
3.  Calculate q<sub>c1Ncs</sub>, with K<sub>c</sub> calculated based on Robertson and Wride (1998). Depths with q<sub>c1Ncs</sub> ≥ 160 are considered not liquefiable.

> K<sub>c</sub> = 0 &nbsp;&nbsp;&nbsp; for FC ≤ 5%
>
> K<sub>c</sub> = 0.0267(FC – 5) &nbsp;&nbsp;&nbsp; for 5 < FC < 35%
>
> K<sub>c</sub> = 0.8 &nbsp;&nbsp;&nbsp; for FC ≥ 35%
>
> **50**

> Δq<sub>c1N</sub> = K<sub>c</sub> / (1 - K<sub>c</sub>) q<sub>c1N</sub>
>
> **51**

> q<sub>c1Ncs</sub> = q<sub>c1N</sub> + Δq<sub>c1N</sub>
>
> **52**

4.  Calculate CRR based on Robertson and Wride (1997).
> CRR₇.₅ = 0.833 [q<sub>c1Ncs</sub> / 1000] + 0.05 &nbsp;&nbsp;&nbsp; if q<sub>c1Ncs</sub> < 50
>
> **53**

> CRR₇.₅ = 93 [q<sub>c1Ncs</sub> / 1000]³ + 0.08 &nbsp;&nbsp;&nbsp; if 50 ≤ q<sub>c1Ncs</sub> < 160
>
> **54**

### 7.2.1. Calculating Ic
The recommended procedure for calculating the soil behavior type index is iterative, as outlined in Robertson and Wride (1998).
1.  Assume n=1.0 and calculate Q and I<sub>c</sub> as outlined in Section 7.1.1. If I<sub>c</sub> > 2.6 then the point is considered not liquefiable.
2.  If I<sub>c</sub> ≤ 2.6, calculate q<sub>c1N</sub> using n=0.5, and recalculate I<sub>c</sub> using q<sub>c1N</sub>.
3.  If the recalculated I<sub>c</sub> ≤ 2.6, the value of I<sub>c</sub> calculated with n=0.5 is used. If I<sub>c</sub> iterates around 2.6 depending on n, then use n=0.75 to calculate q<sub>c1N</sub> and I<sub>c</sub>.

## 7.3. Idriss and Boulanger (2004)
The following methods are employed in the Idriss and Boulanger (2004) triggering method:
1.  Calculate q<sub>c1N</sub> according to Idriss and Boulanger (2004) iterative procedure.
2.  Calculate K<sub>c</sub>, based on Idriss and Boulanger (2004).
> C<sub>σ</sub> = 1 / (37.3 – 8.27(q<sub>c1N</sub>)⁰.²⁶⁴) ≤ 0.3; &nbsp;&nbsp;&nbsp; q<sub>c1N</sub> ≤ 211
>
> **55**

***

> K<sub>σ</sub> = 1 - C<sub>σ</sub> ln(σ'<sub>v0</sub>/P<sub>a</sub>) ≤ 1.0
>
> **56**

3.  Calculate q<sub>c1Ncs</sub>, based on Idriss and Boulanger (2004).
> Δq<sub>c1N</sub> = (5.4 + q<sub>c1N</sub>/16) exp(1.63 + 9.7/(FC + 0.01) - (15.7/(FC + 0.01))²)
>
> **57**

> q<sub>c1Ncs</sub> = q<sub>c1N</sub> + Δq<sub>c1N</sub>
>
> **58**

4.  Calculate CRR based on Idriss and Boulanger (2004).
> CRR<sub>M=7.5,σ'<sub>vc</sub>=1</sub> = exp( (q<sub>c1Ncs</sub>/540) + (q<sub>c1Ncs</sub>/67)² - (q<sub>c1Ncs</sub>/80)³ + (q<sub>c1Ncs</sub>/114)⁴ - 3 )
>
> **59**

### 7.3.1. Calculating q<sub>c1N</sub>
The following iterative procedure is used to calculate q<sub>c1N</sub>:
1.  Calculate q<sub>c1N</sub> using n=1.0.
2.  Recalculate q<sub>c1N</sub> using the following equation for n:
> n = 1.338 - 0.249(q<sub>c1N</sub>)⁰.²⁶⁴
>
> **60**
A total of 100 iterations are performed, after which the last calculated value of q<sub>c1N</sub>is used.

## 7.4. Idriss and Boulanger (2014)
The following methods are employed in the Idriss and Boulanger (2014) triggering method:
1.  Calculate q<sub>cN</sub> = q<sub>t</sub>/P<sub>a</sub>.
> q<sub>t</sub> = q<sub>c</sub> + u₂(1 – a)
>
> where a is the cone area ratio.
>
> **61**

> q<sub>CN</sub> = q<sub>t</sub> / P<sub>a</sub>
>
> **62**

2.  Calculate q<sub>c1Ncs</sub> according to Idriss and Boulanger (2008). This is an iterative procedure, as outlined below.
> C<sub>N</sub> = (P<sub>a</sub>/σ'<sub>v0</sub>)ᵐ ≤ 1.7

***

> m = 1.338 – 0.249(q<sub>c1Ncs</sub>)⁰.²⁶⁴
>
> **63**

> q<sub>c1N</sub> = C<sub>N</sub>q<sub>CN</sub>
>
> **64**

> Δq<sub>c1N</sub> = (11.9 + q<sub>c1N</sub>/14.6) exp(1.63 - 9.7/(FC + 2) - (15.7/(FC + 2))²)
>
> **65**

> q<sub>c1Ncs</sub> = q<sub>c1N</sub> + Δq<sub>c1N</sub>
>
> **66**

3.  Calculate K<sub>σ</sub> according to Idriss and Boulanger (2014).
> C<sub>σ</sub> = 1 / (37.3 – 8.27(q<sub>c1Ncs</sub>)⁰.²⁶⁴) ≤ 0.3
>
> **67**

> K<sub>σ</sub> = 1 - C<sub>σ</sub> ln(σ'<sub>v0</sub>/P<sub>a</sub>) ≤ 1.1
>
> **68**

4.  Calculate CRR based on Idriss and Boulanger (2014).
> CRR<sub>M=7.5,σ'<sub>v</sub>=1atm</sub> = exp( (q<sub>c1Ncs</sub>/113) + (q<sub>c1Ncs</sub>/1000)² - (q<sub>c1Ncs</sub>/140)³ + (q<sub>c1Ncs</sub>/137)⁴ - 2.80 )
>
> **69**

## 7.5. Moss et al. (2006) – Deterministic
The following methods are employed in the deterministic Moss et al. (2006) triggering method:
1.  Calculate q<sub>c1</sub>, with c calculated according to the method outlined in Moss et al. (2006).
> c = f₁(R<sub>f</sub>/f₃)²
>
> **70**

> R<sub>f</sub> = (f<sub>s</sub>/q<sub>c</sub>) * 100
>
> f₁ = x₁ ⋅ q<sub>c</sub><sup>x₂</sup>
>
> f₂ = -(y₁ ⋅ q<sub>c</sub>² + y₃)
>
> f₃ = abs(log(10 + q<sub>c</sub>))<sup>z₁</sup>
>
> where
>
> x₁ = 0.78; x₂ = -0.33; y₁ = -0.32; y₂ = -0.35; y₃ = 0.49; z₁ = 1.21

***

> q<sub>c1</sub> = C<sub>q</sub> ⋅ q<sub>c</sub>

> C<sub>q</sub> = (P<sub>a</sub>/σ'<sub>v</sub>)ᶜ ≤ 1.7

2.  Calculate CRR according to Moss et al. (2006), based on a 50% probability of liquefaction.
> CRR = exp{[q<sub>c,1</sub>¹˙⁰⁴⁵ + q<sub>c,1</sub>(0.110 ⋅ R<sub>f</sub>) + (0.001 ⋅ R<sub>f</sub>) + c(1 + 0.850 ⋅ R<sub>f</sub>) – 0.848 ⋅ ln(M<sub>w</sub>) – 0.002 ⋅ ln(σ'<sub>v</sub>) – 20.923 + 1.632 ⋅ Φ⁻¹(P<sub>L</sub>)]/7.177}
>
> **71**

## 7.6. Moss et al. (2006) – Probabilistic
The following methods are employed in the probabilistic Moss et al. (2006) triggering method:
1.  Calculate q<sub>c1</sub>, with c calculated according to the method outlined in Moss et al. (2006). The calculations are outlined in the section above.
2.  Calculate P<sub>L</sub> according to Moss et al. (2006), based on the user-defined Factor of Safety, or calculate CRR based on the user-defined probability of liquefaction. The CRR calculation method is outlined above.
> P<sub>L</sub> = Φ{ - [ (q<sub>c,1</sub>¹˙⁰⁴⁵ + q<sub>c,1</sub>(0.110 ⋅ R<sub>f</sub>) + (0.001 ⋅ R<sub>f</sub>) + c(1 + 0.850 ⋅ R<sub>f</sub>) – 7.177 ⋅ ln(CSR)) - 0.848 ⋅ ln(M<sub>w</sub>) – 0.002 ⋅ ln(σ'<sub>v</sub>) – 20.923 ] / 1.632 }
>
> **72**

***

# 8. Shear Wave Velocity (V<sub>s</sub>) Based Calculations
The magnitude scaling factor (MSF) and stress reduction factor (r<sub>d</sub>) equations are the same as for CPT and SPT. These equations can be found in sections 4 and 5.

The following methods are available in **Settle3D** for determining triggering of liquefaction based on shear wave input:
*   Andrus (2004)
*   NCEER (1997)
*   Juang et al. (2001) Probabilistic

Before triggering, the input v<sub>s</sub> value is normalized to v<sub>s1</sub> as follows:
> V<sub>s1</sub> = V<sub>s</sub> (P<sub>a</sub>/σ'<sub>v</sub>)⁰.²⁵
>
> **73**

## 8.1. Andrus (2004)
The following methods are employed in the Andrus (2004) triggering method:
1.  Calculate V<sub>s1cs</sub> using the formulation for K<sub>fc</sub> from Juang et al.
2.  Calculate CRR according to Andrus (2004).
> CRR₇.₅ = 0.022 [V<sub>s1cs</sub> / 100]² + 2.8 [ 1 / (215 - V<sub>s1cs</sub>) - 1/215 ]
>
> **74**

You can also account for an overburden correction factor. The Idriss and Boulanger (2004) equation is as follows:
> K<sub>σ</sub> = 1 - C<sub>σ</sub> ln(σ'<sub>v</sub>/P<sub>a</sub>) ≤ 1.1

> C<sub>σ</sub> = 1 / (18.9 – 3.1(V<sub>s1cs</sub>/100)¹˙⁹⁷⁶) ≤ 0.3
>
> **75**

***

## 8.2. NCEER (1997)
The following methods are employed in the NCEER method:
1.  Calculate CRR according to NCEER recommendations.
> CRR = a(V<sub>s1</sub>/100)² + b/(V<sub>s1c</sub> - V<sub>s1</sub>) - b/V<sub>s1c</sub>
>
> **76**
where a = 0.03 and b = 0.9, and
> V<sub>s1cs</sub> = 220 for FC < 5%
> V<sub>s1cs</sub> = 210 for FC < 35%
> V<sub>s1cs</sub> = 200 for all other FC values

2.  Calculate V<sub>s1cs</sub> according to Juang et al, and calculate K<sub>σ</sub> if desired.

## 8.3. Juang et al. (2001) Probabilistic
The Juang et al. (2001) method is outlined below:
1.  Calculate V<sub>s1cs</sub>.
> V<sub>s1cs</sub> = K<sub>fc</sub>V<sub>s1</sub>
>
> **77**
where
> K<sub>fc</sub> = 1, for FC ≤ 5%
> K<sub>fc</sub> = 1 + T(FC – 5) for 5 < FC < 35%
> K<sub>fc</sub> = 1 + 30T for FC ≥ 35%

> T = 0.009 – 0.0109(V<sub>s1</sub>/100) + 0.0038(V<sub>s1</sub>/100)²

2.  Calculate P<sub>L</sub> based on the user-defined Factor of Safety, or calculate CRR based on the user-defined probability of liquefaction.
> ln[ P<sub>L</sub> / (1 - P<sub>L</sub>) ] = 14.8967 – 0.0611V<sub>s1cs</sub> + 2.6418 ln(CSR)
>
> **78**

If the P<sub>L</sub> is calculated, no further calculations are performed. If FS is being calculated based on the CRR, then K<sub>σ</sub> can be calculated.

Tuyệt vời. Dưới đây là kết quả OCR cho các trang tài liệu tiếp theo, được trình bày chính xác theo định dạng Markdown đã thống nhất.

***

# 9. Post-Liquefaction Lateral Displacement
The post-liquefaction lateral spreading is calculated by integrating the maximum shear strain values over depth.
> LDI = ∫<sup>Zmax</sup><sub>0</sub> γ<sub>max</sub> ⋅ dz
>
> **79**

## 9.1. Ground Profile
Zhang et al. (2004) proposed a method for estimating liquefaction-induced lateral displacements based on the ground slope and/or free face height and distance to a free face.

For a gently sloping ground without a free face:
> LD = (S + 0.2) ⋅ LDI
>
> for 0.2% < S < 3.5%
>
> **80**

> LD = 6 ⋅ (L/H)<sup>-0.8</sup> ⋅ LDI
>
> for 4 < L/H < 40
>
> **81**

## 9.2. SPT γ<sub>max</sub> Methods
The following methods are available for calculating the maximum shear strain, when SPT data is used:
*   Zhang, Robertson, and Brachman (2004)
*   Tokimatsu and Yoshimi (1983)
*   Shamato et al. (1998)
*   Wu et al. (1993)
*   Cetin et al. (2009)

### 9.2.1. Zhang, Robertson, and Brachman (2004)
In this method, the relative density (D<sub>r</sub>) is first calculated based on the method selected by the user. The curves shown in the figure below are interpolated to determine the correct maximum shear strain.

***

**Figure 8: Relationship between maximum cyclic shear strain and factor of safety for different relative densities**

***

### 9.2.2. Tokimatsu and Yoshimi (1983)
The curves shown below are interpolated to determine the correct maximum shear strain.

**Figure 9: Shear strain induced by earthquake shaking**

***

### 9.2.3. Shamoto et al. (1998)
For this method, one of three graphs is used to interpolate the maximum shear strain.
For FC < 10%, the graph below is used.

**Figure 10: Relationship between normalized SPT-N value and shear strain potential for clean sands**

***

For FC < 20%, the graph below is used.

**Figure 11: Relationship between normalized SPT-N value and shear strain potential for the case of FC=10%**

***

For FC > 20%, the graph below is used.

**Figure 12: Relationship between normalized SPT-N value and shear strain potential for the case of FC=20%**

***

### 9.2.4. Wu et al. (2003)
The graphs below are interpolated to find the maximum shear strain.

**Figure 13: Estimation of cyclically induced deviatoric strains**

### 9.2.5. Cetin et al. (2009)
The steps for calculating the maximum shear strain according to Cetin et al. (2009) are outlined below.
1.  Calculate K<sub>σ</sub> according to Hynes and Olsen (1999). The formula can be found in Section 6.6.
2.  Calculate the relative density, D<sub>r</sub>, according to the method selected by the user.
3.  Calculate K<sub>mc</sub>.
> K<sub>mc</sub> = -3 × 10⁻⁵ ⋅ D<sub>R</sub>² + 0.0048D<sub>R</sub> + 0.7222
>
> **82**

4.  Calculate CSR<sub>ss201D1</sub>.

***

> CSR<sub>ss,20,1,D,1</sub> = CSR ⋅ K<sub>σ</sub> ⋅ K<sub>mc</sub>
>
> **83**

5.  Calculate γ<sub>max</sub>.
> γ<sub>max</sub> = (-0.025N₁₆₀cs + ln(CSR<sub>ss,20,1,D,1</sub>) + 2.613) / (0.004N₁₆₀cs + 0.001)
>
> **84**

where
5 ≤ N₁₆₀cs ≤ 40; and 0.05 ≤ CSR<sub>ss,20,1,D,1</sub> ≤ 0.6

## 9.3. CPT γ<sub>max</sub> Methods
The following methods are available for calculating the maximum shear strain, when CPT data is used:
*   Zhang, Robertson, and Brachman (2004)
*   Yoshimine (2006)

### 9.3.1. Zhang, Robertson, and Brachman (2004)
The relative density is first calculated according to Tatsuoka et al. (1990).
> D<sub>r</sub> = -85 + 76 log(q<sub>c1N</sub>)
>
> **85**

where q<sub>c1N</sub> ≤ 200.

The graph below is then used to determine γ<sub>max</sub>.

Đã nhận file. Dưới đây là kết quả OCR cho các trang tài liệu tiếp theo, được trình bày chính xác theo định dạng Markdown đã thống nhất.

***

**Figure 14: Relationship between maximum cyclic shear strain and factor of safety for different relative densities**

### 9.3.2. Yoshimine et al. (2006)
The Yoshimine et al. (2006) method is based on F<sub>α</sub> and a limiting shear strain.

> F<sub>α</sub> = -11.74 + 8.34(q<sub>c1Ncs</sub>)<sup>0.264</sup> – 1.371(q<sub>c1Ncs</sub>)<sup>0.528</sup>
>
> **86**

where q<sub>c1Ncs</sub> ≥ 69.

> γ<sub>lim</sub> = 1.859(2.163 – 0.478(q<sub>c1Ncs</sub>)<sup>0.264</sup>)³ ≥ 0
>
> **87**

The maximum shear strain is calculated as follows.

> γ<sub>max</sub> = γ<sub>lim</sub> if FS < F<sub>α</sub>

***

> γ<sub>max</sub> = min( γ<sub>lim</sub>, 0.035(2 – FS)( (1 - F<sub>α</sub>) / (FS - F<sub>α</sub>) ) )
>
> **88**

## 9.4. VST γ<sub>max</sub> Methods
The F<sub>α</sub> and γ<sub>lim</sub> expressions from Yoshimine et al. (2006) and Idriss and Boulanger (2008) were adapted for shear wave velocity by Yi (2010).

> F<sub>α</sub> = 0.032 + 0.836(V<sub>s1cs</sub>/100)<sup>1.976</sup> – 0.190(V<sub>s1cs</sub>/100)<sup>3.952</sup>
>
> **89**

where V<sub>s1cs</sub> ≥ 150 m/s.

> γ<sub>lim</sub> = min[ 0.5, 7.05(V<sub>s1cs</sub>/100)<sup>-5.53</sup> ] ≥ 0
>
> **90**

γ<sub>max</sub> is calculated as follows:

> γ<sub>max</sub> = γ<sub>lim</sub> if FS < F<sub>α</sub>

> γ<sub>max</sub> = min( γ<sub>lim</sub>, 0.035(2 - FS)( (1 - F<sub>α</sub>) / (FS - F<sub>α</sub>) ) )
>
> **91**

***

# 10. Post-Liquefaction Reconsolidation Settlement
The post-liquefaction settlement is calculated by integrating the volumetric strain values over depth.
> S = ∫<sup>Zmax</sup><sub>0</sub> ε<sub>v</sub> ⋅ dz
>
> **92**

## 10.1. SPT ε<sub>v</sub> Methods
The following methods are available for calculating ε<sub>v</sub>, when SPT data is used:
- Ishihara and Yoshimine (1992)
- Tokimatsu and Seed (1984)
- Shamato (1984)
- Wu et al. (2003)
- Cetin et al. (2009)

### 10.1.1. Ishihara and Yoshimine (1992)
The following formulation is used to calculate the volumetric strain:
> ε<sub>v</sub> = 1.5 ⋅ exp(-2.5D<sub>R</sub>) ⋅ min(0.08, γ<sub>max</sub>)
>
> **93**

where D<sub>R</sub> is calculated according to the method specified by the user, and γ<sub>max</sub> is calculated according to Zhang, Robertson, and Brachman (2004).

***

**Figure 15: Ishihara and Yoshimine (1992) method for predicting volumetric and shear strain**

***

### 10.1.2. Tokimatsu and Seed (1984)
The figure below is used to interpolate a value of ε<sub>v</sub>.

**Figure 16: Relationship between CSR, N₁₆₀, and volumetric strain**

***

### 10.1.3. Shamoto (1984)
One of three graphs is used to find ε<sub>v</sub>.

For FC<10%:

**Figure 17: Relationship between normalized SPT-N, dynamic shear stress ratio, and volumetric strain for clean sands**

***

For FC<20%:

**Figure 18: Relationship between normalized SPT-N, dynamic shear stress ratio, and volumetric strain for FC=10%**

***

For other fine content values:

**Figure 19: Relationship between normalized SPT-N, dynamic shear stress ratio, and volumetric strain for FC=20%**

Tuyệt vời. Đây là kết quả OCR cho các trang tài liệu cuối cùng, được trình bày chính xác theo định dạng Markdown đã thống nhất.

***

### 10.1.4. Wu et al. (2003)
The following graph is used to find ε<sub>v</sub>.

**Figure 20: Correlations between CSR, N<sub>1,60,cs</sub>, and reconsolidation volumetric strain (Wu et al., 2003)**

### 10.1.5. Cetin et al. (2009)
The Cetin et al. (2009) method incorporates a depth factor. With the depth factor, the contribution of layers to settlement at the surface decreases as the depth of the layer increases, and beyond a certain depth (z<sub>cr</sub>) the settlement of an individual layer cannot be traced at the ground level. It was determined that the threshold depth is 18m.

The steps for calculating the maximum shear strain according to Cetin et al. (2009) are outlined below:
1.  Calculate K<sub>σ</sub> according to Hynes and Olsen (1999).
2.  Calculate relative density, D<sub>r</sub>, according to the method selected by the user.
3.  Calculate K<sub>mc</sub>, and CSR<sub>ss,20,1,D,1</sub>.

> K<sub>mc</sub> = -3 × 10⁻⁵ ⋅ D<sub>R</sub>² + 0.0048D<sub>R</sub> + 0.7222

> CSR<sub>ss,20,1,D,1</sub> = CSR ⋅ K<sub>σ</sub> ⋅ K<sub>mc</sub>

***

4.  Calculate the critical depth factor, DF.
> DF = 1 - z / z<sub>critical</sub>
>
> **94**
>
> where z<sub>critical</sub> = 18 m.
>
> **95**

5.  Calculate ε<sub>v</sub>, corrected for depth.
> ε<sub>v0</sub> = 1.879 ln( (780.416 ln(CSR<sub>ss,20,1,D,1</sub>) - N<sub>1,60cs</sub> + 2442.465) / (636.613N<sub>1,60cs</sub> + 306.732) ) + 5.583
>
> **96**

> ε<sub>v</sub> = DF ⋅ ε<sub>v0</sub>
>
> **97**

where the following limits apply:
5 ≤ N<sub>1,60cs</sub> ≤ 40; 0.05 ≤ CSR<sub>ss,20,1,D,1</sub> ≤ 0.60; 0% ≤ ε<sub>v</sub> ≤ 5%

Note that it is left to the user to determine the normalized settlement.

### 10.1.6. Dry Sand settlement, Pradel (1998)
Procedure to evaluating earthquake induced settlement in dry sandy soils (Pradel, 1998) in Settle3 is explained by the following steps.

1.  **Determination of cyclic shear stress**
    Cyclic strains are induced in the ground during an earthquake. The following expression proposed by Seed and Idriss (1971) shows average cyclic shear stress which is a good approximation of dry sand deposits.
    > τ<sub>av</sub> = 0.65 * (a<sub>max</sub>/g) * ρ * z * (1 / (1 + (z/z₀)²))
    >
    > **98**
    Where ρ is the unit weight of the material, z is the depth of soil layer, and z₀ is a constant which equals to 30.5m (100 ft).

2.  **Maximum shear modulus**

***

The maximum shear modulus is obtained by field and laboratory tests. Gmax can be approximated by the standard penetration test using examples provided by Seed and Idriss (1970)
> G<sub>max</sub> = 447 * p₀ * (N₁)<sup>1/3</sup> * √(p/p₀)
>
> **99**

Where p is the average stress,
p₀ is a reference stress = 1 tsf (95.76 kPa),
N₁ is the SPT N value normalized to effective overburden of 1 tsf (95.76 kPa), effective of 60% of free-fall energy.

For a dry sand with friction angle of 30°, the lateral stress coefficient of at-rest pressures, K₀ is approximately 0.5. The average stress p then can be approximated by:
> p = ((1 + 2 * K₀)/3) * ρ * z = 0.67 * ρ * z

3.  **Cyclic shear strain**
    The cyclic shear strain induced in the soil can be determined by:
    > γ = τ<sub>av</sub> / (G<sub>max</sub> * (G/G<sub>max</sub>))
    >
    > **100**
    Where G<sub>max</sub> can be obtained from Seed and Idriss (1970):
    > G<sub>max</sub> = 447 * p₀ * (N₁)<sup>1/3</sup> * √(p/p₀)
    >
    > **101**
    However, this cyclic shear strain requires iteration process in obtaining equivalent shear modulus until shear modulus curve reaches previously assumed strain. Thus, estimate of shear strain obtained from experimental study by Iwasaki et al (1978) is used:
    > γ = ( (1 + a * e<sup>b * (τ<sub>av</sub>/G<sub>max</sub>)</sup>) * (τ<sub>av</sub>/G<sub>max</sub>) ) / (1 + a)

***

Where a = 0.0389 * (p/p₀) + 0.124
> b = 6400 * (p/p₀)⁻⁰.⁶
>
> **102**

Note the use of different G/G<sub>max</sub> versus γ curve may result in significantly different settlement prediction.

4.  **Volumetric strain**
    ε₁₅ is the 15 equivalent uniform strain cycle (N=15) which corresponds to 7.5 magnitude earthquake given in percentage,
    > ε₁₅ = γ * (N<sub>c</sub>/20)⁻¹.²
    >
    > **103**
    This leads to estimated volumetric strain ratio where:
    > ε<sub>NC</sub> = ε₁₅ * (N<sub>c</sub>/15)⁰.⁴⁵
    >
    > **104**
    N<sub>c</sub> is the equivalent number of cycles expressed by the following expression:
    > N<sub>c</sub> = (M – 4)².¹⁷
    >
    > **105**
    Where Settle3 takes earthquake magnitude from the liquefaction option dialog and calculates Nc. Then, factor of 2 is multiplied to the volumetric strain for taking account of multidirectional nature of earthquake shaking (Pradel 1998, equation (11)).

***

## 10.2. CPT ε<sub>v</sub> Methods
When CPT input data is used, the strain is calculated according to Yoshimine et al. (2006).
> ε<sub>v</sub> = 1.5 ⋅ exp(2.551 – 1.147(q<sub>c1Ncs</sub>)⁰.²⁶⁴) ⋅ min(0.08, γ<sub>max</sub>)
>
> **106**

where γ<sub>max</sub> is calculated using the Yoshimine et al. (2006) formulation.

***

## 10.3. VST ε<sub>v</sub> Methods
Yi (2010) adapted Ishihara and Yoshimine (1992) for V<sub>s</sub> data, and the following formulation for reconsolidation strain is used.
> ε<sub>v</sub> = 1.5 ⋅ exp(-0.449(V<sub>s1cs</sub>/100)¹˙⁹⁷⁶) ⋅ min(0.08, γ<sub>max</sub>)
>
> **107**

***

# 11. References
Andrus, R., Stokoe, K. H. (1997), "Liquefaction Resistance Based on Shear Wave Velocity", Proceedings of NCEER Workshop on Evaluation of Liquefaction Resistance of Soils.

Boulanger, R. W., (2003a). "Relating Kα to relative state parameter index." J. Geotechnical and Geoenvironmental Eng., ASCE 129(8), 770-73.

Boulanger, R. W., and Idriss, I. M. (2004). "State normalization of penetration resistances and the effect of overburden stress on liquefaction resistance." Proc., 11th Intl. Conf. on Soil Dynamics and Earthquake Engineering, and 3rd Intl. Conf. on Earthquake Geotechnical Engineering, Doolin et al., eds, Stallion Press, Vol. 2, pp. 484-491.

Cetin, K. O., and Bilge, H. T. (2012) “Performance-based assessment of magnitude (duration) scaling factors." J. Geotech. Geoenviron. Eng., 138(3), 324–334.

Cetin, K. O., Bilge, H. T., Wu, J., Kammerer, A. M., and Seed, R. B. (2009). “Probabilistic models for cyclic straining of saturated clean sands." J. Geotech. Geoenviron. Eng., 135(3), 371-386.

Cetin, K. O., Bilge, H. T., Wu, J., Kammerer, A. M., and Seed, R. B. (2009). “Probabilistic Model for the Assessment of Cyclically Induced Reconsolidation (Volumetric) Settlements.” J. Geotech. Geoenviron. Eng., 135(3), 387-398.

Cetin K.O., Seed R.B., Der Kiureghian A., Tokimatsu K., Harder L.F. Jr, Kayen R.E., MossR.E.S. (2004), "SPT-based probabilistic and deterministic assessment of seismic soil liquefaction potential", Journal of Geotechnical and Geoenvironmental Engineering, ASCE, 130(12), 1314-1340.

Hynes, M. E., and Olsen, R. S. (1999), “Influence of confining stress on liquefaction resistance.” Proc., Int. Workshop on Phys. And Mech. Of Soil Liquefaction, Balkema, Rotterdam, The Netherlands, 145-152.

Idriss I. M., 1999, "An update to the Seed-Idriss simplified procedure for evaluating liquefaction potential in Proceedings, TRB Workshop on New Approaches to Liquefaction, Publication No. FHWA-RD-99-165, Federal Highway Administration, January.

I. M. Idriss and R. W. Boulanger, ""Estimating Kα for use in evaluating cyclic resistance of sloping ground." Proc. 8th US Japan Workshop on Earthquake Resistant Design of Lifeline Facilities and Countermeasures against Liquefaction, Hamada, O'Rourke, and Bardet, eds., Report MCEER-03-0003, MCEER, SUNY Buffalo, N.Υ., 2003, 449-468.

***

Idriss IM, Boulanger RW., Semi-empirical procedures for evaluating liquefaction potential during earthquakes. Proc., 11th International conference on soil dynamics and earthquake engineering, and 3rd International conference on earthquake geotechnical engineering, vol. 1. Stallion Press; 2004. p. 32–56.

Idriss, I. M., and Boulanger, R. W. (2008). Soil liquefaction during earthquakes. Monograph MNO-12, Earthquake Engineering Research Institute, Oakland, CA, 261 pp.

Ishihara, K. (1977), "Simple Method of Analysis for Liquefaction of Sand Deposits During Earthquakes", Soils and Foundations, Vol. 17, No. 3, September 1977, pp. 1-17.

Ishihara, K., Shimuzu, K., and Yamada, Y. (1981), “Pore Water Pressures Measured in Sand Deposits During an Earthquake", Soils and Foundations, Vol. 21, No. 4, pp. 85-100.

Ishihara, K., and Yoshimine, M. _1992_. “Evaluation of settlements in sand deposits following liquefaction during earthquakes.” Soils Found., 32(1), 173-188.

JRA (1990), Specification for Highway Bridges: Part V- Seismic Design. Japan Road Association, Tokyo.

Juang, C. H., Fang, S. Y., Khor, E. H. (2006) “First-Order Reliability Method for Probabilistic Liquefaction Triggering Analysis Using CPT”, J. Geotech. Geoenviron. Eng., 132(3), 337-350.

Kayen, R. E, Mitchell, J. K., Seed, R. B.' Lodge, A., Nishio, S., and Coutinho, R. (1992), "Evaluation of SPT-, CPT-, and shear wave-based methods for liquefaction potential assessment using Loma Prieta data", Proc., 4th Japan-U.S. Workshop on Earthquake-Resistant Des. Of Lifeline Fac. And Counterneasures for Soil Liquefaction, Vol. 1, 177-204.

Liao, S. S. C., Veneziano, D., Whitman, R.V. (1988), "Regression Models for Evaluating Liquefaction Probability", Journal of Geotechnical Engineering, ASCE, Vol. 114, No. 4, pp. 389-409.

Liao, S.S.C. and Whitman, R.V. (1986a). "Overburden Correction Factors for SPT in Sand" Journal of Geotechnical Engineering, Vol. 112, No. 3, p. 373 - 377.

Liao, S.S.C. and Whitman, R.V. (1986b). "Catalogue of A Liquefaction and Non-Liquefaction Occurrences During Earthquakes" Research Report, Dept. of Civil Engineering, M.I.T., Cambridge, MA.

Tuyệt vời. Đây là kết quả OCR cho các trang tài liệu cuối cùng, được trình bày chính xác theo định dạng Markdown đã thống nhất.

***

Meyerhof, G. G., 1957. Discussion on research on determining the density of sands by spoon penetration testing, in Proceedings, 4<sup>th</sup> International Conference on Soil Mechanics and Foundation Engineering, London, Vol. 3, p.110.

Moss, R. S. E, Seed, R. B., KAyen, R. E., Stewart, J. P., Der Kiureghian A., Cetin, K. O. (2006) “CPT-Based Probabilistic and Deterministic Assessment of In Situ Seismic Soil Liquefaction Potential", J. Geotech. Geoenviron. Eng., 132(8), 1032-1051.

NCEER, 1997, "Proceedings of the NCEER Workshop on Evaluation of Liquefaction Resistance of Soils", Edited by Youd, T. L., Idriss, I. M., Technical Report No. NCEER-97-0022, December 31, 1997.

Peck, R B Hanson, W E & Thornburn, T H (1974) Foundation engineering Pub: John Wiley, New York

Pradel D. (1998), "Procedure to evaluate earthquake-induced settlements in dry sandy soils". *Journal of Geotechnical and Geoenvironmental Engineering ASCE*. Vol 124 Issue 4.

Robertson, P. K., Wride (Fear), C. E.,(1998) “Evaluating cyclic liquefaction potential using the cone penetration test", Can. Geotech. J. **35**: 442–459 (1998).

Seed, H. B., Idriss, I. M. (1971), “Simplified Procedure for Evaluating Soil Liquefaction Potential", Journal of the Soil Mechanics and Foundations Division, ASCE, Vol. 97, No SM9, Proc. Paper 8371, September 1971, pp. 1249-1273.

Seed, H. B., Idriss, I. M. (1982), "Ground Motions and Soil Liquefaction During Earthquakes", Earthquake Engineering Research Institute Monograph Series.

Seed, H. B., Idriss, I. M., Arango, I. (1983), "Evaluation of Liquefaction Potential Using Field Performance Data", Journal of Geotechnical Engineering, ASCE, Vol. 109, No. 3, pp. 458-482.

Seed, H. B., Tokimatsu, K., Harder, L. F., Chung, R. M. (1984), "The Influence of SPT Procedures in Soil Liquefaction Resistance Evaluations", Earthquake Engineering Research Center Report No. UCB/EERC-84/15, University of California at Berkeley, October, 1984.

Shamoto, Y., Zhang, J., and Tokimatsu, K. (1998). “New charts for predicting large residual post-liquefaction ground deformation.” Soil Dyn. Earthquake Eng., *17_7–8_*, 427–438.

***

Skempton, A.W. 1986. Standard penetration test procedures and the effects in sands of overburden pressure, relative density, particle size, ageing and overconsolidation. Geotechnique 36(3): 425-447.

Tokimatsu, K., and Seed, H. B. _1984_. "Simplified procedures of the evaluation of settlements in clean sands." Rep. No. UCB/GT-84/16, Univ. of California, Berkeley, Calif.

Tokimatsu, K., and Seed, H. B., 1987. Evaluation of settlements in sands due to earthquake shaking, J. Geotechnical Eng., ASCE 113 (GT8), 861-78.

Wu, J., Seed, R. B., and Pestana, J. M. (2003). "Liquefaction triggering and post liquefaction deformations of Monterey 0/30 sand under unidirectional cyclic simple shear loading." Geotechnical Engineering Research Rep. No. UCB/GE-2003/01, Univ. of California, Berkeley, Calif.

Youd, T. L., Hansen, C. M., and Bartlett, S. F., 2002. Revised Multilinear regression equations for prediction of lateral spread displacement, J. Geotechnical and Geoenvironmental Eng. 128(12),1007-017.

Youd, T. L., Idriss, I. M., Andrus, R. D., Arango, I., Castro, G., Christian, J. T., Dobry, E., Finn, W. D. L., Harder Jr., L. F., Hynes, M. E., Ishihara, K., Koester, J. 169 P., Liao, S. S. C., Marcusson III, W. F., Martin, G. R., Mtchell, J. K., Moriwaki, Y., Power, M. S., Robertson, P. K., Seed, R. B., and Stokoe II, K. H. (2001). "Liquefaction resistance of soils: Summary report from the 1966 NCEER and 1998 NCEER/NSF workshops on evaluation of liquefaction resistance of soils" J. Geotechnical and Geoenvironmental Eng., 124(10), 817-833.

Youd, T. L., Noble, S. K. (1997), "Liquefaction Criteria Based on Statistical and Probabilistic Analyses", Proceedings of the NCEER Workshop on Evaluation of Liquefaction Resistance of Soils, December 31, 1997, pp. 201-205.

G. Zhang; P. K. Robertson, M.ASCE; and R. W. I. Brachman (2004). “Estimating Liquefaction-Induced Lateral Displacements Using the Standard Penetration Test or Cone Penetration Test, J. Geotechnical and Geoenvironmental Eng. 130(8), 861-871.