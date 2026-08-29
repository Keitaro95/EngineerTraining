// Factory Method（ファクトリーメソッド）— 生成パターン

// 目的：オブジェクト生成のインターフェースだけを定義し、
// 「どのクラスを実体化するか」の決定はサブクラスに委ねる。
// 呼び出し側は具象クラスを知らずに済み、
// 新しい種類を追加しても既存コードを変更しなくてよくなります（開放閉鎖の原則）

// 構成要素
// Product：生成されるオブジェクトの共通インターフェース
// ConcreteProduct：具体的な生成物
// Creator：factoryMethod() を宣言し、それを使う共通ロジックを持つ
// ConcreteCreator：factoryMethod() をオーバーライドして具象 Product を返す


// 共通インターフェース
interface Notifier {
    send(message: string): string;
}

// Email用の通知
class EmailNotifier implements Notifier {
  send(message: string) { return `Email: ${message}`; }
}
// スラック用の通知
class SlackNotifier implements Notifier {
  send(message: string) { return `Slack: ${message}`; }
}

// 通知の仕方を決める。抽象interface
abstract class NotificationService {
  protected abstract createNotifier(): Notifier; // ← Factory Method

  notify(message: string): string {
    const notifier = this.createNotifier();
    return notifier.send(message.trim());
  }
}

// ConcreteCreator
class EmailService extends NotificationService {
  protected createNotifier() { return new EmailNotifier(); }
}
class SlackService extends NotificationService {
  protected createNotifier() { return new SlackNotifier(); }
}


const service: NotificationService = new SlackService();
console.log(service.notify(" デプロイ完了 "));