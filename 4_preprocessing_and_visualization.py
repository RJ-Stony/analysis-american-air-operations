# --- 4. 날씨는 비행기 지연을 얼마나 잘 예측할 수 있나? ---

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# seaborn의 스타일 적용
sns.set_theme(style="whitegrid")

# 한글 폰트 설정 (Windows 기준)
from matplotlib import font_manager, rc
import platform

if platform.system() == 'Windows':
    path = 'c:/Windows/Fonts/malgun.ttf'
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
elif platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
else:
    print('Check your OS system')

# 1. 파일 병합
## 기상 지연 데이터는 2004~2008에만 존재하기 때문에 해당 파일만 저장해서 병합
file_list = [f'./data/dataverse_files_2000-2008/200{i}.csv' for i in range(4, 9)]
dfs = []

for file_path in file_list:
    try:
        df = pd.read_csv(file_path, encoding='latin-1',
                         usecols=['WeatherDelay', 'ArrDelay', 'DepDelay', 'Origin', 'Dest', 'Month'])
        dfs.append(df)
        print(f"File {file_path} loaded, shape: {df.shape}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

total_df = pd.concat(dfs, ignore_index=True)
total_df.shape

# 2. 데이터 전처리
for col in ['WeatherDelay', 'ArrDelay', 'DepDelay', 'Month']:
    total_df[col] = pd.to_numeric(total_df[col], errors='coerce')

## 결측치 제거
total_df.dropna(subset=['WeatherDelay', 'ArrDelay', 'DepDelay', 'Month', 'Origin', 'Dest'], inplace=True)
total_df.shape

# 3. 필터링 (WeatherDelay, ArrDelay, DepDelay 모두 0보다 크고, WeatherDelay < 1200)
df_filtered = total_df[
    (total_df['WeatherDelay'] > 0) &
    (total_df['ArrDelay'] > 0) &
    (total_df['DepDelay'] > 0) &
    (total_df['WeatherDelay'] < 1200)
].copy()

df_filtered.shape
df_filtered[['WeatherDelay', 'ArrDelay', 'DepDelay']].describe()

# 4. 상관관계 분석
corr_matrix = df_filtered[['WeatherDelay', 'ArrDelay', 'DepDelay']].corr()
plt.figure(figsize=(6, 5))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("지연 변수 간 상관관계")
plt.show()

# 5. 산점도 그래프 (WeatherDelay vs. ArrDelay/DepDelay)
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.scatterplot(data=df_filtered, x='WeatherDelay', y='ArrDelay', alpha=0.3, color='tab:blue')
plt.title('기상 지연 vs. 도착 지연')

plt.subplot(1, 2, 2)
sns.scatterplot(data=df_filtered, x='WeatherDelay', y='DepDelay', alpha=0.3, color='tab:orange')
plt.title('기상 지연 vs. 출발 지연')

plt.tight_layout()
plt.show()
