#!/usr/bin/env python3
"""
Script to generate a Harness pipeline YAML with a specified number of SSCA Orchestration steps.
Each step will have a sequential name and identifier.
"""

import yaml
import argparse
from pathlib import Path

def generate_steps(count, component_count=1000, sbom_format='cyclonedx'):
    """Generate a list of SSCA Orchestration steps with sequential numbering."""
    steps = []
    for i in range(1, count + 1):
        # Use the new filename format: sbom_{format}_{component_count}_{sequential_number}.json
        sbom_filename = f'sbom_{sbom_format}_{component_count}_{i}.json'
        sbom_path = f'/harness/src/sboms/{sbom_filename}'
        
        step = {
            'type': 'SscaOrchestration',
            'name': f'SBOM Orchestration_{i}',
            'identifier': f'SBOMOrchestration_{i}',
            'spec': {
                'mode': 'ingestion',
                'ingestion': {
                    'file': sbom_path
                },
                'source': {
                    'type': 'local',
                    'spec': {
                        'workspace': sbom_path,
                        'artifact_name': f'perf-test-{i}',  # Unique artifact name for each step
                        'type': 'manual'
                    }
                },
                'resources': {
                    'limits': {
                        'memory': '500Mi',
                        'cpu': '0.5'
                    }
                }
            }
        }
        steps.append(step)
    return steps

def generate_pipeline(step_count, component_count=1000, sbom_format='cyclonedx', 
                     project_id='test_ssca_proj_qxSj5T2JXR', 
                     org_id='test_ssca_org_CXdrOvrGvY'):
    """Generate the complete pipeline YAML with the specified number of steps."""
    pipeline = {
        'pipeline': {
            'name': 'Performance Testing',
            'identifier': 'Performance_Testing',
            'projectIdentifier': project_id,
            'orgIdentifier': org_id,
            'tags': {},
            'stages': [
                {
                    'stage': {
                        'name': 'build',
                        'identifier': 'build',
                        'description': "",
                        'type': 'CI',
                        'spec': {
                            'cloneCodebase': False,
                            'caching': {
                                'enabled': True,
                                'override': True
                            },
                            'buildIntelligence': {
                                'enabled': True
                            },
                            'execution': {
                                'steps': [
                                    {
                                        'step': {
                                            'type': 'GitClone',
                                            'name': 'GitClone_1',
                                            'identifier': 'GitClone_1',
                                            'spec': {
                                                'connectorRef': 'perf_test_for_at',
                                                'repoName': 'https://github.com/repo-posture/PerformanceTesting',
                                                'cloneDirectory': '/harness/src',
                                                'build': {
                                                    'type': 'branch',
                                                    'spec': {
                                                        'branch': 'main'
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    {
                                        'parallel': [
                                            {'step': step} for step in generate_steps(step_count, component_count, sbom_format)
                                        ]
                                    }
                                ]
                            },
                            'infrastructure': {
                                'type': 'KubernetesDirect',
                                'spec': {
                                    'connectorRef': 'kubernetes_connector_for_at',
                                    'namespace': 'ssca-at',
                                    'automountServiceAccountToken': True,
                                    'nodeSelector': {},
                                    'os': 'Linux'
                                }
                            }
                        }
                    }
                }
            ]
        }
    }
    return pipeline

def main():
    parser = argparse.ArgumentParser(description='Generate a Harness pipeline YAML with specified number of SSCA steps')
    parser.add_argument('step_count', type=int, help='Number of SSCA Orchestration steps to generate')
    parser.add_argument('--components', type=int, default=1000, 
                       help='Number of components in each SBOM (default: 1000)')
    parser.add_argument('--format', type=str, default='cyclonedx',
                       choices=['cyclonedx', 'spdx'],
                       help='SBOM format (default: cyclonedx)')
    parser.add_argument('--output', type=str, default='pipeline_generated.yaml', 
                       help='Output YAML file (default: pipeline_generated.yaml)')
    parser.add_argument('--project-id', type=str, default='test_ssca_proj_qxSj5T2JXR',
                       help='Project identifier (default: test_ssca_proj_qxSj5T2JXR)')
    parser.add_argument('--org-id', type=str, default='test_ssca_org_CXdrOvrGvY',
                       help='Organization identifier (default: test_ssca_org_CXdrOvrGvY)')
    
    args = parser.parse_args()
    
    if args.step_count <= 0:
        print("Error: step_count must be a positive integer")
        return 1
    
    pipeline = generate_pipeline(args.step_count, args.components, args.format, 
                               args.project_id, args.org_id)
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the YAML file
    with open(output_path, 'w') as f:
        yaml.dump(pipeline, f, default_flow_style=False, sort_keys=False, width=1000)
    
    print(f"Successfully generated pipeline with {args.step_count} SSCA Orchestration steps")
    print(f"  - SBOM format: {args.format}")
    print(f"  - Components per SBOM: {args.components}")
    print(f"  - Project ID: {args.project_id}")
    print(f"  - Organization ID: {args.org_id}")
    print(f"  - Output file: {output_path}")
    return 0

if __name__ == "__main__":
    exit(main())
# python3 generate_pipeline_with_parallel_sbom_orchestration.py 100 --output pipeline_100_sboms_runtime.yaml