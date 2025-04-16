import pandas as pd
import os
from datetime import datetime, timedelta

def generate_time_slots(days, start, end):
    slots = []
    start_dt = datetime.strptime(start, "%H:%M")
    end_dt = datetime.strptime(end, "%H:%M")
    for day in days:
        current = start_dt
        while current <= end_dt:
            time_str = current.strftime("%H:%M")
            slots.append((day, time_str))
            current += timedelta(minutes=30)
    return slots

def build_direct_availability_timetable(folder_files):
    slots = generate_time_slots(["월", "화", "수", "목", "금"], "08:30", "17:30")
    timetable = pd.DataFrame(slots, columns=["요일", "시간"])
    timetable["근무자"] = ""

    for path in folder_files:
        name = os.path.basename(path).replace(".xlsx", "")
        df = pd.read_excel(path)
        df.rename(columns={df.columns[0]: "시간"}, inplace=True)
        days = df.columns[1:]

        for day in days:
            for _, row in df.iterrows():
                t = row["시간"]
                if pd.notna(row[day]) and row[day] == 1:
                    mask = (timetable["요일"] == day) & (timetable["시간"] == t)
                    timetable.loc[mask, "근무자"] += name + ", "

    timetable["근무자"] = timetable["근무자"].str.rstrip(", ")
    df_out = timetable.pivot(index="시간", columns="요일", values="근무자")
    return df_out[["월", "화", "수", "목", "금"]]

def main(output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)

    input_dir = "input"
    xlsx_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.endswith(".xlsx") and not f.startswith("~$")
    ]

    timetable_df = build_direct_availability_timetable(xlsx_files)
    output_path = os.path.join(output_dir, "통합_가용_시간표.xlsx")
    timetable_df.to_excel(output_path)
    print(f"✅ 시간표 생성 완료: {output_path}")

if __name__ == "__main__":
    main()
