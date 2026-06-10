from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtWidgets import QFileDialog
from data_manager import DataManager
from chart_renderer import ChartRenderer
from mplwidget import *


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, exit_icon):
        super().__init__()
        uic.loadUi("data/kurs.ui", self)
        self.setWindowTitle("МедСтат Аналитика")

        self.data_manager = DataManager()
        self.setFixedSize(450, 350)
        self.stackedWidget.setCurrentIndex(0)

        self._bind_events(exit_icon)

        self.combo_file.clear()
        self.combo_file.addItems(self.data_manager.files_map.keys())
        self.combo_chart_type.clear()
        self.combo_chart_type.addItems(["Линейный график", "Столбчатая диаграмма"])

    def _bind_events(self, exit_icon):
        self.btn_start.clicked.connect(self.start_analysis)
        self.btn_load_data.clicked.connect(self.load_selected_file)
        self.btn_draw.clicked.connect(self.draw_custom_graph)

        self.btn_close_p2.setIcon(exit_icon)
        self.btn_close_p2.setIconSize(QtCore.QSize(40, 40))
        self.btn_close_p2.clicked.connect(self.close)
        self.btn_close_p3.setIcon(exit_icon)
        self.btn_close_p3.clicked.connect(self.close)

        self.btn_go_to_pie.clicked.connect(self.show_pie_page)
        self.btn_back_to_main.clicked.connect(self.show_main_page)
        self.btn_save_graph.clicked.connect(self.save_custom_graph_image)
        self.btn_save_pie.clicked.connect(self.save_pie_chart_image)

        self.combo_region.currentTextChanged.connect(self.draw_custom_graph)
        self.combo_nosology.currentTextChanged.connect(self.draw_custom_graph)
        self.combo_chart_type.currentTextChanged.connect(self.draw_custom_graph)
        self.check_compare.toggled.connect(self.toggle_compare_widgets)
        self.combo_region_2.currentTextChanged.connect(self.draw_custom_graph)
        self.combo_nosology_2.currentTextChanged.connect(self.draw_custom_graph)

        self.combo_region_pie.currentTextChanged.connect(self.update_available_years_pie)
        self.combo_year_pie.currentTextChanged.connect(self.draw_pie_chart)
        self.combo_region_pie_2.currentTextChanged.connect(self.update_available_years_pie_2)
        self.combo_year_pie_2.currentTextChanged.connect(self.draw_pie_chart)
        self.check_compare_pie.toggled.connect(self.toggle_compare_pie_widgets)

    def toggle_compare_widgets(self, checked):
        self.combo_region_2.setEnabled(checked)
        self.combo_nosology_2.setEnabled(checked)
        self.draw_custom_graph()

    def toggle_compare_pie_widgets(self, checked):
        self.combo_region_pie_2.setEnabled(checked)
        self.combo_year_pie_2.setEnabled(checked)
        if checked:
            self.update_available_years_pie_2()
        else:
            self.draw_pie_chart()

    def resize_and_center(self, w, h):
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.setGeometry((screen.width() - w) // 2 + screen.left(), (screen.height() - h) // 2 + screen.top(), w, h)
        self.setFixedSize(w, h)

    def start_analysis(self):
        self.resize_and_center(1180, 740)
        self.stackedWidget.setCurrentIndex(2)

    def show_main_page(self):
        self.resize_and_center(1180, 740)
        self.stackedWidget.setCurrentIndex(2)

    def show_pie_page(self):
        regions = self.data_manager.get_unique_regions()

        self.combo_region_pie.blockSignals(True)
        self.combo_region_pie_2.blockSignals(True)

        self.combo_region_pie.clear()
        self.combo_region_pie.addItems(regions)
        self.combo_region_pie_2.clear()
        self.combo_region_pie_2.addItems(regions)

        self.combo_region_pie.blockSignals(False)
        self.combo_region_pie_2.blockSignals(False)

        self.resize_and_center(1150, 680)
        self.stackedWidget.setCurrentIndex(1)

        self.update_available_years_pie()
        self.update_available_years_pie_2()

    def update_available_years_pie(self):
        region = self.combo_region_pie.currentText()
        if not region: return

        years = self.data_manager.get_available_years_pie(region)
        self.combo_year_pie.blockSignals(True)
        self.combo_year_pie.clear()
        self.combo_year_pie.addItems([str(int(y)) if isinstance(y, (int, float)) else str(y) for y in years])
        self.combo_year_pie.blockSignals(False)
        self.draw_pie_chart()

    def update_available_years_pie_2(self):
        region = self.combo_region_pie_2.currentText()
        if not region: return

        years = self.data_manager.get_available_years_pie(region)
        self.combo_year_pie_2.blockSignals(True)
        self.combo_year_pie_2.clear()
        self.combo_year_pie_2.addItems([str(int(y)) if isinstance(y, (int, float)) else str(y) for y in years])
        self.combo_year_pie_2.blockSignals(False)
        self.draw_pie_chart()

    # ЭТОТ МЕТОД БЫЛ ПОТЕРЯН И ИЗ-ЗА НЕГО БЫЛА ОШИБКА НА СКРИНШОТЕ:
    def load_selected_file(self):
        self.data_manager.load_file(self.combo_file.currentText())
        regions = self.data_manager.get_unique_regions()
        nosologies = self.data_manager.get_unique_nosologies()

        self.combo_region.clear()
        self.combo_region.addItems(regions)
        self.combo_region_2.clear()
        self.combo_region_2.addItems(regions)

        self.combo_nosology.clear()
        self.combo_nosology.addItems(nosologies)
        self.combo_nosology_2.clear()
        self.combo_nosology_2.addItems(nosologies)

        for i, name in enumerate(nosologies):
            if name.strip().lower() == "все злокачественные новообразования":
                self.combo_nosology.setCurrentIndex(i)
                break
        self.draw_custom_graph()

    def draw_custom_graph(self):
        r1, n1 = self.combo_region.currentText(), self.combo_nosology.currentText()
        if not r1 or not n1: return

        d1 = self.data_manager.get_trend_data(r1, n1)
        d2 = self.data_manager.get_trend_data(self.combo_region_2.currentText(),
                                              self.combo_nosology_2.currentText()) if self.check_compare.isChecked() else None

        ChartRenderer.render_custom_graph(
            self.widget, d1, d2, r1, self.combo_region_2.currentText(), n1,
            self.combo_nosology_2.currentText(), self.combo_chart_type.currentText(),
            self.check_compare.isChecked(), self.combo_file.currentText()
        )

    def draw_pie_chart(self):
        if self.data_manager.df is None: return

        r1, y1 = self.combo_region_pie.currentText(), self.combo_year_pie.currentText()
        if not r1 or not y1: return

        self.widget_pie.figure.clf()
        label = "ЗАБОЛЕВАЕМОСТЬ" if "Заболеваемость" in self.combo_file.currentText() else "СМЕРТНОСТЬ"
        d1 = self.data_manager.get_pie_structure_data(r1, y1)

        if self.check_compare_pie.isChecked():
            r2, y2 = self.combo_region_pie_2.currentText(), self.combo_year_pie_2.currentText()
            if not r2 or not y2: return

            d2 = self.data_manager.get_pie_structure_data(r2, y2)

            ChartRenderer.render_single_pie(self.widget_pie.figure.add_subplot(1, 2, 1), d1, r1, y1, label)
            ChartRenderer.render_single_pie(self.widget_pie.figure.add_subplot(1, 2, 2), d2, r2, y2, label)
            self.widget_pie.figure.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.2, wspace=0.4)
        else:
            ChartRenderer.render_single_pie(self.widget_pie.figure.add_subplot(1, 1, 1), d1, r1, y1, label,
                                            single_mode=True)
            self.widget_pie.figure.subplots_adjust(left=0.05, right=0.55, top=0.85, bottom=0.1)

        self.widget_pie.canvas.draw()

    def save_custom_graph_image(self):
        self._save(self.widget.figure, "graph_analysis")

    def save_pie_chart_image(self):
        self._save(self.widget_pie.figure, "pie_chart_structure")

    def _save(self, figure, name):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить...", f"{name}.png",
                                              "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)")
        if path: figure.savefig(path, dpi=300, bbox_inches='tight')