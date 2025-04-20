import os
import argparse
import subprocess
import shutil
import tempfile
from PIL import Image
import glob

def compress_with_ghostscript(input_file, output_file, pdf_quality="printer"):
    """
    Стискає PDF за допомогою Ghostscript.
    
    pdf_quality може бути:
    - "screen" (72 dpi)
    - "ebook" (150 dpi)
    - "printer" (300 dpi)
    - "prepress" (300 dpi, збереження кольорів)
    """
    quality_settings = {
        "screen": "/screen",
        "ebook": "/ebook",
        "printer": "/printer",
        "prepress": "/prepress"
    }
    
    quality = quality_settings.get(pdf_quality, "/ebook")
    
    # Формуємо команду ghostscript
    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=" + quality,
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_file}",
        input_file
    ]
    
    print(f"Стискаємо PDF з якістю: {pdf_quality}")
    subprocess.run(cmd, check=True)
    
    input_size = os.path.getsize(input_file) / (1024 * 1024)
    output_size = os.path.getsize(output_file) / (1024 * 1024)
    
    print(f"Початковий розмір: {input_size:.2f} МБ")
    print(f"Кінцевий розмір: {output_size:.2f} МБ")
    print(f"Стиснення: {(1 - output_size / input_size) * 100:.2f}%")
    
    return output_size

def extract_and_compress_images(input_file, target_size_mb=None, quality=75, dpi=200):
    """
    Альтернативний метод: витягує зображення з PDF, стискає їх і створює новий PDF
    """
    temp_dir = tempfile.mkdtemp()
    try:
        # Витягуємо зображення за допомогою pdfimages (потрібен пакет poppler-utils)
        extract_cmd = ["pdfimages", "-png", input_file, os.path.join(temp_dir, "page")]
        subprocess.run(extract_cmd, check=True)
        
        # Стискаємо кожне зображення
        for img_path in sorted(glob.glob(os.path.join(temp_dir, "page-*.png"))):
            img = Image.open(img_path)
            output_path = img_path.replace(".png", ".jpg")
            
            # Конвертуємо в JPG з потрібною якістю
            img.convert("RGB").save(output_path, "JPEG", quality=quality, dpi=(dpi, dpi))
            os.remove(img_path)  # Видаляємо оригінал
        
        # Створюємо новий PDF з стиснених зображень
        output_pdf = os.path.join(temp_dir, "output.pdf")
        img_files = sorted(glob.glob(os.path.join(temp_dir, "page-*.jpg")))
        
        # Використовуємо img2pdf для створення PDF
        img2pdf_cmd = ["img2pdf"] + img_files + ["-o", output_pdf]
        subprocess.run(img2pdf_cmd, check=True)
        
        return output_pdf, temp_dir
    except Exception as e:
        shutil.rmtree(temp_dir)
        raise e

def compress_pdf(input_file, output_file, target_size_mb=None, method="ghostscript"):
    """
    Головна функція для стиснення PDF файлу.
    
    method:
        - "ghostscript": використовує Ghostscript (найнадійніший метод)
        - "extract_compress": витягує зображення, стискає їх і створює новий PDF
    """
    input_size_mb = os.path.getsize(input_file) / (1024 * 1024)
    
    if method == "ghostscript":
        # Спробуємо різні налаштування якості
        quality_levels = ["ebook", "screen"]
        
        for quality in quality_levels:
            compress_with_ghostscript(input_file, output_file, quality)
            
            output_size_mb = os.path.getsize(output_file) / (1024 * 1024)
            if target_size_mb is None or output_size_mb <= target_size_mb:
                break
        
    elif method == "extract_compress":
        # Використовуємо метод витягування і стиснення зображень
        quality_levels = [75, 60, 50, 40]
        dpi_levels = [200, 150, 120, 100]
        
        for quality, dpi in zip(quality_levels, dpi_levels):
            try:
                temp_pdf, temp_dir = extract_and_compress_images(input_file, target_size_mb, quality, dpi)
                shutil.copy(temp_pdf, output_file)
                shutil.rmtree(temp_dir)
                
                output_size_mb = os.path.getsize(output_file) / (1024 * 1024)
                if target_size_mb is None or output_size_mb <= target_size_mb:
                    break
            except Exception as e:
                print(f"Помилка при стисненні: {e}")
                if quality == quality_levels[-1]:
                    # Якщо це остання спроба, використовуємо Ghostscript як запасний варіант
                    compress_with_ghostscript(input_file, output_file, "screen")

def main():
    parser = argparse.ArgumentParser(description='Стиснення PDF файлів')
    parser.add_argument('input', help='Вхідний PDF файл')
    parser.add_argument('-o', '--output', help='Вихідний PDF файл')
    parser.add_argument('-s', '--size', type=float, help='Цільовий розмір в МБ')
    parser.add_argument('-m', '--method', choices=['ghostscript', 'extract_compress'], 
                        default='ghostscript', help='Метод стиснення')
    
    args = parser.parse_args()
    
    input_file = args.input
    output_file = args.output if args.output else f"compressed_{os.path.basename(input_file)}"
    
    compress_pdf(input_file, output_file, args.size, args.method)

if __name__ == "__main__":
    main()
    