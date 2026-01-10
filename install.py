#!/usr/bin/env python3
"""
Universal Installer for SECI AI Assistant (Jarvis)

This script automatically installs SECI on any platform with minimal user interaction.
Works on Linux, macOS, Windows, and ARM-based devices.
"""

import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path
import argparse


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a header message."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")


def print_success(text):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_info(text):
    """Print an info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def detect_platform():
    """Detect the current platform and return info."""
    system = platform.system()
    machine = platform.machine()
    
    info = {
        'system': system,
        'machine': machine,
        'is_arm': machine.lower() in ['arm64', 'aarch64', 'armv7l', 'armv8'],
        'is_mobile': False,  # Would need additional detection for mobile
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }
    
    # Detect if running on limited resources
    try:
        import psutil
        info['ram_gb'] = psutil.virtual_memory().total / (1024**3)
        info['cpu_count'] = os.cpu_count()
    except ImportError:
        info['ram_gb'] = None
        info['cpu_count'] = os.cpu_count()
    
    return info


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print_error(f"Python 3.8+ is required. You have {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")


def check_pip():
    """Check if pip is available."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print_success("pip is available")
        return True
    except subprocess.CalledProcessError:
        print_error("pip is not available")
        return False


def create_venv(venv_path):
    """Create a virtual environment."""
    print_info(f"Creating virtual environment at {venv_path}...")
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        print_success("Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False


def get_venv_pip(venv_path):
    """Get the pip executable from the virtual environment."""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "pip")
    else:
        return os.path.join(venv_path, "bin", "pip")


def get_venv_python(venv_path):
    """Get the python executable from the virtual environment."""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "python")
    else:
        return os.path.join(venv_path, "bin", "python")


def install_dependencies(venv_path, minimal=False):
    """Install required dependencies."""
    pip_cmd = get_venv_pip(venv_path)
    
    print_info("Installing dependencies...")
    
    # Upgrade pip first
    try:
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], 
                      capture_output=True, check=True)
        print_success("pip upgraded")
    except subprocess.CalledProcessError:
        print_warning("Failed to upgrade pip, continuing...")
    
    # Install requirements
    requirements_file = "requirements.txt"
    if minimal and os.path.exists("requirements-minimal.txt"):
        requirements_file = "requirements-minimal.txt"
    
    if os.path.exists(requirements_file):
        try:
            print_info(f"Installing from {requirements_file}...")
            subprocess.run([pip_cmd, "install", "-r", requirements_file], 
                          check=True)
            print_success("Dependencies installed")
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install dependencies: {e}")
            return False
    
    # Install package in editable mode
    try:
        print_info("Installing SECI package...")
        subprocess.run([pip_cmd, "install", "-e", "."], check=True)
        print_success("SECI package installed")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install SECI package: {e}")
        return False
    
    return True


def create_executable_script():
    """Create the jarvis executable script."""
    print_info("Creating jarvis command...")
    
    jarvis_script = """#!/usr/bin/env python3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from jarvis import main

if __name__ == "__main__":
    main()
"""
    
    with open("jarvis_cli.py", "w") as f:
        f.write(jarvis_script)
    
    # Make executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod("jarvis_cli.py", 0o755)
    
    print_success("jarvis command created")


def setup_systemd_service():
    """Create systemd service template for Linux."""
    if platform.system() != "Linux":
        return
    
    print_info("Creating systemd service template...")
    
    service_template = f"""[Unit]
Description=SECI AI Assistant (Jarvis)
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'seci')}
WorkingDirectory={os.getcwd()}
Environment="PATH={os.getcwd()}/venv/bin"
ExecStart={os.getcwd()}/venv/bin/python {os.getcwd()}/api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_dir = Path("systemd")
    service_dir.mkdir(exist_ok=True)
    
    with open(service_dir / "jarvis.service", "w") as f:
        f.write(service_template)
    
    print_success("Systemd service template created at systemd/jarvis.service")
    print_info("To install: sudo cp systemd/jarvis.service /etc/systemd/system/")
    print_info("Then: sudo systemctl enable jarvis && sudo systemctl start jarvis")


def run_config_wizard():
    """Run initial configuration wizard."""
    print_header("Configuration Wizard")
    
    config = {}
    
    # Ask for basic preferences
    print("Let's set up your SECI AI Assistant!")
    print()
    
    # API port
    default_port = "8000"
    port = input(f"API port [{default_port}]: ").strip() or default_port
    config['api_port'] = port
    
    # Enable features
    enable_search = input("Enable web search? [Y/n]: ").strip().lower() != 'n'
    config['enable_search'] = enable_search
    
    # Save config
    config_dir = Path.home() / ".seci"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.json"
    import json
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print_success(f"Configuration saved to {config_file}")
    return config


def main():
    """Main installation process."""
    parser = argparse.ArgumentParser(
        description="Universal installer for SECI AI Assistant (Jarvis)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard installation
  python install.py
  
  # Minimal installation for limited resources
  python install.py --minimal
  
  # Skip configuration wizard
  python install.py --no-config
        """
    )
    
    parser.add_argument("--minimal", action="store_true",
                       help="Install with minimal dependencies for low-resource devices")
    parser.add_argument("--no-config", action="store_true",
                       help="Skip configuration wizard")
    parser.add_argument("--no-venv", action="store_true",
                       help="Skip virtual environment creation (install globally)")
    
    args = parser.parse_args()
    
    print_header("SECI AI Assistant (Jarvis) - Universal Installer")
    
    # Detect platform
    print_info("Detecting platform...")
    platform_info = detect_platform()
    print_success(f"Platform: {platform_info['system']} ({platform_info['machine']})")
    print_success(f"Python: {platform_info['python_version']}")
    
    if platform_info.get('ram_gb'):
        print_success(f"RAM: {platform_info['ram_gb']:.1f} GB")
        if platform_info['ram_gb'] < 2 and not args.minimal:
            print_warning("Low RAM detected. Consider using --minimal flag")
    
    if platform_info.get('cpu_count'):
        print_success(f"CPU cores: {platform_info['cpu_count']}")
    
    if platform_info['is_arm']:
        print_info("ARM platform detected - optimizations will be applied")
    
    # Check prerequisites
    print_header("Checking Prerequisites")
    check_python_version()
    
    if not check_pip():
        print_error("Please install pip and try again")
        sys.exit(1)
    
    # Create virtual environment
    if not args.no_venv:
        print_header("Setting Up Virtual Environment")
        venv_path = "venv"
        
        if os.path.exists(venv_path):
            response = input(f"Virtual environment already exists at {venv_path}. Recreate? [y/N]: ")
            if response.lower() == 'y':
                print_info("Removing existing virtual environment...")
                shutil.rmtree(venv_path)
                create_venv(venv_path)
            else:
                print_info("Using existing virtual environment")
        else:
            create_venv(venv_path)
        
        # Install dependencies
        print_header("Installing Dependencies")
        if not install_dependencies(venv_path, minimal=args.minimal):
            print_error("Installation failed!")
            sys.exit(1)
    else:
        print_warning("Skipping virtual environment creation")
        print_info("Installing dependencies globally...")
        # Install without venv
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                          check=True)
        except subprocess.CalledProcessError:
            print_error("Failed to install dependencies")
            sys.exit(1)
    
    # Create executable script
    print_header("Setting Up CLI")
    create_executable_script()
    
    # Setup service templates
    print_header("Creating Service Templates")
    setup_systemd_service()
    
    # Configuration wizard
    if not args.no_config:
        config = run_config_wizard()
    
    # Final instructions
    print_header("Installation Complete!")
    print()
    print_success("SECI AI Assistant (Jarvis) is now installed!")
    print()
    print(f"{Colors.BOLD}Quick Start:{Colors.ENDC}")
    print()
    
    if not args.no_venv:
        if platform.system() == "Windows":
            print(f"  1. Activate environment: .\\venv\\Scripts\\activate")
        else:
            print(f"  1. Activate environment: source venv/bin/activate")
    
    print(f"  2. Run Jarvis CLI: python jarvis.py")
    print(f"  3. Start API server: python api.py")
    print(f"  4. Test CLI: python cli_test.py health")
    print()
    print(f"{Colors.BOLD}Examples:{Colors.ENDC}")
    print()
    print(f"  # Interactive mode")
    print(f"  python jarvis.py --interactive")
    print()
    print(f"  # Ask a question")
    print(f"  python jarvis.py ask \"What is machine learning?\"")
    print()
    print(f"  # Search the web")
    print(f"  python jarvis.py search \"latest AI developments\"")
    print()
    print_success("For more information, see README.md")
    print()


if __name__ == "__main__":
    main()
