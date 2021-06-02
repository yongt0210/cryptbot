# 가상화폐 자동 매매 프로그램
Bithumb API 연동을 통해 가상화폐를 자동으로 거래하는 프로그램 입니다.

## 전략
* 거래량 상위 5개 가상화폐를 거래 대상으로 지정합니다.
* 변동성돌파전략(Volatility Breakout) 사용
  1. 전일 range 값 계산: (전일 고가 - 전일 저가) * 0.5
  2. 매수: 현시간 가격 >= 금일 시가 + 전일 range
  3. 매도: 다음날 0시에 전량 매도

## 참조
* https://wikidocs.net/21888
* https://cafe.naver.com/invest79/861
