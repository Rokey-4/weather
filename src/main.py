import flet as ft
import flet_charts as fch
import weather_api

# 1. 데이터 전처리 함수
def preprocess_weather(raw_list):
    sky_map = {"1": "☀️ 맑음", "3": "⛅ 구름많음", "4": "☁️ 흐림"}
    processed = []
    
    for item in raw_list:
        processed.append({
            "time": f"{item['fcst_time'][:2]}시",
            "temp": float(item.get('tmp', 0)),
            "hum": int(item.get('hum', 0)),
            "pop": int(item.get('pop', 0)),
            "sky": sky_map.get(str(item.get('sky', '1')), "알수없음")
        })
    return processed

# 2. Flet UI 메인 함수
def main(page: ft.Page):
    page.title = "기상 정보 대시보드"
    page.theme_mode = ft.ThemeMode.DARK 
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    search_input = ft.TextField(label="지역 입력 (예: 서울, 부산)", width=300)
    
    current_temp = ft.Text("0°C", size=60, weight=ft.FontWeight.BOLD)
    current_sky = ft.Text("상태", size=24)
    current_details = ft.Text("습도: 0% | 강수확률: 0%", size=18, color=ft.Colors.WHITE_70)
    
    chart_container = ft.Column()

    def update_charts(processed_data):
        chart_container.controls.clear()
        
        # 💡 팩트: Y축(기온)의 최소/최대 여백을 계산해서 차트가 찌그러지지 않게 폅니다.
        temps = [d["temp"] for d in processed_data]
        min_temp = min(temps) - 5
        max_temp = max(temps) + 5
        
        # 기온 데이터 (Line Chart)
        temp_points = [
            fch.LineChartDataPoint(i, d["temp"], tooltip=f"{d['temp']}°C") 
            for i, d in enumerate(processed_data)
        ]
        temp_chart = fch.LineChart(
            data_series=[
                fch.LineChartData(
                    points=temp_points,
                    stroke_width=4,
                    color=ft.Colors.RED_400,
                    curved=True
                )
            ],
            border=ft.border.all(1, ft.Colors.WHITE_24),
            left_axis=fch.ChartAxis(title=ft.Text("기온 (°C)")),
            bottom_axis=fch.ChartAxis(),
            min_x=0,                               # 💡 X축 시작 고정
            max_x=len(processed_data) - 1,         # 💡 X축 끝 고정
            min_y=min_temp,                        # 💡 Y축 최저 기온 고정
            max_y=max_temp,                        # 💡 Y축 최고 기온 고정
            height=250,
            expand=True,
            interactive=True,
        )

        # 습도 데이터 (Bar Chart)
        hum_groups = [
            fch.BarChartGroup(
                x=i, 
                rods=[fch.BarChartRod(to_y=d["hum"], color=ft.Colors.BLUE_400, width=15, tooltip=f"{d['hum']}%")]
            ) 
            for i, d in enumerate(processed_data)
        ]
        hum_chart = fch.BarChart(
            groups=hum_groups,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.WHITE_24)), 
            left_axis=fch.ChartAxis(title=ft.Text("습도 (%)")),
            bottom_axis=fch.ChartAxis(),
            max_y=100,  # 💡 습도는 최대 100%이므로 고정
            height=250,
            expand=True,
            interactive=True,
        )

        chart_container.controls.extend([
            ft.Text("📈 24시간 기온 변화", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(content=temp_chart, padding=10),
            ft.Divider(height=30),
            ft.Text("💧 24시간 습도 변화", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(content=hum_chart, padding=10)
        ])
    def btn_click(e):
        region = search_input.value.strip()
        if not region:
            return
            
        try:
            raw_result = weather_api.forecast(region)
            processed_data = preprocess_weather(raw_result['data'])
            
            now_weather = processed_data[0]
            current_temp.value = f"{now_weather['temp']}°C"
            current_sky.value = f"{region} | {now_weather['sky']}"
            current_details.value = f"습도: {now_weather['hum']}% | 강수확률: {now_weather['pop']}%"
            
            update_charts(processed_data)
            page.update()
            
        except Exception as ex:
            # 💡 수정됨: 스낵바(알림창)를 띄우는 최신 규격 적용
            page.open(ft.SnackBar(content=ft.Text(f"오류 발생: {str(ex)}")))

    search_row = ft.Row([search_input, ft.ElevatedButton("검색", on_click=btn_click)])
    
    current_weather_view = ft.Column(
        controls=[current_sky, current_temp, current_details],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.add(
        search_row,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=current_weather_view,
            alignment=ft.Alignment(0, 0), 
            padding=20,
            bgcolor=ft.Colors.BLUE_GREY_900,
            border_radius=15
        ),
        ft.Divider(height=30),
        chart_container
    )

if __name__ == '__main__':
    ft.run(main)