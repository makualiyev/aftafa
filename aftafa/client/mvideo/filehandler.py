import os
import logging
from datetime import datetime

import pandas as pd

from aftafa.client.mvideo.models import session as db_session, Supplier


logger = logging.getLogger(__name__)

class FileHandler:
    """
    Class that handles Mail Listing stocks that MVM sends on
    a daily basis. The format of a file template itself changes
    regularly. So there is a numeration of formats:
    """
    FORMATS = {
        'format_1': (datetime(2023, 1, 1), datetime(2023, 11, 15)),
        'format_2': (datetime(2023, 11, 16), datetime(2030, 1, 1))
    }

    REN_COLS = {
            'format_1': {
                'Бизнес-юнит': 'business_unit',
                'Категория': 'category',
                'Планнейм': 'plan_name',
                'Группа': 'group',
                'Технология продажи': 'sale_technology',
                'Артикул': 'material_number',
                'Название': 'name',
                'Цена на ценнике на дату выгрузки': 'price_up_to_date',
                'Годный сток + резерв под самовывоз': 'fit_stock',
                'Общий сток': 'overall_stock',
                'Продано шт за текущий месяц': 'sold_qty'
            },
            'format_2': {
                'Бизнес-юнит': 'business_unit',
                'Категория': 'category',
                'Планнейм': 'plan_name',
                'Группа': 'group',
                'Технология продаж': 'sale_technology',
                'Артикул': 'material_number',
                'Название': 'name',
                'Цена на ценнике': 'price_up_to_date',
                'Основной запас (годный сток), ШТ': 'fit_stock',
                'Общий сток, ШТ': 'overall_stock',
                'Продажи за текущий месяц, ШТ': 'sold_qty',
                'Продажи за текущий месяц, РУБ': 'sold_sum'
            }
        }
    REN_COLS_2 = {
        'format_1': {
            "Объект": "object_number",
            "Город": "city",
            "Название": "object_type",
            "Секция": "object_division",
            "Тип хранения": "storage_type",
            "Поставщик (с регистром)": "supplier",
            "Материал (Номер)": "material_number",
            # "Материал Эльдорадо": ""
            "Материал Текст": "material_name",
            "Материал: Технология продаж Текст": "product_type",
            "Материал бренд": "material_brand",
            "Годный сток + резерв под самовывоз": "fit_stock",
            "Суммарный сток": "overall_stock"
        },
        'format_2': {
            'Объект': 'object_number',
            'Город': 'city',
            'Название': 'object_type',
            'Секция': 'object_division',
            'Тип хранения': 'storage_type',
            'Поставщик': 'supplier',
            'Артикул': 'material_number',
            # 'Артикул Эльдорадо',
            'Название.1': 'material_name',
            'Технология продаж': 'product_type',
            'Материал бренд': 'material_brand',
            'Основной запас (годный сток), ШТ': 'fit_stock',
            'Основной запас (годный сток), РУБ': 'fit_stock_in_rub',
            'Резерв (годный сток), ШТ': 'reserved_stock',
            'Резерв (годный сток), РУБ': 'reserved_stock_in_rub',
            'Общий сток, ШТ': 'overall_stock',
            'Общий сток, РУБ': 'overall_stock_in_rub'
        }
    }

    def __init__(self, supplier: str, report_date: str | None = None) -> None:
        if not report_date:
            report_date = datetime.today().strftime('%Y-%m-%d')
        self._report_date = datetime.strptime(report_date, '%Y-%m-%d').strftime('%d-%m-%Y')
        self.supplier = supplier

    @property
    def source_dir(self) -> str:
        return f'E:\\shoptalk\\marketplace_\\MV\\{self.supplier}\\stocks'
    
    def get_format_of_template(self, report_date: str) -> int:
        if datetime.strptime(report_date, '%Y-%m-%d') > self.FORMATS['format_1'][1]:
            return 2
        else:
            return 1


    def load_file(self, report_date: str | None = None) -> None:
        if not report_date:
            report_date = self._report_date
        else:
            report_date = datetime.strptime(report_date, '%Y-%m-%d').strftime('%d-%m-%Y')
        file_path: str = os.path.join(self.source_dir, f'mvm_stocks_{report_date}.xlsx')
        file_xl: pd.io.excel._base.ExcelFile = pd.ExcelFile(file_path)
        return file_xl
    
    def validate_file(self, xl_file: pd.io.excel._base.ExcelFile) -> bool:
        """
        Validates pandas ExcelFile loaded into memory by parsing
        sheet names and checking some basic information
        """
        # if xl_file.sheet_names != ['Продажи с начала месяца', 'Стоки по объектам']:
        if xl_file.sheet_names != ['Глоссарий', 'Продажи с начала месяца', 'Стоки по объектам']:
            logger.info(f"Not the right sheets for this file")
            return False
        return True

    def load_frame(self, xl_file: pd.io.excel._base.ExcelFile, report_date: str | None = None) -> pd.DataFrame:
        if not report_date:
            report_date = self._report_date
        else:
            report_date = report_date

        report_format: str = f"format_{str(self.get_format_of_template(report_date=report_date))}"

        REN_COLS = self.REN_COLS.get(report_format)

        df: pd.DataFrame = xl_file.parse(sheet_name='Продажи с начала месяца')

        if report_format == 'format_1':
            df = df.set_axis(labels=df.iloc[3], axis=1).iloc[4:][list(REN_COLS.keys())].reset_index(drop=True)

            if 'Сумма:' in set(df.iloc[-1, :].value_counts().index) and len(set(df.iloc[-1, :].value_counts().index)) == 2:
                df = df.iloc[:-1, :]
            else:
                if df.iloc[:-1, :].shape[0] == 1 and not list(df.iloc[:-1, :].value_counts()):
                    print('Empty file')
                    return -1
                else:
                    print('Last row is not for totals now')
                    df = df.iloc[:-1, :]

            df = df.rename(columns=REN_COLS)
            df['report_date'] = report_date
            df[['fit_stock', 'overall_stock', 'sold_qty']] = df[['fit_stock', 'overall_stock', 'sold_qty']].fillna(0)
            df['material_number'] = df['material_number'].map(int)
            df['supplier_code'] = db_session.query(Supplier).filter(Supplier.slug == self.supplier).first().id

        else:
            df = df.set_axis(labels=df.iloc[2], axis=1).iloc[3:][list(REN_COLS.keys())].reset_index(drop=True)

            if 'Сумма:' in set(df.iloc[-1, :].value_counts().index) and len(set(df.iloc[-1, :].value_counts().index)) == 2:
                df = df.iloc[:-1, :]
            else:
                if df.iloc[:-1, :].shape[0] == 1 and not list(df.iloc[:-1, :].value_counts()):
                    print('Empty file')
                    return -1
                else:
                    print('Last row is not for totals now')
                    df = df.iloc[:-1, :]

            df = df.rename(columns=REN_COLS)
            df['report_date'] = report_date
            df[['fit_stock', 'overall_stock', 'sold_qty', 'sold_sum']] = df[['fit_stock', 'overall_stock', 'sold_qty', 'sold_sum']].fillna(0)
            df['material_number'] = df['material_number'].map(int)
            df['supplier_code'] = db_session.query(Supplier).filter(Supplier.slug == self.supplier).first().id

        return df
    
    def prep_records(self, df: pd.DataFrame) -> dict:
        return df.to_dict(orient='records')
    
    def load_frame_second_sheet(self, xl_file: pd.io.excel._base.ExcelFile, report_date: str | None = None) -> pd.DataFrame:
        if not report_date:
            report_date = self._report_date
        else:
            report_date = report_date

        report_format: str = f"format_{str(self.get_format_of_template(report_date=report_date))}"

        REN_COLS_2 = self.REN_COLS_2.get(report_format)

        df: pd.DataFrame = xl_file.parse(sheet_name='Стоки по объектам')
        if report_format == 'format_1':
            df = df.set_axis(labels=df.iloc[0], axis=1).iloc[1:, 1:][list(REN_COLS_2.keys())].rename(columns=REN_COLS_2).reset_index(drop=True)
            df['report_date'] = report_date
            df[['fit_stock', 'overall_stock']] = df[['fit_stock', 'overall_stock']].fillna(0)
            df['material_number'] = df['material_number'].map(int)
            df['supplier_code'] = db_session.query(Supplier).filter(Supplier.slug == self.supplier).first().id
        else:
            null_cols = [
                'fit_stock', 'overall_stock', 'reserved_stock',
                'fit_stock_in_rub', 'overall_stock_in_rub', 'reserved_stock_in_rub'
            ]
            df = df[list(REN_COLS_2.keys())].rename(columns=REN_COLS_2).reset_index(drop=True)
            df = df[~df['material_number'].isna()].reset_index(drop=True)
            df['report_date'] = report_date
            df[null_cols] = df[null_cols].fillna(0)
            df['material_number'] = df['material_number'].map(int)
            df['supplier_code'] = db_session.query(Supplier).filter(Supplier.slug == self.supplier).first().id

        return df
    
    def prep_records_second_sheet(self, df: pd.DataFrame) -> dict:
        return df.to_dict(orient='records')
