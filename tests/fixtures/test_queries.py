"""
Test Query Datasets for Comprehensive Agent Testing
Covers all scenarios: in-scope, out-of-scope, edge cases, and error conditions
"""

from typing import Dict, List, Any, Optional

class TestQueryDatasets:
    """Centralized test query datasets for agent testing"""
    
    # In-scope queries that should work properly
    IN_SCOPE_QUERIES = {
        "settle3_questions": [
            {
                "question": "How does Settle3 determine when secondary consolidation begins?",
                "expected_action": "retrieve",
                "expected_search_query": "Settle3 secondary consolidation",
                "category": "settle3_theory"
            },
            {
                "question": "What methods does Settle3 use to calculate undrained shear strength from CPT data?",
                "expected_action": "retrieve", 
                "expected_search_query": "Settle3 CPT undrained shear strength",
                "category": "settle3_cpt"
            },
            {
                "question": "How does Settle3 model an excavation?",
                "expected_action": "retrieve",
                "expected_search_query": "Settle3 excavation modeling",
                "category": "settle3_modeling"
            }
        ],
        
        "cpt_analysis": [
            {
                "question": "What is the Soil Behaviour Type Index (Ic) formula?",
                "expected_action": "retrieve",
                "expected_search_query": "Soil Behaviour Type Index Ic formula",
                "category": "cpt_theory"
            },
            {
                "question": "How is normalized cone resistance calculated in CPT analysis?",
                "expected_action": "retrieve",
                "expected_search_query": "normalized cone resistance CPT",
                "category": "cpt_calculations"
            }
        ],
        
        "liquefaction_analysis": [
            {
                "question": "How does Settle3 calculate the factor of safety against liquefaction?",
                "expected_action": "retrieve",
                "expected_search_query": "factor of safety liquefaction Settle3",
                "category": "liquefaction_theory"
            },
            {
                "question": "What is the purpose of the Stress Reduction Factor (rd) in liquefaction analysis?",
                "expected_action": "retrieve",
                "expected_search_query": "Stress Reduction Factor rd liquefaction",
                "category": "liquefaction_theory"
            }
        ],
        
        "settlement_calculations": [
            {
                "question": "Calculate settlement for load 1000 kN and Young's modulus 50000 kPa",
                "expected_action": "calculate_settlement",
                "expected_params": {"load": 1000.0, "young_modulus": 50000.0},
                "category": "settlement_calc"
            },
            {
                "question": "What is the settlement for a load of 500 kPa and E = 25 MPa?",
                "expected_action": "calculate_settlement", 
                "expected_params": {"load": 500.0, "young_modulus": 25000.0},
                "category": "settlement_calc"
            }
        ],
        
        "bearing_capacity_calculations": [
            {
                "question": "Calculate bearing capacity for B=2m, gamma=18 kN/m³, Df=1.5m, phi=30°",
                "expected_action": "calculate_bearing_capacity",
                "expected_params": {"B": 2.0, "gamma": 18.0, "Df": 1.5, "phi": 30},
                "category": "bearing_capacity_calc"
            },
            {
                "question": "What is ultimate bearing capacity for footing width 3m, unit weight 20 kN/m³, depth 2m, friction angle 35°?",
                "expected_action": "calculate_bearing_capacity",
                "expected_params": {"B": 3.0, "gamma": 20.0, "Df": 2.0, "phi": 35},
                "category": "bearing_capacity_calc"
            }
        ],
        
        "combined_queries": [
            {
                "question": "Calculate settlement for 800 kN load with E=40 MPa and explain the consolidation theory behind it",
                "expected_action": "both",
                "expected_params": {"load": 800.0, "young_modulus": 40000.0},
                "expected_search_query": "consolidation theory settlement",
                "category": "mixed_calc_retrieval"
            }
        ]
    }
    
    # Out-of-scope queries that should be rejected
    OUT_OF_SCOPE_QUERIES = {
        "general_engineering": [
            {
                "question": "How to design a steel beam for building construction?",
                "expected_action": "out_of_scope",
                "category": "structural_engineering"
            },
            {
                "question": "What is the moment of inertia calculation for concrete columns?",
                "expected_action": "out_of_scope", 
                "category": "structural_engineering"
            }
        ],
        
        "non_engineering": [
            {
                "question": "What's the weather like today?",
                "expected_action": "out_of_scope",
                "category": "general_knowledge"
            },
            {
                "question": "How do I cook pasta?",
                "expected_action": "out_of_scope",
                "category": "cooking"
            },
            {
                "question": "What is machine learning?",
                "expected_action": "out_of_scope",
                "category": "computer_science"
            }
        ],
        
        "other_engineering": [
            {
                "question": "How to calculate electrical resistance in a circuit?",
                "expected_action": "out_of_scope",
                "category": "electrical_engineering"
            },
            {
                "question": "What is the efficiency of a heat engine?",
                "expected_action": "out_of_scope",
                "category": "mechanical_engineering"
            }
        ],
        
        "personal_questions": [
            {
                "question": "How are you feeling today?",
                "expected_action": "out_of_scope",
                "category": "personal"
            },
            {
                "question": "What is your opinion on politics?",
                "expected_action": "out_of_scope",
                "category": "personal"
            }
        ],
        
        "borderline_geotechnical": [
            {
                "question": "How to design a retaining wall with reinforced concrete?",
                "expected_action": "out_of_scope",
                "category": "structural_geotech" # Geotechnical but structural focus
            },
            {
                "question": "What are the environmental impacts of soil contamination?",
                "expected_action": "out_of_scope", 
                "category": "environmental_geotech" # Environmental focus
            }
        ]
    }
    
    # Edge cases and error conditions
    EDGE_CASE_QUERIES = {
        "invalid_calculation_params": [
            {
                "question": "Calculate settlement for load -500 kN and Young's modulus 25000 kPa",
                "expected_action": "calculate_settlement",
                "expected_params": {"load": -500.0, "young_modulus": 25000.0},
                "should_fail": True,
                "error_type": "invalid_negative_load"
            },
            {
                "question": "Calculate bearing capacity for B=-2m, gamma=18 kN/m³, Df=1.5m, phi=30°",
                "expected_action": "calculate_bearing_capacity", 
                "expected_params": {"B": -2.0, "gamma": 18.0, "Df": 1.5, "phi": 30},
                "should_fail": True,
                "error_type": "invalid_negative_dimension"
            },
            {
                "question": "Calculate settlement with Young's modulus = 0",
                "expected_action": "calculate_settlement",
                "expected_params": {"load": 1000.0, "young_modulus": 0.0},
                "should_fail": True,
                "error_type": "division_by_zero"
            }
        ],
        
        "missing_parameters": [
            {
                "question": "Calculate settlement for load 1000 kN",
                "expected_action": "calculate_settlement",
                "should_fail": True,
                "error_type": "missing_young_modulus"
            },
            {
                "question": "Calculate bearing capacity for a footing",
                "expected_action": "calculate_bearing_capacity",
                "should_fail": True, 
                "error_type": "missing_all_parameters"
            }
        ],
        
        "malicious_inputs": [
            {
                "question": "Calculate settlement for load 1e20 kN and Young's modulus 1e20 kPa",
                "expected_action": "calculate_settlement",
                "expected_params": {"load": 1e20, "young_modulus": 1e20},
                "should_fail": True,
                "error_type": "unrealistic_values"
            },
            {
                "question": "Calculate bearing capacity with phi = 999°",
                "expected_action": "calculate_bearing_capacity",
                "expected_params": {"B": 2.0, "gamma": 18.0, "Df": 1.5, "phi": 999},
                "should_fail": True,
                "error_type": "invalid_angle_range"
            }
        ],
        
        "ambiguous_queries": [
            {
                "question": "What is settlement?",
                "expected_action": "retrieve",
                "expected_search_query": "settlement definition",
                "category": "ambiguous_conceptual"
            },
            {
                "question": "Tell me about CPT",
                "expected_action": "retrieve", 
                "expected_search_query": "CPT analysis",
                "category": "ambiguous_conceptual"
            }
        ]
    }

    @classmethod
    def get_all_in_scope_queries(cls) -> List[Dict[str, Any]]:
        """Get all in-scope queries as flat list"""
        queries = []
        for category in cls.IN_SCOPE_QUERIES.values():
            queries.extend(category)
        return queries
    
    @classmethod 
    def get_all_out_of_scope_queries(cls) -> List[Dict[str, Any]]:
        """Get all out-of-scope queries as flat list"""
        queries = []
        for category in cls.OUT_OF_SCOPE_QUERIES.values():
            queries.extend(category)
        return queries
    
    @classmethod
    def get_all_edge_case_queries(cls) -> List[Dict[str, Any]]:
        """Get all edge case queries as flat list"""
        queries = []
        for category in cls.EDGE_CASE_QUERIES.values():
            queries.extend(category)
        return queries
    
    @classmethod
    def get_queries_by_action(cls, action: str) -> List[Dict[str, Any]]:
        """Get all queries that should result in specific action"""
        all_queries = cls.get_all_in_scope_queries() + cls.get_all_out_of_scope_queries()
        return [q for q in all_queries if q.get("expected_action") == action]
    
    @classmethod
    def get_calculation_queries_with_params(cls) -> List[Dict[str, Any]]:
        """Get calculation queries with valid parameters"""
        queries = []
        for query in cls.get_all_in_scope_queries():
            if "expected_params" in query:
                queries.append(query)
        return queries


# Mock responses for testing
class MockResponses:
    """Mock responses for external services"""
    
    @staticmethod
    def mock_llm_planning_response(action: str, reasoning: str, **kwargs) -> Dict[str, Any]:
        """Generate mock LLM planning response"""
        response = {
            "action": action,
            "reasoning": reasoning
        }
        
        if "tool_parameters" in kwargs:
            response["tool_parameters"] = kwargs["tool_parameters"]
        if "search_query" in kwargs:
            response["search_query"] = kwargs["search_query"]
            
        return response
    
    @staticmethod
    def mock_llm_synthesis_response(answer: str) -> str:
        """Generate mock LLM synthesis response"""
        return answer
    
    @staticmethod
    def mock_rag_search_results(query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """Generate mock RAG search results"""
        if "bearing capacity" in query.lower():
            return [
                {
                    "source_name": "Settle3-Theory-Manual.pdf",
                    "content": "Ultimate bearing capacity is calculated using Terzaghi's equation: q_ult = γ*Df*Nq + 0.5*γ*B*Nr",
                    "confidence_score": 0.92,
                    "page_index": 45
                }
            ]
        elif "cpt" in query.lower() or "soil behaviour" in query.lower():
            return [
                {
                    "source_name": "Settle3-CPT-Theory-Manual.pdf", 
                    "content": "The Soil Behaviour Type Index (Ic) is calculated using: Ic = [(3.47 - log(Qtn))² + (log(Fr) + 1.22)²]^0.5",
                    "confidence_score": 0.89,
                    "page_index": 23
                }
            ]
        elif "liquefaction" in query.lower():
            return [
                {
                    "source_name": "Settle3-Liquefaction-Theory-Manual.pdf",
                    "content": "Factor of safety against liquefaction: FS = (CRR_7.5 * MSF * K_σ * K_α) / CSR",
                    "confidence_score": 0.94,
                    "page_index": 67
                }
            ]
        else:
            return []
    
    @staticmethod 
    def mock_settlement_calculation(load: float, young_modulus: float) -> Dict[str, Any]:
        """Generate mock settlement calculation result"""
        if load <= 0:
            return {"status": "error", "error": "Load must be positive"}
        if young_modulus <= 0:
            return {"status": "error", "error": "Young's modulus must be positive"}
        
        settlement = load / young_modulus
        return {
            "settlement": round(settlement, 4),
            "load": load,
            "young_modulus": young_modulus,
            "formula": "settlement = load / young_modulus",
            "status": "success"
        }
    
    @staticmethod
    def mock_bearing_capacity_calculation(B: float, gamma: float, Df: float, phi: int) -> Dict[str, Any]:
        """Generate mock bearing capacity calculation result"""
        if B <= 0:
            return {"status": "error", "error": "Footing width must be positive"}
        if gamma <= 0:
            return {"status": "error", "error": "Unit weight must be positive"}
        if Df < 0:
            return {"status": "error", "error": "Depth must be non-negative"}
        if not (0 <= phi <= 40):
            return {"status": "error", "error": "Friction angle must be between 0° and 40°"}
        
        # Simplified mock calculation
        Nq = 1 + 2 * (phi / 40)  # Simplified factor
        Nr = phi / 10  # Simplified factor
        
        q_ult = gamma * Df * Nq + 0.5 * gamma * B * Nr
        
        return {
            "q_ultimate": round(q_ult, 2),
            "inputs": {"B": B, "gamma": gamma, "Df": Df, "phi": phi},
            "factors": {"Nq": Nq, "Nr": Nr},
            "formula": "q_ult = γ*Df*Nq + 0.5*γ*B*Nr",
            "status": "success"
        }