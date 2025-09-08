"""
Geotech Engineering Calculators
Specialized tools for geotechnical calculations
"""

from typing import Dict, Union, Tuple
from app.core.config.constants import ToolConstants

class GeotechCalculationError(Exception):
    """Custom exception for geotech calculation errors"""
    pass

def settlement_calculator(load: float, young_modulus: float) -> Dict[str, Union[float, str]]:
    """
    Calculate immediate settlement using simplified formula
    
    Args:
        load (float): Applied load (kN or similar units)
        young_modulus (float): Young's modulus of soil (kPa or similar units)
    
    Returns:
        Dict with settlement result and calculation details
    
    Formula: settlement = load / young_modulus
    """
    try:
        # Input validation
        if not isinstance(load, (int, float)):
            raise GeotechCalculationError("Load must be a number")
        if not isinstance(young_modulus, (int, float)):
            raise GeotechCalculationError("Young's modulus must be a number")
        
        if load <= 0:
            raise GeotechCalculationError("Load must be positive (> 0)")
        if young_modulus <= 0:
            raise GeotechCalculationError("Young's modulus must be positive (> 0)")
        
        # Calculate settlement
        settlement = load / young_modulus
        
        return {
            "settlement": round(settlement, 4),
            "load": load,
            "young_modulus": young_modulus,
            "units": "Same units as load/young_modulus ratio",
            "formula": "settlement = load / young_modulus",
            "status": "success"
        }
        
    except GeotechCalculationError as e:
        return {
            "settlement": None,
            "error": str(e),
            "status": "error"
        }
    except Exception as e:
        return {
            "settlement": None,
            "error": f"Calculation error: {str(e)}",
            "status": "error"
        }

def _get_bearing_capacity_factors(phi: int) -> Tuple[float, float, float]:
    """Get bearing capacity factors for given friction angle"""
    if phi in ToolConstants.BEARING_CAPACITY_FACTORS:
        return ToolConstants.BEARING_CAPACITY_FACTORS[phi]
    
    # Linear interpolation for values between table entries
    phi_values = sorted(ToolConstants.BEARING_CAPACITY_FACTORS.keys())
    
    # Find surrounding values
    lower_phi = None
    upper_phi = None
    
    for phi_val in phi_values:
        if phi_val <= phi:
            lower_phi = phi_val
        if phi_val >= phi and upper_phi is None:
            upper_phi = phi_val
            break
    
    if lower_phi is None or upper_phi is None:
        raise GeotechCalculationError(f"Friction angle φ={phi}° is outside valid range ({ValidationConstants.MIN_PHI_ANGLE}-{ValidationConstants.MAX_PHI_ANGLE}°)")
    
    if lower_phi == upper_phi:
        return ToolConstants.BEARING_CAPACITY_FACTORS[lower_phi]
    
    # Linear interpolation
    lower_factors = ToolConstants.BEARING_CAPACITY_FACTORS[lower_phi]
    upper_factors = ToolConstants.BEARING_CAPACITY_FACTORS[upper_phi]
    
    ratio = (phi - lower_phi) / (upper_phi - lower_phi)
    
    nc_interp = lower_factors[0] + ratio * (upper_factors[0] - lower_factors[0])
    nq_interp = lower_factors[1] + ratio * (upper_factors[1] - lower_factors[1])
    nr_interp = lower_factors[2] + ratio * (upper_factors[2] - lower_factors[2])
    
    return (round(nc_interp, 2), round(nq_interp, 2), round(nr_interp, 2))

def bearing_capacity_calculator(
    B: float, 
    gamma: float, 
    Df: float, 
    phi: int
) -> Dict[str, Union[float, str, Dict]]:
    """
    Calculate ultimate bearing capacity using Terzaghi formula for cohesionless soil
    
    Args:
        B (float): Width/diameter of footing (m)
        gamma (float): Unit weight of soil (kN/m³)
        Df (float): Depth of footing (m) 
        phi (int): Internal friction angle (degrees, 0-40)
    
    Returns:
        Dict with bearing capacity result and calculation details
        
    Formula: q_ult = γ*Df*Nq + 0.5*γ*B*Nr
    Note: Nc term omitted for cohesionless soil (c=0)
    """
    try:
        # Input validation
        if not isinstance(B, (int, float)):
            raise GeotechCalculationError("Footing width B must be a number")
        if not isinstance(gamma, (int, float)):
            raise GeotechCalculationError("Unit weight γ must be a number")
        if not isinstance(Df, (int, float)):
            raise GeotechCalculationError("Footing depth Df must be a number")
        if not isinstance(phi, int):
            raise GeotechCalculationError("Friction angle φ must be an integer")
        
        if B <= 0:
            raise GeotechCalculationError("Footing width B must be positive (> 0)")
        if gamma <= 0:
            raise GeotechCalculationError("Unit weight γ must be positive (> 0)")
        if Df < 0:
            raise GeotechCalculationError("Footing depth Df must be non-negative (≥ 0)")
        from app.core.config.constants import ValidationConstants
        if not (ValidationConstants.MIN_PHI_ANGLE <= phi <= ValidationConstants.MAX_PHI_ANGLE):
            raise GeotechCalculationError(f"Friction angle φ must be between {ValidationConstants.MIN_PHI_ANGLE}° and {ValidationConstants.MAX_PHI_ANGLE}°")
        
        # Get bearing capacity factors
        Nc, Nq, Nr = _get_bearing_capacity_factors(phi)
        
        # Calculate ultimate bearing capacity
        # For cohesionless soil: q_ult = γ*Df*Nq + 0.5*γ*B*Nr
        term1 = gamma * Df * Nq  # Overburden term
        term2 = 0.5 * gamma * B * Nr  # Width term
        
        q_ult = term1 + term2
        
        return {
            "q_ultimate": round(q_ult, 2),
            "inputs": {
                "B": B,
                "gamma": gamma, 
                "Df": Df,
                "phi": phi
            },
            "factors": {
                "Nc": Nc,
                "Nq": Nq, 
                "Nr": Nr
            },
            "calculation_breakdown": {
                "overburden_term": round(term1, 2),
                "width_term": round(term2, 2),
                "total": round(q_ult, 2)
            },
            "formula": "q_ult = γ*Df*Nq + 0.5*γ*B*Nr",
            "units": "Same units as γ (typically kPa if γ in kN/m³)",
            "status": "success"
        }
        
    except GeotechCalculationError as e:
        return {
            "q_ultimate": None,
            "error": str(e),
            "status": "error"
        }
    except Exception as e:
        return {
            "q_ultimate": None,
            "error": f"Calculation error: {str(e)}",
            "status": "error"
        }

# Tool descriptions for LLM integration
TOOL_DESCRIPTIONS = {
    "settlement_calculator": {
        "name": "settlement_calculator",
        "description": "Calculate immediate settlement of soil under load using simplified elastic formula",
        "parameters": {
            "type": "object",
            "properties": {
                "load": {
                    "type": "number",
                    "description": "Applied load (kN, kPa, or other force units)"
                },
                "young_modulus": {
                    "type": "number", 
                    "description": "Young's modulus of soil (kPa, MPa, or corresponding units)"
                }
            },
            "required": ["load", "young_modulus"]
        }
    },
    
    "bearing_capacity_calculator": {
        "name": "bearing_capacity_calculator",
        "description": "Calculate ultimate bearing capacity using Terzaghi formula for cohesionless soil",
        "parameters": {
            "type": "object",
            "properties": {
                "B": {
                    "type": "number",
                    "description": "Width or diameter of footing (m)"
                },
                "gamma": {
                    "type": "number",
                    "description": "Unit weight of soil (kN/m³)"
                },
                "Df": {
                    "type": "number", 
                    "description": "Depth of footing below ground surface (m)"
                },
                "phi": {
                    "type": "integer",
                    "description": "Internal friction angle of soil (degrees, 0-40)"
                }
            },
            "required": ["B", "gamma", "Df", "phi"]
        }
    }
}

def get_available_tools():
    """Return list of available geotech tools"""
    return list(TOOL_DESCRIPTIONS.keys())

def get_tool_description(tool_name: str):
    """Get description for a specific tool"""
    return TOOL_DESCRIPTIONS.get(tool_name)

def call_tool(tool_name: str, **kwargs):
    """Generic tool caller"""
    if tool_name == "settlement_calculator":
        return settlement_calculator(**kwargs)
    elif tool_name == "bearing_capacity_calculator":
        return bearing_capacity_calculator(**kwargs)
    else:
        return {
            "error": f"Unknown tool: {tool_name}",
            "available_tools": get_available_tools(),
            "status": "error"
        }