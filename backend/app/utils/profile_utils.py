def profile_to_text(profile, label):
    # TODO: remove for existing functionality
    if not profile:
        return ""
    exclude = {"id", "user_id", "portfolio_id", "name", "created_at", "updated_at"}
    def fmt(val):
        if isinstance(val, list):
            return ', '.join(str(v) for v in val) if val else 'N/A'
        if isinstance(val, str):
            return val if val else 'N/A'
        return str(val) if val else 'N/A'
    lines = [f"Profile for {label}:"]
    for field in vars(profile):
        if field in exclude:
            continue
        value = getattr(profile, field, None)
        lines.append(f"{field}: {fmt(value)}")
    return "\n".join(lines) 