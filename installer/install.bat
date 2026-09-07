@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo superyouzi 一键安装
echo.
set "TARGET=%USERPROFILE%\.claude\skills\superyouzi"
set "STAGE=%TARGET%.installing"
set "SRC=skill"
if not exist "%SRC%\" set "SRC=..\skill"
if not exist "%SRC%\" (
  echo ❌ 找不到 skill 目录，请确认 zip 已完整解压
  pause
  exit /b 1
)
echo → 安装到: %TARGET%
if exist "%STAGE%" rmdir /S /Q "%STAGE%"
mkdir "%STAGE%"
xcopy /E /I /Y "%SRC%\*" "%STAGE%\" >nul
if errorlevel 1 (
  echo ❌ 文件复制失败，原安装未改动
  rmdir /S /Q "%STAGE%"
  pause
  exit /b 1
)
if exist "%TARGET%" rmdir /S /Q "%TARGET%"
move "%STAGE%" "%TARGET%" >nul
echo.
echo → 安装数据依赖（失败不影响使用，会自动降级联网取数）
where python >nul 2>nul
if errorlevel 1 (
  echo   ⚠️ 未找到 Python，跳过数据依赖
) else (
  python -m pip install -r "%TARGET%\scripts\requirements.txt" -q 2>nul || echo   ⚠️ 依赖未装全，跳过
  python "%TARGET%\scripts\fetch.py" quote 600519 >"%TEMP%\superyouzi-check.json" 2>nul
  python -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); sys.exit(0 if d.get('ok') and d.get('data') else 1)" "%TEMP%\superyouzi-check.json" 2>nul
  if errorlevel 1 (
    echo ⚠️ 数据自检未通过（可能离线或缺依赖），框架功能不受影响
  ) else (
    echo ✅ 数据脚本自检通过
  )
  del "%TEMP%\superyouzi-check.json" >nul 2>nul
)
echo.
echo ✅ 安装完成。下一步：新开一个 AI 会话，直接问：
echo    「今天市场情绪怎么样，短线能做吗？」
pause
