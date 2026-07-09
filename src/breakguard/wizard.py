import sys
import os

def run():
    print("\n🛡️ Welcome to BreakGuard! What would you like to do? (Type a number and press Enter)")
    print("  1) 🔍 Scan for downstream breaking changes")
    print("  2) 📝 Generate a Migration Changelog")
    print("  3) 🤖 Auto-Fix Downstream Repositories (AI Magic)")
    print("  4) 📊 Generate HTML Visual Dependency Graph")
    print("  5) ❌ Exit\n")
    
    try:
        choice = input("❯ ")
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)
        
    choice = choice.strip()
    cmd = ["breakguard", "--repo", "."]
    
    if choice == '1':
        print("\nScanning for breakages...\n")
    elif choice == '2':
        print("\nGenerating migration notes...\n")
        cmd.append("--changelog")
    elif choice == '3':
        print("\nFiring up Downstream AI Fixer...\n")
        cmd.append("--auto-fix-downstream")
    elif choice == '4':
        print("\nGenerating HTML Visual Graph...\n")
        cmd.extend(["--format", "html"])
    elif choice == '5':
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice.")
        sys.exit(1)
        
    os.system(" ".join(cmd))
    sys.exit(0)
