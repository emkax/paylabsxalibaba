from data_simulation_module import *

def generate_patterned_timestamp(year, start_month, end_month):
    """
    Generate timestamp dengan pola:
    - Weekend ramai
    - Jumat malam spike
    - Lunch (12-14) & Dinner (19-21) ramai
    """

    # Tentukan bulan random dalam range
    month = random.randint(start_month, end_month)

    # Tentukan jumlah hari dalam bulan tsb
    last_day = calendar.monthrange(year, month)[1]

    # Pilih hari random
    day = random.randint(1, last_day)

    base_date = datetime(year, month, day)
    weekday = base_date.weekday()  # 0=Mon, 6=Sun

    # Pola jam
    if weekday in [5, 6]:  # Weekend
        hour = random.choices(
            [12, 13, 14, 19, 20, 21, 10, 16],
            weights=[15, 15, 15, 20, 20, 20, 5, 5]
        )[0]

    elif weekday == 4:  # Jumat
        hour = random.choices(
            [19, 20, 21, 12, 13, 14],
            weights=[30, 30, 30, 5, 3, 2]
        )[0]

    else:  # Weekday biasa
        hour = random.choices(
            [12, 13, 14, 19, 20, 9, 16],
            weights=[20, 20, 20, 10, 10, 5, 5]
        )[0]

    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    return datetime(year, month, day, hour, minute, second)


def modify_timestamp(
    input_file,
    output_file,
    year,
    start_month,
    end_month,
    intiate_timestamp_column="Initiation Time",
    complete_timestamp_column="Complete time"
):
    """
    Modify kolom timestamp menjadi tersebar dalam range bulan tertentu
    tanpa mengubah format Excel asli.
    """

    # Load file
    df = pd.read_excel(BASE_DIR / input_file)

    # Pastikan kolom ada
    if intiate_timestamp_column not in df.columns:
        raise ValueError(f"Kolom '{intiate_timestamp_column}' tidak ditemukan!")

    
    if complete_timestamp_column not in df.columns:
        raise ValueError(f"Kolom '{complete_timestamp_column}' tidak ditemukan!")

    # Generate timestamp baru
    new_timestamps = [
        generate_patterned_timestamp(year, start_month, end_month)
        for _ in range(len(df))
    ]


    df[intiate_timestamp_column] = pd.to_datetime(new_timestamps)

    df[complete_timestamp_column] = (
        df[intiate_timestamp_column] + pd.Timedelta(minutes=1)
    )
    
    # Simpan kembali tanpa merubah struktur
    df.to_excel(BASE_DIR / output_file, index=False)

    print("Selesai! File baru tersimpan di:", output_file)


# ===============================
# CONTOH PEMAKAIAN
# ===============================

if __name__ == "__main__":
    # input_file = "./Transaction_Order.xlsx"
    # df = pd.read_excel(BASE_DIR / input_file)
    # print(df["Initiation Time"])
    modify_timestamp(
        input_file="./Transaction_Order.xlsx",
        output_file="./Transaction_Order_Modified.xlsx",
        year=2026,
        start_month=1,
        end_month=3
    )