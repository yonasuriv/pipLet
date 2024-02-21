#!/usr/bin/env python3

import subprocess
import json
import sys
import re
import os

class Colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    PURPLE = '\033[35m'
    GREEN = '\033[92m'
    ORANGE = '\033[33m'
    YELLOW = '\033[93m'
    GREY = '\033[37m'
    DGREY = '\033[90m'
    RESET = '\033[0m'

def gather_installed_packages(verbose=False):

    print(f"\n{Colors.BLUE} [*]{Colors.RESET} Fetching all pip packages..")
    result = subprocess.run(['pip', 'list', '--format=json'], capture_output=True, text=True)
    installed_packages = json.loads(result.stdout)
    print(f"{Colors.GREEN} [\u2714]{Colors.RESET} {len(installed_packages)} installed packages found.")
    #for pkg in installed_packages:
    #    print(f"{Colors.CYAN}{pkg['name']}{Colors.RESET}: {pkg['version']}")
    return installed_packages

def gather_deprecated_packages(verbose=False):

    existing_deprecated = set()
    try:
        with open('.deprecated.txt', 'r') as file:
            existing_deprecated = {line.strip() for line in file}
    except FileNotFoundError:
        existing_deprecated = set()

    print(f"\n{Colors.BLUE} [*]{Colors.RESET} Checking for Deprecated Packages..")

    new_deprecated_packages = set()
    result = subprocess.run(['pip', 'check'], capture_output=True, text=True)

    # Adjust the logic to check for deprecated warnings in the output
    deprecated_packages = re.findall(r"DEPRECATION:.*?/dist-packages/([^\.-]+)", result.stderr)
    for warning in deprecated_packages:
        if warning not in existing_deprecated:
            new_deprecated_packages.add(warning)

    if len(deprecated_packages) == 0:
        print(f"{Colors.GREEN} [\u2714]{Colors.RESET} No deprecated packages found.")
    else:
        print(f"{Colors.YELLOW} [*]{Colors.RESET} {len(deprecated_packages)} deprecated package{'s' if deprecated_packages != 1 else ''} found.")
        print(f"{Colors.YELLOW} [*]{Colors.RESET} The following packages are using .egg modules: {', '.join([f'{Colors.ORANGE}{pkg}{Colors.RESET}' for pkg in deprecated_packages])}.")
        print(f"{Colors.GREY} [I] Egg is deprecated and pip 24.3 will enforce the behaviour change.{Colors.RESET}")
        print(f"{Colors.GREY} [I] Discussion can be found at https://github.com/pypa/pip/issues/12330.{Colors.RESET}")
        print(f"{Colors.GREY} [I]{Colors.RESET} {Colors.GREY}Please talk with the developers to update their packages to a newer version or they will become obsolete.")
        print(f"{Colors.RED} [X]{Colors.RESET} Skipping deprecated packages.")

    # Append only new deprecated packages to deprecated.txt
    with open('deprecated.txt', 'a') as f:
        for pkg in new_deprecated_packages:
            f.write(f"{pkg}\n")
    
    return existing_deprecated.union(new_deprecated_packages)

def print_deprecated_packages(verbose=True):
    try:
        with open('deprecated.txt', 'r') as file:
            deprecated_packages = [line.strip() for line in file]
            if deprecated_packages:
                print(f"{Colors.ORANGE} [*]{Colors.RESET} Deprecated packages:")
                for pkg in deprecated_packages:
                    print(f" {Colors.ORANGE}{pkg}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN} [\u2714]{Colors.RESET} No deprecated packages found.")
    except FileNotFoundError:
        print(f"{Colors.RED}[!]{Colors.RESET} 'deprecated.txt' file not found.")

def upgrade_outdated_packages(verbose=False):
    print(f"\n{Colors.BLUE} [*]{Colors.RESET} Checking for Outdated Packages..")
    
    result = subprocess.run(['pip', 'list', '--outdated', '--format=json'], capture_output=True, text=True)
    outdated_packages = json.loads(result.stdout)

    if len(outdated_packages) == 0:
        print(f"{Colors.GREEN} [\u2714]{Colors.RESET} No outdated packages found.")
        
    else:
        print(f"{Colors.YELLOW} [*]{Colors.RESET} {len(outdated_packages)} outdated package{'s' if len(outdated_packages) != 1 else ''} found.")
        
    for package in outdated_packages:
        name = package['name']
        print(f"{Colors.ORANGE} [>]{Colors.RESET} Upgrading {name} {Colors.DGREY}from {package['version']} to {package['latest_version']}{Colors.RESET}")
        if not verbose:
            subprocess.run(['pip', 'install', '--upgrade', name], capture_output=True, text=True)
        else:
            subprocess.run(['pip', 'install', '--upgrade', name], capture_output=False, text=True)

        # Check if installation was successful
        if result.returncode == 0:
            print(f"{Colors.GREEN} [\u2714]{Colors.RESET} Done.")
        else:
            print(f"{Colors.RED} [x]{Colors.RESET} Failed to upgrade package: {name}. Error: {result.stderr}")
            

def install_missing_dependencies(verbose=False):

    print(f"\n{Colors.BLUE} [*]{Colors.RESET} Checking for Missing Dependencies..")

    with open('.dependencies-tmp.txt', 'w') as f:
        result = subprocess.run(['pip', 'check'], stdout=f, stderr=subprocess.DEVNULL)

    with open('.dependencies-tmp.txt', 'r') as dependency_packages_in, open('.dependencies-tmp-2.txt', 'w') as dependency_packages_out:
        for line in dependency_packages_in:
            if not line.startswith('DEPRECATION'):
                words = line.split()
                if words[2] == 'requires': # Check if the dependency is not installed
                    package = words[0]
                    dependency = words[3].split(',')[0]
                    dependency_packages_out.write(f"{package} {dependency}\n")

                    print(f"{Colors.RED} [!]{Colors.RESET} Missing {dependency}, which is required for {package}.")
                    subprocess.run(['pip', 'install', '--upgrade', package], capture_output=True, text=True)
                    print(f"{Colors.GREEN} [\u2714]{Colors.RESET} {Colors.DGREY}{dependency} installed successfully.{Colors.GREEN}")

                else: # Check if the dependency is outdated
                    package = words[0]
                    dependency = words[4].split('<')[0]
                    dependency = words[4].split('>')[0] if '>' in dependency else dependency
                    dependency = dependency.split('~')[0] if '~' in dependency else dependency
                    dependency = dependency.split('=')[0] if '=' in dependency else dependency
                    dependency_packages_out.write(f"{package} {dependency}\n")

                    print(f"{Colors.YELLOW} [>]{Colors.RESET} Outdated {dependency} found, which is required for {package}.")
                    subprocess.run(['pip', 'install', '--upgrade', package], capture_output=True, text=True)
                    print(f"{Colors.GREEN} [\u2714]{Colors.RESET} {Colors.DGREY}{dependency} upgraded successfully.{Colors.GREEN}")
      
        # Delete the temporary file
        os.remove('.dependencies-tmp.txt')
        os.remove('.dependencies-tmp-2.txt')
          
        print(f"\n{Colors.GREEN} [\u2714] All packages are updated to their latest version.{Colors.RESET}")

def main():
    verbose = '-v' in sys.argv
    dependencies = '-d' in sys.argv

    if dependencies:
        print_deprecated_packages()
        return 

    gather_installed_packages(verbose)
    gather_deprecated_packages(verbose)
    upgrade_outdated_packages(verbose)
    install_missing_dependencies(verbose)

if __name__ == "__main__":
    main()
