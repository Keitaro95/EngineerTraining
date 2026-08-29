
// Subjectの状態が変化した時、 Observerへ通知する
// SubjectはObserverの具体的な型を知らなくていい

// オブザーバーの定義
interface Observer<T> {
    update(data: T): void;
}

// 抽象的な層
class Subject<T> {
    // observerの中身は問わない
    // PriceDisplay　や PriceAlert が入る
    private observers = new Set<Observer<T>>();

    // obserberを addする
    attach(o: Observer<T>): void { this.observers.add(o); }
    // observerを deleteする
    detach(o: Observer<T>): void { this.observers.delete(o); }

    //　通知する
    protected notify(data: T): void {
        // 状態が変化した時に通知する
        // ただし 通知する先： updateの

        for (const o of this.observers) o.update(data);
    }
}

type StockPrice = { symbol: string; price: number };


// 取り扱う対象：Subject
class Stock extends Subject<StockPrice> {
    constructor(private symbol: string, private price = 0) { super(); }

    setPrice(price: number): void {
        this.price = price;
        this.notify({ symbol: this.symbol, price });
    }
}

// Observerは通知を受け取った後、どう振る舞うかを決める
// ただ表示する場合こうする：updateの定義
class PriceDisplay implements Observer<StockPrice> {
    update({ symbol, price }: StockPrice): void {
        console.log(`[表示] ${symbol}: ¥${price}`);
    }
}

// Observerは通知を受け取った後、どう振る舞うかを決める
// アラートする場合こうする：updateの定義
class PriceAlert implements Observer<StockPrice> {
    constructor(private threshold: number) {}
    update({ symbol, price }: StockPrice): void {
        if (price > this.threshold) console.log(`[警告] ${symbol} が ${this.threshold} を超過`)
    }
}

const stock = new Stock("ACME"); // symbolがこれ
const display = new PriceDisplay(); 

stock.attach(display); // PriceDisplayを addする
stock.attach(new PriceAlert(1000)); // PriceAlertを addする

// こうして stockに振る舞いをアタッチする

stock.setPrice(950); // 950円ならまだアラートでない
stock.setPrice(1200); // 1000円超過なのでアラート

stock.detach(display);
stock.setPrice(800);