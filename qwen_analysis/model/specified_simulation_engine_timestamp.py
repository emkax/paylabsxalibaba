from data_simulation_module import *

class TransactionSimulator:

    def __init__(
        self,
        year,
        start_month,
        end_month,
        payday_range=(25, 30),
        event_days=[(2, 14)],  # default 14 Feb
        anomaly_ratio=0.02,    # 2% anomaly
        monthly_growth=True
    ):
        self.year = year
        self.start_month = start_month
        self.end_month = end_month
        self.payday_range = payday_range
        self.event_days = event_days
        self.anomaly_ratio = anomaly_ratio
        self.monthly_growth = monthly_growth

    def _is_payday(self, day):
        return self.payday_range[0] <= day <= self.payday_range[1]

    def _is_event_day(self, month, day):
        return (month, day) in self.event_days

    def _generate_hour(self, weekday, is_payday, is_event):
        """
        Jam transaksi dengan pola kompleks
        """

        # Event day → super spike
        if is_event:
            return random.choices(
                [12,13,14,19,20,21,22],
                weights=[10,10,10,25,25,25,15]
            )[0]

        # Payday → lebih ramai malam
        if is_payday:
            return random.choices(
                [12,13,14,19,20,21,22,23],
                weights=[10,10,10,20,25,25,15,10]
            )[0]

        # Weekend
        if weekday in [5,6]:
            return random.choices(
                [12,13,14,19,20,21,10,16],
                weights=[15,15,15,20,20,20,5,5]
            )[0]

        # Friday night spike
        if weekday == 4:
            return random.choices(
                [19,20,21,12,13,14],
                weights=[30,30,30,5,3,2]
            )[0]

        # Weekday normal (pagi sepi)
        return random.choices(
            [9,10,11,12,13,14,19,20],
            weights=[2,3,5,20,20,20,15,15]
        )[0]

    def generate_timestamp(self):
        """
        Generate timestamp dengan semua faktor spike
        """

        # Monthly growth logic
        if self.monthly_growth:
            months = list(range(self.start_month, self.end_month + 1))
            weights = np.linspace(1, 3, len(months))  # growth effect
            month = random.choices(months, weights=weights)[0]
        else:
            month = random.randint(self.start_month, self.end_month)

        last_day = calendar.monthrange(self.year, month)[1]
        day = random.randint(1, last_day)

        weekday = datetime(self.year, month, day).weekday()

        is_payday = self._is_payday(day)
        is_event = self._is_event_day(month, day)

        hour = self._generate_hour(weekday, is_payday, is_event)

        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        return datetime(self.year, month, day, hour, minute, second)

    def inject_anomaly(self, df, amount_column="Amount"):
        """
        Inject anomaly:
        - Very high transaction
        - Unusual 3AM activity
        - Random status flip
        """

        total_rows = len(df)
        anomaly_count = int(total_rows * self.anomaly_ratio)

        anomaly_indices = random.sample(range(total_rows), anomaly_count)

        for idx in anomaly_indices:

            anomaly_type = random.choice(["high_amount", "night_activity"])

            if anomaly_type == "high_amount":
                df.at[idx, amount_column] = random.randint(5_000_000, 20_000_000)

            elif anomaly_type == "night_activity":
                dt = pd.to_datetime(df.at[idx, "Initiation Time"])
                df.at[idx, "Initiation Time"] = dt.replace(hour=3).strftime("%Y-%m-%d %H:%M:%S")

        return df


def modify_excel_with_advanced_pattern(
    input_file,
    output_file,
    year,
    start_month,
    end_month,
    payday_range=(25, 30),
    event_days=[(2, 14)],
    anomaly_ratio=0.02
):
    df = pd.read_excel(BASE_DIR / input_file)

    simulator = TransactionSimulator(
        year=year,
        start_month=start_month,
        end_month=end_month,
        payday_range=payday_range,
        event_days=event_days,
        anomaly_ratio=anomaly_ratio,
        monthly_growth=True
    )

    new_timestamps = []
    for _ in range(len(df)):
        ts = simulator.generate_timestamp()
        new_timestamps.append(ts.strftime("%Y-%m-%d %H:%M:%S"))

    df["Initiation Time"] = new_timestamps

    # Inject anomaly
    df = simulator.inject_anomaly(df)

    df.to_excel(BASE_DIR / output_file, index=False)

    print("Advanced simulation complete!")
    print("Saved to:", output_file)


# ===============================
# 🔥 EXAMPLE USAGE
# ===============================

if __name__ == "__main__":

    modify_excel_with_advanced_pattern(
        input_file="./Transaction_Order.xlsx",
        output_file="./Transaction_Order_Advanced_Simulated.xlsx",
        year=2026,
        start_month=1,
        end_month=3,

        # Default (bisa diubah)
        payday_range=(25, 30),
        event_days=[(2, 14)],  # 14 Februari
        anomaly_ratio=0.03     # 3% anomaly
    )