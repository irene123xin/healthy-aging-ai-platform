def explain(category: str, category_average: float | None, overall_average: float | None, days_since: int | None, preference: bool) -> str:
    reasons = []
    if category_average is None: reasons.append("it will broaden your training mix")
    elif overall_average is not None and category_average < overall_average:
        reasons.append(f"your recent {category.lower()} score is {overall_average-category_average:.0f} points below your overall average")
    if days_since is None: reasons.append("you have not tried it yet")
    elif days_since >= 2: reasons.append(f"it has been {days_since} days since your last {category.lower()} activity")
    if preference: reasons.append("it matches your training preferences")
    return f"{category} is recommended because " + " and ".join(reasons[:2]) + "."

