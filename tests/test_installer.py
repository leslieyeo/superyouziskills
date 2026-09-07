import os
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "installer" / "install.sh"


def _run_installer(tmp_path, payload):
    target = tmp_path / "installed"
    target.mkdir()
    (target / "obsolete.md").write_text("old", encoding="utf-8")
    (target / "scripts").mkdir()
    (target / "scripts/license.py").write_text("raise RuntimeError('old gate')")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_python = fake_bin / "python3"
    call_log = tmp_path / "python-calls.log"
    fake_python.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"$*\" >> \"$CALL_LOG\"\n"
        "if [ \"$1\" = \"-m\" ]; then exit 0; fi\n"
        f"if [ \"$1\" = \"-c\" ]; then exec {shlex.quote(sys.executable)} \"$@\"; fi\n"
        f"printf '%s' {shlex.quote(payload)}\n",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)
    env = {**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}",
           "CALL_LOG": str(call_log)}

    result = subprocess.run(
        ["bash", str(INSTALLER), str(target)],
        capture_output=True, text=True, env=env, timeout=30,
    )
    calls = call_log.read_text(encoding="utf-8").splitlines()
    return result, target, calls


def test_installer_replaces_stale_files_and_checks_json(tmp_path):
    result, target, calls = _run_installer(
        tmp_path, '{"ok":true,"data":{"price":1}}'
    )
    assert result.returncode == 0, result.stderr
    assert "数据脚本自检通过" in result.stdout
    assert (target / "SKILL.md").exists()
    assert not any("license.py" in line for line in calls)
    assert any("fetch.py" in line for line in calls)
    assert not (target / "obsolete.md").exists()
    assert not (target / "scripts/license.py").exists()


def test_installer_does_not_claim_success_for_missing_data(tmp_path):
    result, _, _ = _run_installer(
        tmp_path, '{"ok":false,"source":"missing","data":null}'
    )
    assert result.returncode == 0, result.stderr
    assert "数据自检未通过" in result.stdout
    assert "数据脚本自检通过" not in result.stdout


def test_windows_installer_supports_zip_and_repo_layouts():
    text = (ROOT / "installer" / "install.bat").read_text(encoding="utf-8")
    assert 'set "SRC=skill"' in text
    assert 'set "SRC=..\\skill"' in text
    assert 'xcopy /E /I /Y "%SRC%\\*"' in text
