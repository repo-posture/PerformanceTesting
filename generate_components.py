#!/usr/bin/env python3
import json
import random
import argparse
import subprocess
from pathlib import Path

# Common package names to use when generating installed components
COMMON_PACKAGES = [
    "requests", "numpy", "pandas", "matplotlib", "flask", "django", "sqlalchemy", 
    "pytest", "pillow", "tensorflow", "torch", "boto3", "scikit-learn", "scipy",
    "beautifulsoup4", "pyyaml", "cryptography", "psycopg2", "fastapi", "aiohttp",
    "jinja2", "celery", "click", "pydantic", "pymongo", "redis", "marshmallow", 
    "httpx", "attrs", "tqdm", "seaborn", "streamlit", "networkx", "nltk", "dash"
]

# Common licenses to use when generating custom components
COMMON_LICENSES = [
    "MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "LGPL-2.1", 
    "MPL-2.0", "BSD-2-Clause", "AGPL-3.0", "ISC", "Unlicense", "CC0-1.0"
]

def get_installed_packages():
    """Get a list of packages actually installed in the current environment"""
    try:
        result = subprocess.run(['pip', 'list', '--format', 'json'], 
                                capture_output=True, text=True, check=True)
        return [pkg['name'] for pkg in json.loads(result.stdout)]
    except Exception as e:
        print(f"Warning: Could not get installed packages: {e}")
        return COMMON_PACKAGES

def generate_components(total_count, installed_ratio=0.7, use_real_packages=True, output_file="components.json"):
    """
    Generate a components.json file with the specified number of components.
    
    Args:
        total_count (int): The total number of components to generate
        installed_ratio (float): Ratio of installed components (vs custom)
        use_real_packages (bool): Use actually installed packages for 'installed' type
        output_file (str): Path to output file
    """
    # Calculate counts
    installed_count = int(total_count * installed_ratio)
    custom_count = total_count - installed_count
    
    # Get available packages
    if use_real_packages:
        available_packages = get_installed_packages()
        # Fallback to common packages if we don't have enough real ones
        if len(available_packages) < installed_count:
            available_packages.extend(COMMON_PACKAGES)
            available_packages = list(set(available_packages))  # Remove duplicates
    else:
        available_packages = COMMON_PACKAGES
    
    # Generate components
    components = []
    
    # Generate installed components
    for _ in range(installed_count):
        if available_packages:
            package = random.choice(available_packages)
            available_packages.remove(package)  # Avoid duplicates
            components.append({"type": "installed", "name": package})
        else:
            # If we run out of known packages, create fake ones
            fake_package = f"package-{random.randint(1000, 9999)}"
            components.append({"type": "installed", "name": fake_package})
    
    # Generate custom components
    for i in range(custom_count):
        components.append({
            "type": "custom",
            "name": f"custom-library-{i+1}",
            "version": f"{random.randint(0, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "license": random.choice(COMMON_LICENSES)
        })
    
    # Shuffle components to mix installed and custom
    random.shuffle(components)
    
    # Write to file
    with open(output_file, 'w') as f:
        json.dump(components, f, indent=4)
    
    print(f"✅ Generated {len(components)} components ({installed_count} installed, {custom_count} custom)")
    print(f"   Output written to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate a components.json file for SBOM testing')
    parser.add_argument('--count', type=int, required=True, 
                      help='Total number of components to generate')
    parser.add_argument('--installed-ratio', type=float, default=0.7,
                      help='Ratio of installed components (vs. custom) (default: 0.7)')
    parser.add_argument('--output', default='components.json',
                      help='Output file path (default: components.json)')
    parser.add_argument('--use-fake-packages', action='store_true',
                      help='Use only fake package names instead of real installed ones')
    
    args = parser.parse_args()
    
    if args.count <= 0:
        parser.error("--count must be a positive number")
    if not 0 <= args.installed_ratio <= 1:
        parser.error("--installed-ratio must be between 0.0 and 1.0")
    
    # Generate components
    generate_components(
        args.count,
        installed_ratio=args.installed_ratio,
        use_real_packages=not args.use_fake_packages,
        output_file=args.output
    )

if __name__ == "__main__":
    main()
