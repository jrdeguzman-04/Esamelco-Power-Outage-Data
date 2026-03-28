import os
import subprocess
import sys

TRANSFORM_SCRIPTS = [
    "../extract/save_json.py",
    "filter_interruption.py",
    "semi_cleaned_posts.py",
    "cleaned_posts.py",
    "explode_areas.py",
    "validate_areas.py",
    "standardize_areas.py",
    "split_barangays.py",
    "split_barangays_v2.py",
    "standardize_reason.py",
    "standardize_reasons.py",
    "clean_final_output.py",
]


def run_script(script_path):
    script_abspath = os.path.normpath(os.path.join(os.path.dirname(__file__), script_path))
    print(f"\n--- Running: {script_abspath} ---")
    result = subprocess.run([sys.executable, script_abspath], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: script failed: {script_abspath}")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        raise SystemExit(result.returncode)
    else:
        print(result.stdout)


if __name__ == "__main__":
    for script in TRANSFORM_SCRIPTS:
        run_script(script)

    print("\n✅ Transform pipeline completed successfully.")
