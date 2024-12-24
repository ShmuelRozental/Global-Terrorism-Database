import pandas as pd


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.rename(columns={
        'Country': 'country_txt',
        'City': 'city',
        'Perpetrator': 'gname',
        'Injuries': 'nwound',
        'Fatalities': 'nkill',
    }, inplace=True)
    return df