# HW6
김영헌 · 21011658

## 실행 방법
1. .venv 에서 jupyter 로 hw6.ipynb 를 Run All
2. flask --app app run 뒤 http://127.0.0.1:5000/api/docs

- 가상환경은 6장 `data_analysis` 것 그대로. 패키지 : `pip install pandas scikit-learn joblib flask flask-restx jupyter ipykernel` (scikit-learn 1.9.1 에서 실행)
- `HW6/` 에서 실행. Run All 하면 단계 ⑥ 에서 `sales_model.pkl` 이 다시 만들어짐
- /api/docs 에서 POST `/api/sales/predict` → Try it out → Execute. 그 화면이 `docs.png` (Response body `{"total_sales": 8000000}`)

| 파일 | 내용 |
|---|---|
| `hw6.ipynb` | 단계 ① ~ ⑦. Restart → Run All 뒤 저장 (출력 포함) |
| `sales_clean.csv` | 입력. HW5 단계 ④ 에서 만든 파일 그대로 (1004 줄) |
| `sales_model.pkl` | 단계 ⑥ 에서 저장한 linear regression + qp |
| `app.py` | POST `/api/sales/predict`. `{"quantity", "unit_price"}` → `{"total_sales": 정수}` |
| `docs.png` | Swagger UI 에서 수량 40 · 단가 200,000 으로 Execute 한 화면 |
| `README.md` | 이 파일 |

## 단계 ③ 답
- linear regression 의 규칙은 `a × 수량 + b × 단가 + c` 모양 (학습 결과 `251,541 × 수량 + 49 × 단가 − 12,387,684`) 이라 두 열을 곱한 항이 없음
- 실제 규칙은 `총액 = 수량 × 단가`. 곱셈을 직선의 합으로 흉내만 내서 나머지 14 % 를 못 맞추고 0.862 에 멈춤
- qp (= 수량 × 단가) 를 열로 주면 계수 `[0, 0, 1]`, 절편 0 → `총액 = qp` 로 실제 규칙과 똑같아져 1.0

## 단계 ⑤ 결정과 이유
- **max_depth 8**. cross-validation 평균 0.992 · std 0.000 이고 그 뒤 (12 · None) 로는 0.003 차이뿐인데 잎은 250 개로 781 · 800 개의 1/3. 점수가 거의 같으면 단순한 쪽
- training 1.000 과 test 0.994 의 차이가 작은 이유 : `총액 = 수량 × 단가` 라는 규칙이 실제로 있어서 잘게 나눠 외운 것이 처음 보는 줄에도 그대로 맞음

| max_depth | 1 | 2 | 3 | 5 | 8 | 12 | None |
|---|---|---|---|---|---|---|---|
| 잎 | 2 | 4 | 8 | 32 | 250 | 781 | 800 |
| training R² | 0.361 | 0.739 | 0.876 | 0.972 | 0.998 | 1.000 | 1.000 |
| test R² | 0.346 | 0.711 | 0.846 | 0.961 | 0.991 | 0.994 | 0.994 |
| cross-validation 평균 (std) | | | 0.845 (0.019) | 0.961 (0.003) | 0.992 (0.000) | 0.995 (0.000) | 0.995 (0.001) |

- None 의 평균이 수업 자료 (0.994) 와 다른 이유 : 이 `sales_clean.csv` 는 HW5 에서 직접 만든 것이라 총액 131 줄이 수업 자료 파일과 0.00000001 원 미만 (float 저장 자리) 으로 다름. 제한 없는 tree 는 이 차이로도 잎 나눔이 조금 바뀌어 평균 0.9946 (수업 자료 파일로는 0.9944) → 셋째 자리 반올림만 갈림. 나머지 숫자는 모두 같음

## 단계 ⑦ 답
- 수량 40 · 단가 200,000 에 linear + qp 는 8,000,000, tree (depth 8) 는 7,362,301, 실제 곱은 8,000,000
- **linear regression + qp** 를 고름. 실제 곱과 한 원도 다르지 않음. tree 는 잎에 모인 training 줄들의 평균을 내놓는 계단 모양이라 637,699 원 (약 8 %) 모자람
- 공식이 있으니 서버에서 곱만 해도 같은 답이지만, model 을 API 로 내보내는 과제라 그 공식을 그대로 배운 linear + qp 를 올림
