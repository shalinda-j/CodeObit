#!/usr/bin/env python3

from cli.utils.project_analyzer import ProjectAnalyzer

def main():
    print("🔍 Analyzing codeobit-v1 project...")
    
    analyzer = ProjectAnalyzer()
    result = analyzer.analyze_project()
    
    print("\n=== PROJECT ANALYSIS RESULTS ===")
    print(f"📁 Project Type: {result['project_type']}")
    print(f"📄 Total Files: {result['structure']['total_files']}")
    print(f"💾 Project Size: {result['structure']['size_mb']} MB")
    print(f"📊 Health Score: {result['health'].score}/100")
    
    # Dependencies summary
    deps = result['dependencies']['summary']
    print(f"📦 Dependencies: {deps['total']} total, {deps['installed']} installed, {deps['missing']} missing")
    
    # Key files found
    key_files = result['structure']['key_files']
    print(f"🔑 Key Files Found: {', '.join(key_files.keys())}")
    
    # Health issues
    health = result['health']
    if health.issues:
        print(f"⚠️  Issues: {len(health.issues)} found")
        for issue in health.issues[:3]:  # Show first 3
            print(f"   - {issue}")
    
    if health.warnings:
        print(f"💡 Warnings: {len(health.warnings)} found")
        for warning in health.warnings[:3]:  # Show first 3
            print(f"   - {warning}")
    
    # Save analysis
    analysis_file = analyzer.save_analysis()
    print(f"\n✅ Full analysis saved to: {analysis_file}")
    
    # Show build capabilities
    print("\n=== BUILD CONFIGURATION ===")
    build_config = result['build_config']
    print(f"🔨 Build Tool: {build_config.build_tool}")
    print(f"📝 Requirements Files: {', '.join(build_config.requirements_files)}")
    if build_config.build_commands:
        print(f"⚙️  Build Commands: {', '.join(build_config.build_commands)}")
    if build_config.test_commands:
        print(f"🧪 Test Commands: {', '.join(build_config.test_commands)}")

if __name__ == "__main__":
    main()
