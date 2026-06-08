from app.parser import parse_log_file

apache_results = parse_log_file("app/sample_logs/apache_access.log", "apache")
auth_results = parse_log_file("app/sample_logs/auth.log", "auth")

print(f"Apache parsed: {len(apache_results)} lines")
print(f"Auth parsed: {len(auth_results)} lines")
print("\nFirst Apache entry:")
print(apache_results[0])
print("\nFirst Auth entry:")
print(auth_results[0])