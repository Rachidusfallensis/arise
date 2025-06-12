#!/usr/bin/env python3
"""
SAFE MBSE RAG System - Evaluation Script

This script provides immediate evaluation capabilities for the SAFE MBSE RAG system.
Run this to get a comprehensive assessment of system performance.
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.rag_system import SAFEMBSERAGSystem
from config.config import *

class SAFEMBSEEvaluator:
    """Comprehensive evaluator for SAFE MBSE RAG system"""
    
    def __init__(self):
        """Initialize the evaluator with system components"""
        print("🚀 Initializing SAFE MBSE RAG Evaluator...")
        try:
            self.rag_system = SAFEMBSERAGSystem()
            self.evaluation_results = {}
            self.start_time = datetime.now()
            print("✅ System initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize system: {e}")
            sys.exit(1)
    
    def evaluate_system_connectivity(self) -> Dict[str, Any]:
        """Test basic system connectivity and model availability"""
        print("\n🔗 Testing System Connectivity...")
        results = {
            "server_accessible": False,
            "models_available": {},
            "embedding_model_working": False,
            "chat_model_working": False
        }
        
        try:
            # Test server connectivity
            import requests
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
            if response.status_code == 200:
                results["server_accessible"] = True
                models_data = response.json()
                available_models = [model.get('name', model.get('id', 'unknown')) 
                                  for model in models_data.get('models', models_data.get('data', []))]
                results["models_available"] = available_models
                print(f"✅ Server accessible: {len(available_models)} models found")
            else:
                print(f"❌ Server returned status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Server connectivity error: {e}")
        
        # Test embedding model
        try:
            test_embedding = self.rag_system.ollama_client.embeddings(
                model=EMBEDDING_MODEL,
                prompt="test"
            )
            if test_embedding and 'embedding' in test_embedding:
                results["embedding_model_working"] = True
                print(f"✅ Embedding model '{EMBEDDING_MODEL}' working")
            else:
                print(f"❌ Embedding model '{EMBEDDING_MODEL}' failed")
        except Exception as e:
            print(f"❌ Embedding model error: {e}")
        
        # Test chat model
        try:
            test_response = self.rag_system.ollama_client.chat(
                model="llama3:instruct",
                messages=[{"role": "user", "content": "Hello"}]
            )
            if test_response and 'message' in test_response:
                results["chat_model_working"] = True
                print(f"✅ Chat model 'llama3:instruct' working")
            else:
                print(f"❌ Chat model 'llama3:instruct' failed")
        except Exception as e:
            print(f"❌ Chat model error: {e}")
        
        return results
    
    def evaluate_requirement_generation(self) -> Dict[str, Any]:
        """Test requirement generation with sample proposals"""
        print("\n📝 Testing Requirement Generation...")
        
        # Sample test proposal
        test_proposal = """
        Project: Advanced Driver Assistance System (ADAS)
        
        Objective: Develop a comprehensive ADAS for passenger vehicles that enhances safety 
        and driving comfort through automated features including adaptive cruise control, 
        lane departure warning, and collision avoidance.
        
        Stakeholders:
        - Vehicle manufacturers
        - Safety regulators
        - End users (drivers and passengers)
        - Insurance companies
        
        Key Requirements:
        - System must detect obstacles within 150 meters
        - Response time must be under 100 milliseconds
        - System must operate in various weather conditions
        - Integration with existing vehicle systems required
        """
        
        results = {
            "generation_successful": False,
            "generation_time": 0,
            "requirements_generated": 0,
            "phases_covered": [],
            "requirement_types": [],
            "quality_metrics": {}
        }
        
        try:
            start_time = time.time()
            
            # Generate requirements
            generation_results = self.rag_system.generate_requirements_from_proposal(
                proposal_text=test_proposal,
                target_phase="all",
                requirement_types=["functional", "non_functional", "stakeholder"]
            )
            
            generation_time = time.time() - start_time
            results["generation_time"] = round(generation_time, 2)
            results["generation_successful"] = True
            
            # Analyze results
            if "requirements" in generation_results:
                total_reqs = 0
                phases = list(generation_results["requirements"].keys())
                req_types = set()
                
                for phase, phase_reqs in generation_results["requirements"].items():
                    for req_type, reqs in phase_reqs.items():
                        req_types.add(req_type)
                        total_reqs += len(reqs) if isinstance(reqs, list) else 0
                
                results["requirements_generated"] = total_reqs
                results["phases_covered"] = phases
                results["requirement_types"] = list(req_types)
                
                print(f"✅ Generated {total_reqs} requirements in {generation_time:.2f}s")
                print(f"   Phases: {', '.join(phases)}")
                print(f"   Types: {', '.join(req_types)}")
            
            # Calculate quality metrics
            if "statistics" in generation_results:
                stats = generation_results["statistics"]
                results["quality_metrics"] = {
                    "total_requirements": stats.get("total_requirements", 0),
                    "by_priority": stats.get("by_priority", {}),
                    "by_phase": stats.get("by_phase", {}),
                    "by_type": stats.get("by_type", {})
                }
            
        except Exception as e:
            print(f"❌ Requirement generation failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def evaluate_export_functionality(self) -> Dict[str, Any]:
        """Test all export formats"""
        print("\n📤 Testing Export Functionality...")
        
        # Sample requirements for testing
        test_requirements = {
            "requirements": {
                "operational": {
                    "functional": [
                        {
                            "id": "FUNC-OP-001",
                            "title": "System Activation",
                            "description": "The system shall activate automatically when vehicle speed exceeds 30 km/h",
                            "priority": "MUST",
                            "verification_method": "Test & Demonstration"
                        }
                    ],
                    "non_functional": [
                        {
                            "id": "NFUNC-OP-001",
                            "title": "Response Time",
                            "description": "System response time shall not exceed 100ms",
                            "priority": "MUST",
                            "verification_method": "Test & Analysis"
                        }
                    ]
                }
            }
        }
        
        results = {
            "formats_tested": [],
            "successful_exports": [],
            "failed_exports": [],
            "export_sizes": {}
        }
        
        for format_name in REQUIREMENTS_OUTPUT_FORMATS:
            try:
                exported_content = self.rag_system.export_requirements(test_requirements, format_name)
                results["formats_tested"].append(format_name)
                results["successful_exports"].append(format_name)
                results["export_sizes"][format_name] = len(exported_content)
                print(f"✅ {format_name}: {len(exported_content)} characters")
                
            except Exception as e:
                results["failed_exports"].append(format_name)
                print(f"❌ {format_name}: {e}")
        
        return results
    
    def evaluate_chat_functionality(self) -> Dict[str, Any]:
        """Test chat/query functionality"""
        print("\n💬 Testing Chat Functionality...")
        
        test_queries = [
            "What is ARCADIA methodology?",
            "Explain the operational analysis phase",
            "What are functional requirements?",
            "How do you validate requirements in MBSE?"
        ]
        
        results = {
            "queries_tested": len(test_queries),
            "successful_responses": 0,
            "failed_responses": 0,
            "average_response_time": 0,
            "response_lengths": [],
            "errors": []
        }
        
        total_time = 0
        
        for i, query in enumerate(test_queries):
            try:
                start_time = time.time()
                response_data = self.rag_system.query_documents(query)
                response_time = time.time() - start_time
                
                if isinstance(response_data, dict) and "answer" in response_data:
                    answer = response_data["answer"]
                    results["successful_responses"] += 1
                    results["response_lengths"].append(len(answer))
                    total_time += response_time
                    print(f"✅ Query {i+1}: {len(answer)} chars in {response_time:.2f}s")
                else:
                    results["failed_responses"] += 1
                    print(f"❌ Query {i+1}: Invalid response format")
                    
            except Exception as e:
                results["failed_responses"] += 1
                results["errors"].append(str(e))
                print(f"❌ Query {i+1}: {e}")
        
        if results["successful_responses"] > 0:
            results["average_response_time"] = round(total_time / results["successful_responses"], 2)
        
        return results
    
    def evaluate_cyderco_compliance(self) -> Dict[str, Any]:
        """Test CYDERCO benchmark compliance"""
        print("\n🎯 Testing CYDERCO Compliance...")
        
        # Sample requirements to test against CYDERCO
        sample_requirements = {
            "requirements": {
                "operational": {
                    "functional": [
                        {"id": "FUNC-001", "description": "Data correlation capabilities"},
                        {"id": "FUNC-002", "description": "Traffic monitoring functions"}
                    ],
                    "non_functional": [
                        {"id": "NFUNC-001", "description": "System scalability requirements"},
                        {"id": "NFUNC-002", "description": "Performance constraints"}
                    ]
                }
            }
        }
        
        results = {
            "evaluation_successful": False,
            "coverage_score": 0,
            "missing_requirements": [],
            "additional_requirements": [],
            "quality_metrics": {}
        }
        
        try:
            evaluation = self.rag_system.evaluate_against_cyderco(sample_requirements)
            
            results["evaluation_successful"] = True
            results["coverage_score"] = evaluation.get("coverage_score", 0)
            results["missing_requirements"] = evaluation.get("missing_requirements", [])
            results["additional_requirements"] = evaluation.get("additional_requirements", [])
            results["quality_metrics"] = evaluation.get("quality_metrics", {})
            
            print(f"✅ CYDERCO evaluation completed")
            print(f"   Coverage Score: {results['coverage_score']:.1f}%")
            print(f"   Missing Requirements: {len(results['missing_requirements'])}")
            print(f"   Additional Requirements: {len(results['additional_requirements'])}")
            
        except Exception as e:
            print(f"❌ CYDERCO evaluation failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def evaluate_performance_metrics(self) -> Dict[str, Any]:
        """Test system performance metrics"""
        print("\n⚡ Testing Performance Metrics...")
        
        results = {
            "vectorstore_stats": {},
            "memory_usage": "N/A",
            "processing_speed": {},
            "system_health": {}
        }
        
        try:
            # Test vectorstore statistics
            vectorstore_stats = self.rag_system.get_vectorstore_stats()
            results["vectorstore_stats"] = vectorstore_stats
            print(f"✅ Vectorstore: {vectorstore_stats.get('total_chunks', 0)} chunks")
            
            # Test processing speed with sample text
            sample_text = "This is a sample project proposal for testing processing speed. " * 100
            
            start_time = time.time()
            analysis = self.rag_system.analyze_text_with_enhanced_extraction(sample_text)
            processing_time = time.time() - start_time
            
            results["processing_speed"] = {
                "text_analysis_time": round(processing_time, 2),
                "text_length": len(sample_text),
                "processing_rate": round(len(sample_text) / processing_time, 2)
            }
            
            print(f"✅ Text processing: {processing_time:.2f}s for {len(sample_text)} chars")
            print(f"   Rate: {results['processing_speed']['processing_rate']:.2f} chars/sec")
            
        except Exception as e:
            print(f"❌ Performance evaluation failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def generate_evaluation_report(self) -> str:
        """Generate comprehensive evaluation report"""
        print("\n📊 Generating Evaluation Report...")
        
        report = {
            "evaluation_metadata": {
                "timestamp": self.start_time.isoformat(),
                "system_version": "SAFE MBSE RAG v1.0",
                "evaluator_version": "1.0",
                "evaluation_duration": str(datetime.now() - self.start_time)
            },
            "results": self.evaluation_results,
            "summary": {
                "overall_health": "Unknown",
                "critical_issues": [],
                "recommendations": []
            }
        }
        
        # Calculate overall health score
        health_score = 0
        max_score = 0
        critical_issues = []
        recommendations = []
        
        # Analyze connectivity
        if "connectivity" in self.evaluation_results:
            conn = self.evaluation_results["connectivity"]
            if conn.get("server_accessible", False):
                health_score += 20
            else:
                critical_issues.append("Server not accessible")
            
            if conn.get("embedding_model_working", False):
                health_score += 15
            else:
                critical_issues.append("Embedding model not working")
                
            if conn.get("chat_model_working", False):
                health_score += 15
            else:
                critical_issues.append("Chat model not working")
            
            max_score += 50
        
        # Analyze requirement generation
        if "requirement_generation" in self.evaluation_results:
            req_gen = self.evaluation_results["requirement_generation"]
            if req_gen.get("generation_successful", False):
                health_score += 25
                if req_gen.get("generation_time", 999) < 10:
                    health_score += 10
                else:
                    recommendations.append("Consider optimizing generation speed")
            else:
                critical_issues.append("Requirement generation failed")
            
            max_score += 35
        
        # Analyze export functionality
        if "export_functionality" in self.evaluation_results:
            export = self.evaluation_results["export_functionality"]
            successful_exports = len(export.get("successful_exports", []))
            total_formats = len(REQUIREMENTS_OUTPUT_FORMATS)
            if successful_exports == total_formats:
                health_score += 15
            elif successful_exports > 0:
                health_score += 10
                recommendations.append(f"Fix {total_formats - successful_exports} export formats")
            else:
                critical_issues.append("All export formats failed")
            
            max_score += 15
        
        # Calculate overall health
        if max_score > 0:
            health_percentage = (health_score / max_score) * 100
            if health_percentage >= 90:
                overall_health = "Excellent"
            elif health_percentage >= 75:
                overall_health = "Good"
            elif health_percentage >= 50:
                overall_health = "Fair"
            else:
                overall_health = "Poor"
        else:
            overall_health = "Unknown"
        
        report["summary"]["overall_health"] = f"{overall_health} ({health_score}/{max_score} - {health_percentage:.1f}%)"
        report["summary"]["critical_issues"] = critical_issues
        report["summary"]["recommendations"] = recommendations
        
        # Save report
        report_path = f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✅ Report saved to: {report_path}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
        
        return json.dumps(report, indent=2)
    
    def run_full_evaluation(self) -> Dict[str, Any]:
        """Run complete system evaluation"""
        print("=" * 60)
        print("🚀 SAFE MBSE RAG System Evaluation")
        print("=" * 60)
        
        # Run all evaluation components
        self.evaluation_results["connectivity"] = self.evaluate_system_connectivity()
        self.evaluation_results["requirement_generation"] = self.evaluate_requirement_generation()
        self.evaluation_results["export_functionality"] = self.evaluate_export_functionality()
        self.evaluation_results["chat_functionality"] = self.evaluate_chat_functionality()
        self.evaluation_results["cyderco_compliance"] = self.evaluate_cyderco_compliance()
        self.evaluation_results["performance_metrics"] = self.evaluate_performance_metrics()
        
        # Generate final report
        report = self.generate_evaluation_report()
        
        print("\n" + "=" * 60)
        print("✅ Evaluation Complete!")
        print("=" * 60)
        
        # Print summary
        summary = json.loads(report)["summary"]
        print(f"Overall Health: {summary['overall_health']}")
        
        if summary['critical_issues']:
            print("\n❌ Critical Issues:")
            for issue in summary['critical_issues']:
                print(f"   • {issue}")
        
        if summary['recommendations']:
            print("\n💡 Recommendations:")
            for rec in summary['recommendations']:
                print(f"   • {rec}")
        
        print(f"\nDetailed report available in evaluation_report_*.json")
        
        return self.evaluation_results


def main():
    """Main evaluation function"""
    evaluator = SAFEMBSEEvaluator()
    results = evaluator.run_full_evaluation()
    return results


if __name__ == "__main__":
    main()
