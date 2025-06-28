Qubi通信プロトコル実装 要求仕様書
1. プロジェクト概要
プロジェクト名: Qubi Communication Protocol
目的: モジュール型ソーシャルロボット「Qubi」のWeb-ESP32間UDP通信プロトコルの実装
公開先: GitHub Pages (https://[username].github.io/qubi-protocol/)
2. 技術要件
2.1 ドキュメントシステム

静的サイトジェネレータ: Docusaurus v3.x または MkDocs Material
デプロイ: GitHub Actions による自動デプロイ
バージョン管理: Git-based versioning

2.2 実装言語

ESP32/Arduino: C++
Web Interface: TypeScript
サンプルコード: Python, JavaScript/TypeScript, C++

3. 機能要件
3.1 通信プロトコル
json{
  "version": "1.0",
  "timestamp": <unix_timestamp_ms>,
  "sequence": <optional_number>,
  "commands": [
    {
      "module_id": "<string>",
      "module_type": "<actuator|display|mobile|sensor|custom>",
      "action": "<string>",
      "params": {
        // action-specific parameters
      }
    }
  ]
}
通信仕様:

プロトコル: UDP
ポート: 8888 (デフォルト)
エンコーディング: UTF-8
最大パケットサイズ: 1024 bytes
データ形式: JSON

3.2 モジュール別実装
3.2.1 アクチュエータモジュール
Actions:
- set_servo: サーボモータ角度制御
  - angle: 0-180 (必須)
  - speed: 0-255 (オプション)
  - easing: linear|ease-in|ease-out (オプション)
- set_position: 3D座標指定
  - x, y, z: ミリメートル単位
3.2.2 ディスプレイモジュール
Actions:
- set_eyes: 視線制御
  - left_eye: {x, y} ピクセル座標
  - right_eye: {x, y} ピクセル座標
  - blink: boolean (オプション)
- set_expression: 表情変更
  - expression: happy|sad|surprised|neutral|angry
  - intensity: 0-100 (オプション)
4. 実装要件
4.1 ライブラリ構造
qubi-protocol/
├── docs/                    # Docusaurus/MkDocs ソース
│   ├── docs/               
│   │   ├── intro.md
│   │   ├── getting-started/
│   │   ├── api-reference/
│   │   └── tutorials/
│   ├── src/                # カスタムコンポーネント
│   ├── static/             # 静的ファイル
│   └── docusaurus.config.js # または mkdocs.yml
├── libraries/
│   ├── arduino/
│   │   ├── QubiProtocol/
│   │   │   ├── QubiProtocol.h
│   │   │   ├── QubiProtocol.cpp
│   │   │   └── examples/
│   │   └── library.properties
│   ├── python/
│   │   ├── qubi_protocol/
│   │   ├── setup.py
│   │   └── requirements.txt
│   └── typescript/
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── examples/
├── tests/
├── .github/
│   └── workflows/
│       ├── docs.yml        # ドキュメントビルド
│       └── tests.yml       # テスト実行
└── README.md
4.2 ESP32/Arduinoライブラリ実装
cpp// QubiProtocol.h
class QubiModule {
protected:
    String moduleId;
    String moduleType;
    WiFiUDP udp;
    uint16_t port;
    
public:
    void begin(const String& id, const String& type, uint16_t port = 8888);
    void processMessages();
    virtual void handleCommand(const JsonObject& cmd) = 0;
    void sendResponse(uint16_t statusCode, const String& message, const JsonObject& data = {});
};

// 各モジュールタイプのベースクラス
class ActuatorModule : public QubiModule {};
class DisplayModule : public QubiModule {};
class MobileModule : public QubiModule {};
class SensorModule : public QubiModule {};
4.3 Web/TypeScriptライブラリ実装
typescript// qubi-protocol.ts
export interface QubiCommand {
  module_id: string;
  module_type: ModuleType;
  action: string;
  params: Record<string, any>;
}

export class QubiController {
  constructor(private host: string, private port: number = 8888) {}
  
  async sendCommand(command: QubiCommand): Promise<QubiResponse>;
  async sendBatch(commands: QubiCommand[]): Promise<QubiResponse[]>;
  async discover(): Promise<QubiModule[]>;
}

// 型安全なビルダーパターン
export class CommandBuilder {
  actuator(id: string): ActuatorCommandBuilder;
  display(id: string): DisplayCommandBuilder;
  // ...
}
5. ドキュメント要件
5.1 Docusaurus設定
javascript// docusaurus.config.js
module.exports = {
  title: 'Qubi Protocol',
  tagline: 'Modular Social Robot Communication Protocol',
  url: 'https://[username].github.io',
  baseUrl: '/qubi-protocol/',
  onBrokenLinks: 'throw',
  favicon: 'img/favicon.ico',
  organizationName: '[username]',
  projectName: 'qubi-protocol',
  
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/[username]/qubi-protocol/tree/main/',
          remarkPlugins: [require('remark-math')],
          rehypePlugins: [require('rehype-katex')],
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/[username]/qubi-protocol/tree/main/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
  
  themeConfig: {
    navbar: {
      title: 'Qubi Protocol',
      logo: {
        alt: 'Qubi Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: 'Docs',
        },
        {to: '/blog', label: 'Blog', position: 'left'},
        {
          href: 'https://github.com/[username]/qubi-protocol',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/intro',
            },
            {
              label: 'API Reference',
              to: '/docs/api-reference',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Discord',
              href: 'https://discord.gg/qubi',
            },
            {
              label: 'Forum',
              href: 'https://forum.qubi.dev',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Qubi Project. Built with Docusaurus.`,
    },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
      additionalLanguages: ['arduino', 'json'],
    },
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'qubi-protocol',
    },
  },
};
5.2 ドキュメント構成
docs/
├── intro.md                    # はじめに
├── getting-started/
│   ├── installation.md         # インストール
│   ├── quick-start.md         # クイックスタート
│   └── first-robot.md         # 最初のロボット作成
├── protocol/
│   ├── overview.md            # プロトコル概要
│   ├── message-format.md      # メッセージフォーマット
│   └── error-handling.md      # エラーハンドリング
├── modules/
│   ├── actuator.md           # アクチュエータモジュール
│   ├── display.md            # ディスプレイモジュール
│   ├── mobile.md             # モバイルモジュール
│   └── sensor.md             # センサモジュール
├── api-reference/
│   ├── arduino.md            # Arduino API
│   ├── python.md             # Python API
│   └── typescript.md         # TypeScript API
├── tutorials/
│   ├── custom-module.md      # カスタムモジュール作成
│   ├── web-interface.md      # Webインターフェース開発
│   └── advanced-patterns.md  # 高度なパターン
└── contributing/
    ├── guidelines.md         # 貢献ガイドライン
    └── code-style.md         # コードスタイル
6. 非機能要件
6.1 パフォーマンス

UDP通信レイテンシ: < 10ms (ローカルネットワーク)
メッセージ処理: 100 messages/sec以上
メモリ使用量: ESP32で < 50KB

6.2 互換性

ESP32: Arduino Core 2.x以上
Python: 3.8以上
Node.js: 18.x以上
ブラウザ: Chrome/Firefox/Safari最新版

6.3 テスト

単体テスト: 各言語でカバレッジ80%以上
統合テスト: プロトコル準拠性テスト
E2Eテスト: 実機での動作確認

7. 成果物

ライブラリ

Arduino/ESP32ライブラリ (Arduino Library Manager対応)
Pythonパッケージ (PyPI公開)
TypeScript/npmパッケージ (npm公開)


ドキュメント

Docusaurusベースのドキュメントサイト
API リファレンス (自動生成)
チュートリアル・サンプルコード


ツール

プロトコルバリデータ
モジュールシミュレータ
デバッグツール


CI/CD

GitHub Actions ワークフロー
自動テスト・ビルド・デプロイ



8. オープンソースドキュメント管理のベストプラクティス
推奨ツール・サービス

Docusaurus (推奨)

React ベースで拡張性が高い
バージョニング機能内蔵
検索機能 (Algolia) 統合
i18n サポート


MkDocs Material

シンプルで設定が簡単
Material Design
豊富なプラグイン


補助ツール

TypeDoc: TypeScript APIドキュメント自動生成
Doxygen: C++ APIドキュメント自動生成
Sphinx: Python APIドキュメント自動生成
Mermaid: 図表作成
PlantUML: UML図作成



GitHub Pages デプロイ設定
yaml# .github/workflows/deploy-docs.yml
name: Deploy Docs

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
          
      - name: Install dependencies
        run: npm ci
        
      - name: Build website
        run: npm run build
        
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        if: github.ref == 'refs/heads/main'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
この仕様書を基に、コーディングエージェントが実装を進められます。特にDocusaurusを使用することで、モダンで検索性の高いドキュメントサイトを構築できます。