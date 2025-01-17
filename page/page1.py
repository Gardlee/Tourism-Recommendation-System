import streamlit as st
import pandas as pd

# อ่านข้อมูลจากไฟล์ CSV
df = pd.read_csv("C:/Users/user/Documents/DSI 444 the project/Place_DSI444 - Sheet1.csv")
df2 = pd.read_csv("C:/Users/user/Documents/DSI 444 the project/graph_similarity.csv")


# แสดงข้อมูลใน Streamlit
st.title("Tourism Place Recommendation")

# สร้าง state สำหรับเก็บ index ของภาพที่แสดงในแต่ละแถว
if 'image_index' not in st.session_state:
    st.session_state.image_index = {tag: 0 for tag in df['Tag'].unique()}

# ตรวจสอบว่ามี state สำหรับ selected_place หรือไม่ ถ้ายังไม่มีให้สร้างใหม่
if 'selected_place' not in st.session_state:
    st.session_state.selected_place = None

if 'similar_index' not in st.session_state:
    st.session_state.similar_index = 0  # กำหนดดัชนีเริ่มต้นสำหรับ similar places

if 'similar_place' not in st.session_state:
    st.session_state.similar_place = None

# จำนวนรูปภาพต่อแถว
images_per_row = 3

# วนลูปตาม tag
def show_main_page():
    for tag in df['Tag'].unique():
        st.write(f"### {tag}")
        
        # ดึงข้อมูลของแถวตาม Tag
        rows = df[df['Tag'] == tag]

        # ตรวจสอบว่า index เกินจำนวนแถวที่มีหรือไม่ ถ้าเกินให้รีเซ็ตกลับไปที่ 0
        if st.session_state.image_index[tag] >= len(rows):
            st.session_state.image_index[tag] = 0  # รีเซ็ตให้กลับไปที่ภาพแรก

        # คำนวณดัชนีเริ่มต้นและสิ้นสุดของภาพในแถว
        start_index = st.session_state.image_index[tag]
        end_index = start_index + images_per_row
        
        # แสดงภาพปัจจุบันตาม index
        current_index = st.session_state.image_index[tag]
        
        cols = st.columns(images_per_row)
        for i in range(images_per_row):
            idx = (current_index + i) % len(rows)
            row = rows.iloc[idx]

            with cols[i]:
                    st.image(row['Image_URL'], use_column_width=True)

                    # สร้างปุ่มที่ไม่มีข้อความแล้วแสดงภาพ
                    if st.button(label= row['Name'], key=f"img_{tag}_{i}", help=row['Name']):
                        st.session_state.selected_place = row  # บันทึกสถานที่ที่เลือก
                        st.rerun()  # รีเฟรชหน้าเพื่อไปยังหน้ารายละเอียด

    
        # สร้างปุ่ม "Back" และ "Next"
        col1, col2 = st.columns([1, 0.1])

        with col1:
            if st.button("Back", key=f"back_{tag}"):
                # ลดดัชนีลงและวนไปยังภาพสุดท้ายถ้าดัชนีติดลบ
                st.session_state.image_index[tag] = (st.session_state.image_index[tag] - images_per_row) % len(rows)
                st.session_state.image_index[tag] = max(st.session_state.image_index[tag], 0)  # ป้องกันไม่ให้ติดลบ
                

        with col2:
            if st.button("Next", key=f"next_{tag}"):
                # เพิ่มดัชนีและวนกลับไปที่ภาพแรกเมื่อถึงภาพสุดท้าย
                st.session_state.image_index[tag] = (st.session_state.image_index[tag] + images_per_row) % len(rows)


# ฟังก์ชันเพื่อแสดงหน้ารายละเอียดของสถานที่
def show_detail_page():
    selected = st.session_state.selected_place
    st.title(selected['Name'])  # แสดงชื่อสถานที่
    st.image(selected['Image_URL'], caption=selected['Name'], use_column_width=True)
    st.write(f'Location: {selected["Location"]}')
    st.write(selected['Details'])  # แสดงข้อมูลเพิ่มเติม

    st.write("### Similar Places")

    # ดึงสถานที่ใกล้เคียงจาก df2 (ข้อมูลอีกไฟล์หนึ่ง)
    similar_places = df2[df2['Source_Place'] == selected['Name']]['Similar_Place'].values

    if len(similar_places) > 0:
        # คำนวณ index เริ่มต้นและสิ้นสุดตาม current index
        start_index = st.session_state.similar_index
        end_index = start_index + images_per_row
        
        cols = st.columns(images_per_row)
        for i, similar_place in enumerate(similar_places[start_index:end_index]):
            # ตรวจสอบให้แน่ใจว่า index ไม่เกินจำนวนสถานที่ที่มี
            if i < images_per_row and start_index + i < len(similar_places):
                # ค้นหาข้อมูลสถานที่ใกล้เคียงจาก df (ไฟล์หลัก)
                similar_row = df[df['Name'] == similar_place]
                if not similar_row.empty:
                    similar_row = similar_row.iloc[0]  # ดึงข้อมูลแถวแรกที่ตรงกัน

                    with cols[i]:
                        st.image(similar_row['Image_URL'], caption=similar_row['Name'], use_column_width=True)
                        if st.button(f"More about {similar_row['Name']}", key=f"similar_{i}"):
                            # บันทึกสถานที่ใกล้เคียงที่เลือก
                            st.session_state.selected_place = similar_row  # เปลี่ยนไปยังสถานที่ใกล้เคียง
                            st.session_state.similar_index = 0  # รีเซ็ตดัชนี
                            st.rerun()  # รีเฟรชหน้าเพื่อไปยังหน้ารายละเอียด

        # สร้างปุ่ม "Back" และ "Next" เพื่อเลื่อนดูสถานที่ใกล้เคียง
        col1, col2 = st.columns([1, 0.1])
        
        with col1:
            if st.button("Back", key="back"):
                # ลดดัชนีหากยังมีสถานที่ที่มากกว่า 0
                st.session_state.similar_index = (st.session_state.similar_index - images_per_row) % len(similar_places)
                # ป้องกันไม่ให้ดัชนีติดลบ
                if st.session_state.similar_index < 0:
                    st.session_state.similar_index = max(0, st.session_state.similar_index)  # ตรวจสอบให้แน่ใจว่าไม่ติดลบ

        with col2:
            if st.button("Next", key="next"):
                # เพิ่มดัชนีและวนกลับไปที่ภาพแรกเมื่อถึงภาพสุดท้าย
                st.session_state.similar_index = (st.session_state.similar_index + images_per_row) % len(similar_places)

    else:
        st.write("No similar places found.")


    # ปุ่มกลับไปยังหน้าหลัก
    if st.button("Back to List"):
        st.session_state.selected_place = None  # รีเซ็ตสถานที่ที่เลือก
        st.session_state.similar_place = None
        st.rerun()  # รีเฟรชหน้าเพื่อแสดงรายการสถานที่

# เช็คว่า selected_place มีค่าหรือไม่
if st.session_state.selected_place is not None:
    show_detail_page()  # ถ้ามีค่าจะแสดงหน้ารายละเอียด
else:
    show_main_page()  # ถ้าไม่มีค่าจะแสดงหน้าหลัก



        