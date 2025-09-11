#!/usr/bin/env python3
"""
Script to generate a Harness pipeline YAML with a specified number of SSCA Orchestration steps.
Each step will have a sequential name and identifier.
"""

import yaml
import argparse
from pathlib import Path

def generate_steps(count):
    """Generate a list of SSCA Orchestration steps with sequential numbering."""
    steps = []
    for i in range(1, count + 1):
        # Calculate the file number for this step (20000, 20001, 20002, etc.)
        file_number = 20000 + i
        sbom_path = f'/harness/src/sboms/synthetic_cyclonedx_{file_number}_c1.json'
        
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
                        'artifact_name': 'perf-test',
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

def generate_pipeline(step_count):
    """Generate the complete pipeline YAML with the specified number of steps."""
    pipeline = {
        'pipeline': {
            'name': 'Performance Testing',
            'identifier': 'Performance_Testing',
            'projectIdentifier': 'SSCA_Sanity_Automation',
            'orgIdentifier': 'SSCA',
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
                                            {'step': step} for step in generate_steps(step_count)
                                        ]
                                    }
                                ]
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
    parser.add_argument('--output', type=str, default='pipeline_generated.yaml', 
                       help='Output YAML file (default: pipeline_generated.yaml)')
    
    args = parser.parse_args()
    
    if args.step_count <= 0:
        print("Error: step_count must be a positive integer")
        return 1
    
    pipeline = generate_pipeline(args.step_count)
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the YAML file
    with open(output_path, 'w') as f:
        yaml.dump(pipeline, f, default_flow_style=False, sort_keys=False)
    
    print(f"Successfully generated pipeline with {args.step_count} SSCA Orchestration steps in {output_path}")
    return 0

if __name__ == "__main__":
    exit(main())
