
# MIGRATION GUIDE: Import Statement Updates

## OLD IMPORTS (to be replaced):

```python
# OLD - Multiple different systems
from src.core.rag_system import SAFEMBSERAGSystem
from src.core.enhanced_rag_service import EnhancedRAGService  
from src.core.enhanced_structured_rag_system import EnhancedStructuredRAGSystem
from src.core.simple_persistent_rag_system import SimplePersistentRAGSystem
from src.core.enhanced_persistent_rag_system import EnhancedPersistentRAGSystem
```

## NEW IMPORTS (unified approach):

```python
# NEW - Single unified system with configuration
from src.core.unified_rag_system import UnifiedRAGSystem, RAGConfiguration

# Create different configurations as needed
basic_config = RAGConfiguration(
    enable_enhanced_generation=False,
    enable_structured_analysis=False,
    enable_persistence=False
)

enhanced_config = RAGConfiguration(
    enable_enhanced_generation=True,
    enable_structured_analysis=True,
    enable_persistence=True,
    enable_validation=True,
    enable_enrichment=True
)

# Initialize with desired configuration
rag_system = UnifiedRAGSystem(enhanced_config)
```

## MAIN METHOD CHANGES:

### Old approach:
```python
# Different methods for different systems
results = basic_rag.generate_requirements_from_proposal(text)
enhanced_results = enhanced_rag.generate_enhanced_requirements_from_proposal(text)
structured_results = structured_rag.generate_enhanced_requirements_from_proposal(text)
```

### New approach:
```python
# Single method, different configurations
results = rag_system.generate_requirements_from_proposal(
    proposal_text=text,
    target_phase="all",
    requirement_types=["functional", "non_functional", "stakeholder"],
    project_name="my_project"  # Optional for persistence
)

# Access different parts of results
traditional_reqs = results.traditional_requirements
structured_analysis = results.structured_analysis  # If enabled
validation_report = results.validation_report      # If enabled
quality_score = results.quality_score
```

## BENEFITS:

✅ Single import instead of 5+ different systems
✅ Consistent API across all functionality
✅ Configurable features (enable only what you need)
✅ Better performance (shared infrastructure)
✅ Easier maintenance and debugging
✅ Unified result format with comprehensive metadata
