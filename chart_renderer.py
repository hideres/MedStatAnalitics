import pandas as pd
import seaborn as sns


class ChartRenderer:
    @staticmethod
    def render_custom_graph(widget, plot_data_1, plot_data_2, region_1, region_2,
                            nosology_1, nosology_2, chart_type, is_compare, file_label):
        widget.axes.clear()
        widget.axes.set_axis_on()
        sns.set_style("whitegrid")

        y_label = "Число заболевших (чел.)" if "Заболеваемость" in file_label else "Число умерших (чел.)"

        if chart_type == "Линейный график":
            label_1 = f"{nosology_1[:15]}... ({region_1})" if is_compare else "Основной показатель"
            sns.lineplot(data=plot_data_1, x='year', y='indicator_value', marker='o', linewidth=2, errorbar=None,
                         ax=widget.axes, label=label_1, color="#1f77b4")
            if is_compare:
                label_2 = f"{nosology_2[:15]}... ({region_2})"
                sns.lineplot(data=plot_data_2, x='year', y='indicator_value', marker='s', linewidth=2, errorbar=None,
                             ax=widget.axes, label=label_2, color="#d62728")
            widget.axes.xaxis.get_major_locator().set_params(integer=True)
        else:
            if is_compare:
                df1, df2 = plot_data_1.copy(), plot_data_2.copy()
                df1['Группа'] = f"{nosology_1[:12]}.. ({region_1})"
                df2['Группа'] = f"{nosology_2[:12]}.. ({region_2})"
                sns.barplot(data=pd.concat([df1, df2]), x='year', y='indicator_value', hue='Группа', palette="muted",
                            errorbar=None, ax=widget.axes)
            else:
                sns.barplot(data=plot_data_1, x='year', y='indicator_value', hue='year', palette="viridis",
                            errorbar=None, legend=False, ax=widget.axes)

        widget.axes.set_ylabel(y_label, fontsize=9, fontweight='bold')
        widget.axes.set_xlabel("Год", fontsize=9, fontweight='bold')
        widget.axes.set_title(
            "Сравнительный анализ динамики показателей" if is_compare else f"Анализ: {nosology_1}\nРегион: {region_1}",
            fontsize=9, fontweight='bold')
        widget.figure.tight_layout()
        widget.canvas.draw()

    @staticmethod
    def render_single_pie(ax, disease_data, region, year_str, center_label, single_mode=False):
        ax.set_axis_off()
        top_n = 20 if not single_mode else 25

        if len(disease_data) > top_n:
            plot_series = pd.concat(
                [disease_data.head(top_n), pd.Series([disease_data.iloc[top_n:].sum()], index=['Другие заболевания'])])
        else:
            plot_series = disease_data

        wedges, _, autotexts = ax.pie(
            plot_series, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("viridis", len(plot_series)),
            pctdistance=0.80, radius=1.1,
            textprops={'fontsize': 5.5 if not single_mode else 6.0, 'fontweight': 'bold', 'color': 'white'},
            wedgeprops={'edgecolor': 'white', 'linewidth': 0.6, 'width': 0.45}
        )

        for autotext in autotexts:
            if float(autotext.get_text().replace('%', '')) < 1.5:
                autotext.set_visible(False)

        ax.text(0, 0, f"{center_label}\n{int(plot_series.sum()):,}".replace(',', ' '), ha='center', va='center',
                fontsize=7 if not single_mode else 9, fontweight='bold', color='#34495e')
        ax.set_title(f"Регион: {region}\nГод: {year_str} г.", fontsize=8 if not single_mode else 9, fontweight='bold',
                     pad=10)

        labels = [str(i)[:28] + '...' if len(str(i)) > 28 else str(i) for i in plot_series.index]
        if single_mode:
            ax.legend(wedges, labels, title="Заболевания", loc="center left", bbox_to_anchor=(1.05, 0.5), fontsize=5.5)
        else:
            ax.legend(wedges, labels, loc="upper center", bbox_to_anchor=(0.5, -0.05), fontsize=4.8, ncol=3)