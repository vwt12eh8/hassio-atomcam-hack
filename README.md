# HomeAssistant × ATOMCam(Hacked)
[mnakada/atomcam_tools](https://github.com/mnakada/atomcam_tools)を導入済みのATOMCamシリーズをHomeAssistantから利用できるようにするためのカスタムコンポーネントです。

## 注意
- HomeAssistantはVer.2022.4.0以上である必要があります
- 上記を導入していない公式状態のATOMCamシリーズは連携できません
- HomeAssistantにカスタムコンポーネントをインストールする方法は各自で調べてください
- atomcam_toolsのログイン認証には対応していません（要望があれば対応検討します）

## 主な機能
- cameraエンティティによる映像表示
- ATOMCam Hack画面からできる一部設定の取得および変更
- updateエンティティを用いたatomcam_toolsのアップデート

## 開発方針
- atomcam_toolsの機能を全て実装している訳ではありません
- 機能追加は要望があれば検討します。直接PRでも構いません
- バグ報告や質問などはIssueでお願いします
- ブランチ戦略はGitHub Flowを採用します

## 免責事項
- 当カスタムコンポーネントやatomcam_toolsはアトムテック株式会社様の公式ツールではありません
  - メリット・デメリットをよく理解の上で導入してください
    - [atomcam_toolsのREADME](https://github.com/mnakada/atomcam_tools#readme)もよくお読みください
    - 当カスタムコンポーネントに関する動作保証およびユーザサポートはいたしません
    - 当カスタムコンポーネントを使用したことによって、ATOMCamの製品保証が無効となる場合があります
  - 当カスタムコンポーネントやatomcam_toolsについて、アトムテック株式会社様に問い合わせることは謹んでください
  - 当カスタムコンポーネントについて、atomcam_toolsのIssueで取り上げることも謹んでください
  - 全てのバグ修正や機能追加などに対応する保証はいたしません
