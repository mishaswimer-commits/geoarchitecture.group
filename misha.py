from pathlib import Path

# Указываем папку с проектами (текущая директория скрипта)
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "projects"

def scan_projects():
    if not PROJECTS_DIR.exists():
        PROJECTS_DIR.mkdir(exist_ok=True)
        print("Создана папка 'projects'. Закиньте туда папки с вашими проектами!")
        return []

    projects = []
    for item in PROJECTS_DIR.iterdir():
        if item.is_dir():
            images = []
            for img in item.iterdir():
                if img.suffix.lower() in ('.jpg', '.jpeg', '.png'):
                    images.append(img.name)
                        
            projects.append({
                "name": item.name,
                "images": images
            })
    return projects

def generate_html(projects):
    html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Архитектурное Портфолио</title>
    <style>
        body { font-family: sans-serif; background: #111; color: #eee; margin: 0; padding: 40px; }
        h1 { border-bottom: 1px solid #333; padding-bottom: 10px; }
        .project { background: #1a1a1a; padding: 20px; margin-bottom: 25px; border-radius: 8px; }
        .gallery { display: flex; gap: 15px; flex-wrap: wrap; margin-top: 15px; }
        .img-card { background: #222; padding: 10px; border-radius: 6px; border: 1px solid #333; width: 220px; }
        
        /* Стили для миниатюр с курсором-лупой */
        img.thumb { width: 100%; height: 140px; object-fit: cover; border-radius: 4px; display: block; cursor: pointer; transition: opacity 0.2s; }
        img.thumb:hover { opacity: 0.8; }
        
        .caption { font-size: 12px; margin-top: 8px; color: #aaa; word-break: break-all; text-align: center; }

        /* Модальное окно (Lightbox) для увеличения */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            justify-content: center;
            align-items: center;
            cursor: pointer;
        }
        .modal img {
            max-width: 90%;
            max-height: 90%;
            object-fit: contain;
            border-radius: 4px;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        }
        .close-hint {
            position: absolute;
            top: 20px;
            right: 30px;
            color: #fff;
            font-size: 16px;
            background: rgba(255,255,255,0.1);
            padding: 8px 12px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>Архитектурное портфолио</h1>
"""
    
    if not projects:
        html_content += "<p>Проекты не найдены. Добавьте папки в директорию 'projects'.</p>"
    
    for proj in projects:
        html_content += f"""
        <div class="project">
            <h2>Проект: {proj['name']}</h2>
            <div class="gallery">
        """
        for img_name in proj['images']:
            img_path = f"projects/{proj['name']}/{img_name}"
            html_content += f"""
                <div class="img-card">
                    <img src="{img_path}" alt="{img_name}" class="thumb" onclick="openModal('{img_path}')">
                    <div class="caption">{img_name}</div>
                </div>
            """
            
        html_content += """
            </div>
        </div>
        """
        
    # Добавляем разметку модального окна и скрипт управления в конец HTML
    html_content += """
    <!-- Модальное окно для просмотра -->
    <div id="lightbox" class="modal" onclick="closeModal()">
        <div class="close-hint">Нажмите в любое место, чтобы закрыть</div>
        <img id="lightbox-img">
    </div>

    <script>
        function openModal(imageSrc) {
            const modal = document.getElementById('lightbox');
            const modalImg = document.getElementById('lightbox-img');
            modal.style.display = 'flex';
            modalImg.src = imageSrc;
        }

        function closeModal() {
            document.getElementById('lightbox').style.display = 'none';
        }
    </script>
</body>
</html>
"""
    
    output_file = BASE_DIR / "portfolio.html"
    output_file.write_text(html_content, encoding='utf-8')
    print(f" Успешно! Сгенерирован интерактивный файл: {output_file}")

if __name__ == "__main__":
    print("Сканирование проектов...")
    my_projects = scan_projects()
    generate_html(my_projects)