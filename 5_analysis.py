import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform
from matplotlib import font_manager, rc
import datetime
import matplotlib.dates as mdates

sns.set_theme(style="whitegrid")

# --- 한글 폰트 설정 (Windows 기준) ---
if platform.system() == 'Windows':
    path = 'c:/Windows/Fonts/malgun.ttf'
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
elif platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
else:
    print('Check your OS system')

# ========== 1. CSV 파일 병합 및 전처리 ==========

file_list = [f'./data/dataverse_files_2000-2008/200{i}.csv' for i in range(4, 9)]
dfs = []

for file_path in file_list:
    try:
        # 분석에 필요한 컬럼만 읽어오기 (Origin, Dest 추가)
        df_temp = pd.read_csv(
            file_path,
            encoding='latin-1',
            usecols=[
                'Year', 'Month', 'DayofMonth',
                'DepTime', 'ArrTime', 'CRSDepTime', 'CRSArrTime',
                'TailNum', 'Origin', 'Dest',
                'ArrDelay', 'DepDelay', 'LateAircraftDelay'
            ]
        )
        dfs.append(df_temp)
        print(f"Loaded {file_path} with shape: {df_temp.shape}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

df = pd.concat(dfs, ignore_index=True)
print("Merged df shape:", df.shape)

# 숫자형 변환
num_cols = ['Year','Month','DayofMonth','DepTime','ArrTime','CRSDepTime','CRSArrTime','ArrDelay','DepDelay','LateAircraftDelay']
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 결측치 제거
df.dropna(subset=num_cols + ['TailNum','Origin','Dest'], inplace=True)
print("After dropping NA, df shape:", df.shape)

# ---------- 0. 허브 공항 선정 및 일별 평균 지연 집계 ----------
# (전제) df에 'Date'(datetime), 'Origin', 'Dest', 'ArrDelay', 'DepDelay' 컬럼 존재

# 가장 많이 출발하는 공항(Origin 기준)을 허브로 선정
airport_counts = df['Origin'].value_counts().reset_index()
airport_counts.columns = ['Airport', 'FlightCount']
hub_airport = airport_counts.iloc[0]['Airport']
print("선택된 허브 공항:", hub_airport)

# 허브 공항에 도착한 항공편 → 일별 평균 도착 지연
hub_arr = (
    df[df['Dest'] == hub_airport]
    .groupby('Date')['ArrDelay']
    .mean()
    .reset_index()
    .rename(columns={'ArrDelay': 'AvgArrDelay'})
)

# 허브 공항에서 출발한 항공편 → 일별 평균 출발 지연
hub_dep = (
    df[df['Origin'] == hub_airport]
    .groupby('Date')['DepDelay']
    .mean()
    .reset_index()
    .rename(columns={'DepDelay': 'AvgDepDelay'})
)

# 병합 & 정렬
hub_df = pd.merge(hub_arr, hub_dep, on='Date', how='inner')
hub_df.sort_values('Date', inplace=True)

# 전날 도착 지연(1일 lag)
hub_df['LagAvgArrDelay'] = hub_df['AvgArrDelay'].shift(1)

# ---------- (A) 주 단위 집계 & 시각화 ----------
hub_df['Week'] = hub_df['Date'].dt.to_period('W')  # 주(Week) 단위

weekly_df = hub_df.groupby('Week', as_index=False).agg({
    'AvgArrDelay': 'mean',
    'AvgDepDelay': 'mean',
    'LagAvgArrDelay': 'mean'
})

plt.figure(figsize=(14,6))
plt.plot(weekly_df['Week'].astype(str), weekly_df['AvgDepDelay'],
         label='주간 평균 출발 지연',
         marker='o', markersize=4, linewidth=2)
plt.plot(weekly_df['Week'].astype(str), weekly_df['AvgArrDelay'],
         label='주간 평균 도착 지연',
         marker='s', markersize=4, linewidth=2)
plt.plot(weekly_df['Week'].astype(str), weekly_df['LagAvgArrDelay'],
         label='전주 평균 도착 지연',
         marker='^', markersize=4, linestyle='--', linewidth=2)

plt.title(f'{hub_airport} 공항 - 주 단위 지연 전파 분석')
plt.xlabel('주(Week)')
plt.ylabel('지연 시간 (분)')
plt.legend()

# x축 라벨 간격 줄이기:  주가 많으면 모든 tick을 표시하면 겹침
# -> 예: x축 tick을 일정 간격(예: 5주 간격)만 표시
xtick_step = max(len(weekly_df)//20, 1)  # 전체 주 개수에 따라 동적 설정
plt.xticks(
    ticks=range(0, len(weekly_df), xtick_step),
    labels=weekly_df['Week'].astype(str).iloc[::xtick_step],
    rotation=45
)

plt.tight_layout()
plt.show()

# ---------- (B) 이동평균(7일) & 시각화 ----------
hub_df = hub_df.sort_values('Date')
hub_df['AvgArrDelay_7d'] = hub_df['AvgArrDelay'].rolling(7).mean()
hub_df['AvgDepDelay_7d'] = hub_df['AvgDepDelay'].rolling(7).mean()
hub_df['LagAvgArrDelay_7d'] = hub_df['LagAvgArrDelay'].rolling(7).mean()

plt.figure(figsize=(14, 6))
plt.plot(hub_df['Date'], hub_df['AvgDepDelay_7d'],
         label='7일 이동평균 출발 지연',
         marker='o', markersize=3, linewidth=2)
plt.plot(hub_df['Date'], hub_df['AvgArrDelay_7d'],
         label='7일 이동평균 도착 지연',
         marker='s', markersize=3, linewidth=2)
plt.plot(hub_df['Date'], hub_df['LagAvgArrDelay_7d'],
         label='(전날) 7일 이동평균 도착 지연',
         marker='^', markersize=3, linestyle='--', linewidth=2)

plt.title(f'{hub_airport} 공항 - 7일 이동평균 지연 추세')
plt.xlabel('날짜')
plt.ylabel('지연 시간 (분)')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ---------- (C) Box Plot (월별) ----------
hub_df['YearMonth'] = hub_df['Date'].dt.to_period('M').astype(str)

plt.figure(figsize=(14,6))
sns.boxplot(data=hub_df, x='YearMonth', y='AvgDepDelay')
plt.title(f'{hub_airport} 공항 - 월별 출발 지연 Box Plot')
plt.xlabel('월(YearMonth)')
plt.ylabel('지연 시간 (분)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 만약 'DepTime' / 'ArrTime' / 'DepDelay' / 'ArrDelay' 등이 문자열일 경우 숫자로 변환
df['DepTime'] = pd.to_numeric(df['DepTime'], errors='coerce')
df['ArrTime'] = pd.to_numeric(df['ArrTime'], errors='coerce')
df['DepDelay'] = pd.to_numeric(df['DepDelay'], errors='coerce')
df['ArrDelay'] = pd.to_numeric(df['ArrDelay'], errors='coerce')

# 결측치가 있으면 제거 (옵션)
df.dropna(subset=['TailNum','Date','DepTime','ArrTime','DepDelay','ArrDelay','Origin','Dest'], inplace=True)

# ============================
# 1. 상위 5개 기체(TailNum) 선택
# ============================
tail_stats = df.groupby('TailNum').agg(flight_count=('TailNum', 'count')).reset_index()
top_tails = tail_stats.sort_values('flight_count', ascending=False).head(5)['TailNum'].tolist()
print("선택된 상위 5개 기체:", top_tails)

# 상위 기체 데이터만 선택
df_subset = df[df['TailNum'].isin(top_tails)].copy()

# ===============================
# 2. 기체별로 날짜+DepTime 정렬
# ===============================
df_subset.sort_values(['TailNum','Date','DepTime'], inplace=True)

# ===============================
# 3. 이전 항공편 정보 연결 (shift)
# ===============================
# 이전 비행의 도착 공항, 도착 지연, 도착 시각
df_subset['PrevDest'] = df_subset.groupby('TailNum')['Dest'].shift(1)
df_subset['PrevArrDelay'] = df_subset.groupby('TailNum')['ArrDelay'].shift(1)
df_subset['PrevArrTime'] = df_subset.groupby('TailNum')['ArrTime'].shift(1)
df_subset['PrevDate'] = df_subset.groupby('TailNum')['Date'].shift(1)

# 이전 비행의 도착 공항 == 현재 비행의 출발 공항 → 연결된 항공편
df_subset['IsConnected'] = (df_subset['Origin'] == df_subset['PrevDest'])

# ===============================
# 4. 연결된 항공편만 추출
# ===============================
df_connected = df_subset[df_subset['IsConnected']].copy()
print("연결된 항공편 개수:", df_connected.shape[0])

# ===============================
# 5. 0보다 큰 지연만 필터링
# ===============================
# 이전 도착 지연과 현재 출발 지연이 모두 0보다 큰 경우만
df_filtered = df_connected.dropna(subset=['PrevArrDelay','DepDelay'])
df_filtered = df_filtered[(df_filtered['PrevArrDelay'] > 0) & (df_filtered['DepDelay'] > 0)]
print("0 초과 지연 (이전도착 & 현재출발) 항공편 개수:", df_filtered.shape[0])

# ===============================
# 6. 전체 상관분석 & 산점도 (필터링된 데이터)
# ===============================
overall_corr = df_filtered[['PrevArrDelay', 'DepDelay']].corr().iloc[0, 1]
print("전체 상관계수 (PrevArrDelay vs DepDelay):", overall_corr)

plt.figure(figsize=(10,6))
sns.scatterplot(data=df_filtered, x='PrevArrDelay', y='DepDelay', hue='TailNum')
plt.title("이전 도착 지연 vs. 현재 출발 지연")
plt.xlabel("이전 도착 지연")
plt.ylabel("현재 출발 지연")
plt.legend(title='TailNum')
plt.tight_layout()
plt.show()
