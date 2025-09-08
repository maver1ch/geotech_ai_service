
## Settle3

# CPT Data Interpretation

### Theory Manual

© 2025 Rocscience Inc.

***

# Table of Contents

1.  **Introduction** ............................................................................................................................................. 4
2.  **Soil Parameter Interpretation**.............................................................................................................. 6
    2.1. Corrected Cone Resistance, qt ........................................................................................................ 6
    2.2. Friction Ratio, R<sub>f</sub>................................................................................................................................ 6
    2.3. Soil Unit Weight, γ ............................................................................................................................ 6
    2.4. Total and Effective Overburden Stress, σ<sub>ν0</sub> and σ'<sub>ν0</sub> ........................................................................ 7
    2.5. Pre-consolidation Stress .................................................................................................................. 7
    2.6. Normalized Cone Resistance, Q<sub>t</sub> ..................................................................................................... 7
    2.7. Normalized Pore Pressure Ratio, B<sub>q</sub>................................................................................................. 8
    2.8. Equilibrium pore pressure, u<sub>o</sub>.......................................................................................................... 8
    2.9. Normalized Friction Ratio, F<sub>r</sub> ............................................................................................................ 8
    2.10. Soil Behaviour Type Index, I<sub>c</sub> ........................................................................................................... 8
    2.11. Shear Wave Velocity ........................................................................................................................ 8
    2.12. Maximum Shear Modulus,............................................................................................................... 9
    2.13. Equivalent SPT N<sub>60</sub> .......................................................................................................................... 9
    2.14. Hydraulic Conductivity, k.................................................................................................................. 9
    2.15. Normalized Cone Resistance, Q<sub>tn</sub> .................................................................................................. 10
    2.16. Friction Angle, φ' ............................................................................................................................ 10
    2.17. Overconsolidation Ratio, OCR ....................................................................................................... 10
    2.18. Insitu Lateral Stress Coefficient, K<sub>o</sub> ............................................................................................... 11
    2.19. Relative Density, D<sub>r</sub> ........................................................................................................................ 11
    2.20. Undrained Shear Strength, s<sub>u</sub> ........................................................................................................ 11
    2.20.1. Undrained shear strength (Mayne 2015)........................................................................ 12
    2.20.2. Undrained shear strength (Moon 2018) ....................................................................... 12
    2.21. Soil Sensitivity, S<sub>t</sub>............................................................................................................................ 12
    2.22. Fines Content, FC ........................................................................................................................... 12
    2.23. Young's Modulus, E ....................................................................................................................... 13
    2.24. Constrained Modulus, M ............................................................................................................... 13
    2.25. Plasticity index and liquid limit....................................................................................................... 13
    2.26. Coefficient of consolidation (Robertson 2015)............................................................................ 14
    2.27. Coefficient of consolidation .......................................................................................................... 14
    2.28. Recompression Index (Cr) .............................................................................................................. 15

***
2.29. Compression Index (Cc).................................................................................................................. 15
2.30. Secondary compression Index (Cae).............................................................................................. 15
3.  **Soil Profiling**.......................................................................................................................................... 16
    3.1. Non-Normalized SBT Charts............................................................................................................ 16
    3.2. Normalized SBT<sub>n</sub> Charts .................................................................................................................. 19
    3.2.1. Robertson (1990)................................................................................................................. 19
    3.2.2. Schneider et al. (2008) ........................................................................................................ 20
4.  **Filtering of CPT Data** ........................................................................................................................... 22
5.  **References**............................................................................................................................................. 23


***
# 1. Introduction

The Cone Penetration Test allows for a continuous soil profile and can collect up to 5 independent readings in a single sounding. These readings, notably the cone tip resistance (q_c), sleeve friction (f_s), and penetration pore water pressure (u_2) are interpreted to give the soil parameters used to asses subsurface stratigraphy.

Note that *Settle3* assumes that all reading of penetration pore water pressure are u_2.

The empirical correlations in the CPT engine vary in terms of their reliability and applicability, and it is important to understand the degree to which the derived soil parameters can be used. The CPT Guide (2015) presents a table which shows estimates of the perceived applicability of the CPTu to estimate soil parameters.

**Table 1: Perceived applicability of CPTu for deriving soil parameters (from CPT Guide 6th Ed. (2015))**
| Soil Type | D_r | ψ | K_₀ | OCR | S_t | s_u | φ' * | E, G | M | G_₀ * | K | C_ₕ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Coarse-grained (sand) | 2-3 | 2-3 | 5 | 5 | | | | 2-3 | 2-3 | 2-3 | 2-3 | 3-4 | 3-4 |
| Fine-grained (clay) | | | 2 | 1 | 2 | 1-2 | 4 | 2-4 | 2-3 | 2-4 | 2-3 | 2-3 |

1 = high; 2 = high to moderate; 3 = moderate; 4 = moderate to low; 5 = low reliability; Blank = no applicability; \*improved with SCPT

Where:

D_r &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; relative density  
ψ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; state parameter  
E, G &nbsp;&nbsp;&nbsp;&nbsp; Young's and shear moduli  
OCR &nbsp;&nbsp;&nbsp;&nbsp; overconsolidation ratio  
s_u &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; undrained shear strength  
C_h &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; coefficient of consolidation


***
φ' &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; peak friction angle  
K_₀ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; in-situ stress ratio  
G_₀ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; small strain shear modulus  
M &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 1D compressibility  
S_t &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; sensitivity  
K &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; permeability

In terms of units, CPT data can be input into Settle3 in either Metric or Imperial units. The conventions for each are summarized in the table below.

| Unit System | Depth | qc | fs | u2 |
| :--- | :--- | :--- | :--- | :--- |
| **SI** | m | MPa | kPa | kPa |
| **Imperial** | ft | tsf | tsf | psi |

***

# 2. Soil Parameter Interpretation

As mentioned in the Introduction, the CPT calculations are based on empirical correlations. Be sure to refer to the table of reliability and applicability.

### 2.1. Corrected Cone Resistance, q_t

The corrected cone resistance, q_t, is calculated as:

> q_t = q_c + u₂(1 - a)

where

*a* &nbsp;&nbsp;&nbsp; = net area ratio.

In the absence of u_2, q_c = q_t.

### 2.2. Friction Ratio, R_f

The friction ratio is defined as the percentage of sleeve friction, f_s, to cone resistance, q_c, at the same depth.

> R_f = (f_s/q_t) ⋅ 100%

### 2.3. Soil Unit Weight, γ

The following relationship from Robertson expresses the soil unit weight in terms of the friction ratio and cone resistance (Robertson, 2010).

> γ/γ_w = 0.27(log R_f) + 0.36[log(q_t/P_a)] + 1.236

where

R_f &nbsp;&nbsp;&nbsp;&nbsp; = friction ratio  
γ_w &nbsp;&nbsp;&nbsp; = unit weight of water  
P_a &nbsp;&nbsp;&nbsp;&nbsp; = atmospheric pressure


***
### 2.4. Total and Effective Overburden Stress, σ_v0 and σ'_v0

The total and effective overburden stresses are calculated using the calculated soil unit weight for each depth.

> σ_v0 = Σ(z_i ⋅ γ_i)

> σ'_v0 = σ_v0 - u

where

γ_i &nbsp;&nbsp;&nbsp; = soil unit weight of the i-th layer  
z_i &nbsp;&nbsp;&nbsp; = depth of the i-th layer from the ground surface

### 2.5. Pre-consolidation Stress

Preconsolidation stress is calculated based on the expression below by Mayne (2012):

> σ'_p = 0.33(q_t - σ_v0)m'(P_a/100)^(1-m')

Where

Pa is the atmospheric pressure,
m' is the exponent for the consolidation given by the expression:

> m' = 1 - ( 0.28 / (1 + (I_c/2.65)^1.25) )

Ic is the soil behavior type index described below in the theory manual.

### 2.6. Normalized Cone Resistance, Q_t

> Q_t = (q_t - σ_v0)/σ'_v0



***
### 2.7. Normalized Pore Pressure Ratio, B_q

The normalized pore pressure ratio, B_q, is the difference in measured and equilibrium pore pressures, normalized with respect to the net cone resistance.

> B_q = Δu/q_n

where

Δu &nbsp;&nbsp;&nbsp; = u₂ - u₀  
q_n &nbsp;&nbsp;&nbsp; = q_t - σ_v0

### 2.8. Equilibrium pore pressure, u_o

The equilibrium pore pressure is calculated based on water table depth.

### 2.9. Normalized Friction Ratio, F_r

> F_r = [f_s/(q_t - σ_v0)] ⋅ 100%

### 2.10. Soil Behaviour Type Index, I_c

The soil behavior type index can be thought of as a representative value that combines Q_t and F_r to produce concentric circles delineating Robertson's 1990 SBT chart zones. I_c expresses the radius of those concentric circles.

> I_c = ((3.47 – log Q_t)² + (log F_r + 1.22)²)⁰.⁵

### 2.11. Shear Wave Velocity

There are two ways to correlate shear wave velocity with CPT cone resistance. Robertson (2009) calculates shear wave velocity using soil type and SBT I_c.

> V_s = [α_vs(q_t - σ_v)/P_a]⁰.⁵ (m/s)


***

where

> α_vs = 10^(0.55I_c+1.68)

Mayne (2006) proposed the correlation below, where V_s is a function of the logarithm of f_s.

> V_s = 51.6 ln f_s + 18.5

### 2.12. Maximum Shear Modulus,

The small strain shear modulus, G_o, can be calculated as:

> G_o = (γ/g) ⋅ V_s²

### 2.13. Equivalent SPT N₆₀

Before the CPT came into popularity, the Standard Penetration Test was the standard soil test. The SPT, while used less frequently, is still used today. There have been many attempts by researchers to relate the SPT N value to the CPT cone penetration resistance q_c.

Jefferies and Davies (1993) suggested the following relationship, which correlates (q_c/P_a)/N₆₀ to I_c.

> (q_t/P_a) / N₆₀ = 8.5 (1 - I_c / 4.6)

### 2.14. Hydraulic Conductivity, k

The soil hydraulic conductivity or coefficient of permeability can be approximately estimated using the following equations:

> k = 10^(0.952-3.04I_c) for I_c ≤ 3.27

> k = 10^(-4.52-1.37I_c) otherwise


***

### 2.15. Normalized Cone Resistance, Q_tn

The cone resistance can be expressed in a non-dimensional form, normalized for the in-situ vertical stress with the stress exponent, *n*, varying with soil type and stress level. When n=1, Q_tn = Q_t.

> n = 0.381I_c + 0.05(σ'_v0/P_a) - 0.15

> Q_tn = ((q_t - σ_v0) / P_a) (P_a / σ'_v0)^n

### 2.16. Friction Angle, φ'

There are several correlations relating friction angle, φ', to CPT parameters. Robertson and Campanella (1983) suggested the correlation below for estimating the peak friction angle for sands, where φ' is in radians.

> tan φ' = [1 / 2.68] [log(q_c / σ'_v0) + 0.29]

Kulhawy and Mayne (1990) suggested an alternate relationship for clean sands.

> φ' = 17.6 + 11 log Q_tn

Finally, for fine-grained soils, Mayne (2006) recommends the following correlation:

> φ'(deg) = 29.5 ⋅ B_q^0.121 [0.256 + 0.336B_q + log Q_t]

### 2.17. Overconsolidation Ratio, OCR

The overconsolidation ratio is defined as the ratio of the highest stress the soil has experienced to the current stress in the soil. Robertson (2009) proposed the following equation:

> OCR = 0.25Q_t^1.25


***

### 2.18. Insitu Lateral Stress Coefficient, K_o

Kulhawy and Mayne (1990) proposed the following equation for K_o, in terms of both the horizontal stress index K_D and the normalized cone tip resistance.

> K_o = 0.1 ⋅ (q_t - σ_v0) / σ'_v0

> K_o = 0.359 + 0.071 ⋅ K_D - 0.00093 ⋅ (q_c/σ'_v0)

where

> K_D = 2 ⋅ (OCR_sand)^1.56

> OCR_sand = [ 0.192 ⋅ (q_t/P_a)^0.22 / ((1 - sin φ') ⋅ (σ'_v0/P_a)^0.31) ]^(1 / (sin φ' - 0.27))

### 2.19. Relative Density, D_r

Jamiolkowski et al. (2001) proposed the following equation for relative density of sands.

> D_r = 100 ⋅ [0.268 ⋅ ln(q_t1) - b_x]

where

> q_t1 = (q_t/P_a) / (σ'_v0/P_a)^0.5 and b_x = 0.675.

### 2.20. Undrained Shear Strength, s_u

No single value of undrained shear strength exists, since it is dependent on the direction of loading, soil anisotropy, strain rate, and stress history. A number of theoretical solutions have been developed, and are all of the form shown below.

> s_u = (q_t - σ_v) / N_kt


***

In general, N_kt varies from 10 to 18. Settle3 uses N_kt = 14. Note that for SBT 1986 chart with classification of 5 or less will be used in Settle3 for calculating the undrained shear strength. Settle3 does not provide undrained shear strength calculation for SBT classification beyond 5.

There are two additional methods Settle3 calculates undrained shear strength: shear strength based on Mayne 2015, and Moon 2018.

#### 2.20.1. Undrained shear strength (Mayne 2015)

This method allows users to calculate shear strength based on the following equation provided by Remai (2013) for empirical cone factor:

> N_Δu = 24.3 * (u₂ - u₀)/(q_t - σ_v0)

Then, this empirical cone factor is used for calculating shear strength equation with the Mayne 2015.

> s_u = (u₂ - u₀) / N_Δu

#### 2.20.2. Undrained shear strength (Moon 2018)

Moon 2018 has proposed a correlation of shear strength, Su, with shear wave velocity Vs, and OCR.

> s_u = 0.114 * V_s^1.18 * OCR^0.15

### 2.21. Soil Sensitivity, s_t

The sensitivity of clay is defined as the ratio of the undisturbed peak undrained shear strength to the remolded undrained shear strength. The remolded undrained shear strength can be assumed to be equal to the sleeve resistance, f_s.

> s_t = s_u / f_s

### 2.22. Fines Content, FC

Davies (1999) suggested the following linear relationship for determining fines content:


***

> FC (%) = 42.4179I_c – 54.8574

### 2.23. Young's Modulus, E

The Young's modulus is calculated as:

> α_E = 0.015[10^(0.55I_c+1.68)]

> E = α_E(q_t - σ_v0)

### 2.24. Constrained Modulus, M

The constrained modulus can be estimated from CPT results using the following relationship:

> M = α_M(q_t - σ_v0)

Robertson (2009) suggested values for α_M which vary with Q_t.

When I_c > 2.2 (fine-grained soils):

> α_M = Q_t when Q_t < 14
>
> α_M = 14 when Q_t > 14

When I_c < 2.2 (coarse-grained soils):

> α_M = 0.0188[10^(0.55I_c+1.68)]

### 2.25. Plasticity index and liquid limit

Cetin and Ozan (2009) has provided correlation of CPT analysis results with plasticity index and liquid limit as the following expression below:

> P_I = 10^((2.37 + 1.33*log10(F_r) - log10(qt1net))/2.25)

---

***

> L_L = 10^(((3.79 + 0.79*log10(F_r) - log10(qt1net)))/2.52)

Where P_I is the plasticity index and L_L is the liquid limit index in Settle3.

More description of the parameters within P_I and L_L functions are:

where F_r is the friction ratio,
qt1net = ((qt\*1000 -σ_v) / (σ'/Pa)^((n1 - 272.38)/2.81)))/1000 in MPa
qt is the corrected cone resistance,
σ_v is the total overburden stress, and σ' is the effective stress.
Pa is the atmospheric pressure.

### 2.26. Coefficient of consolidation (Robertson 2015)

The coefficient of consolidation for this method is calculated as the following in Robertson (2015).

> c_v = kM / γ_w

Where
M is the 1-D constrained modulus
*k* is the hydraulic conductivity (calculated with Ic, shown above)
And γ_w is the unit weight of water.

Note c_v values may vary by orders of magnitude (Robertson 2015). We have also capped the value of c_v based on estimated range of coefficient of consolidation for variety of soil types (Roberson et al. 2011).

### 2.27. Coefficient of consolidation

The coefficient of consolidation is calculated based on t50 data by The and Houlsby (1988) method outlined in Mayne (2015).

> c_h = (T\*a²√I_R) / t₅₀

There are several constants that is used in Settle3:
T\* = 0.245 for shoulder position.


***

a = 1.78 cm (assuming 10cm² cone),
t50 is time data taken from Chai et al (2004). If the CPT data has less data than the defined t50 data, then Settle3 will fill zeros for the rest of the data.

### 2.28. Recompression Index (Cr)

The recompression index, Cr, is calculated based on the prediction of recompression index using GMDH-type neural network based on geotechnical soil properties (Kordnaeij et al. 2015) in equation (10) of Table 1.

> C_r = 0.0007LL + 0.0062

Where LL is the liquid limit index in Settle3.

### 2.29. Compression Index (Cc)

The compression index, Cc, is calculated in Settle3 based on estimation from correlation of plasticity index and compression index of soil (Jain et al. 2015) in equation 8.

> C_c = 0.014(PI + 3.6)

### 2.30. Secondary compression Index (Cae)

The secondary compression index is calculated in Settle3 based on equation presented by Tonni and Simonini (2012).

---

***

# 3. Soil Profiling

One of the greatest advantages of the CPT is its ability to provide a continuous soil profile with minimum error. Conclusions about soil type can be drawn from the CPT data. The following options are available in Settle3.

*   Non-normalized CPT Soil Behaviour Type (SBT) Chart
    *   Robertson et al. (1986)
    *   Robertson (2010)
*   Normalized CPT Soil Behaviour Type (SBT_n) Chart
    *   Robertson (1990)
    *   Robertson (2010)
    *   Schneider et al. (2008)

### 3.1. Non-Normalized SBT Charts

The Robertson et al. (1986) SBT chart, updated in Robertson (2010), is the most commonly used soil behavior type chart. The Robertson et al. (1986) chart uses the corrected cone resistance, q_t, and the friction ratio, R_f, and has 12 soil types.

Robertson (2010) provides an update in terms of dimensionless cone resistance q_c/P_a and R_f on log scales. It also reduces the number of soil behavior types to 9, matching the Robertson (1990) chart. The table below summarizes the unification of the 12 soil types to the 9 Robertson (1990) soil types.

| SBT zone <br> Robertson et al. (1986) | SBT_n zone <br> Robertson (1990) | Common SBT description |
| :--- | :--- | :--- |
| 1 | 1 | Sensitive fine-grained |
| 2 | 2 | Clay – organic soil |
| 3 | 3 | Clays – clay to silty clay |
| 4 & 5 | 4 | Silt mixtures – clayey silt & silty clay |
| 6 & 7 | 5 | Sand mixtures – silty sand to sandy silt |
| 8 | 6 | Sands – clean sands to silty sands |
| 9 & 10 | 7 | Dense sand to gravelly sand |
| 12 | 8 | Stiff sand to clayey sand* |

---



***

| 11 | 9 | Stiff fine-grained* |
| :--- | :--- | :--- |
<td colspan=3>\* overconsolidated or cemented</td>

| Zone | Soil Behavior Type |
| :--- | :--- |
| 1 | Sensitive fine grained |
| 2 | Organic material |
| 3 | Clay |
| 4 | Silty Clay to clay |
| 5 | Clayey silt to silty clay |
| 6 | Sandy silt to clayey silt |
| 7 | Silty sand to sandy silt |
| 8 | Sand to silty sand |
| 9 | Sand |
| 10 | Gravelly sand to sand |
| 11 | Very stiff fine grained\* |
| 12 | Sand to clayey sand\* |
| \* Overconsolidated or cemented | |

Figure 1: SBT chart by Robertson et al. (1986) based on q_t and R_f

---


***

| Zone | Soil Behaviour Type (SBT) |
| :--- | :--- |
| 1 | Sensitive fine-grained |
| 2 | Clay - organic soil |
| 3 | Clays: clay to silty clay |
| 4 | Silt mixtures: clayey silt & silty clay |
| 5 | Sand mixtures: silty sand to sandy silt |
| 6 | Sands: clean sands to silty sands |
| 7 | Dense sand to gravelly sand |
| 8 | Stiff sand to clayey sand\* |
| 9 | Stiff fine-grained\* |
| \* Overconsolidated or cemented | |

Figure 2: Updated non-normalized SBT chart based on q_c/P_a and R_f (Robertson, 2010)

---


***

### 3.2. Normalized SBT_n Charts
Using normalized parameters is beneficial since both the penetration and sleeve resistances increase with depth due to the increase in effective overburden stress. Normalization is often required for very shallow and very deep soundings.

#### 3.2.1. Robertson (1990)

*(Lưu ý: Phần hình ảnh của biểu đồ không được OCR, chỉ phần chú thích được OCR lại)*

**Chú thích cho biểu đồ:**

1.  SENSITIVE, FINE GRAINED
2.  ORGANIC SOILS - PEATS
3.  CLAYS - CLAY TO SILTY CLAY
4.  SILT MIXTURES - CLAYEY SILT TO SILTY CLAY
5.  SAND MIXTURES - SILTY SAND TO SANDY SILT
6.  SANDS - CLEAN SAND TO SILTY SAND
7.  GRAVELLY SAND TO SAND
8.  VERY STIFF SAND TO CLAYEY* SAND
9.  VERY STIFF, FINE GRAINED*

(\*) HEAVILY OVERCONSOLIDATED OR CEMENTED

Figure 3: Robertson (1990) SBT classification chart based on normalized parameters

The figure below compares the non-normalized SBT and normalized SBT_n charts.

---


***

Figure 4: Comparison of updated SBT (Robertson, 2010) and SBT_n (Robertson, 1990) for the same CPT_u profile

#### 3.2.2. Schneider et al. (2008)
Schneider et al. (2008) plot classification charts using Q_t and Δu₂/σ'_v0. The following five soil classifications are considered:

1.  Zone 1a – silty (partially consolidated) and “Low I_r” clays (undrained)
2.  Zone 1b – clays (undrained)
3.  Zone 1c – sensitive clays (undrained)
4.  Zone 2 – sands or sand mixtures (essentially drained)
5.  Zone 3 – transitional soils (drained, undrained, or partially consolidated)

Schneider et al. (2008) plot the classification charts in three different formats, each suited for particular cases:
1.  log-log Q_t – Δu₂/σ'_v0 space – clays, clayey silts, silts, sandy silts, and sands with no negative penetration pore pressures
2.  semi-log Q_t – Δu₂/σ'_v0 space – sands and transitional soils with small negative excess penetration pore pressures
3.  semi-log Q_t – B_q space – clay soils with large negative excess penetration pore pressures

---


***

Figure 5: Schneider et al. (2008) soil classification charts in three plotting formats

Schneider 2008 A plots log-log Q_t – Δu₂/σ'_v0 space while Schneider 2008 B plots semi-log Q_t – Δu₂/σ'_v0 space in Settle3.

---


***

# 4. Filtering of CPT Data
In Settle3 you can filter CPT to remove data spikes. The filter will discard data outside of a defined bandwidth.

The boring is divided into *n* sections, where *n* = *depth*/*(window size)*. The default window size in Settle3 is 0.25m. For each section of the boring the mean q_c and standard deviation, σ_i, are calculated.

For each section, compute

> σ_ai = (σ²_(i-1) + σ²_i)¹ᐟ²

and

> σ_bi = (σ²_(i+1) + σ²_i)¹ᐟ²

For top section, only σ_bi is calculated. For the bottom section, only σ_ai is calculated.

The bandwidth for each section is calculated as:

> W_bi = q_cmean + BS ⋅ σ_ai &nbsp;&nbsp;&nbsp; if σ_ai < σ_bi

> W_bi = q_cmean + BS ⋅ σ_bi &nbsp;&nbsp;&nbsp; if σ_ai > σ_bi

*BS* is a filtering constant, chosen based on the degree of filtering desired. The default value in Settle3 is 1. Values that are outside of the bandwidth are filtered out.

---


***

# 5. References

Guide To Cone Penetration Testing, 6th Edition, 2015

Davies, M.P., Piezocone Technology for the Geoenvironmental Characterization of Mine Tailings. PhD Thesis. 1999.

Mayne, PW (2006). *In situ* test calibrations for evaluating soil parameters. *Proc*., Characterization and Engineering Properties of Natural Soils II, Singapore.

Robertson, PK (2009). Interpretation of cone penetration tests – a unified approach, *Canadian Geotech. J*., 46(11):1337–1355.

Jain, V.K., Dixit, M.,and Chitra, R. (2015) “Correlation of Plasticity Index and Compression Index of Soil” *International Journal of Innovations in Engineering and Technology (IJIET)*. ISSN: 2319-1058.

Jefferies, M.G., and Davies, M.P., 1993. Use of CPTU to estimate equivalent
SPT N60. *Geotechnical Testing Journal, ASTM*, **16**(4): 458-468.

Robertson, P.K., and Campanella, R.G., 1983a. Interpretation of cone
penetration tests – Part I (sand). *Canadian Geotechnical Journal*, **20**(4):
718-733.

Robertson, P.K., and Campanella, R.G. 1983b. Interpretation of cone
penetration tests – Part II (clay). *Canadian Geotechnical Journal*, **20**(4):
734-745.

Robertson, P. & Sully, John & Woeller, D. & Lunne, Tom & Powell, John & Gillespie, D.. (2011).
Estimating coefficient of consolidation from piezocone tests. Canadian Geotechnical Journal. 29. 539-550. 10.1139/t92-061.

Kordnaeij, A. Kalantary, F., Kordtabar, B. and Mola-Abasi, H. "Prediction of recompression index using GMDH-type neural network based on geotechnical soil properties” *Soils and Foundations*. Volume 55, Issue 6, 2015, Pages 1335-1345,
ISSN 0038-0806.

---


***

Kulhawy, F.H., and Mayne, P.H., 1990. *Manual on estimating soil properties for foundation design*, Report EL-6800 Electric Power Research Institute, EPRI, August 1990.

Schneider et al., 2008. Analysis of Factors Influencing Soil Classification Using Normalized Piezocone Tip Resistance and Pore Pressure Parameters. *Journal of Geotechnical and Geoenvironmental Engineering*, 134(11):1569-1586.

Cetin, K.O. and Ozan, N.S., 2009. CPT-Based Probabilistic Soil Characterization and Classification. Journal of Geotechnical and Geoenvironmental Engineering, ASCE, Vol. 135, no.1, 84-107.

Moon, S.W. and Kim, T.K. 2018. Undrained Shear Strength in Cohesive vs Soils Estimated by Directional Modes of In-Situ Shear Wave Velocity. *Geotech Gelo Eng*. 36:2851-2868.

Remai, Z. (2013) Correlation of undrained shear strength and CPT resistance. *Periodican polytechnica*. 57/1 (2013) 39-44. Doi:10.3311/PPci.2140.

---
