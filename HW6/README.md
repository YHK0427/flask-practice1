# HW6 21011658 김영헌

## 실행 방법

1. 이 폴더(`HW6/`)에 `hw6.ipynb` · `sales_clean.csv` · `sales_model.pkl` · `app.py` 가 같이 있어야 함
2. 가상환경에 패키지 설치 : `pip install pandas scikit-learn joblib flask flask-restx jupyter ipykernel` (scikit-learn 1.9.1 에서 실행)
3. VSCode 에서 `hw6.ipynb` 를 열고 Select Kernel → 가상환경 선택 → Restart → Run All. 단계 ⑥ 에서 `sales_model.pkl` 이 다시 만들어짐
4. `HW6/` 에서 `flask --app app run` 뒤 http://127.0.0.1:5000/api/docs → POST `/api/sales/predict` → Try it out → Execute

| 파일 | 내용 |
|---|---|
| `hw6.ipynb` | 단계 ① ~ ⑦. Run All 뒤 저장 (출력 포함) |
| `sales_clean.csv` | 입력. HW5 에서 만든 파일 그대로 (1004 줄) |
| `sales_model.pkl` | 단계 ⑥ 에서 저장한 linear regression + qp |
| `app.py` | POST `/api/sales/predict`. `{"quantity", "unit_price"}` → `{"total_sales": 정수}` |
| `docs.png` | Swagger UI 에서 수량 40 · 단가 200,000 으로 Execute 한 화면. Response body `{"total_sales": 8000000}` |
| `README.md` | 이 파일 |

## 단계 ① ~ ② : 결과

- ① training 803 · test 201 (test_size=0.2, random_state=0)
- ② test R² : linear 0.862 · linear + qp 1.0 · decision tree (제한 없음) 0.994

## 단계 ③ 답 : linear regression 이 0.862 에 그친 이유, qp 를 더하면 1.0 이 되는 이유

- linear regression 의 규칙은 `a × 수량 + b × 단가 + c` 모양. 학습 결과 `총액 ≈ 251,541 × 수량 + 49 × 단가 − 12,387,684` 로, 두 열을 곱한 항이 들어갈 자리가 없음
- 실제 규칙은 `총액 = 수량 × 단가` (HW5 ③ 에서 불일치 0 으로 맞춰 둠). 곱의 모양을 직선 합으로 흉내만 내서 남은 14 % 가 오차로 남아 0.862 에 멈춤
- qp (= 수량 × 단가) 칸을 주면 계수가 `[0, 0, 1]`, 절편 0 으로 나와 `총액 = 1 × qp` 가 되어 실제 규칙과 똑같아짐 → 1.0

## 단계 ④ ~ ⑤ : max_depth 결정과 이유

| max_depth | 1 | 2 | 3 | 5 | 8 | 12 | None |
|---|---|---|---|---|---|---|---|
| 잎 | 2 | 4 | 8 | 32 | 250 | 781 | 800 |
| training R² | 0.361 | 0.739 | 0.876 | 0.972 | 0.998 | 1.000 | 1.000 |
| test R² | 0.346 | 0.711 | 0.846 | 0.961 | 0.991 | 0.994 | 0.994 |
| cross-validation 평균 (std) | | | 0.845 (0.019) | 0.961 (0.003) | 0.992 (0.000) | 0.995 (0.000) | 0.995 (0.001) |

- **max_depth 8** 을 고름. cross-validation 평균 0.992 · std 0.000 으로 12 · None (0.995) 과 0.003 차이밖에 안 나는데 잎은 250 개로 781 · 800 개의 1/3. 점수가 거의 같으면 단순한 쪽
- 제한 없음의 training 1.000 과 test 0.994 차이가 작은 이유 : `총액 = 수량 × 단가` 라는 규칙이 데이터에 실제로 있어서, 잘게 나눠 외워도 처음 보는 test 줄에서 그대로 맞음 (외운 것이 잡음이 아니라 규칙)
- None 의 cross-validation 평균이 수업 자료 (0.994) 와 0.001 다른 것은 HW5 에서 직접 만든 `sales_clean.csv` 를 써서 생긴 반올림 차이

## 단계 ⑦ 답 : 어느 model 인가, 왜

수량 40 · 단가 200,000 을 넣으면 linear + qp **8,000,000**, tree (depth 8) **7,362,301**, 실제 곱 40 × 200,000 = **8,000,000**.

- **linear regression + qp** 를 서버에 올림. 실제 곱 8,000,000 과 한 원도 안 다르고, test R² 도 1.0
- tree (depth 8) 는 637,699 원 (약 8 %) 모자람. tree 는 잎 하나에 들어온 training 줄들의 평균을 내놓아서 계단 모양으로만 답하므로, 잎 안에서 값이 곱으로 커지는 것을 못 따라감. test R² 0.991 도 잎 평균이 대체로 비슷해서 나온 점수일 뿐 한 주문의 금액은 틀릴 수 있음
- 사실 규칙이 `수량 × 단가` 로 정해져 있으니 서버에서 곱만 해도 같은 답 (model 이 꼭 필요하지는 않음). 그래도 과제가 model 을 API 로 내보내는 것이라, 규칙을 그대로 배운 linear + qp 를 고름
