"""
Enhanced project analysis and build system for codeobit
Provides comprehensive project analysis, dependency management, and build capabilities
"""

import ast
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ProjectHealth:
    """Project health assessment metrics"""
    score: float  # 0-100
    issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    dependencies_status: str
    build_status: str
    test_coverage: float
    code_quality: float
    security_score: float

@dataclass
class DependencyInfo:
    """Information about a project dependency"""
    name: str
    version: Optional[str]
    source: str  # pip, npm, conda, etc.
    required: bool
    installed: bool
    latest_version: Optional[str]
    security_issues: List[str]

@dataclass
class BuildConfiguration:
    """Build configuration and setup"""
    build_tool: str  # pip, npm, gradle, etc.
    entry_point: Optional[str]
    scripts: Dict[str, str]
    environment: Dict[str, str]
    requirements_files: List[str]
    build_commands: List[str]
    test_commands: List[str]

class ProjectAnalyzer:
    """Comprehensive project analyzer with enhanced capabilities"""
    
    def __init__(self, project_path: str = "."):
        """
        Initialize project analyzer
        
        Args:
            project_path: Path to project root
        """
        self.project_path = Path(project_path).resolve()
        self.project_info = {}
        self.dependencies = {}
        self.build_config = None
        
    def analyze_project(self) -> Dict[str, Any]:
        """
        Perform comprehensive project analysis
        
        Returns:
            Complete project analysis data
        """
        logger.info(f"Analyzing project at {self.project_path}")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "project_type": self._detect_project_type(),
            "structure": self._analyze_project_structure(),
            "dependencies": self._analyze_dependencies(),
            "build_config": self._analyze_build_configuration(),
            "code_metrics": self._analyze_code_metrics(),
            "health": self._assess_project_health(),
            "recommendations": self._generate_recommendations()
        }
        
        self.project_info = analysis
        return analysis
    
    def _detect_project_type(self) -> str:
        """Detect the type of project"""
        indicators = {
            "python": ["setup.py", "pyproject.toml", "requirements.txt", "Pipfile", "environment.yml"],
            "node": ["package.json", "package-lock.json", "yarn.lock", "node_modules"],
            "java": ["pom.xml", "build.gradle", "build.gradle.kts", "build.xml"],
            "dotnet": ["*.csproj", "*.sln", "project.json"],
            "go": ["go.mod", "go.sum", "Gopkg.toml"],
            "rust": ["Cargo.toml", "Cargo.lock"],
            "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
            "web": ["index.html", "webpack.config.js", "vite.config.js"],
        }
        
        detected_types = []
        for project_type, files in indicators.items():
            for file_pattern in files:
                if list(self.project_path.glob(file_pattern)):
                    detected_types.append(project_type)
                    break
        
        if not detected_types:
            # Check by file extensions
            python_files = list(self.project_path.glob("**/*.py"))
            js_files = list(self.project_path.glob("**/*.js"))
            java_files = list(self.project_path.glob("**/*.java"))
            
            if python_files:
                detected_types.append("python")
            if js_files:
                detected_types.append("javascript")
            if java_files:
                detected_types.append("java")
        
        return detected_types[0] if detected_types else "unknown"
    
    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project directory structure"""
        structure = {
            "total_files": 0,
            "directories": [],
            "file_types": {},
            "size_mb": 0,
            "key_files": {},
            "structure_quality": "good"
        }
        
        # Exclude common build/cache directories
        exclude_dirs = {
            '__pycache__', '.git', '.venv', 'venv', 'node_modules', 
            'build', 'dist', '.pytest_cache', '.mypy_cache', 'target'
        }
        
        total_size = 0
        file_count = 0
        
        for item in self.project_path.rglob("*"):
            if item.is_file() and not any(exc in item.parts for exc in exclude_dirs):
                file_count += 1
                try:
                    size = item.stat().st_size
                    total_size += size
                    
                    # Track file types
                    ext = item.suffix.lower()
                    if ext:
                        structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                    
                    # Identify key files
                    if item.name in ["README.md", "LICENSE", "setup.py", "package.json", "requirements.txt"]:
                        structure["key_files"][item.name] = str(item.relative_to(self.project_path))
                        
                except OSError:
                    continue
            elif item.is_dir() and item != self.project_path:
                if not any(exc in item.parts for exc in exclude_dirs):
                    structure["directories"].append(str(item.relative_to(self.project_path)))
        
        structure["total_files"] = file_count
        structure["size_mb"] = round(total_size / (1024 * 1024), 2)
        
        return structure
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies"""
        dependencies = {
            "python": self._analyze_python_dependencies(),
            "node": self._analyze_node_dependencies(),
            "system": self._analyze_system_dependencies(),
            "summary": {},
            "security_issues": [],
            "outdated": []
        }
        
        # Summarize dependency info
        total_deps = 0
        installed_deps = 0
        
        for dep_type, deps in dependencies.items():
            if isinstance(deps, list):
                total_deps += len(deps)
                installed_deps += sum(1 for dep in deps if dep.get("installed", False))
        
        dependencies["summary"] = {
            "total": total_deps,
            "installed": installed_deps,
            "missing": total_deps - installed_deps
        }
        
        return dependencies
    
    def _analyze_python_dependencies(self) -> List[Dict[str, Any]]:
        """Analyze Python dependencies"""
        deps = []
        
        # Check requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            dep_name = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                            deps.append({
                                "name": dep_name,
                                "version": self._extract_version(line),
                                "source": "requirements.txt",
                                "installed": self._is_python_package_installed(dep_name)
                            })
            except Exception as e:
                logger.warning(f"Failed to parse requirements.txt: {e}")
        
        # Check pyproject.toml
        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            try:
                import toml
                with open(pyproject, 'r') as f:
                    data = toml.load(f)
                    
                # Check different dependency sections
                dep_sections = [
                    data.get("build-system", {}).get("requires", []),
                    data.get("project", {}).get("dependencies", []),
                    data.get("tool", {}).get("poetry", {}).get("dependencies", {})
                ]
                
                for section in dep_sections:
                    if isinstance(section, list):
                        for dep in section:
                            dep_name = dep.split('==')[0].split('>=')[0].strip()
                            deps.append({
                                "name": dep_name,
                                "version": self._extract_version(dep),
                                "source": "pyproject.toml",
                                "installed": self._is_python_package_installed(dep_name)
                            })
                    elif isinstance(section, dict):
                        for dep_name, version in section.items():
                            deps.append({
                                "name": dep_name,
                                "version": str(version) if version != "*" else None,
                                "source": "pyproject.toml",
                                "installed": self._is_python_package_installed(dep_name)
                            })
            except Exception as e:
                logger.warning(f"Failed to parse pyproject.toml: {e}")
        
        return deps
    
    def _analyze_node_dependencies(self) -> List[Dict[str, Any]]:
        """Analyze Node.js dependencies"""
        deps = []
        
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                # Regular dependencies
                for dep_name, version in data.get("dependencies", {}).items():
                    deps.append({
                        "name": dep_name,
                        "version": version,
                        "source": "package.json",
                        "dev": False,
                        "installed": (self.project_path / "node_modules" / dep_name).exists()
                    })
                
                # Dev dependencies
                for dep_name, version in data.get("devDependencies", {}).items():
                    deps.append({
                        "name": dep_name,
                        "version": version,
                        "source": "package.json",
                        "dev": True,
                        "installed": (self.project_path / "node_modules" / dep_name).exists()
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to parse package.json: {e}")
        
        return deps
    
    def _analyze_system_dependencies(self) -> List[Dict[str, Any]]:
        """Analyze system-level dependencies"""
        deps = []
        
        # Check for Docker
        if (self.project_path / "Dockerfile").exists():
            deps.append({
                "name": "docker",
                "type": "system",
                "required": True,
                "installed": self._is_command_available("docker")
            })
        
        # Check for git
        if (self.project_path / ".git").exists():
            deps.append({
                "name": "git",
                "type": "system", 
                "required": True,
                "installed": self._is_command_available("git")
            })
        
        return deps
    
    def _analyze_build_configuration(self) -> BuildConfiguration:
        """Analyze build configuration"""
        project_type = self._detect_project_type()
        
        if project_type == "python":
            return self._get_python_build_config()
        elif project_type == "node":
            return self._get_node_build_config()
        else:
            return BuildConfiguration(
                build_tool="unknown",
                entry_point=None,
                scripts={},
                environment={},
                requirements_files=[],
                build_commands=[],
                test_commands=[]
            )
    
    def _get_python_build_config(self) -> BuildConfiguration:
        """Get Python build configuration"""
        config = BuildConfiguration(
            build_tool="pip",
            entry_point=None,
            scripts={},
            environment={},
            requirements_files=[],
            build_commands=[],
            test_commands=[]
        )
        
        # Find requirements files
        for req_file in ["requirements.txt", "requirements-dev.txt", "dev-requirements.txt"]:
            if (self.project_path / req_file).exists():
                config.requirements_files.append(req_file)
        
        # Check for setup.py
        if (self.project_path / "setup.py").exists():
            config.build_commands.append("python setup.py build")
            config.entry_point = "setup.py"
        
        # Check for pyproject.toml
        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            config.build_tool = "pip"  # or poetry, depending on content
            config.build_commands.append("pip install -e .")
        
        # Standard test commands
        if any((self.project_path / test_dir).exists() for test_dir in ["tests", "test"]):
            config.test_commands.extend(["python -m pytest", "python -m unittest discover"])
        
        return config
    
    def _get_node_build_config(self) -> BuildConfiguration:
        """Get Node.js build configuration"""
        config = BuildConfiguration(
            build_tool="npm",
            entry_point=None,
            scripts={},
            environment={},
            requirements_files=["package.json"],
            build_commands=["npm install"],
            test_commands=[]
        )
        
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                config.entry_point = data.get("main", "index.js")
                config.scripts = data.get("scripts", {})
                
                # Add build and test commands from scripts
                if "build" in config.scripts:
                    config.build_commands.append("npm run build")
                if "test" in config.scripts:
                    config.test_commands.append("npm test")
                    
            except Exception as e:
                logger.warning(f"Failed to parse package.json for build config: {e}")
        
        # Check for yarn
        if (self.project_path / "yarn.lock").exists():
            config.build_tool = "yarn"
            config.build_commands = ["yarn install"]
        
        return config
    
    def _analyze_code_metrics(self) -> Dict[str, Any]:
        """Analyze code quality metrics"""
        metrics = {
            "lines_of_code": 0,
            "complexity": 0,
            "duplication": 0,
            "test_coverage": 0,
            "documentation": 0,
            "files_analyzed": 0,
            "languages": {}
        }
        
        project_type = self._detect_project_type()
        
        if project_type == "python":
            metrics.update(self._analyze_python_code())
        elif project_type in ["node", "javascript"]:
            metrics.update(self._analyze_javascript_code())
        
        return metrics
    
    def _analyze_python_code(self) -> Dict[str, Any]:
        """Analyze Python code quality"""
        metrics = {"python_files": 0, "functions": 0, "classes": 0, "complexity": 0}
        
        for py_file in self.project_path.glob("**/*.py"):
            if "__pycache__" not in str(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)
                        
                    metrics["python_files"] += 1
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            metrics["functions"] += 1
                        elif isinstance(node, ast.ClassDef):
                            metrics["classes"] += 1
                            
                except Exception as e:
                    logger.debug(f"Failed to analyze {py_file}: {e}")
        
        return metrics
    
    def _analyze_javascript_code(self) -> Dict[str, Any]:
        """Analyze JavaScript code quality"""
        metrics = {"js_files": 0, "functions": 0}
        
        for js_file in self.project_path.glob("**/*.js"):
            if "node_modules" not in str(js_file):
                try:
                    with open(js_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    metrics["js_files"] += 1
                    # Simple function counting (not AST-based)
                    metrics["functions"] += content.count("function ")
                    
                except Exception as e:
                    logger.debug(f"Failed to analyze {js_file}: {e}")
        
        return metrics
    
    def _assess_project_health(self) -> ProjectHealth:
        """Assess overall project health"""
        issues = []
        warnings = []
        recommendations = []
        
        # Check for essential files
        essential_files = ["README.md", "README.rst", "README.txt"]
        if not any((self.project_path / f).exists() for f in essential_files):
            issues.append("Missing README file")
            recommendations.append("Add a README.md file with project description")
        
        # Check for license
        license_files = ["LICENSE", "LICENSE.txt", "LICENSE.md"]
        if not any((self.project_path / f).exists() for f in license_files):
            warnings.append("No license file found")
            recommendations.append("Add a LICENSE file to clarify usage terms")
        
        # Check for version control
        if not (self.project_path / ".git").exists():
            warnings.append("Not using version control")
            recommendations.append("Initialize git repository: git init")
        
        # Dependency checks
        dep_summary = self.project_info.get("dependencies", {}).get("summary", {})
        missing_deps = dep_summary.get("missing", 0)
        if missing_deps > 0:
            issues.append(f"{missing_deps} dependencies not installed")
            recommendations.append("Install missing dependencies")
        
        # Calculate health score
        score = 100
        score -= len(issues) * 20  # Major issues
        score -= len(warnings) * 10  # Minor issues
        score = max(0, score)
        
        return ProjectHealth(
            score=score,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations,
            dependencies_status="good" if missing_deps == 0 else "issues",
            build_status="unknown",
            test_coverage=0.0,
            code_quality=75.0,  # Default value, would need deeper analysis
            security_score=80.0  # Default value, would need security scan
        )
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        project_type = self._detect_project_type()
        
        # Type-specific recommendations
        if project_type == "python":
            if not (self.project_path / "tests").exists():
                recommendations.append("Add a tests directory with unit tests")
            if not (self.project_path / ".gitignore").exists():
                recommendations.append("Add .gitignore file for Python projects")
            if not (self.project_path / "requirements.txt").exists():
                recommendations.append("Create requirements.txt for dependencies")
        
        elif project_type == "node":
            if not (self.project_path / "package.json").exists():
                recommendations.append("Initialize package.json: npm init")
            if not (self.project_path / ".gitignore").exists():
                recommendations.append("Add .gitignore file for Node.js projects")
        
        # General recommendations
        recommendations.extend([
            "Set up continuous integration (CI/CD)",
            "Add code formatting and linting tools",
            "Implement automated testing",
            "Add security scanning to development workflow"
        ])
        
        return recommendations
    
    def build_project(self) -> Dict[str, Any]:
        """Build the project using detected configuration"""
        if not self.build_config:
            self.build_config = self._analyze_build_configuration()
        
        build_result = {
            "success": False,
            "commands_run": [],
            "outputs": [],
            "errors": [],
            "duration": 0
        }
        
        start_time = datetime.now()
        
        try:
            for command in self.build_config.build_commands:
                logger.info(f"Running build command: {command}")
                result = self._run_command(command)
                
                build_result["commands_run"].append(command)
                build_result["outputs"].append(result["stdout"])
                
                if result["returncode"] != 0:
                    build_result["errors"].append(result["stderr"])
                    logger.error(f"Build command failed: {command}")
                    break
            else:
                build_result["success"] = True
                
        except Exception as e:
            build_result["errors"].append(str(e))
            logger.error(f"Build failed with exception: {e}")
        
        build_result["duration"] = (datetime.now() - start_time).total_seconds()
        return build_result
    
    def run_tests(self) -> Dict[str, Any]:
        """Run project tests"""
        if not self.build_config:
            self.build_config = self._analyze_build_configuration()
        
        test_result = {
            "success": False,
            "commands_run": [],
            "outputs": [],
            "errors": [],
            "coverage": 0.0
        }
        
        try:
            for command in self.build_config.test_commands:
                logger.info(f"Running test command: {command}")
                result = self._run_command(command)
                
                test_result["commands_run"].append(command)
                test_result["outputs"].append(result["stdout"])
                
                if result["returncode"] != 0:
                    test_result["errors"].append(result["stderr"])
                    logger.warning(f"Test command failed: {command}")
                else:
                    test_result["success"] = True
                    break
                    
        except Exception as e:
            test_result["errors"].append(str(e))
            logger.error(f"Tests failed with exception: {e}")
        
        return test_result
    
    def _run_command(self, command: str) -> Dict[str, Any]:
        """Run a shell command and return result"""
        try:
            result = subprocess.run(
                command.split(),
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "command": command,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "command": command,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    def _extract_version(self, requirement: str) -> Optional[str]:
        """Extract version from requirement string"""
        for op in ["==", ">=", "<=", ">", "<", "~="]:
            if op in requirement:
                return requirement.split(op)[1].strip()
        return None
    
    def _is_python_package_installed(self, package_name: str) -> bool:
        """Check if Python package is installed"""
        try:
            subprocess.run([sys.executable, "-c", f"import {package_name}"], 
                         check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, ImportError):
            return False
    
    def _is_command_available(self, command: str) -> bool:
        """Check if system command is available"""
        try:
            subprocess.run([command, "--version"], 
                         check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def save_analysis(self, output_file: str = "project_analysis.json"):
        """Save analysis results to file"""
        if not self.project_info:
            self.analyze_project()
        
        output_path = self.project_path / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.project_info, f, indent=2, default=str)
        
        logger.info(f"Project analysis saved to {output_path}")
        return str(output_path)
