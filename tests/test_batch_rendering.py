from server.batch import scan_and_render
from pathlib import Path

input_path = Path(__file__).parent.parent / "test_input"
output_path = Path(__file__).parent.parent / "test_output"

scan_and_render(input_path, "img_expand", output_path)