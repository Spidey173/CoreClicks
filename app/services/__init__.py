from app.services.auth_service import (
    register_user,
    authenticate_user,
    log_activity,
    create_api_key,
)
from app.services.search_service import global_omni_search
from app.services.notification_service import (
    send_notification,
    get_user_notifications,
    mark_notification_as_read,
    mark_all_notifications_read,
)
from app.services.math_service import safe_calculate, MathEvaluationError
from app.services.password_service import (
    analyze_password,
    generate_secure_password,
    generate_passphrase,
    mask_password,
    calculate_entropy,
)
from app.services.task_service import (
    get_user_tasks,
    get_kanban_columns,
    get_task_statistics,
    update_task_position,
)
from app.services.note_service import (
    render_markdown_to_html,
    compute_reading_stats,
    save_note_version,
    restore_note_version,
)
from app.services.api_tester_service import execute_http_request
from app.services.analytics_service import parse_csv_bytes, analyze_csv_dataframe
from app.services.expense_service import (
    get_monthly_expense_summary,
    export_expenses_to_csv,
)
from app.services.file_service import (
    process_image,
    merge_pdfs,
    split_or_extract_pdf_pages,
    protect_pdf_with_password,
    inspect_pdf_metadata,
)
from app.services.color_service import (
    generate_color_palette,
    calculate_contrast_ratio,
    export_tailwind_palette,
    hex_to_rgb,
    rgb_to_hex,
    rgb_to_hsl,
)
from app.services.url_service import (
    is_valid_url,
    normalize_url,
    generate_short_code,
    generate_qr_code_bytes,
)

__all__ = [
    "register_user",
    "authenticate_user",
    "log_activity",
    "create_api_key",
    "global_omni_search",
    "send_notification",
    "get_user_notifications",
    "mark_notification_as_read",
    "mark_all_notifications_read",
    "safe_calculate",
    "MathEvaluationError",
    "analyze_password",
    "generate_secure_password",
    "generate_passphrase",
    "mask_password",
    "calculate_entropy",
    "get_user_tasks",
    "get_kanban_columns",
    "get_task_statistics",
    "update_task_position",
    "render_markdown_to_html",
    "compute_reading_stats",
    "save_note_version",
    "restore_note_version",
    "execute_http_request",
    "parse_csv_bytes",
    "analyze_csv_dataframe",
    "get_monthly_expense_summary",
    "export_expenses_to_csv",
    "process_image",
    "merge_pdfs",
    "split_or_extract_pdf_pages",
    "protect_pdf_with_password",
    "inspect_pdf_metadata",
    "generate_color_palette",
    "calculate_contrast_ratio",
    "export_tailwind_palette",
    "hex_to_rgb",
    "rgb_to_hex",
    "rgb_to_hsl",
    "is_valid_url",
    "normalize_url",
    "generate_short_code",
    "generate_qr_code_bytes",
]
