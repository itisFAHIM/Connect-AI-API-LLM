import json
import requests

API_URL = "http://127.0.0.1:8000/triage"

def run_evaluation():
    with open("evals/cases.json", "r") as f:
        cases = json.load(f)

    passed = 0
    total = len(cases)

    print(f"Running evaluation on {total} test cases...\n" + "-"*40)

    for case in cases:
        resp = requests.post(API_URL, json={"text": case["input"]})
        if resp.status_code == 200:
            data = resp.json()
            predicted = data.get("category")
            is_correct = predicted == case["expected_category"]
            if is_correct:
                passed += 1
            status = "PASS" if is_correct else "FAIL"
            print(f"[{status}] Case {case['id']}: Pred='{predicted}', Expected='{case['expected_category']}'")
        else:
            print(f"[FAIL] Case {case['id']}: HTTP {resp.status_code} - {resp.text}")

    score = (passed / total) * 100
    print("-" * 40)
    print(f"Final Score: {passed}/{total} ({score:.1f}%)")

if __name__ == "__main__":
    run_evaluation()