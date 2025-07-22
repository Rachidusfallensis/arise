# Unified Document Processor Integration Guide

## Overview

The Unified Document Processor provides centralized, intelligent document handling across all tabs in the ARISE application with advanced features like cross-tab linking and automatic fallback mechanisms.

## Integration Architecture

### Safe Integration Strategy

The integration uses a **safe wrapper pattern** with feature flags to ensure:
- **Zero Downtime**: App continues working even if advanced features fail
- **Gradual Rollout**: Features can be enabled/disabled dynamically
- **Backward Compatibility**: Legacy code continues to work
- **Fallback Mechanisms**: Automatic recovery from failures

### Core Components

```python
safe_document_processor()  # Main wrapper with feature flags
  ├── unified_document_processor()  # Advanced processing
  └── legacy_document_processor()   # Fallback processing

FEATURE_FLAGS = {
    'use_unified_processor': True,      # Enable/disable advanced processing
    'enable_duplicate_detection': True, # Smart duplicate handling
    'enable_cross_tab_linking': True,   # Cross-tab document availability
    'enable_ui_feedback': True,         # Detailed progress indicators
    'enable_automatic_linking': True,   # Auto-link duplicates
    'fallback_to_legacy': True,         # Auto-fallback on errors
}
```

## Using the Unified Processor

### Basic Usage

All existing upload interfaces now use the safe wrapper:

```python
# Standard usage (replaces all direct unified_document_processor calls)
results = safe_document_processor(
    rag_system=rag_system,
    uploaded_files=uploaded_files,
    context="project",  # or "chat", "requirements", "traditional"
    current_project=current_project,
    extract_content=True,
    show_ui=True
)
```

### Context Types

| Context | Purpose | Features |
|---------|---------|----------|
| `"project"` | Project-specific uploads | Full project integration, persistence |
| `"chat"` | Chat document uploads | Global availability, chat integration |
| `"requirements"` | Requirements generation | Content extraction, analysis ready |
| `"traditional"` | Legacy mode | Basic upload, minimal features |

### Feature Flag Control

#### UI Controls (Sidebar → Advanced Settings)

Users can dynamically control features:
- **Enable Unified Document Processor**: Turn on/off advanced processing
- **Enable Direct Processing**: Process all files in new projects
- **Enable Cross-Tab Linking**: Documents available across all tabs
- **Enable UI Feedback**: Detailed progress bars and status
- **Enable Automatic Linking**: Auto-link duplicates without confirmation
- **Enable Legacy Fallback**: Auto-fallback to basic processing on errors

#### Programmatic Control

```python
# Disable specific features temporarily
FEATURE_FLAGS['use_unified_processor'] = False  # Use legacy only
FEATURE_FLAGS['enable_duplicate_detection'] = False  # Skip duplicate checks
FEATURE_FLAGS['fallback_to_legacy'] = False  # No fallback (fail fast)
```

## Migration from Direct Usage

### Before (Direct Unified Processor)
```python
# Old approach - direct calls
results = unified_document_processor(
    rag_system=rag_system,
    uploaded_files=uploaded_files,
    context="project",
    current_project=current_project,
    extract_content=True,
    show_ui=True
)
```

### After (Safe Wrapper)
```python
# New approach - safe wrapper
results = safe_document_processor(
    rag_system=rag_system,
    uploaded_files=uploaded_files,
    context="project",
    current_project=current_project,
    extract_content=True,
    show_ui=True
)
```

### Automatic Migration

The integration automatically updates all existing calls:
- Chat tab uploads → `safe_document_processor`
- Requirements tab uploads → `safe_document_processor`
- Project document uploads → `safe_document_processor`
- Legacy `process_documents_with_duplicate_detection` → `safe_document_processor`

## Advanced Features

### 1. Direct Document Processing

**How it works:**
- Processes all uploaded documents directly
- Creates new embeddings and chunks for each project
- Ensures complete project isolation
- Provides clear processing feedback

**Benefits:**
- **Project Isolation**: Each project maintains its own documents
- **Predictable Behavior**: All files are processed consistently
- **Simple Workflow**: No duplicate handling decisions needed

### 2. Cross-Tab Document Availability

Documents uploaded in any tab become immediately available in all other tabs:
- Upload in "Document Management" → Available in "Requirements & Analysis"
- Upload in "Requirements" → Available for "Chat"
- Upload in "Chat" → Available for "Requirements Generation"

### 3. Context-Aware Session State

```python
# Context-specific storage (no conflicts)
st.session_state[f'{context}_extracted_document_content'] = content
st.session_state[f'{context}_extracted_files_info'] = file_info

# Backward compatibility
st.session_state['extracted_document_content'] = content  # Legacy key
```

### 4. Enhanced Error Handling

**Three-Layer Error Protection:**

1. **Feature Flag Bypass**: Disable features causing issues
2. **Automatic Fallback**: Switch to legacy processing on errors
3. **Graceful Degradation**: App continues working with basic features

```python
try:
    # Attempt advanced processing
    result = unified_document_processor(...)
except Exception as e:
    logger.error(f"Advanced processing failed: {e}")
    
    if FEATURE_FLAGS['fallback_to_legacy']:
        # Automatic fallback
        result = legacy_document_processor(...)
    else:
        # Fail fast (development/debugging)
        raise e
```

## Troubleshooting

### Common Issues

**1. "Advanced processing unavailable, using standard upload mode"**
- **Cause**: Unified processor encountered an error
- **Solution**: Check logs, verify feature flags, test with smaller files
- **Action**: App automatically uses legacy mode, no user impact

**2. Document processing issues**
- **Cause**: Processing settings are disabled or persistence unavailable  
- **Solution**: Check project settings and ensure proper project setup
- **Workaround**: Manual file management still works

**3. Documents not appearing across tabs**
- **Cause**: `enable_cross_tab_linking` disabled or project not selected
- **Solution**: Enable cross-tab linking, ensure project is active
- **Check**: Verify project selection in sidebar

**4. Slow upload performance**
- **Cause**: Large files, network issues, or detailed UI feedback
- **Solution**: Disable `enable_ui_feedback` for faster uploads
- **Alternative**: Use legacy mode for simple uploads

### Debugging Steps

1. **Check Feature Flags**
   ```python
   # In sidebar Advanced Settings
   st.json(FEATURE_FLAGS)  # View current configuration
   ```

2. **Check Logs**
   ```bash
   tail -f logs/requirements_generation.log
   ```

3. **Test Individual Components**
   ```python
   # Test basic RAG system
   test_rag = SAFEMBSERAGSystem()
   
   # Test persistence
   if hasattr(rag_system, 'persistence_service'):
       print("✅ Persistence available")
   else:
       print("❌ Persistence unavailable - limited features")
   ```

4. **Progressive Debugging**
   - Disable all advanced features
   - Enable one feature at a time
   - Identify problematic feature
   - Check specific error messages

### Performance Tuning

**For Large Files (>10MB):**
```python
FEATURE_FLAGS['enable_ui_feedback'] = False  # Reduce UI overhead
FEATURE_FLAGS['enable_duplicate_detection'] = False  # Skip hash calculation
```

**For High Volume Uploads:**
```python
FEATURE_FLAGS['enable_automatic_linking'] = True  # Faster duplicate handling
FEATURE_FLAGS['enable_cross_tab_linking'] = False  # Reduce cross-tab overhead
```

**For Development/Testing:**
```python
FEATURE_FLAGS['fallback_to_legacy'] = False  # Fail fast for debugging
FEATURE_FLAGS['enable_ui_feedback'] = True  # Detailed error reporting
```

## Rollback Strategy

### Emergency Rollback

If issues occur, disable all advanced features:

```python
# In sidebar Advanced Settings, or programmatically:
FEATURE_FLAGS = {
    'use_unified_processor': False,      # ← Disable all advanced features
    'enable_duplicate_detection': False,
    'enable_cross_tab_linking': False,
    'enable_ui_feedback': False,
    'enable_automatic_linking': False,
    'fallback_to_legacy': True,          # ← Ensure fallback works
}
```

### Gradual Re-enablement

1. **Start with basic unified processing:**
   ```python
   FEATURE_FLAGS['use_unified_processor'] = True
   FEATURE_FLAGS['fallback_to_legacy'] = True
   # All other features = False
   ```

2. **Add features one by one:**
   ```python
   FEATURE_FLAGS['enable_ui_feedback'] = True  # Safe to enable
   # Test, then enable next feature
   ```

3. **Enable advanced features last:**
   ```python
   FEATURE_FLAGS['enable_duplicate_detection'] = True  # More complex
   FEATURE_FLAGS['enable_cross_tab_linking'] = True    # Most complex
   ```

## Best Practices

### 1. Always Use Safe Wrapper
```python
# ✅ Correct
results = safe_document_processor(...)

# ❌ Avoid direct calls
results = unified_document_processor(...)
```

### 2. Handle Return Values Properly
```python
results = safe_document_processor(...)

if results.get('processed', 0) > 0:
    st.success(f"✅ Processed {results['processed']} files")
    
if results.get('errors'):
    for error in results['errors']:
        st.error(f"❌ {error}")
        
# Check for legacy mode
if results.get('legacy_mode'):
    st.info("ℹ️ Using basic processing mode")
```

### 3. Context-Specific Implementation
```python
# Use appropriate context for different upload scenarios
contexts = {
    'project_management': 'project',
    'chat_interface': 'chat', 
    'requirements_generation': 'requirements',
    'basic_upload': 'traditional'
}

context = contexts.get(current_tab, 'traditional')
results = safe_document_processor(..., context=context, ...)
```

### 4. Monitor and Log
```python
# Log important events
logger.info(f"Document processing: {context} - {len(uploaded_files)} files")

# Monitor performance
start_time = time.time()
results = safe_document_processor(...)
duration = time.time() - start_time
logger.info(f"Processing completed in {duration:.1f}s")
```

## Integration Validation

Use the built-in validation function:

```python
# Check integration status
status = validate_document_processor_integration()

for component, info in status.items():
    print(f"{component}: {info['status']}")
    print(f"  Details: {info['details']}")
```

Expected output:
```
✅ project_management_tab: Integrated
✅ chat_tab: Integrated  
✅ requirements_analysis_tab: Integrated
✅ traditional_upload: Integrated
✅ session_state_management: Standardized
✅ duplicate_detection: Unified
✅ error_handling: Standardized
```

## Support and Maintenance

### Regular Maintenance

1. **Monitor logs for errors:**
   ```bash
   grep "ERROR\|Failed\|Exception" logs/requirements_generation.log
   ```

2. **Check feature flag usage:**
   ```bash
   grep "Feature flags" logs/requirements_generation.log
   ```

3. **Monitor performance:**
   ```bash
   grep "Processing completed" logs/requirements_generation.log | tail -10
   ```

### Updates and Extensions

To add new features:

1. **Add feature flag:**
   ```python
   FEATURE_FLAGS['new_feature'] = False  # Start disabled
   ```

2. **Implement in unified processor:**
   ```python
   if FEATURE_FLAGS.get('new_feature', False):
       # New feature implementation
   ```

3. **Add UI control:**
   ```python
   new_flags['new_feature'] = st.checkbox(
       "Enable New Feature",
       value=FEATURE_FLAGS['new_feature'],
       help="Description of new feature"
   )
   ```

4. **Test thoroughly with fallbacks**

This integration approach ensures your app remains stable while gradually adopting advanced document processing capabilities. 