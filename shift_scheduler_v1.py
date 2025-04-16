import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Tuple, Dict

def generate_time_slots(days: List[str], start: str, end: str) -> List[Tuple[str, str]]:
    slots = []
    start_dt = datetime.strptime(start, "%H:%M")
    end_dt = datetime.strptime(end, "%H:%M")
    for day in days:
        current = start_dt
        while current <= end_dt:
            slots.append((day, current.strftime("%H:%M")))
            current += timedelta(minutes=30)
    return slots

def load_excel_as_availability(folder_files):
    all_avail_df = None
    for path in folder_files:
        name = os.path.basename(path).replace(".xlsx", "")
        df_xlsx = pd.read_excel(path)
        df_xlsx.rename(columns={df_xlsx.columns[0]: "시간"}, inplace=True)
        days = df_xlsx.columns[1:]

        slots = generate_time_slots(["월", "화", "수", "목", "금"], "08:30", "17:30")
        base_df = pd.DataFrame(slots, columns=["요일", "시간"])
        base_df[name] = 0

        for day in days:
            for _, row in df_xlsx.iterrows():
                t = row["시간"]
                try:
                    if row[day] == 1:
                        base_df.loc[(base_df["요일"] == day) & (base_df["시간"] == t), name] = 1
                except:
                    continue

        if all_avail_df is None:
            all_avail_df = base_df
        else:
            all_avail_df = all_avail_df.merge(base_df, on=["요일", "시간"], how="outer")

    return all_avail_df

def schedule_with_all_constraints(availability_df, workers, slots):
    assignment_df = availability_df[["요일", "시간"] + workers].copy()
    for w in workers:
        assignment_df[w] = 0

    work_count = {name: 0 for name in workers}
    work_streaks = {name: [] for name in workers}
    morning_count = {name: 0 for name in workers}

    def get_previous_time(current_time_str):
        t = datetime.strptime(current_time_str, "%H:%M")
        return (t - timedelta(minutes=30)).strftime("%H:%M")

    def get_next_time(current_time_str):
        t = datetime.strptime(current_time_str, "%H:%M")
        return (t + timedelta(minutes=30)).strftime("%H:%M")

    def check_lunch_streak_violation(streak):
        if len(streak) >= 14:
            if any(t[1] in ["12:00", "12:30"] for t in streak):
                return True
        return False

    def can_work_minimum_one_hour(name, day, time):
        next_time = get_next_time(time)
        if (day, next_time) in slots:
            return all([
                availability_df.loc[(availability_df["요일"] == day) & (availability_df["시간"] == time), name].values[0] == 1,
                availability_df.loc[(availability_df["요일"] == day) & (availability_df["시간"] == next_time), name].values[0] == 1
            ])
        return False

    for (day, time) in slots:
        available = [w for w in workers if availability_df.loc[
            (availability_df['요일'] == day) & (availability_df['시간'] == time), w].values[0] == 1]

        prev_time = get_previous_time(time) if time != "08:30" else None
        prev_workers = []
        if prev_time:
            prev_workers = [
                w for w in available
                if assignment_df.loc[(assignment_df["요일"] == day) & (assignment_df["시간"] == prev_time), w].values[0] == 1
            ]

        prioritized = sorted(prev_workers, key=lambda w: work_count[w])
        remaining = [w for w in available if w not in prioritized]

        if time == "08:30":
            candidates = sorted(available, key=lambda w: morning_count[w])
            for name in candidates:
                if can_work_minimum_one_hour(name, day, time):
                    assignment_df.loc[(assignment_df["요일"] == day) & (assignment_df["시간"] == time), name] = 1
                    morning_count[name] += 1
                    work_count[name] += 1
                    work_streaks[name] = [(day, time)]
                    break
            continue

        prioritized += sorted(remaining, key=lambda w: work_count[w])
        selected = []
        for name in prioritized:
            if name in prev_workers:
                new_streak = work_streaks[name] + [(day, time)]
            else:
                if not can_work_minimum_one_hour(name, day, time):
                    continue
                new_streak = [(day, time)]

            if not check_lunch_streak_violation(new_streak):
                assignment_df.loc[(assignment_df["요일"] == day) & (assignment_df["시간"] == time), name] = 1
                work_count[name] += 1
                work_streaks[name] = new_streak
                selected.append(name)

            if len(selected) >= 2:
                break

    return assignment_df

def convert_to_pretty_timetable(assignment_df: pd.DataFrame, workers: List[str]) -> pd.DataFrame:
    def join_names(row):
        return ", ".join([name for name in workers if row[name] == 1])
    df = assignment_df.copy()
    df["근무자"] = df.apply(join_names, axis=1)
    df_out = df[["요일", "시간", "근무자"]]
    df_pivot = df_out.pivot(index="시간", columns="요일", values="근무자")
    return df_pivot[["월", "화", "수", "목", "금"]]

def calculate_total_hours(assignment_df: pd.DataFrame, workers: List[str]) -> Dict[str, float]:
    return {name: assignment_df[name].sum() * 0.5 for name in workers}

def save_results_to_excel(pretty_df: pd.DataFrame, total_hours: Dict[str, float], folder: str = "."):
    result_df = pd.DataFrame(list(total_hours.items()), columns=["이름", "총 근무시간"])
    os.makedirs(folder, exist_ok=True)
    pretty_df.to_excel(os.path.join(folder, "자동배정_시간표.xlsx"), index=True)
    result_df.to_excel(os.path.join(folder, "총_근무시간.xlsx"), index=False)

def main():
    input_dir = "input"
    output_dir = "output"

    xlsx_files = [
        os.path.join(input_dir, f) for f in os.listdir(input_dir)
        if f.endswith(".xlsx") and not f.startswith("~$")
    ]
    workers = [os.path.basename(f).replace(".xlsx", "") for f in xlsx_files]
    weekdays = ["월", "화", "수", "목", "금"]
    slots = generate_time_slots(weekdays, "08:30", "17:30")

    availability_df = load_excel_as_availability(xlsx_files)
    assignment_df = schedule_with_all_constraints(availability_df, workers, slots)
    pretty_df = convert_to_pretty_timetable(assignment_df, workers)
    total_hours = calculate_total_hours(assignment_df, workers)

    save_results_to_excel(pretty_df, total_hours, output_dir)
    print("✅ 자동 배정 완료 → output 폴더에 결과 저장됨")

if __name__ == "__main__":
    main()
