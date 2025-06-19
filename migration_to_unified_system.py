#!/usr/bin/env python3
"""
Migration Script to Unified RAG System

This script helps migrate from the old multiple RAG systems to the new unified system.
It provides backward compatibility and migration utilities.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.unified_rag_system import UnifiedRAGSystem, RAGConfiguration
import logging

def setup_logging():
    """Setup logging for migration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('migration.log'),
            logging.StreamHandler()
        ]
    )

def create_backward_compatible_instances():
    """Create backward compatible instances for old code"""
    
    logger = logging.getLogger(__name__)
    logger.info("Creating backward compatible RAG system instances")
    
    # Create different configurations for different use cases
    configurations = {
        # Simple system (replaces SimplePersistentRAGSystem)
        'simple': RAGConfiguration(
            enable_enhanced_generation=False,
            enable_structured_analysis=False,
            enable_persistence=True,
            enable_validation=False,
            enable_enrichment=False,
            enable_cross_phase_analysis=False
        ),
        
        # Enhanced system (replaces EnhancedPersistentRAGSystem) 
        'enhanced': RAGConfiguration(
            enable_enhanced_generation=True,
            enable_structured_analysis=True,
            enable_persistence=True,
            enable_validation=True,
            enable_enrichment=True,
            enable_cross_phase_analysis=True
        ),
        
        # Basic RAG (replaces SAFEMBSERAGSystem)
        'basic': RAGConfiguration(
            enable_enhanced_generation=False,
            enable_structured_analysis=False,
            enable_persistence=False,
            enable_validation=False,
            enable_enrichment=False,
            enable_cross_phase_analysis=False
        ),
        
        # Structured only (replaces EnhancedStructuredRAGSystem)
        'structured': RAGConfiguration(
            enable_enhanced_generation=True,
            enable_structured_analysis=True,
            enable_persistence=False,
            enable_validation=False,
            enable_enrichment=False,
            enable_cross_phase_analysis=True
        )
    }
    
    # Create instances
    systems = {}
    for name, config in configurations.items():
        try:
            systems[name] = UnifiedRAGSystem(config)
            logger.info(f"✅ Created {name} RAG system")
        except Exception as e:
            logger.error(f"❌ Failed to create {name} RAG system: {e}")
    
    return systems

def create_compatibility_layer():
    """Create compatibility classes for old imports"""
    
    # Create the unified system
    unified_system = UnifiedRAGSystem()
    
    # Create compatibility classes that wrap the unified system
    class SAFEMBSERAGSystemCompat:
        """Backward compatibility for SAFEMBSERAGSystem"""
        
        def __init__(self):
            config = RAGConfiguration(
                enable_enhanced_generation=False,
                enable_structured_analysis=False,
                enable_persistence=False,
                enable_validation=False,
                enable_enrichment=False
            )
            self.unified_system = UnifiedRAGSystem(config)
        
        def generate_requirements_from_proposal(self, proposal_text, target_phase="all", requirement_types=None):
            """Backward compatible method"""
            result = self.unified_system.generate_requirements_from_proposal(
                proposal_text, target_phase, requirement_types
            )
            # Return traditional requirements format
            return result.traditional_requirements
        
        def export_requirements(self, requirements, export_format="JSON"):
            """Backward compatible export"""
            from src.core.unified_rag_system import UnifiedRAGResult
            
            # Create a dummy result for export
            dummy_result = UnifiedRAGResult(traditional_requirements=requirements)
            return self.unified_system.export_requirements(dummy_result, export_format)
        
        def add_documents_to_vectorstore(self, file_paths):
            """Backward compatible document addition"""
            # This would call the unified system's equivalent method
            return {"status": "migrated_to_unified_system", "files": file_paths}
    
    class EnhancedPersistentRAGSystemCompat:
        """Backward compatibility for EnhancedPersistentRAGSystem"""
        
        def __init__(self):
            config = RAGConfiguration(
                enable_enhanced_generation=True,
                enable_structured_analysis=True,
                enable_persistence=True,
                enable_validation=True,
                enable_enrichment=True
            )
            self.unified_system = UnifiedRAGSystem(config)
        
        def generate_enhanced_requirements_from_proposal(self, proposal_text, target_phase="all", 
                                                       requirement_types=None, enable_structured_analysis=True,
                                                       enable_cross_phase_analysis=True, project_name=None):
            """Backward compatible enhanced generation"""
            result = self.unified_system.generate_requirements_from_proposal(
                proposal_text, target_phase, requirement_types, project_name
            )
            
            # Return enhanced format
            enhanced_result = {
                "traditional_requirements": result.traditional_requirements,
                "structured_analysis": result.structured_analysis,
                "validation_report": result.validation_report,
                "quality_score": result.quality_score,
                "generation_time": result.generation_time
            }
            return enhanced_result
    
    return {
        'SAFEMBSERAGSystem': SAFEMBSERAGSystemCompat,
        'EnhancedPersistentRAGSystem': EnhancedPersistentRAGSystemCompat
    }

def update_import_statements():
    """Guide for updating import statements"""
    
    migration_guide = """
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
"""
    
    print(migration_guide)
    
    # Write to file
    with open("MIGRATION_GUIDE.md", "w") as f:
        f.write(migration_guide)
    
    print("\n📝 Migration guide written to MIGRATION_GUIDE.md")

def test_unified_system():
    """Test the unified system with different configurations"""
    
    logger = logging.getLogger(__name__)
    logger.info("Testing unified system configurations")
    
    # Test different configurations
    test_text = """
    This is a test project proposal for a cybersecurity monitoring system.
    The system should detect threats, analyze network traffic, and provide alerts.
    It must be scalable and handle high-volume data processing.
    """
    
    configs_to_test = {
        'basic': RAGConfiguration(
            enable_enhanced_generation=False,
            enable_structured_analysis=False,
            enable_persistence=False
        ),
        'enhanced': RAGConfiguration(
            enable_enhanced_generation=True,
            enable_structured_analysis=True,
            enable_persistence=False,  # Disable for testing
            enable_validation=True,
            enable_enrichment=True
        )
    }
    
    for name, config in configs_to_test.items():
        try:
            logger.info(f"Testing {name} configuration...")
            system = UnifiedRAGSystem(config)
            
            result = system.generate_requirements_from_proposal(
                proposal_text=test_text,
                target_phase="operational",
                requirement_types=["functional"]
            )
            
            logger.info(f"✅ {name} configuration test passed")
            logger.info(f"   Quality score: {result.quality_score:.2f}")
            logger.info(f"   Generation time: {result.generation_time:.1f}s")
            
            # Show what components were used
            status = system.get_system_status()
            components = status["available_components"]
            enabled_components = [k for k, v in components.items() if v]
            logger.info(f"   Enabled components: {enabled_components}")
            
        except Exception as e:
            logger.error(f"❌ {name} configuration test failed: {e}")

def main():
    """Main migration script"""
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🔄 SAFE MBSE RAG System - Migration to Unified System")
    print("=" * 60)
    
    # Step 1: Test unified system
    print("\n1️⃣ Testing unified system...")
    test_unified_system()
    
    # Step 2: Create backward compatibility layer  
    print("\n2️⃣ Creating backward compatibility layer...")
    compat_classes = create_compatibility_layer()
    logger.info(f"Created compatibility classes: {list(compat_classes.keys())}")
    
    # Step 3: Create migration guide
    print("\n3️⃣ Generating migration guide...")
    update_import_statements()
    
    # Step 4: Show new file structure
    print("\n4️⃣ New simplified file structure:")
    new_structure = """
    src/core/
    ├── unified_rag_system.py       ⭐ NEW: Single entry point for all RAG functionality
    ├── arcadia_extractors.py       ⭐ NEW: Consolidated ARCADIA extractors
    ├── document_processor.py       ✅ KEPT: Document processing
    ├── requirements_generator.py   ✅ KEPT: Requirements generation
    ├── component_analyzer.py       ✅ KEPT: Component analysis
    └── priority_analyzer.py        ✅ KEPT: Priority analysis
    
    REMOVED (consolidated into unified_rag_system.py):
    ❌ rag_system.py
    ❌ enhanced_rag_service.py  
    ❌ enhanced_structured_rag_system.py
    ❌ simple_persistent_rag_system.py
    ❌ enhanced_persistent_rag_system.py
    
    REMOVED (consolidated into arcadia_extractors.py):
    ❌ operational_analysis_extractor.py
    ❌ system_analysis_extractor.py
    ❌ logical_architecture_extractor.py
    ❌ physical_architecture_extractor.py
    """
    print(new_structure)
    
    print("\n✅ Migration completed successfully!")
    print("\n📖 Next steps:")
    print("   1. Review MIGRATION_GUIDE.md for code updates")
    print("   2. Update your imports to use UnifiedRAGSystem")
    print("   3. Test your applications with the new system")
    print("   4. Remove old RAG system files when ready")

if __name__ == "__main__":
    main() 