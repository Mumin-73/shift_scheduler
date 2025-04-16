import cv2
import numpy as np
import pandas as pd
import os
import sys

def is_horizontal(line, angle_threshold=10):
    x1, y1, x2, y2 = line
    angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
    return abs(angle) < angle_threshold

def is_vertical(line, angle_threshold=10):
    x1, y1, x2, y2 = line
    angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
    return abs(abs(angle) - 90) < angle_threshold

def merge_lines_by_axis(lines, is_axis_fn, axis=1, gap=30):
    lines = [line[0] for line in lines if is_axis_fn(line[0])]
    grouped = {}
    for line in lines:
        coord = (line[1] + line[3]) // 2 if axis == 1 else (line[0] + line[2]) // 2
        found = False
        for k in list(grouped.keys()):
            if abs(coord - k) < gap:
                grouped[k].append(line)
                found = True
                break
        if not found:
            grouped[coord] = [line]

    merged = []
    for k, group in grouped.items():
        xs = [p for line in group for p in [line[0], line[2]]]
        ys = [p for line in group for p in [line[1], line[3]]]
        if axis == 1:
            merged.append((min(xs), k, max(xs), k))
        else:
            merged.append((k, min(ys), k, max(ys)))
    return merged

def imread_unicode(path):
    stream = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(stream, cv2.IMREAD_COLOR)

def standardize_dataframe(df):
    standard_index = ["8:30", "9:00", "9:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
                      "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"]
    standard_columns = ['월', '화', '수', '목', '금']
    return df.reindex(index=standard_index, columns=standard_columns, fill_value=1)

def generate_availability_from_image(image_path, bg='auto'):
    img = imread_unicode(image_path)
    if img is None:
        raise FileNotFoundError(f"이미지를 불러올 수 없습니다: {image_path}")

    original = img.copy()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0, 30, 60), (180, 255, 255))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    cleaned_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(cleaned_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(cnt) for cnt in contours if cv2.boundingRect(cnt)[2] > 30 and cv2.boundingRect(cnt)[3] > 30]

    if bg == 'auto':
        bg_sample = img[5, 5]
        bg_brightness = np.mean(bg_sample)
        bg = 'white' if bg_brightness > 127 else 'black'

    img_cleaned = img.copy()
    bg_color = np.median(original, axis=(0, 1)).astype(np.uint8)
    for (x, y, w, h) in boxes:
        if w > 60 and h > 40:
            cv2.rectangle(img_cleaned, (x, y), (x + w, y + h), color=bg_color.tolist(), thickness=-1)

    gray = cv2.cvtColor(img_cleaned, cv2.COLOR_BGR2GRAY)
    if bg == 'black':
        gray = cv2.bitwise_not(gray)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    binary = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 10)

    edges = cv2.Canny(binary, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=20)
    if lines is None:
        raise ValueError("❌ 선을 감지하지 못했습니다.")

    horiz_lines = merge_lines_by_axis(lines, is_horizontal, axis=1)
    vert_lines = merge_lines_by_axis(lines, is_vertical, axis=0)

    height, width = original.shape[:2]
    full_horiz_lines = []
    full_vert_lines = []
    for x1, y1, x2, y2 in horiz_lines:
        y = (y1 + y2) // 2
        full_horiz_lines.append(y)
    for x1, y1, x2, y2 in vert_lines:
        x = (x1 + x2) // 2
        full_vert_lines.append(x)

    full_horiz_lines = sorted(full_horiz_lines)
    full_vert_lines = sorted(full_vert_lines)

    midlines = []
    for i in range(len(full_horiz_lines) - 1):
        y = (full_horiz_lines[i] + full_horiz_lines[i + 1]) // 2
        midlines.append(y)

    all_y = sorted(full_horiz_lines + midlines)
    all_x = full_vert_lines

    availability = np.ones((len(all_y)-1, len(all_x)-1), dtype=int)
    for (bx, by, bw, bh) in boxes:
        for i in range(len(all_y) - 1):
            for j in range(len(all_x) - 1):
                cell_x1, cell_x2 = all_x[j], all_x[j+1]
                cell_y1, cell_y2 = all_y[i], all_y[i+1]
                if (bx < cell_x2 and bx + bw > cell_x1 and
                    by < cell_y2 and by + bh > cell_y1):
                    availability[i, j] = 0

    df = pd.DataFrame(availability, 
                      index=[f'{i//2 + 9}:{"30" if i%2 else "00"}' for i in range(len(all_y)-1)],
                      columns=['월', '화', '수', '목', '금'][:len(all_x)-1])

    return standardize_dataframe(df)

def process_all_images(image_dir="images", output_dir="input"):
    os.makedirs(output_dir, exist_ok=True)
    for file in os.listdir(image_dir):
        if file.lower().endswith(".jpg"):
            name = os.path.splitext(file)[0]
            image_path = os.path.join(image_dir, file)
            try:
                df = generate_availability_from_image(image_path)
                df.to_excel(os.path.join(output_dir, f"{name}.xlsx"), index=True)
                print(f"✅ {file} → {name}.xlsx 저장 완료")
            except Exception as e:
                print(f"⚠️ {file} 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    image_dir = sys.argv[1] if len(sys.argv) > 1 else "images"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "input"
    process_all_images(image_dir, output_dir)
