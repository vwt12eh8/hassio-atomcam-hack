![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)

# HomeAssistant × ATOMCam(Hacked)
[mnakada/atomcam_tools](https://github.com/mnakada/atomcam_tools)を導入済みのATOMCamシリーズをHomeAssistantから利用できるようにするためのカスタムコンポーネントです。

## 注意
- HomeAssistantはVer.2022.7.0以上である必要があります
- atomcam_toolsを導入していない公式状態のATOMCamシリーズは連携できません
- HomeAssistantにカスタムコンポーネントをインストールする方法は各自で調べてください
- atomcam_toolsのログイン認証には対応していません（要望があれば対応検討します）
- 将来のatomcam_toolsの仕様変更により動作しなくなる可能性があります
- 当カスタムコンポーネントやatomcam_toolsはアトムテック株式会社様の公式ツールではありません
  - メリット・デメリットをよく理解の上で導入してください
    - [atomcam_toolsのREADME](https://github.com/mnakada/atomcam_tools#readme)もよくお読みください
    - 当カスタムコンポーネントに関する動作保証およびユーザサポートはいたしません
    - 当カスタムコンポーネントやatomcam_toolsを使用したことによって、ATOMCamの製品保証が無効となる場合があります
  - 当カスタムコンポーネントやatomcam_toolsについて、アトムテック株式会社様に問い合わせることは謹んでください
  - 当カスタムコンポーネントについて、atomcam_toolsのIssueで取り上げることも謹んでください
  - 全てのバグ修正や機能追加などに対応する保証はいたしません

## 主な機能
- cameraエンティティによる映像表示
- ATOMCam Hack画面からできる一部設定の取得および変更
- updateエンティティを用いたatomcam_toolsのアップデート

## 開発方針
- atomcam_toolsの機能を全て実装している訳ではありません
- 機能追加は要望があれば検討します。直接PRでも構いません
- バグ報告や質問などはIssueでお願いします

## Q&A
### なぜセットアップ時にMACアドレスを入力する必要があるのですか？
内部で使用するUniqueIDに使用するためです。
これにより、同一のATOMCamを重複登録してしまうことを防ぎます。

入力する際は、大文字小文字は問わず、`:`や`-`は付けても省略してもどちらでも入力できます。

なお、HomeAssistantの自動検出機能から登録する場合、MACアドレスは自動的に取得されます。

### MACアドレスはどうやって取得しますか？
公式アプリのデバイス情報から確認することができます。

### セットアップ後、ATOMCamのIPアドレスが変わりました
通常はHomeAssistantの自動検出機能により自動更新されます。

もし更新されない場合、既存の設定は削除せずに、新規デバイスとして追加し直すことで設定を更新できます。
その際、MACアドレスは既存のものから変えずに登録してください。

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=atomcam_hack)
