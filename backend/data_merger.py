import re

def merge_subjects(programs_subjects, plans_subjects):
    """
    Merges subject data from two sources: programs and plans.
    """
    merged_subjects = {}

    for subject in programs_subjects:
        # Normalize the name by removing the number and dot at the beginning
        normalized_name = re.sub(r"^\d+\.\d*\s*", "", subject["name"]).strip()
        if normalized_name not in merged_subjects:
            merged_subjects[normalized_name] = subject

    for subject in plans_subjects:
        normalized_name = re.sub(r"^\d+\.\s*", "", subject["name"]).strip()
        if normalized_name in merged_subjects:
            # Merge the hours
            merged_subjects[normalized_name]["hours_lecture"] = subject.get("hours_lecture", 0)
            merged_subjects[normalized_name]["hours_classes"] = subject.get("hours_classes", 0)
        else:
            # This case should not happen if the data is consistent
            # But if it does, we can add it as a new subject
            merged_subjects[normalized_name] = subject

    return list(merged_subjects.values())
