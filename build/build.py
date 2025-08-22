#!/usr/bin/env python3
"""
CodeObit CLI Cross-Platform Build Script
Detects the operating system and runs the appropriate build process
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def print_banner():
    """Print the build script banner"""
    print("=" * 60)
    print("CodeObit CLI Cross-Platform Build Script")
    print("=" * 60)
    print(f"Build started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {sys.version}")
    print("=" * 60)
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} is installed")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0.0"])
        print("✓ PyInstaller installed successfully")
    
    # Check project dependencies
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"
    
    if requirements_file.exists():
        print("Installing project dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✓ Project dependencies installed")
    else:
        print("⚠ Warning: requirements.txt not found")
    
    print()

def clean_build_artifacts(project_root):
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")
    
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    
    # Remove dist directory
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("✓ Removed previous dist directory")
    
    # Clean build directory (keep the directory but remove PyInstaller files)
    if build_dir.exists():
        for item in build_dir.iterdir():
            if item.suffix in ['.log', '.toc', '.pyz'] or item.name.startswith('warn-'):
                item.unlink()
                print(f"✓ Removed {item.name}")
    
    print("✓ Build artifacts cleaned")
    print()

def build_with_pyinstaller(project_root):
    """Build the executable using PyInstaller"""
    spec_file = project_root / "codeobit.spec"
    
    if not spec_file.exists():
        print(f"✗ Error: Spec file not found at {spec_file}")
        return False
    
    print("Building executable with PyInstaller...")
    print(f"Spec file: {spec_file}")
    print()
    
    try:
        # Run PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", str(spec_file)]
        print(f"Running: {' '.join(cmd)}")
        print()
        
        result = subprocess.run(cmd, cwd=project_root, capture_output=False)
        
        if result.returncode == 0:
            print("✓ PyInstaller build completed successfully")
            return True
        else:
            print(f"✗ PyInstaller build failed with return code {result.returncode}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ PyInstaller build failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during build: {e}")
        return False

def verify_build(project_root):
    """Verify that the build was successful"""
    print("Verifying build...")
    
    system = platform.system().lower()
    dist_dir = project_root / "dist"
    
    if system == "windows":
        exe_path = dist_dir / "codeobit.exe"
    else:
        exe_path = dist_dir / "codeobit"
    
    if not exe_path.exists():
        print(f"✗ Executable not found at {exe_path}")
        return False
    
    # Get file size
    file_size = exe_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"✓ Executable found: {exe_path}")
    print(f"✓ File size: {file_size:,} bytes ({file_size_mb:.1f} MB)")
    
    # Make executable on Unix systems
    if system != "windows":
        exe_path.chmod(0o755)
        print("✓ Execute permissions set")
    
    # Test the executable
    try:
        result = subprocess.run([str(exe_path), "--help"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ Executable test passed")
        else:
            print(f"⚠ Executable test returned code {result.returncode}")
            print(f"  stdout: {result.stdout[:200]}...")
            print(f"  stderr: {result.stderr[:200]}...")
    except subprocess.TimeoutExpired:
        print("⚠ Executable test timed out")
    except Exception as e:
        print(f"⚠ Executable test failed: {e}")
    
    return True

def create_distribution_package(project_root):
    """Create a distribution package"""
    print("Creating distribution package...")
    
    system = platform.system().lower()
    architecture = platform.machine().lower()
    dist_dir = project_root / "dist"
    
    # Map architecture names
    arch_map = {
        'x86_64': 'x64',
        'amd64': 'x64',
        'i386': 'x86',
        'i686': 'x86',
        'aarch64': 'arm64',
        'arm64': 'arm64'
    }
    arch = arch_map.get(architecture, architecture)
    
    if system == "windows":
        exe_name = "codeobit.exe"
        package_name = f"codeobit-windows-{arch}.zip"
    else:
        exe_name = "codeobit"
        package_name = f"codeobit-{system}-{arch}.tar.gz"
    
    exe_path = dist_dir / exe_name
    package_path = dist_dir / package_name
    
    if not exe_path.exists():
        print(f"✗ Executable not found: {exe_path}")
        return False
    
    try:
        if system == "windows":
            # Create ZIP package for Windows
            import zipfile
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(exe_path, exe_name)
                
                # Add README if exists
                readme_path = project_root / "README.md"
                if readme_path.exists():
                    zipf.write(readme_path, "README.md")
                    
                # Add LICENSE if exists
                license_path = project_root / "LICENSE"
                if license_path.exists():
                    zipf.write(license_path, "LICENSE")
        else:
            # Create TAR.GZ package for Unix systems
            import tarfile
            with tarfile.open(package_path, 'w:gz') as tar:
                tar.add(exe_path, arcname=exe_name)
                
                # Add README if exists
                readme_path = project_root / "README.md"
                if readme_path.exists():
                    tar.add(readme_path, arcname="README.md")
                    
                # Add LICENSE if exists
                license_path = project_root / "LICENSE"
                if license_path.exists():
                    tar.add(license_path, arcname="LICENSE")
        
        package_size = package_path.stat().st_size
        package_size_mb = package_size / (1024 * 1024)
        
        print(f"✓ Distribution package created: {package_path}")
        print(f"✓ Package size: {package_size:,} bytes ({package_size_mb:.1f} MB)")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to create distribution package: {e}")
        return False

def main():
    """Main build function"""
    try:
        print_banner()
        
        # Get project root
        project_root = Path(__file__).parent.parent
        print(f"Project root: {project_root}")
        print()
        
        # Change to project root
        os.chdir(project_root)
        
        # Check dependencies
        check_dependencies()
        
        # Clean previous builds
        clean_build_artifacts(project_root)
        
        # Build with PyInstaller
        if not build_with_pyinstaller(project_root):
            print("✗ Build failed!")
            return 1
        
        print()
        
        # Verify build
        if not verify_build(project_root):
            print("✗ Build verification failed!")
            return 1
        
        print()
        
        # Create distribution package
        if not create_distribution_package(project_root):
            print("⚠ Failed to create distribution package")
        
        print()
        print("=" * 60)
        print("BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("Build artifacts:")
        
        dist_dir = project_root / "dist"
        if dist_dir.exists():
            for item in dist_dir.iterdir():
                if item.is_file():
                    size = item.stat().st_size
                    size_mb = size / (1024 * 1024)
                    print(f"  - {item.name}: {size:,} bytes ({size_mb:.1f} MB)")
        
        print()
        print("To distribute the application:")
        print("1. Use the standalone executable from the dist/ directory")
        print("2. Or distribute the compressed package")
        print("3. No additional dependencies required on target systems")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n✗ Build cancelled by user")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())