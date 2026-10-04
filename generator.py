from pathlib import Path
import json
import sys

# Безопасно определяем базовую директорию скрипта
try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    BASE_DIR = Path.cwd()

PROJECTS_DIR = BASE_DIR / "projects"
OUTPUT_FILE = BASE_DIR / "portfolio.html"

def scan_projects():
    """Сканирует директорию проектов, валидирует изображения и возвращает чистую структуру."""
    if not PROJECTS_DIR.exists():
        try:
            PROJECTS_DIR.mkdir(exist_ok=True, parents=True)
            print(f"[INFO] Создана папка 'projects' по пути: {PROJECTS_DIR}")
            print("[INFO] Пожалуйста, добавьте туда папки с вашими проектами и изображениями.")
        except Exception as e:
            print(f"[ERROR] Не удалось создать директорию проектов: {e}")
        return []

    projects = []
    valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}

    try:
        # Безопасная сортировка папок проектов
        project_items = sorted([item for item in PROJECTS_DIR.iterdir() if item.is_dir()])
        
        for item in project_items:
            images = []
            try:
                # Безопасная сортировка файлов внутри проекта
                file_items = sorted([img for img in item.iterdir() if img.is_file()])
                for img in file_items:
                    if img.suffix.lower() in valid_extensions:
                        images.append(img.name)
            except Exception as e:
                print(f"[WARNING] Ошибка при чтении содержимого папки проекта '{item.name}': {e}")
                continue

            # Добавляем проект только если в нем действительно есть подходящие изображения
            if images:
                projects.append({
                    "name": item.name,
                    "images": images
                })
    except Exception as e:
        print(f"[ERROR] Произошла ошибка при сканировании директории: {e}")

    return projects

def generate_html(projects):
    """Генерирует защищенный, валидный и адаптивный HTML-файл портфолио."""
    try:
        projects_json = json.dumps(projects, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Ошибка сериализации данных проектов в JSON: {e}")
        projects_json = "[]"

    html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Архитектурное Портфолио</title>
    <style>
        :root {
            --bg-color: #111;
            --card-bg: #1a1a1a;
            --inner-bg: #222;
            --border-color: #333;
            --text-color: #eee;
            --text-muted: #aaa;
            --accent-hover: rgba(255, 255, 255, 0.2);
        }
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg-color); color: var(--text-color); margin: 0; padding: 40px; }
        h1 { border-bottom: 1px solid var(--border-color); padding-bottom: 10px; margin-top: 0; }
        .project { background: var(--card-bg); padding: 20px; margin-bottom: 25px; border-radius: 8px; border: 1px solid var(--border-color); }
        .project h2 { margin-top: 0; font-size: 1.4rem; color: #fff; }
        .gallery { display: flex; gap: 15px; flex-wrap: wrap; margin-top: 15px; }
        .img-card { background: var(--inner-bg); padding: 10px; border-radius: 6px; border: 1px solid var(--border-color); width: 220px; }
        
        img.thumb { width: 100%; height: 140px; object-fit: cover; border-radius: 4px; display: block; cursor: pointer; transition: opacity 0.2s ease; }
        img.thumb:hover { opacity: 0.8; }
        
        .caption { font-size: 12px; margin-top: 8px; color: var(--text-muted); word-break: break-all; text-align: center; }

        /* Модальное окно (Lightbox) */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.95);
            justify-content: center;
            align-items: center;
        }
        .modal-content-wrapper {
            position: relative;
            max-width: 90%;
            max-height: 90%;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .modal img {
            max-width: 100%;
            max-height: 85vh;
            object-fit: contain;
            border-radius: 4px;
            box-shadow: 0 0 25px rgba(0,0,0,0.7);
            cursor: pointer;
        }
        .close-btn {
            position: absolute;
            top: -50px;
            right: 0;
            color: #fff;
            font-size: 28px;
            background: rgba(255, 255, 255, 0.1);
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background 0.2s ease;
            z-index: 1010;
        }
        .close-btn:hover { background: var(--accent-hover); }
        
        /* Исправленные стрелки навигации на фиксированных позициях по краям экрана */
        .nav-btn {
            position: fixed;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255, 255, 255, 0.15);
            color: white;
            border: none;
            font-size: 32px;
            padding: 20px 25px;
            cursor: pointer;
            border-radius: 8px;
            transition: background 0.2s ease;
            z-index: 1020;
        }
        .nav-btn:hover { background: rgba(255, 255, 255, 0.3); }
        .prev-btn { left: 30px; }
        .next-btn { right: 30px; }
        
        .image-counter {
            position: absolute;
            bottom: -40px;
            left: 50%;
            transform: translateX(-50%);
            color: var(--text-muted);
            font-size: 14px;
            white-space: nowrap;
        }

        .empty-notice { color: var(--text-muted); font-style: italic; }

        /* Адаптивность для мобильных экранов */
        @media (max-width: 768px) {
            body { padding: 15px; }
            .prev-btn { left: 10px; }
            .next-btn { right: 10px; }
            .nav-btn { padding: 10px 15px; font-size: 18px; background: rgba(0,0,0,0.6); }
        }
    </style>
</head>
<body>
    <h1>Архитектурное портфолио</h1>
"""
    
    if not projects:
        html_content += '<p class="empty-notice">Проекты не найдены. Создайте папку <code>projects</code> и добавьте в неё подпапки с изображениями.</p>'
    else:
        for p_idx, proj in enumerate(projects):
            safe_proj_name = html_escape(proj['name'])
            html_content += f"""
        <div class="project">
            <h2>Проект: {safe_proj_name}</h2>
            <div class="gallery">
"""
            for img_idx, img_name in enumerate(proj['images']):
                img_path = f"projects/{proj['name']}/{img_name}"
                safe_img_name = html_escape(img_name)
                html_content += f"""
                <div class="img-card">
                    <img src="{img_path}" alt="{safe_img_name}" class="thumb" onclick="openModal({p_idx}, {img_idx})" loading="lazy">
                    <div class="caption" title="{safe_img_name}">{safe_img_name}</div>
                </div>
"""
            html_content += """
            </div>
        </div>
"""
        
    # Разметка модального окна с корректным выносом кнопок навигации
    html_content += """
    <!-- Модальное окно для просмотрщика -->
    <div id="lightbox" class="modal" role="dialog" aria-modal="true" onclick="handleModalClick(event)">
        <button class="nav-btn prev-btn" onclick="changeImage(-1); event.stopPropagation();" title="Предыдущая (←)">&#10094;</button>
        <div class="modal-content-wrapper">
            <div class="close-btn" onclick="closeModal()" title="Закрыть (Esc)">&times;</div>
            <img id="lightbox-img" onclick="changeImage(1); event.stopPropagation();" title="Следующая (клик)" alt="Увеличенное изображение">
            <div id="image-counter" class="image-counter"></div>
        </div>
        <button class="nav-btn next-btn" onclick="changeImage(1); event.stopPropagation();" title="Следующая (→)">&#10095;</button>
    </div>
"""

    script_template = """
    <script>
        const projectsData = __PROJECTS_JSON__;

        let currentProjectIndex = 0;
        let currentImageIndex = 0;

        function openModal(projectIdx, imageIdx) {
            if (!projectsData[projectIdx] || !projectsData[projectIdx].images[imageIdx]) return;
            
            currentProjectIndex = projectIdx;
            currentImageIndex = imageIdx;
            
            const modal = document.getElementById('lightbox');
            modal.style.display = 'flex';
            updateModalImage();
            
            document.body.style.overflow = 'hidden';
        }

        function closeModal() {
            const modal = document.getElementById('lightbox');
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }

        function changeImage(direction) {
            if (!projectsData[currentProjectIndex]) return;
            const images = projectsData[currentProjectIndex].images;
            
            currentImageIndex += direction;

            if (currentImageIndex < 0) {
                currentImageIndex = images.length - 1;
            } else if (currentImageIndex >= images.length) {
                currentImageIndex = 0;
            }

            updateModalImage();
        }

        function updateModalImage() {
            const proj = projectsData[currentProjectIndex];
            if (!proj) return;
            
            const imageName = proj.images[currentImageIndex];
            const imagePath = `projects/${encodeURIComponent(proj.name)}/${encodeURIComponent(imageName)}`;
            
            const modalImg = document.getElementById('lightbox-img');
            modalImg.src = imagePath;
            modalImg.alt = imageName;

            const counter = document.getElementById('image-counter');
            counter.innerText = `${currentImageIndex + 1} / ${proj.images.length} — Проект: ${proj.name}`;
        }

        function handleModalClick(event) {
            if (event.target.id === 'lightbox') {
                closeModal();
            }
        }

        document.addEventListener('keydown', function(event) {
            const modal = document.getElementById('lightbox');
            if (modal && modal.style.display === 'flex') {
                if (event.key === 'Escape') {
                    closeModal();
                } else if (event.key === 'ArrowLeft') {
                    changeImage(-1);
                } else if (event.key === 'ArrowRight') {
                    changeImage(1);
                }
            }
        });
    </script>
</body>
</html>
"""
    
    html_content += script_template.replace("__PROJECTS_JSON__", projects_json)

    try:
        OUTPUT_FILE.write_text(html_content, encoding='utf-8')
        print(f"[SUCCESS] Портфолио успешно сгенерировано: {OUTPUT_FILE}")
    except Exception as e:
        print(f"[ERROR] Не удалось записать HTML-файл: {e}")

def html_escape(text):
    return (text
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
        .replace("<", "&lt;")
        .replace(">", "&gt;"))

if __name__ == "__main__":
    print("[INFO] Запуск сканирования проектов...")
    my_projects = scan_projects()
    generate_html(my_projects)