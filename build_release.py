"""
Script de compilación automatizado y ultra-optimizado para ConvertMD.
1. Genera el ejecutable portable independiente: dist/ConvertMD.exe
2. Compila el instalador para Windows con Inno Setup: dist/ConvertMD_Setup.exe
"""

import os
import sys
import shutil
import subprocess

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PROJECT_DIR, "dist")
BUILD_DIR = os.path.join(PROJECT_DIR, "build")
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "app_icon.ico")

INNO_COMPILER_CANDIDATES = [
    r"C:\Users\Ingca\AppData\Local\Programs\Inno Setup 6\ISCC.exe",
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
    shutil.which("ISCC.exe") or ""
]


def find_inno_compiler() -> str:
    """Encuentra el compilador ISCC de Inno Setup en el sistema."""
    for path in INNO_COMPILER_CANDIDATES:
        if path and os.path.exists(path):
            return path
    return ""


def clean_previous_builds():
    """Limpia carpetas temporales anteriores."""
    print("[INFO] Limpiando carpetas de compilaciones anteriores...")
    for folder in [BUILD_DIR]:
        if os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)


def build_portable_executable():
    """Compila el ejecutable portable con PyInstaller."""
    print("\n[1/2] Compilando ejecutable portable con PyInstaller (optimizando dependencias)...")

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name", "ConvertMD",
        "--onefile",
        "--windowed",
        "--icon", ICON_PATH,
        "--add-data", f"{ASSETS_DIR};assets",
        "--collect-all", "customtkinter",
        "--collect-all", "markitdown",
        "--collect-all", "magika",
        "--collect-all", "onnxruntime",
        "--collect-all", "pdfminer",
        "--collect-all", "winrt",
        "--collect-all", "winocr",
        "--hidden-import", "docx",
        "--hidden-import", "openpyxl",
        "--hidden-import", "pptx",
        "--hidden-import", "csv",
        "--hidden-import", "json",
        # Excluir paquetes gigantes no requeridos para conversión de documentos estándar
        "--exclude-module", "torch",
        "--exclude-module", "torchvision",
        "--exclude-module", "torchaudio",
        "--exclude-module", "transformers",
        "--exclude-module", "tensorflow",
        "--exclude-module", "scipy",
        "--exclude-module", "matplotlib",
        "--exclude-module", "sklearn",
        "--exclude-module", "sympy",
        "--noconfirm",
        "main.py"
    ]

    print(f"Ejecutando PyInstaller...")
    result = subprocess.run(cmd, cwd=PROJECT_DIR)

    if result.returncode != 0:
        print("[ERROR] Error al compilar con PyInstaller.")
        sys.exit(result.returncode)

    exe_path = os.path.join(DIST_DIR, "ConvertMD.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"[OK] Ejecutable portable generado: {exe_path} ({size_mb:.2f} MB)")
    else:
        print("[ERROR] No se encontro el archivo dist/ConvertMD.exe")
        sys.exit(1)


def build_installer():
    """Compila el instalador de Windows con Inno Setup."""
    print("\n[2/2] Compilando instalador de Windows con Inno Setup...")
    iscc = find_inno_compiler()
    if not iscc:
        print("[AVISO] No se encontro el compilador ISCC.exe de Inno Setup.")
        print("El ejecutable portable dist/ConvertMD.exe ya esta listo.")
        return

    iss_file = os.path.join(PROJECT_DIR, "installer.iss")
    cmd = [iscc, iss_file]
    print(f"Ejecutando ISCC: {iscc} {iss_file}")
    result = subprocess.run(cmd, cwd=PROJECT_DIR)

    if result.returncode != 0:
        print("[ERROR] Error al compilar el instalador con Inno Setup.")
        sys.exit(result.returncode)

    setup_path = os.path.join(DIST_DIR, "ConvertMD_Setup.exe")
    if os.path.exists(setup_path):
        size_mb = os.path.getsize(setup_path) / (1024 * 1024)
        print(f"[OK] Instalador de Windows generado: {setup_path} ({size_mb:.2f} MB)")
    else:
        print("[ERROR] No se encontro dist/ConvertMD_Setup.exe")


def main():
    print("=" * 60)
    print("       ConvertMD - Proceso de Compilacion y Distribucion")
    print("=" * 60)

    clean_previous_builds()
    build_portable_executable()
    build_installer()

    print("\n" + "=" * 60)
    print("[EXITO] TODOS LOS ENTREGABLES HAN SIDO GENERADOS:")
    print(f"Carpeta de salida: {DIST_DIR}")
    print(f"  1. Ejecutable Portable: {os.path.join(DIST_DIR, 'ConvertMD.exe')}")
    print(f"  2. Instalador Windows:   {os.path.join(DIST_DIR, 'ConvertMD_Setup.exe')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
