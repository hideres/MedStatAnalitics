import pandas as pd


class DataManager:
    def __init__(self):
        self.df = None
        # Обновленные названия файлов в соответствии с новым скриншотом структуры
        self.files_map = {
            "Заболеваемость (абс. число)": "data/morbidity.csv",
            "Смертность (абс. число)": "data/mortality_rate.csv"
        }

    def load_file(self, label):
        self.df = pd.read_csv(self.files_map[label], sep=';', encoding='utf-8-sig')

    def get_unique_regions(self):
        return sorted(self.df['object_name'].dropna().unique().astype(str))

    def get_unique_nosologies(self):
        return sorted(self.df['nosology_name'].dropna().unique().astype(str))

    def get_trend_data(self, region, nosology):
        return self.df[(self.df['object_name'] == region) & (self.df['nosology_name'] == nosology)].sort_values('year')

    def get_available_years_pie(self, region):
        return sorted(
            self.df[(self.df['object_name'] == region) & (self.df['indicator_value'] > 0)]['year'].dropna().unique())

    def get_pie_structure_data(self, region, year_str):
        y = float(year_str) if '.' in year_str else int(year_str)
        f_df = self.df[(self.df['year'] == y) & (self.df['object_name'] == region)].copy()
        f_df['nosology_name'] = f_df['nosology_name'].astype(str).str.strip()

        exclude = ["все злокачественные новообразования", "все причины смерти"]
        f_df = f_df[~f_df['nosology_name'].str.lower().isin(exclude)]

        d_data = f_df.groupby('nosology_name')['indicator_value'].sum().dropna()
        return d_data[d_data > 0].sort_values(ascending=False)