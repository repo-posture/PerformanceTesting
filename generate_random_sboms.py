#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import datetime
import shutil
from pathlib import Path

# Default configuration
DEFAULT_COMPONENT_COUNT = 1000
DEFAULT_OUTPUT_DIR = "sboms"
COMPONENTS_FILE = "components.json"
SBOM_OUTPUT = "sbom.json"


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate random SBOMs and store them in the sboms directory"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_COMPONENT_COUNT,
        help=f"Number of components to generate (default: {DEFAULT_COMPONENT_COUNT})",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to store generated SBOMs (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--sboms",
        type=int,
        default=1,
        help="Number of SBOMs to generate (default: 1)",
    )
    parser.add_argument(
        "--installed-ratio",
        type=float,
        default=0.7,
        help="Ratio of installed components (vs. custom) (default: 0.7)",
    )
    parser.add_argument(
        "--format",
        choices=["cyclonedx", "spdx"],
        default="cyclonedx",
        help="SBOM format (default: cyclonedx)",
    )
    return parser.parse_args()


def ensure_output_directory(output_dir):
    """Ensure the output directory exists."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"✅ Output directory: {output_dir}")


def generate_components(count, installed_ratio=0.7):
    """Generate random components using the generate_components.py script."""
    print(f"🔄 Generating {count} random components...")
    try:
        result = subprocess.run(
            [
                "python3",
                "generate_components.py",
                "--count",
                str(count),
                "--installed-ratio",
                str(installed_ratio),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating components: {e}")
        print(f"Error output: {e.stderr}")
        return False


def generate_sbom(output_file, sbom_format="cyclonedx"):
    """Generate SBOM using the sbom_generator.py script."""
    print(f"🔄 Generating SBOM in {sbom_format} format...")
    try:
        result = subprocess.run(
            [
                "python3",
                "sbom_generator.py",
                "--format",
                sbom_format,
                "--output",
                SBOM_OUTPUT,
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        print("\n".join(result.stdout.splitlines()[-5:]))  # Print last few lines of output
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating SBOM: {e}")
        print(f"Error output: {e.stderr}")
        return False


def generate_unique_filename(output_dir, sbom_format, component_count, sequential_number):
    """Generate a sequential filename for the SBOM in format: sbom_{format}_{count}_{sequential}."""
    filename = f"sbom_{sbom_format}_{component_count}_{sequential_number}.json"
    return os.path.join(output_dir, filename)


def copy_sbom_to_output(output_file):
    """Copy the generated SBOM to the output directory."""
    if not os.path.exists(SBOM_OUTPUT):
        print(f"❌ Generated SBOM file not found: {SBOM_OUTPUT}")
        return False
    
    try:
        shutil.copy2(SBOM_OUTPUT, output_file)
        print(f"✅ SBOM saved to {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error copying SBOM to output directory: {e}")
        return False


def main():
    args = parse_arguments()
    
    # Ensure output directory exists
    ensure_output_directory(args.output_dir)
    
    # Generate multiple SBOMs if requested
    for i in range(args.sboms):
        sequential_number = i + 1  # Sequential numbering starting from 1
        print(f"\n{'=' * 50}")
        print(f"Generating SBOM {sequential_number}/{args.sboms}")
        print(f"{'=' * 50}")
        
        # Generate random components
        if not generate_components(args.count, args.installed_ratio):
            print("❌ Failed to generate components. Skipping SBOM generation.")
            continue
        
        # Generate SBOM
        if not generate_sbom(SBOM_OUTPUT, args.format):
            print("❌ Failed to generate SBOM.")
            continue
        
        # Generate sequential filename for this SBOM
        output_file = generate_unique_filename(args.output_dir, args.format, args.count, sequential_number)
        
        # Copy SBOM to output directory
        copy_sbom_to_output(output_file)
    
    print(f"\n✅ Generated {args.sboms} SBOMs successfully!")
    print(f"📁 Check the {args.output_dir} directory for your SBOM files")


if __name__ == "__main__":
    main()
# python3 generate_random_sboms.py --count 1000 --sboms 100