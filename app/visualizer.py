from app.config import settings
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


def generate_trend_chart(topic, data):

    plt.style.use('dark_background')

    fig, ax = plt.subplots(figsize=(10, 6), dpi=120)

    years = list(data.keys())
    values = list(data.values())

    ax.plot(years, values, marker='o', linestyle='-', color='#00f2ff',
            linewidth=3, markersize=8, markerfacecolor='#ffffff',
            markeredgewidth=2)

    ax.fill_between(years, values, color='#00f2ff', alpha=0.1)

    ax.grid(True, linestyle='--', alpha=0.3, color='#444444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_title(f"Тренд: {topic}", fontsize=16,
                 fontweight='bold', pad=20, color='#ffffff')

    # Добавляем подписи значений
    for i, v in enumerate(values):
        ax.text(years[i], v + (max(values)*0.02), str(v),
                color='#00f2ff', fontweight='bold', ha='center')

    # Имя файла
    filename = f"chart_{hash(topic)}.png"

    # ПУТЬ ДЛЯ СОХРАНЕНИЯ (полный путь системы)
    full_save_path = os.path.join(settings.charts_dir, filename)

    plt.savefig(full_save_path, bbox_inches='tight', facecolor='#121212')
    plt.close()

    # ПУТЬ ДЛЯ БРАУЗЕРА (относительный)
    return f"storage/charts/{filename}"
